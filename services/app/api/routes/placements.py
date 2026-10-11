"""Placements (Jobs) API routes.

Endpoints:
  GET  /api/v1/placements/recommendations  — AI-matched job feed
  POST /api/v1/placements/search           — keyword/semantic search
  GET  /api/v1/placements/opportunities    — raw listing (no auth scoring)
  POST /api/v1/placements/applications     — save / apply to a job
  GET  /api/v1/placements/applications     — list user's saved jobs
"""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.agents.placement import PlacementAgent
from app.api.deps import get_current_user, get_student_profile
from app.db.models import Application, Opportunity, OpportunityCategory, StudentProfile, User
from app.db.session import get_db
from app.schemas import ApplicationCreate, ApplicationResponse, OpportunityResponse

router = APIRouter(prefix="/placements", tags=["placements"])
_agent = PlacementAgent()


# ── Pydantic schemas ──────────────────────────────────────────────────────────

class JobMatchOpportunity(BaseModel):
    id: str
    source: str
    title: str
    description: Optional[str]
    company: Optional[str]
    location: Optional[str]
    work_type: Optional[str]
    experience: Optional[str]
    salary_lpa: Optional[float]
    amount_min: Optional[float]
    amount_max: Optional[float]
    deadline: Optional[str]
    application_url: Optional[str]
    tags: list[str]
    documents_required: list[str]

    model_config = {"from_attributes": True}


class JobMatchResult(BaseModel):
    opportunity: JobMatchOpportunity
    match_score: float


class JobRecommendationResponse(BaseModel):
    matches: list[JobMatchResult]
    total: int
    readiness_score: float


class PlacementSearchRequest(BaseModel):
    query: Optional[str] = None
    location: Optional[str] = None
    work_type: Optional[str] = None
    salary_min: Optional[float] = None
    source: Optional[str] = None
    limit: int = 30


# ── Routes ────────────────────────────────────────────────────────────────────

@router.get("/recommendations", response_model=JobRecommendationResponse)
def get_job_recommendations(
    query:       Optional[str]   = Query(None, description="Keyword/semantic search"),
    location:    Optional[str]   = Query(None, description="Location filter"),
    work_type:   Optional[str]   = Query(None, description="remote | onsite | hybrid"),
    salary_min:  Optional[float] = Query(None, description="Minimum CTC in LPA"),
    experience:  Optional[str]   = Query(None, description="fresher | 0-1 | 1-3 | 3+"),
    source:      Optional[str]   = Query(None, description="Platform slug"),
    limit:       int             = Query(30, ge=1, le=100),
    user:        User            = Depends(get_current_user),
    profile:     StudentProfile | None = Depends(get_student_profile),
    db:          Session         = Depends(get_db),
):
    result = _agent.recommend(
        db, profile,
        query=query, location=location, work_type=work_type,
        salary_min=salary_min, experience=experience, source=source, limit=limit,
    )
    return JobRecommendationResponse(**result)


@router.post("/search", response_model=JobRecommendationResponse)
def search_jobs(
    body:    PlacementSearchRequest,
    user:    User    = Depends(get_current_user),
    profile: StudentProfile | None = Depends(get_student_profile),
    db:      Session = Depends(get_db),
):
    result = _agent.recommend(
        db, profile,
        query=body.query, location=body.location, work_type=body.work_type,
        salary_min=body.salary_min, source=body.source, limit=body.limit,
    )
    return JobRecommendationResponse(**result)


@router.get("/opportunities", response_model=list[OpportunityResponse])
def list_job_opportunities(db: Session = Depends(get_db)):
    opps = db.query(Opportunity).filter_by(
        category=OpportunityCategory.PLACEMENT, is_active=True
    ).all()
    return [OpportunityResponse.model_validate(o) for o in opps]


@router.post("/applications", response_model=ApplicationResponse)
def save_job(
    body:    ApplicationCreate,
    user:    User    = Depends(get_current_user),
    db:      Session = Depends(get_db),
):
    try:
        app = _agent.start_application(db, user.id, body.opportunity_id, saved=body.saved)
    except ValueError as e:
        raise HTTPException(404, str(e))
    resp = ApplicationResponse.model_validate(app)
    resp.opportunity = OpportunityResponse.model_validate(app.opportunity) if app.opportunity else None
    return resp


@router.get("/applications", response_model=list[ApplicationResponse])
def list_saved_jobs(
    user: User    = Depends(get_current_user),
    db:   Session = Depends(get_db),
):
    apps = (
        db.query(Application)
        .filter_by(user_id=user.id)
        .join(Opportunity)
        .filter(Opportunity.category == OpportunityCategory.PLACEMENT)
        .order_by(Application.updated_at.desc())
        .all()
    )
    result = []
    for app in apps:
        resp = ApplicationResponse.model_validate(app)
        if app.opportunity:
            resp.opportunity = OpportunityResponse.model_validate(app.opportunity)
        result.append(resp)
    return result
