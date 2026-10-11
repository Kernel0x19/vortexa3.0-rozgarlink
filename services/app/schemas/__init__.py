from app.db.models import OpportunityCategory, ApplicationState
from app.schemas.opportunity import (
    OpportunityResponse,
    SearchRequest,
    ApplicationCreate,
    ApplicationResponse,
    WorkflowTransitionRequest,
)
from app.schemas.student import (
    StudentProfileBase,
    StudentProfileCreate,
    StudentProfileResponse,
    NotificationResponse,
)
from app.schemas.recommendation import (
    EligibilityResult,
    MatchResult,
    RecommendationResponse,
    DashboardStats,
)

__all__ = [
    "OpportunityCategory",
    "ApplicationState",
    "OpportunityResponse",
    "SearchRequest",
    "ApplicationCreate",
    "ApplicationResponse",
    "WorkflowTransitionRequest",
    "StudentProfileBase",
    "StudentProfileCreate",
    "StudentProfileResponse",
    "NotificationResponse",
    "EligibilityResult",
    "MatchResult",
    "RecommendationResponse",
    "DashboardStats",
]
