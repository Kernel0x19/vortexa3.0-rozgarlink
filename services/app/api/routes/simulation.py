"""Career Impact Lab — Simulation API routes."""

from __future__ import annotations

import logging
from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_current_user_optional, get_db
from app.db.models import StudentProfile, User
from app.intelligence.what_if_simulator import (
    COURSE_PRESETS,
    WhatIfRequest,
    WhatIfSimulationResponse,
    WhatIfSimulator,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/simulation", tags=["simulation"])


class ApplyToProfileRequest(BaseModel):
    user_id: str
    skills: List[str]
    skill_proficiencies: Dict[str, str] = {}
    preferred_cities: List[str] = []
    preferred_work_modes: List[str] = []
    confirmed: bool = False


@router.post("/what-if", response_model=WhatIfSimulationResponse)
def simulate_what_if(
    request: WhatIfRequest,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user_optional),
):
    """Run counterfactual what-if simulation against real placement and internship opportunities.
    
    Strictly isolated: does not alter student profile until explicit confirmation.
    """
    effective_user_id = request.user_id or (user.id if user else None)
    req_copy = request.model_copy(update={"user_id": effective_user_id})

    simulator = WhatIfSimulator(db)
    result = simulator.run_simulation(req_copy)
    return result


@router.get("/courses")
def get_available_courses():
    """Return list of simulation-ready course and certification presets."""
    return [
        {
            "key": k,
            "title": v["title"],
            "provider": v["provider"],
            "duration": v["duration"],
            "category": v["category"],
            "skills": v["skills_awarded"],
        }
        for k, v in COURSE_PRESETS.items()
    ]


@router.post("/apply-to-profile")
def apply_simulated_changes_to_profile(
    body: ApplyToProfileRequest,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user_optional),
):
    """Apply simulated changes to the real database profile ONLY upon explicit confirmation."""
    if not body.confirmed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Explicit user confirmation required to apply simulated changes to actual profile.",
        )

    target_user_id = body.user_id or (user.id if user else None)
    if not target_user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Valid user_id required to save changes.",
        )

    profile = db.query(StudentProfile).filter_by(user_id=target_user_id).first()
    if not profile:
        profile = StudentProfile(user_id=target_user_id)
        db.add(profile)

    # Safely merge skills
    current_skills = profile.skills or []
    merged_skills = list(set(current_skills + body.skills))
    profile.skills = merged_skills

    # Update preferences
    current_prefs = profile.preferences or {}
    if body.skill_proficiencies:
        current_prof = current_prefs.get("proficiencies", {})
        current_prof.update(body.skill_proficiencies)
        current_prefs["proficiencies"] = current_prof

    if body.preferred_cities:
        current_prefs["pref_locations"] = body.preferred_cities

    if body.preferred_work_modes:
        current_prefs["work_mode"] = body.preferred_work_modes[0]

    profile.preferences = current_prefs
    db.commit()

    return {
        "status": "success",
        "message": f"Successfully applied {len(body.skills)} skill(s) and preferences to real profile.",
        "skills": profile.skills,
        "preferences": profile.preferences,
    }
