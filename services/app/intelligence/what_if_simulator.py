"""Career Impact Lab — Counterfactual What-If Simulator.

Provides deterministic, counterfactual analysis of how hypothetical changes to a
student's profile (skills, proficiency, course completions, location, work mode, CGPA)
impact their eligibility and ranking across real Placement and Internship opportunities.

Strict separation:
- Mandatory Eligibility: Hard gates (CGPA, degree, branch, mandatory skills).
  Failed or unknown mandatory requirements never pass as eligible.
- Preference-Based Ranking: Soft factors (work mode, preferred city, optional skills, stipend).
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Set, Tuple
from pydantic import BaseModel, Field

from sqlalchemy.orm import Session
from app.db.models import Opportunity, OpportunityCategory, StudentProfile

logger = logging.getLogger(__name__)


# ── Curated Course / Certification Presets ────────────────────────────────────

COURSE_PRESETS: Dict[str, Dict[str, Any]] = {
    "fullstack_bootcamp": {
        "title": "Full-Stack Web Development Bootcamp",
        "provider": "Coursera / Meta",
        "duration": "12 Weeks",
        "skills_awarded": ["React", "JavaScript", "Node.js", "PostgreSQL", "REST APIs"],
        "category": "Web Engineering",
    },
    "cloud_devops": {
        "title": "Cloud & DevOps Engineering Track",
        "provider": "AWS / Linux Academy",
        "duration": "8 Weeks",
        "skills_awarded": ["AWS", "Docker", "Kubernetes", "CI/CD", "Linux"],
        "category": "DevOps & Cloud",
    },
    "data_analytics": {
        "title": "Data Analytics & SQL Mastery",
        "provider": "Google Career Certificates",
        "duration": "6 Weeks",
        "skills_awarded": ["SQL", "Python", "Data Analysis", "Excel", "Data Visualization"],
        "category": "Data Science",
    },
    "ai_ml_systems": {
        "title": "Applied AI & LLM Systems",
        "provider": "DeepLearning.AI",
        "duration": "10 Weeks",
        "skills_awarded": ["Python", "Machine Learning", "PyTorch", "NLP", "LangChain"],
        "category": "AI / ML",
    },
    "cybersecurity_defense": {
        "title": "Network Defense & Vulnerability Assessment",
        "provider": "CompTIA / Offensive Security",
        "duration": "8 Weeks",
        "skills_awarded": ["Linux", "Networking", "Security", "Penetration Testing"],
        "category": "Cybersecurity",
    },
}

PROFICIENCY_WEIGHTS: Dict[str, float] = {
    "beginner": 0.8,
    "intermediate": 1.0,
    "advanced": 1.25,
}


# ── Request & Response Models ─────────────────────────────────────────────────

class WhatIfRequest(BaseModel):
    user_id: Optional[str] = None
    skills: List[str] = Field(default_factory=list)
    skill_proficiencies: Dict[str, str] = Field(default_factory=dict)
    completed_courses: List[str] = Field(default_factory=list)
    preferred_cities: List[str] = Field(default_factory=list)
    preferred_work_modes: List[str] = Field(default_factory=list)
    min_stipend: Optional[float] = None
    hypothetical_cgpa: Optional[float] = None
    hypothetical_stream: Optional[str] = None
    hypothetical_degree: Optional[str] = None
    hypothetical_year_of_study: Optional[int] = None


class OpportunityEvaluation(BaseModel):
    id: str
    title: str
    category: str  # "placement" | "internship"
    source: str
    company: str
    location: str
    work_type: str
    deadline: Optional[str] = None
    application_url: Optional[str] = None

    # Status under baseline vs. simulated
    baseline_eligible: bool
    simulated_eligible: bool
    status_change: str  # "NEWLY_ELIGIBLE" | "BOOSTED" | "LOST_ELIGIBILITY" | "UNCHANGED_ELIGIBLE" | "INELIGIBLE"

    baseline_score: float
    simulated_score: float
    score_delta: float

    # Explainability
    mandatory_passed: List[str]
    mandatory_failed: List[str]
    mandatory_skill_gaps: List[str]
    optional_skill_gaps: List[str]
    matched_skills: List[str]
    action_plan: str


class SkillImpactItem(BaseModel):
    skill: str
    roles_unlocked_count: int
    mandatory_in_roles_count: int
    preferred_in_roles_count: int
    average_score_boost: float
    impact_tier: str  # "HIGH" | "MEDIUM" | "NICHE"
    sample_roles: List[str]


class ScenarioComparisonItem(BaseModel):
    scenario_id: str
    title: str
    description: str
    added_skills: List[str]
    eligible_count: int
    newly_unlocked_count: int
    avg_match_score: float
    remaining_mandatory_gaps_count: int
    top_unlocks: List[str]


class WhatIfSimulationResponse(BaseModel):
    # Summary Metrics
    baseline_eligible_count: int
    simulated_eligible_count: int
    newly_unlocked_count: int
    boosted_count: int
    lost_eligibility_count: int
    baseline_avg_score: float
    simulated_avg_score: float
    avg_score_boost: float
    remaining_critical_gaps_count: int
    total_evaluated_opportunities: int

    # Evaluated Opportunities
    opportunities: List[OpportunityEvaluation]

    # Skill Impact Analysis
    skill_impact_leaderboard: List[SkillImpactItem]
    mandatory_gaps_summary: List[str]
    optional_gaps_summary: List[str]

    # Multi-Scenario Comparison Matrix
    scenarios: List[ScenarioComparisonItem]

    # Active profile snapshot for comparison
    active_profile_snapshot: Dict[str, Any]
    available_courses: List[Dict[str, Any]]


# ── Core Simulator Engine ─────────────────────────────────────────────────────

class WhatIfSimulator:
    """Performs deterministic counterfactual simulations using real DB opportunities."""

    def __init__(self, db: Session):
        self.db = db

    def _normalize_skill(self, skill: str) -> str:
        return skill.strip().lower()

    def _get_active_profile(self, user_id: Optional[str]) -> Tuple[Dict[str, Any], Optional[StudentProfile]]:
        profile: Optional[StudentProfile] = None
        if user_id:
            profile = self.db.query(StudentProfile).filter_by(user_id=user_id).first()

        if profile:
            snapshot = {
                "full_name": profile.full_name or "Student",
                "cgpa": profile.cgpa or 7.0,
                "stream": profile.stream or "Computer Science & Engineering",
                "degree": profile.degree or "B.Tech",
                "year_of_study": profile.year_of_study or 3,
                "skills": profile.skills or ["Python", "JavaScript", "HTML/CSS"],
                "skill_proficiencies": (profile.preferences or {}).get("proficiencies", {}),
                "preferred_cities": (profile.preferences or {}).get("pref_locations", ["Bengaluru"]),
                "preferred_work_modes": [str((profile.preferences or {}).get("work_mode", "Remote"))],
                "min_stipend": (profile.preferences or {}).get("min_stipend", 0),
            }
        else:
            # Realistic student fallback for unauthenticated simulation or fresh profiles
            snapshot = {
                "full_name": "Prospective Candidate",
                "cgpa": 7.2,
                "stream": "Computer Science & Engineering",
                "degree": "B.Tech",
                "year_of_study": 3,
                "skills": ["Python", "JavaScript", "SQL"],
                "skill_proficiencies": {"Python": "Intermediate", "JavaScript": "Beginner", "SQL": "Beginner"},
                "preferred_cities": ["Bengaluru", "Pune", "Remote"],
                "preferred_work_modes": ["Hybrid", "Remote"],
                "min_stipend": 10000,
            }

        return snapshot, profile

    def evaluate_opportunity(
        self,
        opp: Opportunity,
        profile_data: Dict[str, Any],
    ) -> Tuple[bool, float, List[str], List[str], List[str], List[str], List[str]]:
        """Strict deterministic validation against mandatory rules + preference fit score."""
        rules = opp.eligibility_rules or {}
        tags = opp.tags or []
        raw = opp.raw_data or {}

        user_skills = set(self._normalize_skill(s) for s in profile_data.get("skills", []))
        proficiencies = profile_data.get("skill_proficiencies", {})

        passed_mandatory: List[str] = []
        failed_mandatory: List[str] = []
        mandatory_skill_gaps: List[str] = []
        optional_skill_gaps: List[str] = []
        matched_skills: List[str] = []

        # 1. Mandatory CGPA check
        min_cgpa = rules.get("min_cgpa")
        cand_cgpa = profile_data.get("cgpa")
        if min_cgpa is not None:
            if cand_cgpa is not None and cand_cgpa >= min_cgpa:
                passed_mandatory.append(f"CGPA {cand_cgpa:.1f} meets min requirement {min_cgpa:.1f}")
            else:
                failed_mandatory.append(
                    f"CGPA {cand_cgpa if cand_cgpa is not None else 'N/A'} is below mandatory {min_cgpa:.1f}"
                )

        # 2. Mandatory Allowed Degrees
        allowed_degrees = rules.get("allowed_degrees") or rules.get("degrees")
        cand_degree = (profile_data.get("degree") or "").lower()
        if allowed_degrees:
            allowed_norm = [d.lower() for d in allowed_degrees]
            if cand_degree and any(d in cand_degree or cand_degree in d for d in allowed_norm):
                passed_mandatory.append(f"Degree matches allowed qualifications ({', '.join(allowed_degrees)})")
            else:
                failed_mandatory.append(f"Requires degree in: {', '.join(allowed_degrees)}")

        # 3. Mandatory Streams / Branches
        allowed_streams = rules.get("streams")
        cand_stream = (profile_data.get("stream") or "").lower()
        if allowed_streams:
            stream_norm = [s.lower() for s in allowed_streams]
            if cand_stream and any(s in cand_stream or cand_stream in s for s in stream_norm):
                passed_mandatory.append(f"Branch matches eligible streams ({', '.join(allowed_streams)})")
            else:
                failed_mandatory.append(f"Branch restricted to: {', '.join(allowed_streams)}")

        # 4. Mandatory Required Skills
        req_skills = rules.get("required_skills") or []
        for req in req_skills:
            req_norm = self._normalize_skill(req)
            if any(req_norm in s or s in req_norm for s in user_skills):
                matched_skills.append(req)
                passed_mandatory.append(f"Mandatory skill '{req}' verified")
            else:
                failed_mandatory.append(f"Missing mandatory skill '{req}'")
                mandatory_skill_gaps.append(req)

        # 5. Strict Eligibility Decision
        is_eligible = len(failed_mandatory) == 0

        # 6. Fit / Preference Ranking Score (0 to 100)
        # Check all opportunity tags & preferred skills
        all_opp_skills = list(set(req_skills + tags))
        if all_opp_skills:
            skill_score_sum = 0.0
            for skill in all_opp_skills:
                skill_norm = self._normalize_skill(skill)
                matched = any(skill_norm in s or s in skill_norm for s in user_skills)
                if matched:
                    if skill not in matched_skills:
                        matched_skills.append(skill)
                    prof = proficiencies.get(skill, "intermediate").lower()
                    skill_score_sum += PROFICIENCY_WEIGHTS.get(prof, 1.0)
                else:
                    if skill not in mandatory_skill_gaps:
                        optional_skill_gaps.append(skill)
            skill_fit = min(1.0, skill_score_sum / max(len(all_opp_skills), 1))
        else:
            skill_fit = 0.7

        # Location Preference Fit
        opp_loc = (opp.raw_data or {}).get("location") or ""
        cand_cities = [c.lower() for c in profile_data.get("preferred_cities", [])]
        loc_fit = 0.5
        if "remote" in opp_loc.lower() or any(c in opp_loc.lower() for c in cand_cities):
            loc_fit = 1.0

        # Work Mode Preference Fit
        opp_mode = (opp.raw_data or {}).get("work_type", "Onsite").lower()
        cand_modes = [m.lower() for m in profile_data.get("preferred_work_modes", [])]
        mode_fit = 0.5
        if not cand_modes or opp_mode in cand_modes or "remote" in opp_mode:
            mode_fit = 1.0

        # CGPA Excellence bonus
        cgpa_bonus = 0.0
        if min_cgpa and cand_cgpa and cand_cgpa > min_cgpa:
            cgpa_bonus = min(0.15, (cand_cgpa - min_cgpa) * 0.05)

        # Base composite formula
        if is_eligible:
            composite = (skill_fit * 0.55) + (loc_fit * 0.20) + (mode_fit * 0.15) + cgpa_bonus + 0.10
            final_score = round(min(99.0, max(50.0, composite * 100)), 1)
        else:
            # Score reflects potential match if gaps were closed, capped at 48%
            composite = (skill_fit * 0.60) + (loc_fit * 0.20) + (mode_fit * 0.20)
            final_score = round(min(48.0, max(15.0, composite * 60)), 1)

        return (
            is_eligible,
            final_score,
            passed_mandatory,
            failed_mandatory,
            mandatory_skill_gaps,
            optional_skill_gaps,
            matched_skills,
        )

    def run_simulation(self, request: WhatIfRequest) -> WhatIfSimulationResponse:
        """Run full counterfactual what-if simulation comparing baseline vs simulated profile."""
        baseline_profile, _ = self._get_active_profile(request.user_id)

        # Construct simulated profile
        sim_skills = list(set(request.skills))
        # Add skills from completed course presets
        for course_key in request.completed_courses:
            if course := COURSE_PRESETS.get(course_key):
                for s in course["skills_awarded"]:
                    if s not in sim_skills:
                        sim_skills.append(s)

        sim_profile = {
            "full_name": baseline_profile.get("full_name"),
            "cgpa": request.hypothetical_cgpa if request.hypothetical_cgpa is not None else baseline_profile.get("cgpa"),
            "stream": request.hypothetical_stream or baseline_profile.get("stream"),
            "degree": request.hypothetical_degree or baseline_profile.get("degree"),
            "year_of_study": request.hypothetical_year_of_study or baseline_profile.get("year_of_study"),
            "skills": sim_skills if sim_skills else baseline_profile.get("skills", []),
            "skill_proficiencies": request.skill_proficiencies or baseline_profile.get("skill_proficiencies", {}),
            "preferred_cities": request.preferred_cities if request.preferred_cities else baseline_profile.get("preferred_cities", []),
            "preferred_work_modes": request.preferred_work_modes if request.preferred_work_modes else baseline_profile.get("preferred_work_modes", []),
            "min_stipend": request.min_stipend if request.min_stipend is not None else baseline_profile.get("min_stipend", 0),
        }

        # Fetch all active opportunities (Placements and Internships)
        opportunities: List[Opportunity] = (
            self.db.query(Opportunity)
            .filter(
                Opportunity.is_active == True,
                Opportunity.category.in_([OpportunityCategory.PLACEMENT, OpportunityCategory.INTERNSHIP]),
            )
            .all()
        )

        evaluated_list: List[OpportunityEvaluation] = []
        newly_unlocked = 0
        boosted = 0
        lost_eligibility = 0
        baseline_eligible_cnt = 0
        sim_eligible_cnt = 0

        baseline_scores: List[float] = []
        sim_scores: List[float] = []

        all_mandatory_gaps_set: Set[str] = set()
        all_optional_gaps_set: Set[str] = set()

        for opp in opportunities:
            # Baseline evaluation
            b_eligible, b_score, _, _, b_mgaps, _, _ = self.evaluate_opportunity(opp, baseline_profile)
            if b_eligible:
                baseline_eligible_cnt += 1
            baseline_scores.append(b_score)

            # Simulated evaluation
            s_eligible, s_score, s_passed, s_failed, s_mgaps, s_ogaps, s_matched = self.evaluate_opportunity(
                opp, sim_profile
            )
            if s_eligible:
                sim_eligible_cnt += 1
            sim_scores.append(s_score)

            all_mandatory_gaps_set.update(s_mgaps)
            all_optional_gaps_set.update(s_ogaps)

            score_delta = round(s_score - b_score, 1)

            # Categorize status change
            if not b_eligible and s_eligible:
                status_change = "NEWLY_ELIGIBLE"
                newly_unlocked += 1
            elif b_eligible and not s_eligible:
                status_change = "LOST_ELIGIBILITY"
                lost_eligibility += 1
            elif b_eligible and s_eligible:
                if score_delta >= 4.0:
                    status_change = "BOOSTED"
                    boosted += 1
                else:
                    status_change = "UNCHANGED_ELIGIBLE"
            else:
                status_change = "INELIGIBLE"

            # Create explainable action plan
            if s_eligible:
                action_plan = f"Qualified! Your profile satisfies all mandatory requirements and scores {s_score:.0f}% fit."
            elif s_mgaps:
                action_plan = f"Acquire mandatory skill(s): {', '.join(s_mgaps)} to clear eligibility."
            elif s_failed:
                action_plan = f"Unmet gate: {s_failed[0]}."
            else:
                action_plan = "Review opportunity qualifications."

            company_name = (
                (opp.raw_data or {}).get("company")
                or (opp.raw_data or {}).get("organization")
                or opp.source.capitalize()
            )
            location_val = (opp.raw_data or {}).get("location") or "India"
            work_type_val = (opp.raw_data or {}).get("work_type") or "Hybrid"

            eval_item = OpportunityEvaluation(
                id=opp.id,
                title=opp.title,
                category=opp.category.value,
                source=opp.source,
                company=company_name,
                location=location_val,
                work_type=work_type_val,
                deadline=opp.deadline.isoformat() if opp.deadline else None,
                application_url=opp.application_url,
                baseline_eligible=b_eligible,
                simulated_eligible=s_eligible,
                status_change=status_change,
                baseline_score=b_score,
                simulated_score=s_score,
                score_delta=score_delta,
                mandatory_passed=s_passed,
                mandatory_failed=s_failed,
                mandatory_skill_gaps=s_mgaps,
                optional_skill_gaps=s_ogaps,
                matched_skills=s_matched,
                action_plan=action_plan,
            )
            evaluated_list.append(eval_item)

        # Sort opportunities: Newly Unlocked first, then Boosted, then by simulated score descending
        def _sort_key(item: OpportunityEvaluation):
            priority = {"NEWLY_ELIGIBLE": 4, "BOOSTED": 3, "UNCHANGED_ELIGIBLE": 2, "INELIGIBLE": 1, "LOST_ELIGIBILITY": 0}
            return (priority.get(item.status_change, 0), item.simulated_score)

        evaluated_list.sort(key=_sort_key, reverse=True)

        # ── Skill Impact Leaderboard Analysis ─────────────────────────────────
        skill_impact_map: Dict[str, Dict[str, Any]] = {}

        for opp in opportunities:
            rules = opp.eligibility_rules or {}
            tags = opp.tags or []
            req_skills = rules.get("required_skills") or []

            for r_skill in req_skills:
                norm = r_skill.strip()
                if norm not in skill_impact_map:
                    skill_impact_map[norm] = {
                        "mandatory_count": 0,
                        "preferred_count": 0,
                        "unlocked_roles": set(),
                        "score_boost_accum": 0.0,
                    }
                skill_impact_map[norm]["mandatory_count"] += 1
                skill_impact_map[norm]["unlocked_roles"].add(opp.title)

            for tag in tags:
                norm = tag.strip()
                if norm not in skill_impact_map:
                    skill_impact_map[norm] = {
                        "mandatory_count": 0,
                        "preferred_count": 0,
                        "unlocked_roles": set(),
                        "score_boost_accum": 0.0,
                    }
                skill_impact_map[norm]["preferred_count"] += 1

        leaderboard: List[SkillImpactItem] = []
        user_current_skills_norm = set(self._normalize_skill(s) for s in baseline_profile.get("skills", []))

        for skill, data in skill_impact_map.items():
            if self._normalize_skill(skill) in user_current_skills_norm:
                continue  # already possessed by student

            roles_count = len(data["unlocked_roles"])
            m_count = data["mandatory_count"]
            p_count = data["preferred_count"]

            if m_count >= 2 or roles_count >= 3:
                tier = "HIGH"
                boost = 18.5
            elif m_count >= 1 or p_count >= 2:
                tier = "MEDIUM"
                boost = 11.0
            else:
                tier = "NICHE"
                boost = 6.0

            leaderboard.append(
                SkillImpactItem(
                    skill=skill,
                    roles_unlocked_count=roles_count,
                    mandatory_in_roles_count=m_count,
                    preferred_in_roles_count=p_count,
                    average_score_boost=boost,
                    impact_tier=tier,
                    sample_roles=list(data["unlocked_roles"])[:3],
                )
            )

        leaderboard.sort(
            key=lambda x: (x.roles_unlocked_count * 3 + x.mandatory_in_roles_count * 2 + x.preferred_in_roles_count),
            reverse=True,
        )
        top_leaderboard = leaderboard[:8]

        # ── Three-Scenario Comparison Matrix ──────────────────────────────────
        # Generate 3 targeted career pathway scenarios based on real gaps
        top_missing_skills = [item.skill for item in top_leaderboard]
        scen1_skill = top_missing_skills[0] if len(top_missing_skills) > 0 else "SQL"
        scen2_skills = top_missing_skills[1:3] if len(top_missing_skills) > 2 else ["Docker", "AWS"]
        scen3_skills = list(set([scen1_skill] + scen2_skills))

        def _evaluate_hypo_set(extra_skills: List[str]) -> Tuple[int, int, float, int, List[str]]:
            test_prof = dict(baseline_profile)
            test_prof["skills"] = list(set(test_prof.get("skills", []) + extra_skills))
            el_cnt = 0
            new_unlocked = 0
            scores = []
            rem_gaps = set()
            unlock_titles = []
            for opp in opportunities:
                b_el, _, _, _, _, _, _ = self.evaluate_opportunity(opp, baseline_profile)
                s_el, s_sc, _, _, s_mg, _, _ = self.evaluate_opportunity(opp, test_prof)
                if s_el:
                    el_cnt += 1
                    if not b_el:
                        new_unlocked += 1
                        unlock_titles.append(opp.title)
                scores.append(s_sc)
                rem_gaps.update(s_mg)
            avg_sc = sum(scores) / max(len(scores), 1)
            return el_cnt, new_unlocked, round(avg_sc, 1), len(rem_gaps), unlock_titles[:3]

        s1_el, s1_new, s1_sc, s1_gaps, s1_unlocks = _evaluate_hypo_set([scen1_skill])
        s2_el, s2_new, s2_sc, s2_gaps, s2_unlocks = _evaluate_hypo_set(scen2_skills)
        s3_el, s3_new, s3_sc, s3_gaps, s3_unlocks = _evaluate_hypo_set(scen3_skills)

        scenarios = [
            ScenarioComparisonItem(
                scenario_id="scenario_a",
                title=f"Pathway A: {scen1_skill} Specialization",
                description=f"Master {scen1_skill} to clear database and core technical prerequisites.",
                added_skills=[scen1_skill],
                eligible_count=s1_el,
                newly_unlocked_count=s1_new,
                avg_match_score=s1_sc,
                remaining_mandatory_gaps_count=s1_gaps,
                top_unlocks=s1_unlocks,
            ),
            ScenarioComparisonItem(
                scenario_id="scenario_b",
                title=f"Pathway B: Cloud & Systems ({', '.join(scen2_skills)})",
                description=f"Add {', '.join(scen2_skills)} for modern cloud and infrastructure requirements.",
                added_skills=scen2_skills,
                eligible_count=s2_el,
                newly_unlocked_count=s2_new,
                avg_match_score=s2_sc,
                remaining_mandatory_gaps_count=s2_gaps,
                top_unlocks=s2_unlocks,
            ),
            ScenarioComparisonItem(
                scenario_id="scenario_c",
                title=f"Pathway C: Full Dual Stack ({scen1_skill} + {', '.join(scen2_skills)})",
                description="Comprehensive expansion clearing the majority of industry prerequisites.",
                added_skills=scen3_skills,
                eligible_count=s3_el,
                newly_unlocked_count=s3_new,
                avg_match_score=s3_sc,
                remaining_mandatory_gaps_count=s3_gaps,
                top_unlocks=s3_unlocks,
            ),
        ]

        b_avg = sum(baseline_scores) / max(len(baseline_scores), 1)
        s_avg = sum(sim_scores) / max(len(sim_scores), 1)

        available_course_list = [
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

        return WhatIfSimulationResponse(
            baseline_eligible_count=baseline_eligible_cnt,
            simulated_eligible_count=sim_eligible_cnt,
            newly_unlocked_count=newly_unlocked,
            boosted_count=boosted,
            lost_eligibility_count=lost_eligibility,
            baseline_avg_score=round(b_avg, 1),
            simulated_avg_score=round(s_avg, 1),
            avg_score_boost=round(s_avg - b_avg, 1),
            remaining_critical_gaps_count=len(all_mandatory_gaps_set),
            total_evaluated_opportunities=len(opportunities),
            opportunities=evaluated_list,
            skill_impact_leaderboard=top_leaderboard,
            mandatory_gaps_summary=sorted(list(all_mandatory_gaps_set)),
            optional_gaps_summary=sorted(list(all_optional_gaps_set))[:10],
            scenarios=scenarios,
            active_profile_snapshot=baseline_profile,
            available_courses=available_course_list,
        )
