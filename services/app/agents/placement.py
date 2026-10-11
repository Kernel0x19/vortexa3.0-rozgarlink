"""PlacementAgent — recommendation and deadline-scan layer for full-time jobs.

Filter dimensions supported:
  - query        : semantic search across title + company + description
  - location     : substring match against raw_data location
  - work_type    : remote | onsite | hybrid
  - salary_min   : minimum CTC in LPA (lakhs per annum)
  - experience   : fresher | 0-1 | 1-3 | 3+
  - source       : platform slug (naukri, linkedin, wellfound, …)
"""

from __future__ import annotations

import logging
from collections import defaultdict
from datetime import date, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from app.db.models import Application, Notification, Opportunity, OpportunityCategory
from app.notifications.orchestrator import NotificationOrchestrator
from app.notifications.service import NotificationType

logger = logging.getLogger(__name__)


# ── small helpers ─────────────────────────────────────────────────────────────

def _loc_matches(opp: Opportunity, location_filter: str) -> bool:
    loc = ((opp.raw_data or {}).get("location") or "").lower()
    f = location_filter.lower()
    return f in loc or "remote" in loc or "work from home" in loc or f == "remote"


def _work_type(opp: Opportunity) -> str:
    loc = ((opp.raw_data or {}).get("location") or "").lower()
    if "remote" in loc or "work from home" in loc:
        return "remote"
    if "hybrid" in loc:
        return "hybrid"
    return "onsite"


def _salary_lpa(opp: Opportunity) -> Optional[float]:
    """Return best-guess annual CTC in LPA from amount_min/max (stored in ₹/month)."""
    monthly = opp.amount_min or opp.amount_max
    if monthly:
        return round(monthly * 12 / 100_000, 2)
    return None


def _has_apply_url(opp: Opportunity) -> bool:
    from urllib.parse import urlparse
    url = (opp.application_url or "").strip()
    if not url or url == "#":
        return False
    p = urlparse(url)
    return bool(p.scheme in {"http", "https"} and p.netloc)


# ── agent ─────────────────────────────────────────────────────────────────────

class PlacementAgent:
    """Orchestration layer for full-time job (placement) recommendations."""

    def recommend(
        self,
        db: Session,
        profile=None,
        query: str | None = None,
        location: str | None = None,
        work_type: str | None = None,
        salary_min: float | None = None,
        experience: str | None = None,
        source: str | None = None,
        limit: int = 30,
    ) -> dict:
        """Return job recommendations with optional filters.

        Returns dict with keys: matches (list[dict]), total (int), readiness_score (float).
        """
        jobs: list[Opportunity] = (
            db.query(Opportunity)
            .filter_by(category=OpportunityCategory.PLACEMENT, is_active=True)
            .all()
        )
        jobs = [j for j in jobs if _has_apply_url(j)]

        # Platform filter
        if source:
            jobs = [j for j in jobs if j.source.lower() == source.lower()]

        # Hard filters
        if location:
            jobs = [j for j in jobs if _loc_matches(j, location)]
        if work_type:
            jobs = [j for j in jobs if _work_type(j) == work_type.lower()]
        if salary_min is not None:
            jobs = [j for j in jobs if (_salary_lpa(j) or 0) >= salary_min]
        if experience:
            exp_lower = experience.lower()
            jobs = [
                j for j in jobs
                if exp_lower in ((j.raw_data or {}).get("experience", "") or "").lower()
                or exp_lower == "fresher" and (j.raw_data or {}).get("experience", "fresher") in ("fresher", "0", "0-1")
            ]

        # Semantic search
        if query:
            from app.knowledge.hybrid_rag import HybridRAG
            try:
                rag = HybridRAG()
                semantic = rag.semantic_search(query, limit=limit * 2, category="placement")
                id_order = {s["opportunity_id"]: s["score"] for s in semantic if s.get("opportunity_id")}
                if id_order:
                    in_res = sorted([j for j in jobs if j.id in id_order], key=lambda j: id_order.get(j.id, 0), reverse=True)
                    not_in = [j for j in jobs if j.id not in id_order]
                    jobs = in_res + not_in
            except Exception:
                pass
            jobs = jobs[: limit * 3]
        else:
            # Source-balanced sampling
            buckets: dict[str, list] = defaultdict(list)
            for j in jobs:
                buckets[j.source].append(j)
            n_sources = max(len(buckets), 1)
            per_source = max(5, (limit * 3) // n_sources)
            balanced: list[Opportunity] = []
            for src_jobs in buckets.values():
                balanced.extend(src_jobs[:per_source])
            seen = {j.id for j in balanced}
            for j in jobs:
                if j.id not in seen:
                    balanced.append(j)
            jobs = balanced[: limit * 3]

        # Build match cards (no eligibility scoring — jobs are open to all)
        matches = []
        for j in jobs[:limit]:
            salary = _salary_lpa(j)
            raw = j.raw_data or {}
            matches.append({
                "opportunity": {
                    "id": j.id,
                    "source": j.source,
                    "title": j.title,
                    "description": j.description,
                    "company": raw.get("company") or raw.get("organization", ""),
                    "location": raw.get("location", ""),
                    "work_type": raw.get("work_type", _work_type(j)),
                    "experience": raw.get("experience", "Fresher / 0–1 yr"),
                    "salary_lpa": salary,
                    "amount_min": j.amount_min,
                    "amount_max": j.amount_max,
                    "deadline": j.deadline.isoformat() if j.deadline else None,
                    "application_url": j.application_url,
                    "tags": j.tags or [],
                    "documents_required": j.documents_required or [],
                },
                "match_score": round(75 + (hash(j.id) % 20), 1),  # deterministic placeholder
            })

        readiness = getattr(profile, "readiness_score", 0.0) if profile else 0.0
        return {"matches": matches, "total": len(matches), "readiness_score": readiness}

    def start_application(
        self,
        db: Session,
        user_id: str,
        opportunity_id: str,
        saved: bool = False,
    ) -> Application:
        from app.db.models import ApplicationState
        opp = db.query(Opportunity).filter_by(id=opportunity_id).first()
        if not opp:
            raise ValueError("Job not found")

        existing = db.query(Application).filter_by(
            user_id=user_id, opportunity_id=opportunity_id
        ).first()
        if existing:
            if saved and not existing.saved:
                existing.saved = True
                db.commit()
            return existing

        app = Application(
            user_id=user_id,
            opportunity_id=opportunity_id,
            state=ApplicationState.DISCOVERED,
            match_score=75.0,
            eligibility_result={},
            checklist=[],
            saved=saved,
            progress_pct=10,
        )
        db.add(app)
        db.commit()
        db.refresh(app)
        return app

    def scan_deadlines(self, db: Session) -> int:
        """Dispatch 7-day and 2-day reminders for tracked jobs."""
        import asyncio

        count = 0
        apps = (
            db.query(Application)
            .join(Opportunity)
            .filter(
                Opportunity.category == OpportunityCategory.PLACEMENT,
                Application.saved.is_(True),
                Opportunity.deadline.isnot(None),
                Opportunity.deadline.in_([
                    date.today() + timedelta(days=7),
                    date.today() + timedelta(days=2),
                ]),
            )
            .all()
        )
        for app in apps:
            opp = app.opportunity
            days = (opp.deadline - date.today()).days
            title = f"Job deadline in {days} days: {opp.title[:80]}"
            if db.query(Notification).filter_by(user_id=app.user_id, title=title).first():
                continue
            asyncio.run(NotificationOrchestrator(db).send_notification(
                user_id=app.user_id,
                notification_type=NotificationType.DEADLINE_REMINDER,
                title=title,
                body=f"Application for {opp.title} closes in {days} days. Make sure your resume is ready.",
                metadata={"opportunity_id": opp.id, "deadline_days": days, "kind": "placement"},
                include_voice=days == 2,
            ))
            count += 1
        return count
