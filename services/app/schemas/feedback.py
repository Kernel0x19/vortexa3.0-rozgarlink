from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class FeedbackCreate(BaseModel):
    opportunity_id: str
    feedback_type: str
    comment: Optional[str] = None


class FeedbackResponse(BaseModel):
    id: Optional[str] = None
    opportunity_id: str
    feedback_type: str
    comment: Optional[str] = None
    experiment_name: Optional[str] = None
    variant_name: Optional[str] = None
    submitted_at: datetime = Field(default_factory=datetime.utcnow)
