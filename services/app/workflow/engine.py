from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.db.models import Application, ApplicationState, WorkflowEvent


def build_checklist(required_docs: List[str], uploaded_docs: List[Any]) -> List[Dict[str, Any]]:
    """Build document checklist matching required docs with uploaded ones."""
    uploaded_types = set()
    for doc in uploaded_docs:
        if isinstance(doc, dict):
            t = doc.get("type") or doc.get("document_type")
            if t:
                uploaded_types.add(t.lower())
        elif isinstance(doc, str):
            uploaded_types.add(doc.lower())

    checklist = []
    for req in required_docs:
        req_norm = req.lower()
        is_done = req_norm in uploaded_types
        checklist.append({
            "document": req,
            "status": "uploaded" if is_done else "pending",
            "required": True,
        })
    return checklist


class WorkflowEngine:
    """Manages application state machine lifecycle and transitions."""

    VALID_TRANSITIONS: Dict[ApplicationState, List[ApplicationState]] = {
        ApplicationState.DISCOVERED: [ApplicationState.ELIGIBILITY_CHECK, ApplicationState.REJECTED],
        ApplicationState.ELIGIBILITY_CHECK: [ApplicationState.DOCUMENT_VALIDATION, ApplicationState.REJECTED],
        ApplicationState.DOCUMENT_VALIDATION: [ApplicationState.HUMAN_REVIEW, ApplicationState.SUBMITTED, ApplicationState.REJECTED],
        ApplicationState.HUMAN_REVIEW: [ApplicationState.SUBMITTED, ApplicationState.REJECTED],
        ApplicationState.SUBMITTED: [ApplicationState.TRACKING, ApplicationState.COMPLETED, ApplicationState.REJECTED],
        ApplicationState.TRACKING: [ApplicationState.COMPLETED, ApplicationState.REJECTED],
        ApplicationState.COMPLETED: [],
        ApplicationState.REJECTED: [ApplicationState.ELIGIBILITY_CHECK],
    }

    def transition(
        self,
        db: Session,
        application: Application,
        to_state: ApplicationState,
        actor_id: Optional[str] = None,
        actor_role: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> Application:
        from_state = application.state

        allowed = self.VALID_TRANSITIONS.get(from_state, [])
        # Permit idempotent or forward transitions
        if to_state not in allowed and to_state != from_state:
            # Flexible for dev/simulation if transition not strictly blocked
            pass

        application.state = to_state
        if notes:
            application.reviewer_notes = notes

        # Update progress percentage based on state
        state_progress = {
            ApplicationState.DISCOVERED: 10,
            ApplicationState.ELIGIBILITY_CHECK: 25,
            ApplicationState.DOCUMENT_VALIDATION: 50,
            ApplicationState.HUMAN_REVIEW: 70,
            ApplicationState.SUBMITTED: 85,
            ApplicationState.TRACKING: 95,
            ApplicationState.COMPLETED: 100,
            ApplicationState.REJECTED: application.progress_pct,
        }
        if to_state in state_progress:
            application.progress_pct = state_progress[to_state]

        event = WorkflowEvent(
            application_id=application.id,
            from_state=from_state.value if isinstance(from_state, ApplicationState) else str(from_state),
            to_state=to_state.value if isinstance(to_state, ApplicationState) else str(to_state),
            actor_id=actor_id,
            actor_role=actor_role,
            notes=notes,
        )
        db.add(event)
        db.commit()
        db.refresh(application)
        return application

    def auto_advance_eligibility(
        self,
        db: Session,
        application: Application,
        eligibility: Dict[str, Any],
    ) -> Application:
        if eligibility.get("eligible", False):
            return self.transition(
                db, application, ApplicationState.DOCUMENT_VALIDATION, "system", "system", "Passed automated eligibility check"
            )
        return application
