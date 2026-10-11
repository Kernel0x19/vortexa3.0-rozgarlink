from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.db.models import Application, ApplicationState, Notification, Opportunity, OpportunityCategory, StudentProfile
from app.intelligence.eligibility import evaluate_eligibility
from app.intelligence.recommendation import compute_match_score, compute_readiness_score, apply_feedback_learning
from app.knowledge.hybrid_rag import HybridRAG
from app.schemas import MatchResult, OpportunityResponse, RecommendationResponse
from app.workflow.engine import WorkflowEngine, build_checklist


class ScholarshipAgent:
    """Thin orchestration layer over shared intelligence + workflow services."""

    def __init__(self) -> None:
        self.rag = HybridRAG()
        self.workflow = WorkflowEngine()

    def recommend(
        self,
        db: Session,
        profile: StudentProfile | None,
        query: str | None = None,
        state: str | None = None,
        limit: int = 20,
        # ── Scholarship-specific filters ──────────────────────────────────
        academic_level: str | None = None,
        category_filter: str | None = None,
        is_pwd: bool | None = None,
        is_girl: bool | None = None,
        is_orphan: bool | None = None,
        is_ward: bool | None = None,
        amount_min: float | None = None,
        amount_max: float | None = None,
    ) -> RecommendationResponse:
        """
        Generate personalized scholarship recommendations with feedback-based learning.

        Filter precedence: explicit params > profile auto-detection > no filter.

        This method:
        1. Retrieves active scholarship opportunities
        2. Filters by state / domicile, academic_level, category, special criteria
        3. Applies semantic search if query provided
        4. Computes match scores with eligibility evaluation
        5. Applies feedback learning to adjust recommendations (Requirement 21.6)
        6. Returns top N matches sorted by adjusted score

        **Validates: Requirement 21.6** - Use negative feedback to improve future recommendations
        """
        opportunities = (
            db.query(Opportunity)
            .filter_by(category=OpportunityCategory.SCHOLARSHIP, is_active=True)
            .all()
        )

        # ── 1. State / domicile filter ────────────────────────────────────
        effective_state = state or (getattr(profile, "domicile_state", None) or getattr(profile, "state", None))
        if effective_state:
            opportunities = [
                o for o in opportunities
                if not o.state_filter
                or "ALL" in o.state_filter
                or effective_state in o.state_filter
            ]

        # ── 2. Amount range filter ────────────────────────────────────────
        if amount_min is not None:
            opportunities = [o for o in opportunities if o.amount_max is None or (o.amount_max or 0) >= amount_min]
        if amount_max is not None:
            opportunities = [o for o in opportunities if o.amount_min is None or (o.amount_min or 0) <= amount_max]

        # ── 3. Profile-derived eligibility tags ──────────────────────────
        # Auto-detect from profile when not explicitly overridden
        eff_is_pwd    = is_pwd    if is_pwd    is not None else getattr(profile, "is_pwd",                    None)
        eff_is_girl   = is_girl   if is_girl   is not None else getattr(profile, "is_single_girl_child",      None)
        eff_is_orphan = is_orphan if is_orphan is not None else getattr(profile, "is_orphan",                 None)
        eff_is_ward   = is_ward   if is_ward   is not None else getattr(profile, "is_ward_of_defense_personnel", None)

        def _tag_filter(opp: Opportunity, tag: str, active: bool | None) -> bool:
            """Keep opp if the user satisfies the tag OR the opp doesn't require it."""
            rules = opp.eligibility_rules or {}
            if rules.get("requires_" + tag) and not active:
                return False  # opp requires tag but user doesn't qualify
            return True

        opportunities = [
            o for o in opportunities
            if _tag_filter(o, "pwd",  eff_is_pwd)
            and _tag_filter(o, "girl", eff_is_girl)
            and _tag_filter(o, "orphan", eff_is_orphan)
            and _tag_filter(o, "defense_ward", eff_is_ward)
        ]

        # ── 4. Semantic search ────────────────────────────────────────────
        if query:
            semantic = self.rag.semantic_search(query, limit=limit, category="scholarship")
            id_order = {s["opportunity_id"]: s["score"] for s in semantic if s.get("opportunity_id")}
            opportunities = [o for o in opportunities if o.id in id_order]
            opportunities.sort(key=lambda o: id_order.get(o.id, 0), reverse=True)
        else:
            opportunities = opportunities[: limit * 2]

        # ── 5. Score + feedback learning ─────────────────────────────────
        matches: list[MatchResult] = []
        for opp in opportunities:
            score, eligibility, reasons = compute_match_score(profile, opp)

            if profile:
                adjusted_score = apply_feedback_learning(profile, opp, score / 100.0, db)
                final_score = adjusted_score * 100.0
            else:
                final_score = score

            if query:
                # Give semantic relevance 60% weight if user explicitly searched for something
                semantic_relevance = id_order.get(opp.id, 0.0)
                final_score = (final_score * 0.4) + (semantic_relevance * 100.0 * 0.6)

            matches.append(
                MatchResult(
                    opportunity=OpportunityResponse.model_validate(opp),
                    match_score=final_score,
                    eligibility=eligibility,
                    reasons=reasons,
                )
            )

        matches.sort(key=lambda m: m.match_score, reverse=True)
        readiness = compute_readiness_score(profile)
        if profile:
            profile.readiness_score = readiness
            db.add(profile)
            db.commit()

        return RecommendationResponse(
            matches=matches[:limit],
            total=len(matches),
            readiness_score=readiness,
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

        existing = (
            db.query(Application)
            .filter_by(user_id=user_id, opportunity_id=opportunity_id)
            .first()
        )
        if existing:
            if saved and not existing.saved:
                existing.saved = True
                db.commit()
            return existing

        score, eligibility, _ = compute_match_score(profile, opp)
        checklist = build_checklist(
            opp.documents_required or [],
            (profile.documents if profile else []) or [],
        )

        app = Application(
            user_id=user_id,
            opportunity_id=opportunity_id,
            state=ApplicationState.DISCOVERED,
            match_score=score,
            eligibility_result=eligibility,
            checklist=checklist,
            saved=saved,
            progress_pct=10,
        )
        db.add(app)
        db.commit()
        db.refresh(app)

        self.workflow.transition(
            db, app, ApplicationState.ELIGIBILITY_CHECK, "system", "system", "Started scholarship workflow"
        )
        return self.workflow.auto_advance_eligibility(db, app, eligibility)

    def get_checklist(self, db: Session, application_id: str) -> list[dict]:
        app = db.query(Application).filter_by(id=application_id).first()
        if not app:
            raise ValueError("Application not found")
        return app.checklist or []

    def scan_deadlines(self, db: Session) -> int:
        """Create deadline reminder notifications for saved/active applications."""
        threshold = date.today() + timedelta(days=14)
        count = 0
        apps = (
            db.query(Application)
            .join(Opportunity)
            .filter(
                Application.saved.is_(True) | Application.state.notin_([ApplicationState.COMPLETED, ApplicationState.REJECTED]),
                Opportunity.deadline.isnot(None),
                Opportunity.deadline <= threshold,
                Opportunity.deadline >= date.today(),
            )
            .all()
        )
        for app in apps:
            opp = app.opportunity
            days = (opp.deadline - date.today()).days
            existing = (
                db.query(Notification)
                .filter_by(user_id=app.user_id, title=f"Deadline: {opp.title[:100]}")
                .first()
            )
            if existing:
                continue
            notif = Notification(
                user_id=app.user_id,
                title=f"Deadline: {opp.title[:100]}",
                body=f"{opp.title} closes in {days} days. Complete your application checklist.",
                channel="in_app",
            )
            db.add(notif)
            count += 1
        db.commit()
        return count
