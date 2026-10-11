from __future__ import annotations

import logging
import re
from collections import defaultdict
from itertools import islice
from typing import Optional
from urllib.parse import urlparse

from sqlalchemy.orm import Session

from app.db.models import (
    Application, ApplicationState, Opportunity, OpportunityCategory, StudentProfile,
)
from app.intelligence.recommendation import (
    apply_feedback_learning, compute_match_score, compute_readiness_score,
)
from app.knowledge.hybrid_rag import HybridRAG
from app.schemas import MatchResult, OpportunityResponse, RecommendationResponse
from app.workflow.engine import WorkflowEngine, build_checklist

logger = logging.getLogger(__name__)


# ─── small helpers ────────────────────────────────────────────────────────────

def _location_matches(opp: Opportunity, location_filter: str) -> bool:
    loc = ((opp.raw_data or {}).get("location") or "").lower()
    f   = location_filter.lower()
    return f in loc or "work from home" in loc or "remote" in loc or f == "remote"


def _work_type(opp: Opportunity) -> str:
    loc = ((opp.raw_data or {}).get("location") or "").lower()
    if "work from home" in loc or "remote" in loc:
        return "remote"
    if "hybrid" in loc:
        return "hybrid"
    return "onsite"


def _duration_months(opp: Opportunity) -> Optional[int]:
    dur = ((opp.raw_data or {}).get("duration") or "").lower()
    m = re.search(r"(\d+)\s*month", dur)
    if m:
        return int(m.group(1))
    m = re.search(r"(\d+)\s*week", dur)
    if m:
        return max(1, int(m.group(1)) // 4)
    return None


def _has_direct_application_url(opp: Opportunity) -> bool:
    """Accept valid source URLs for opportunities."""
    url = (opp.application_url or "").strip()
    if not url or url == "#":
        return False
    parsed = urlparse(url)
    return bool(parsed.scheme in {"http", "https"} and parsed.netloc)


# ─── agent ────────────────────────────────────────────────────────────────────

class InternshipAgent:
    """Orchestration layer for internship recommendations.

    Shows only internships with a direct source application URL.
    """

    def __init__(self) -> None:
        self.rag = HybridRAG()
        self.workflow = WorkflowEngine()

    def recommend(
        self,
        db: Session,
        profile: StudentProfile | None,
        query: str | None = None,
        state: str | None = None,
        location: str | None = None,
        work_type: str | None = None,
        duration_max: int | None = None,
        stipend_min: int | None = None,
        source: str | None = None,
        limit: int = 30,
    ) -> RecommendationResponse:

        # Profile preferences are used to enrich the semantic query and boost
        # scores — they do NOT act as hard filters, so the full cross-platform
        # feed is always visible. Users can apply hard filters via the UI.
        prefs = (profile.preferences or {}) if profile else {}

        # 1. Fetch all active internships
        opportunities: list[Opportunity] = (
            db.query(Opportunity)
            .filter_by(category=OpportunityCategory.INTERNSHIP, is_active=True)
            .all()
        )
        opportunities = [o for o in opportunities if _has_direct_application_url(o)]

        # 2. State filter
        if state:
            opportunities = [
                o for o in opportunities
                if not o.state_filter or "ALL" in o.state_filter or state in o.state_filter
            ]

        # 3. Platform / source filter
        if source:
            opportunities = [o for o in opportunities if o.source.lower() == source.lower()]

        # 4. Hard filters
        if location or work_type or duration_max is not None or stipend_min is not None:
            filtered = []
            for o in opportunities:
                if location and not _location_matches(o, location):
                    continue
                if work_type and _work_type(o) != work_type.lower():
                    continue
                if duration_max is not None:
                    months = _duration_months(o)
                    if months is not None and months > duration_max:
                        continue
                if stipend_min is not None:
                    effective = o.amount_min or o.amount_max or 0
                    if effective < stipend_min:
                        continue
                filtered.append(o)
            opportunities = filtered

        # 5. Semantic search or source-balanced sampling
        if query:
            enriched = query
            if profile:
                parts = [query]
                if profile.stream:        parts.append(profile.stream)
                if profile.skills:        parts.extend((profile.skills or [])[:5])
                if isinstance(prefs.get("interests"), list):
                    parts.extend(prefs["interests"][:3])
                enriched = " ".join(parts)

            semantic = self.rag.semantic_search(enriched, limit=limit * 2, category="internship")
            id_order = {s["opportunity_id"]: s["score"] for s in semantic if s.get("opportunity_id")}
            if id_order:
                in_results  = sorted([o for o in opportunities if o.id in id_order],
                                     key=lambda o: id_order.get(o.id, 0), reverse=True)
                not_in      = [o for o in opportunities if o.id not in id_order]
                opportunities = in_results + not_in
            opportunities = opportunities[: limit * 3]
        else:
            # Source-balanced: take evenly from each platform so Internshala's
            # larger pool (100+ rows) doesn't crowd out dummy sources (5 rows each).
            buckets: dict[str, list] = defaultdict(list)
            for o in opportunities:
                buckets[o.source].append(o)
            n_sources  = max(len(buckets), 1)
            per_source = max(5, (limit * 3) // n_sources)
            balanced: list[Opportunity] = []
            for src_opps in buckets.values():
                balanced.extend(src_opps[:per_source])
            seen_ids = {o.id for o in balanced}
            for o in opportunities:
                if o.id not in seen_ids:
                    balanced.append(o)
            opportunities = balanced[: limit * 3]

        # 6. Score
        matches: list[MatchResult] = []
        for opp in opportunities:
            base, eligibility, reasons = compute_match_score(profile, opp)
            if profile:
                adjusted = apply_feedback_learning(profile, opp, base / 100.0, db)
                final    = min(adjusted * 100.0, 99.0)
            else:
                final = base
            matches.append(
                MatchResult(
                    opportunity=OpportunityResponse.model_validate(opp),
                    match_score=round(final, 1),
                    eligibility=eligibility,
                    reasons=reasons,
                )
            )

        matches.sort(key=lambda m: m.match_score, reverse=True)

        # Round-robin interleave so every platform is guaranteed to appear in
        # the final output, even when scores are tied (stable sort preserves
        # insertion order, causing late-added platforms like Internshala to be
        # sliced off when all scores are equal).
        src_buckets: dict[str, list[MatchResult]] = defaultdict(list)
        for m in matches:
            src_buckets[m.opportunity.source].append(m)
        # Sort bucket keys so output is deterministic
        src_keys = sorted(src_buckets.keys())
        interleaved: list[MatchResult] = []
        iters = {k: iter(src_buckets[k]) for k in src_keys}
        while len(interleaved) < limit:
            added = False
            for k in src_keys:
                if len(interleaved) >= limit:
                    break
                item = next(iters[k], None)
                if item is not None:
                    interleaved.append(item)
                    added = True
            if not added:
                break

        return RecommendationResponse(
            matches=interleaved,
            total=len(matches),
            readiness_score=compute_readiness_score(profile),
        )

    def start_application(
        self,
        db: Session,
        user_id: str,
        opportunity_id: str,
        profile: StudentProfile | None,
        saved: bool = False,
    ) -> Application:
        opp = db.query(Opportunity).filter_by(id=opportunity_id).first()
        if not opp:
            raise ValueError("Opportunity not found")

        existing = db.query(Application).filter_by(
            user_id=user_id, opportunity_id=opportunity_id
        ).first()
        if existing:
            if saved and not existing.saved:
                existing.saved = True
                db.commit()
            return existing

        base, eligibility, _ = compute_match_score(profile, opp)
        checklist = build_checklist(
            opp.documents_required or [],
            (profile.documents if profile else []) or [],
        )
        app = Application(
            user_id=user_id, opportunity_id=opportunity_id,
            state=ApplicationState.DISCOVERED, match_score=base,
            eligibility_result=eligibility, checklist=checklist,
            saved=saved, progress_pct=10,
        )
        db.add(app)
        db.commit()
        db.refresh(app)
        self.workflow.transition(db, app, ApplicationState.ELIGIBILITY_CHECK,
                                 "system", "system", "Started internship workflow")
        return self.workflow.auto_advance_eligibility(db, app, eligibility)

    def scan_deadlines(self, db: Session) -> int:
        """Dispatch 7-day and 2-day reminders for tracked internships."""
        import asyncio
        from datetime import date, timedelta
        from app.db.models import Notification
        from app.notifications.orchestrator import NotificationOrchestrator
        from app.notifications.service import NotificationType

        count = 0
        apps = (
            db.query(Application)
            .join(Opportunity)
            .filter(
                Opportunity.category == OpportunityCategory.INTERNSHIP,
                Application.saved.is_(True) | Application.state.notin_([ApplicationState.COMPLETED, ApplicationState.REJECTED]),
                Opportunity.deadline.isnot(None),
                Opportunity.deadline.in_([date.today() + timedelta(days=7), date.today() + timedelta(days=2)]),
            )
            .all()
        )
        for app in apps:
            opp = app.opportunity
            days = (opp.deadline - date.today()).days
            title = f"Internship deadline in {days} days: {opp.title[:80]}"
            existing = (
                db.query(Notification)
                .filter_by(user_id=app.user_id, title=title)
                .first()
            )
            if existing:
                continue
            asyncio.run(NotificationOrchestrator(db).send_notification(
                user_id=app.user_id,
                notification_type=NotificationType.DEADLINE_REMINDER,
                title=title,
                body=f"{opp.title} application closes in {days} days. Make sure your profile and documents are ready.",
                metadata={"opportunity_id": opp.id, "deadline_days": days, "kind": "internship"},
                include_voice=days == 2,
            ))
            count += 1
        return count

