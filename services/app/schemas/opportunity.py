from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import date, datetime
from app.db.models import OpportunityCategory, ApplicationState


class OpportunityResponse(BaseModel):
    id: str
    source: str
    category: OpportunityCategory
    title: str
    description: Optional[str] = None
    amount_min: Optional[float] = None
    amount_max: Optional[float] = None
    deadline: Optional[date] = None
    eligibility_rules: Optional[Dict[str, Any]] = None
    documents_required: Optional[List[str]] = None
    application_url: Optional[str] = None
    state_filter: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    raw_data: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SearchRequest(BaseModel):
    query: Optional[str] = None
    category: Optional[OpportunityCategory] = None
    state: Optional[str] = None
    limit: int = 20


class ApplicationCreate(BaseModel):
    opportunity_id: str
    saved: bool = False


class ApplicationResponse(BaseModel):
    id: str
    user_id: str
    opportunity_id: str
    state: ApplicationState
    match_score: float = 0.0
    eligibility_result: Optional[Dict[str, Any]] = None
    checklist: Optional[List[Dict[str, Any]]] = None
    reviewer_notes: Optional[str] = None
    progress_pct: int = 0
    saved: bool = False
    created_at: datetime
    updated_at: datetime
    opportunity: Optional[OpportunityResponse] = None

    class Config:
        from_attributes = True


class WorkflowTransitionRequest(BaseModel):
    to_state: ApplicationState
    notes: Optional[str] = None
