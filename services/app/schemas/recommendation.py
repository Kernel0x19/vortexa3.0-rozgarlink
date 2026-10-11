from typing import List, Dict, Any
from pydantic import BaseModel
from app.schemas.opportunity import OpportunityResponse


class EligibilityResult(BaseModel):
    eligible: bool
    score: float
    passed: List[str]
    failed: List[str]
    warnings: List[str]


class MatchResult(BaseModel):
    opportunity: OpportunityResponse
    match_score: float
    eligibility: EligibilityResult
    reasons: List[str]


class RecommendationResponse(BaseModel):
    matches: List[MatchResult]
    total: int
    readiness_score: float = 0.0


class DashboardStats(BaseModel):
    # Fields expected by frontend StatsSection
    eligible_matches: int = 0
    opportunities_available: int = 0
    skill_gaps_identified: int = 0
    applications_tracked: int = 0
    readiness_score: float = 0.0
    # Legacy aliases for backward compat
    scholarships_matched: int = 0
    internships_available: int = 0
    documents_uploaded: int = 0
