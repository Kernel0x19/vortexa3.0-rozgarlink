from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.agents.scholarship import ScholarshipAgent
from app.api.deps import get_current_user, get_student_profile
from app.db.models import Application, Notification, OpportunityCategory, StudentProfile, User
from app.db.session import get_db
from app.intelligence.recommendation import compute_readiness_score
from app.schemas import (
    ApplicationCreate,
    ApplicationResponse,
    DashboardStats,
    MatchResult,
    OpportunityResponse,
    RecommendationResponse,
    SearchRequest,
)
from app.schemas import OpportunityCategory as OppCat

router = APIRouter(prefix="/scholarships", tags=["scholarships"])
agent = ScholarshipAgent()

ACADEMIC_LEVELS = [
    "Pre-Matric (Class 9-10)",
    "Post-Matric (Class 11-12)",
    "Diploma",
    "Undergraduate (UG)",
    "Postgraduate (PG)",
    "PhD / Doctorate",
]
INSTITUTION_TYPES = ["Government", "AICTE Approved", "Autonomous", "Private", "Deemed University"]


@router.get("/filters")
def get_filter_options():
    """Return available filter options for the scholarship discovery UI."""
    return {
        "academic_levels": ACADEMIC_LEVELS,
        "institution_types": INSTITUTION_TYPES,
        "special_categories": [
            {"key": "is_pwd",    "label": "Person with Disability (PwD)"},
            {"key": "is_girl",   "label": "Single Girl Child"},
            {"key": "is_orphan", "label": "Orphan / Lost Guardian"},
            {"key": "is_ward",   "label": "Ward of Defence / Covid Victim"},
        ],
    }


@router.get("/recommendations", response_model=RecommendationResponse)
def get_recommendations(
    query: str | None = None,
    state: str | None = None,
    limit: int = 20,
    academic_level: str | None = Query(None, description="Filter by academic level"),
    is_pwd:    bool | None = Query(None, description="Only include PwD-eligible scholarships"),
    is_girl:   bool | None = Query(None, description="Only include Single Girl Child scholarships"),
    is_orphan: bool | None = Query(None, description="Only include orphan-eligible scholarships"),
    is_ward:   bool | None = Query(None, description="Ward of defence personnel filter"),
    amount_min: float | None = Query(None, description="Minimum scholarship amount (₹)"),
    amount_max: float | None = Query(None, description="Maximum scholarship amount (₹)"),
    user: User = Depends(get_current_user),
    profile: StudentProfile | None = Depends(get_student_profile),
    db: Session = Depends(get_db),
):
    return agent.recommend(
        db, profile,
        query=query, state=state, limit=limit,
        academic_level=academic_level,
        is_pwd=is_pwd, is_girl=is_girl, is_orphan=is_orphan, is_ward=is_ward,
        amount_min=amount_min, amount_max=amount_max,
    )


@router.post("/search", response_model=RecommendationResponse)
def search_scholarships(
    body: SearchRequest,
    user: User = Depends(get_current_user),
    profile: StudentProfile | None = Depends(get_student_profile),
    db: Session = Depends(get_db),
):
    return agent.recommend(
        db, profile,
        query=body.query, state=body.state, limit=body.limit,
    )


@router.get("/opportunities", response_model=list[OpportunityResponse])
def list_opportunities(db: Session = Depends(get_db)):
    from app.db.models import Opportunity

    opps = db.query(Opportunity).filter_by(category=OpportunityCategory.SCHOLARSHIP, is_active=True).all()
    return [OpportunityResponse.model_validate(o) for o in opps]


@router.post("/applications", response_model=ApplicationResponse)
def create_application(
    body: ApplicationCreate,
    user: User = Depends(get_current_user),
    profile: StudentProfile | None = Depends(get_student_profile),
    db: Session = Depends(get_db),
):
    try:
        app = agent.start_application(db, user.id, body.opportunity_id, profile, saved=body.saved)
    except ValueError as e:
        raise HTTPException(404, str(e))
    opp = app.opportunity
    resp = ApplicationResponse.model_validate(app)
    resp.opportunity = OpportunityResponse.model_validate(opp) if opp else None
    return resp


@router.get("/applications", response_model=list[ApplicationResponse])
def list_applications(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    apps = db.query(Application).filter_by(user_id=user.id).order_by(Application.updated_at.desc()).all()
    result = []
    for app in apps:
        resp = ApplicationResponse.model_validate(app)
        if app.opportunity:
            resp.opportunity = OpportunityResponse.model_validate(app.opportunity)
        result.append(resp)
    return result


@router.get("/dashboard", response_model=DashboardStats)
def dashboard_stats(
    user: User = Depends(get_current_user),
    profile: StudentProfile | None = Depends(get_student_profile),
    db: Session = Depends(get_db),
):
    from app.db.models import Opportunity
    from app.agents.hackathon import HackathonAgent
    from app.agents.internship import InternshipAgent

    # Total active opportunities across internships and hackathons
    total_opps = db.query(Opportunity).filter(Opportunity.is_active == True).count()
    internships = db.query(Opportunity).filter(
        Opportunity.category == OppCat.INTERNSHIP, Opportunity.is_active == True
    ).count()
    hackathons = db.query(Opportunity).filter(
        Opportunity.category == OppCat.HACKATHON, Opportunity.is_active == True
    ).count()
    apps = db.query(Application).filter_by(user_id=user.id).count()
    docs = len(profile.documents) if profile and profile.documents else 0

    # Calculate skill gaps and eligible matches if profile exists
    skill_gaps = 0
    eligible_matches = 0
    if profile:
        user_skills = set([s.lower().strip() for s in (profile.skills or [])])
        for opp in db.query(Opportunity).filter(Opportunity.is_active == True).limit(50):
            rules = opp.eligibility_rules or {}
            skills_list = rules.get("required_skills") or opp.tags or []
            req_skills = set([str(s).lower().strip() for s in skills_list])
            if req_skills:
                missing = req_skills - user_skills
                if missing:
                    skill_gaps += len(missing)
                if len(user_skills & req_skills) > 0:
                    eligible_matches += 1
            else:
                eligible_matches += 1
    else:
        eligible_matches = total_opps

    readiness = compute_readiness_score(profile)

    return DashboardStats(
        eligible_matches=eligible_matches,
        opportunities_available=total_opps,
        skill_gaps_identified=min(skill_gaps, 20),
        applications_tracked=apps,
        readiness_score=readiness,
        scholarships_matched=eligible_matches,
        internships_available=internships,
        documents_uploaded=docs,
    )
