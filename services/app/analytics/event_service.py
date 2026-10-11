from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime
from app.db.models import UserEvent


class AnalyticsEventService:
    def __init__(self, db: Session):
        self.db = db

    def track_event(
        self,
        user_id: str,
        event_type: str,
        opportunity_id: Optional[str] = None,
        application_id: Optional[str] = None,
        experiment_name: Optional[str] = None,
        variant_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> UserEvent:
        event = UserEvent(
            user_id=user_id,
            event_type=event_type,
            opportunity_id=opportunity_id,
            application_id=application_id,
            experiment_name=experiment_name,
            variant_name=variant_name,
            event_metadata=metadata,
            created_at=datetime.utcnow(),
        )
        self.db.add(event)
        self.db.commit()
        return event
