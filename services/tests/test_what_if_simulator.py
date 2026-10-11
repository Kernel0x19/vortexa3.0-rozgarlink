"""Unit tests for Career Impact Lab — Counterfactual What-If Simulator."""

import unittest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.models import Base, Opportunity, OpportunityCategory, StudentProfile, User
from app.db.session import get_db
from app.intelligence.what_if_simulator import WhatIfRequest, WhatIfSimulator
from app.main import app


class TestWhatIfSimulator(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        cls.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=cls.engine)
        Base.metadata.create_all(bind=cls.engine)

        cls.db = cls.SessionLocal()

        # Seed sample opportunities with strict criteria
        cls.opp_devops = Opportunity(
            id="test-devops-1",
            source="naukri",
            category=OpportunityCategory.PLACEMENT,
            title="Cloud DevOps Engineer",
            tags=["AWS", "Docker", "Linux", "Kubernetes"],
            eligibility_rules={
                "min_cgpa": 7.0,
                "allowed_degrees": ["B.Tech", "MCA"],
                "required_skills": ["Docker", "Linux"],
            },
            raw_data={"company": "CloudSprint", "location": "Pune", "work_type": "Hybrid"},
            is_active=True,
        )

        cls.opp_ai = Opportunity(
            id="test-ai-1",
            source="linkedin",
            category=OpportunityCategory.PLACEMENT,
            title="Junior AI / ML Engineer",
            tags=["Python", "PyTorch", "NLP", "Machine Learning"],
            eligibility_rules={
                "min_cgpa": 8.0,  # High CGPA gate
                "required_skills": ["Python", "Machine Learning"],
            },
            raw_data={"company": "Vectrix AI", "location": "Remote", "work_type": "Remote"},
            is_active=True,
        )

        cls.opp_web = Opportunity(
            id="test-web-1",
            source="internshala",
            category=OpportunityCategory.INTERNSHIP,
            title="Full Stack Web Intern",
            tags=["React", "Node.js", "JavaScript"],
            eligibility_rules={
                "min_cgpa": 6.5,
                "required_skills": ["JavaScript", "React"],
            },
            raw_data={"company": "WebCorp", "location": "Bengaluru", "work_type": "Remote"},
            is_active=True,
        )

        cls.db.add_all([cls.opp_devops, cls.opp_ai, cls.opp_web])
        cls.db.commit()

        def override_get_db():
            try:
                db = cls.SessionLocal()
                yield db
            finally:
                db.close()

        app.dependency_overrides[get_db] = override_get_db
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        cls.db.close()
        Base.metadata.drop_all(bind=cls.engine)

    def test_strict_eligibility_fails_missing_mandatory_skill(self):
        """Student with high CGPA but missing mandatory skill 'Docker' must NOT be eligible."""
        simulator = WhatIfSimulator(self.db)
        profile_data = {
            "cgpa": 8.5,
            "degree": "B.Tech",
            "skills": ["Python", "AWS", "Linux"],  # Missing 'Docker'
            "skill_proficiencies": {},
            "preferred_cities": ["Pune"],
            "preferred_work_modes": ["Hybrid"],
        }
        eligible, score, passed, failed, mgaps, _, _ = simulator.evaluate_opportunity(
            self.opp_devops, profile_data
        )
        self.assertFalse(eligible, "Must fail eligibility when mandatory skill is missing")
        self.assertIn("Docker", mgaps)
        self.assertTrue(score < 50.0, "Ineligible opportunity score must be penalized below 50")

    def test_strict_eligibility_fails_cgpa_gate(self):
        """Student with all required skills but CGPA 7.5 must fail for role requiring min_cgpa 8.0."""
        simulator = WhatIfSimulator(self.db)
        profile_data = {
            "cgpa": 7.5,  # Below 8.0
            "degree": "B.Tech",
            "skills": ["Python", "Machine Learning", "PyTorch"],
            "skill_proficiencies": {},
            "preferred_cities": ["Remote"],
            "preferred_work_modes": ["Remote"],
        }
        eligible, score, passed, failed, mgaps, _, _ = simulator.evaluate_opportunity(
            self.opp_ai, profile_data
        )
        self.assertFalse(eligible, "Must fail eligibility when CGPA is below mandatory minimum")
        self.assertTrue(any("CGPA" in f for f in failed))

    def test_live_recalculation_unlocks_newly_eligible(self):
        """Adding missing mandatory skills via simulation should transition role to NEWLY_ELIGIBLE."""
        simulator = WhatIfSimulator(self.db)

        # Baseline: lacks Docker and React
        req = WhatIfRequest(
            skills=["Python", "Linux", "Docker", "JavaScript", "React"],
            hypothetical_cgpa=7.5,
            completed_courses=["cloud_devops"],
            preferred_cities=["Pune", "Bengaluru"],
            preferred_work_modes=["Hybrid", "Remote"],
        )
        res = simulator.run_simulation(req)
        self.assertGreaterEqual(res.newly_unlocked_count, 1)

        # Verify DevOps engineer is now marked as NEWLY_ELIGIBLE or BOOSTED
        devops_eval = next((o for o in res.opportunities if o.id == "test-devops-1"), None)
        self.assertIsNotNone(devops_eval)
        self.assertTrue(devops_eval.simulated_eligible)

    def test_three_scenario_comparison_generated(self):
        """Simulator must generate exactly 3 distinct comparison scenarios."""
        simulator = WhatIfSimulator(self.db)
        req = WhatIfRequest(skills=["Python"])
        res = simulator.run_simulation(req)
        self.assertEqual(len(res.scenarios), 3)
        for s in res.scenarios:
            self.assertTrue(s.title)
            self.assertIsInstance(s.eligible_count, int)
            self.assertIsInstance(s.avg_match_score, float)

    def test_skill_impact_leaderboard(self):
        """Skills must be analyzed and ranked by impact."""
        simulator = WhatIfSimulator(self.db)
        req = WhatIfRequest(skills=["HTML"])
        res = simulator.run_simulation(req)
        self.assertTrue(len(res.skill_impact_leaderboard) > 0)
        top_skill = res.skill_impact_leaderboard[0]
        self.assertTrue(top_skill.skill)
        self.assertIn(top_skill.impact_tier, ["HIGH", "MEDIUM", "NICHE"])

    def test_api_what_if_endpoint(self):
        """FastAPI POST /api/v1/simulation/what-if returns valid payload."""
        response = self.client.post(
            "/api/v1/simulation/what-if",
            json={
                "skills": ["Python", "Docker", "Linux"],
                "completed_courses": ["data_analytics"],
                "preferred_cities": ["Bengaluru"],
                "preferred_work_modes": ["Remote"],
            },
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("opportunities", data)
        self.assertIn("skill_impact_leaderboard", data)
        self.assertIn("scenarios", data)


if __name__ == "__main__":
    unittest.main()
