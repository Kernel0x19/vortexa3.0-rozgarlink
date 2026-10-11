"""Job (Placement) connectors — three platforms: Naukri, LinkedIn, Wellfound.

Each connector provides realistic seeded data that closely mirrors the platform's
actual feed structure. When live API access is available the fetch() methods
can be swapped out for real HTTP calls without changing anything else.
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any, Dict, List
import logging

from app.ingestion.base import BaseConnector
from app.ingestion.normalizer import upsert_placement

logger = logging.getLogger(__name__)


# ── Naukri ────────────────────────────────────────────────────────────────────

class NaukriJobsConnector(BaseConnector):
    """Connector for Naukri.com full-time job listings."""

    name = "naukri"
    category = "placement"

    async def fetch(self) -> List[Dict[str, Any]]:
        today = date.today()
        return [
            {
                "external_id": "naukri-sde-1-2026",
                "source": "naukri",
                "source_url": "https://www.naukri.com/sde-1-jobs",
                "title": "Software Engineer (SDE-1) — Backend",
                "description": (
                    "Join a high-growth fintech startup building India's next payments platform. "
                    "Work on distributed microservices in Python/Go, design low-latency APIs, "
                    "and contribute to our ML-powered fraud detection layer."
                ),
                "company": "PayEdge Technologies",
                "location": "Bengaluru, Karnataka",
                "work_type": "Hybrid",
                "experience": "0–1 yr (Fresher welcome)",
                "amount_min": 700_000 / 12,
                "amount_max": 1_000_000 / 12,
                "deadline": (today + timedelta(days=25)).isoformat(),
                "tags": ["Python", "FastAPI", "PostgreSQL", "Redis", "Microservices"],
                "documents_required": ["Resume", "GitHub Portfolio"],
                "eligibility_rules": {
                    "min_cgpa": 6.5,
                    "allowed_degrees": ["B.Tech", "B.E.", "MCA"],
                    "required_skills": ["Python", "REST APIs"],
                },
            },
            {
                "external_id": "naukri-fe-dev-2026",
                "source": "naukri",
                "source_url": "https://www.naukri.com/frontend-developer-jobs-in-delhi",
                "title": "Frontend Developer (React / Next.js)",
                "description": (
                    "Build pixel-perfect, accessible UI for a B2B SaaS platform used by 500+ enterprises. "
                    "You'll own entire feature verticals from Figma mock to production deployment."
                ),
                "company": "ClarityHR Labs",
                "location": "Delhi NCR / Remote",
                "work_type": "Remote",
                "experience": "0–2 yr",
                "amount_min": 600_000 / 12,
                "amount_max": 900_000 / 12,
                "deadline": (today + timedelta(days=18)).isoformat(),
                "tags": ["React", "Next.js", "TypeScript", "TailwindCSS", "GraphQL"],
                "documents_required": ["Resume", "Portfolio Link"],
                "eligibility_rules": {
                    "min_cgpa": 6.0,
                    "required_skills": ["JavaScript", "React", "CSS"],
                },
            },
            {
                "external_id": "naukri-data-analyst-2026",
                "source": "naukri",
                "source_url": "https://www.naukri.com/data-analyst-jobs",
                "title": "Data Analyst — Product Analytics",
                "description": (
                    "Analyse product funnels, retention cohorts, and A/B experiment results for "
                    "a 10-million-user consumer app. Tools: SQL, Python (pandas), Metabase, Amplitude."
                ),
                "company": "KreativeMind Media",
                "location": "Hyderabad, Telangana",
                "work_type": "Onsite",
                "experience": "Fresher / 0–1 yr",
                "amount_min": 500_000 / 12,
                "amount_max": 750_000 / 12,
                "deadline": (today + timedelta(days=14)).isoformat(),
                "tags": ["SQL", "Python", "Metabase", "Excel", "Statistics"],
                "documents_required": ["Resume"],
                "eligibility_rules": {
                    "min_cgpa": 6.0,
                    "required_skills": ["SQL", "Data Analysis"],
                },
            },
            {
                "external_id": "naukri-devops-2026",
                "source": "naukri",
                "source_url": "https://www.naukri.com/devops-engineer-jobs",
                "title": "DevOps / Cloud Engineer",
                "description": (
                    "Manage CI/CD pipelines on GitHub Actions, containerise services on Kubernetes (EKS), "
                    "and maintain 99.9% SLA for our SaaS infrastructure on AWS."
                ),
                "company": "CloudSprint Technologies",
                "location": "Pune, Maharashtra",
                "work_type": "Hybrid",
                "experience": "0–2 yr",
                "amount_min": 750_000 / 12,
                "amount_max": 1_200_000 / 12,
                "deadline": (today + timedelta(days=30)).isoformat(),
                "tags": ["AWS", "Kubernetes", "Docker", "Terraform", "CI/CD"],
                "documents_required": ["Resume", "Certifications (if any)"],
                "eligibility_rules": {
                    "min_cgpa": 6.5,
                    "required_skills": ["Linux", "Docker", "AWS"],
                },
            },
        ]

    def normalize_and_store(self, raw_records: List[Dict[str, Any]]) -> int:
        count = 0
        for item in raw_records:
            upsert_placement(self.db, item)
            count += 1
        self.db.commit()
        return count


# ── LinkedIn Jobs ──────────────────────────────────────────────────────────────

class LinkedInJobsConnector(BaseConnector):
    """Connector for LinkedIn job postings (India, fresher/0-2 yr)."""

    name = "linkedin"
    category = "placement"

    async def fetch(self) -> List[Dict[str, Any]]:
        today = date.today()
        return [
            {
                "external_id": "linkedin-aiml-eng-2026",
                "source": "linkedin",
                "source_url": "https://www.linkedin.com/jobs/ai-ml-engineer-india",
                "title": "Junior AI / ML Engineer",
                "description": (
                    "Work on production LLM inference systems, RAG pipelines, and model fine-tuning "
                    "workflows at one of India's fastest-growing AI infrastructure companies."
                ),
                "company": "Vectrix AI",
                "location": "Remote (India)",
                "work_type": "Remote",
                "experience": "Fresher / 0–1 yr",
                "amount_min": 1_000_000 / 12,
                "amount_max": 1_500_000 / 12,
                "deadline": (today + timedelta(days=20)).isoformat(),
                "tags": ["Python", "PyTorch", "LangChain", "LLM", "MLOps"],
                "documents_required": ["Resume", "GitHub / Kaggle Profile"],
                "eligibility_rules": {
                    "min_cgpa": 7.0,
                    "required_skills": ["Python", "Machine Learning"],
                },
            },
            {
                "external_id": "linkedin-product-analyst-2026",
                "source": "linkedin",
                "source_url": "https://www.linkedin.com/jobs/product-analyst-india",
                "title": "Product Analyst — Growth",
                "description": (
                    "Own growth metrics for a Series-B SaaS startup: run A/B tests, "
                    "instrument feature analytics with Mixpanel, and present weekly insights to the CEO."
                ),
                "company": "LaunchPad SaaS",
                "location": "Mumbai, Maharashtra",
                "work_type": "Hybrid",
                "experience": "0–2 yr",
                "amount_min": 800_000 / 12,
                "amount_max": 1_100_000 / 12,
                "deadline": (today + timedelta(days=16)).isoformat(),
                "tags": ["SQL", "Mixpanel", "A/B Testing", "Product Analytics", "Excel"],
                "documents_required": ["Resume"],
                "eligibility_rules": {
                    "min_cgpa": 6.5,
                    "required_skills": ["SQL", "Product Thinking"],
                },
            },
            {
                "external_id": "linkedin-backend-go-2026",
                "source": "linkedin",
                "source_url": "https://www.linkedin.com/jobs/golang-backend-engineer",
                "title": "Backend Engineer — Go / gRPC",
                "description": (
                    "Build ultra-low-latency trading infrastructure in Go, design gRPC services, "
                    "and optimise database queries processing 10k transactions per second."
                ),
                "company": "AlphaQuant Systems",
                "location": "Bengaluru, Karnataka",
                "work_type": "Onsite",
                "experience": "0–2 yr",
                "amount_min": 1_200_000 / 12,
                "amount_max": 1_800_000 / 12,
                "deadline": (today + timedelta(days=12)).isoformat(),
                "tags": ["Go", "gRPC", "PostgreSQL", "Kafka", "Distributed Systems"],
                "documents_required": ["Resume", "GitHub Profile"],
                "eligibility_rules": {
                    "min_cgpa": 7.5,
                    "required_skills": ["Go", "Distributed Systems"],
                },
            },
            {
                "external_id": "linkedin-cybersec-analyst-2026",
                "source": "linkedin",
                "source_url": "https://www.linkedin.com/jobs/cybersecurity-analyst-india",
                "title": "Junior Cybersecurity Analyst",
                "description": (
                    "Perform vulnerability assessments, monitor SIEM alerts, triage incidents, "
                    "and contribute to security hardening of our cloud-native platform."
                ),
                "company": "ShieldLayer Security",
                "location": "Chennai, Tamil Nadu",
                "work_type": "Hybrid",
                "experience": "Fresher / 0–1 yr",
                "amount_min": 600_000 / 12,
                "amount_max": 900_000 / 12,
                "deadline": (today + timedelta(days=22)).isoformat(),
                "tags": ["Cybersecurity", "SIEM", "Linux", "Networking", "OWASP"],
                "documents_required": ["Resume", "CEH / CompTIA (preferred)"],
                "eligibility_rules": {
                    "min_cgpa": 6.0,
                    "required_skills": ["Linux", "Networking"],
                },
            },
        ]

    def normalize_and_store(self, raw_records: List[Dict[str, Any]]) -> int:
        count = 0
        for item in raw_records:
            upsert_placement(self.db, item)
            count += 1
        self.db.commit()
        return count


# ── Wellfound (AngelList) ──────────────────────────────────────────────────────

class WellfoundJobsConnector(BaseConnector):
    """Connector for Wellfound (ex-AngelList Talent) startup job listings."""

    name = "wellfound"
    category = "placement"

    async def fetch(self) -> List[Dict[str, Any]]:
        today = date.today()
        return [
            {
                "external_id": "wellfound-fullstack-2026",
                "source": "wellfound",
                "source_url": "https://wellfound.com/jobs/fullstack-engineer-india",
                "title": "Full-Stack Engineer (Early-Stage Startup)",
                "description": (
                    "Be an early engineer at a climate-tech startup building IoT sensor dashboards "
                    "and carbon credit marketplace. Ownership from day one — ship features weekly."
                ),
                "company": "Greenloop Tech",
                "location": "Remote (India)",
                "work_type": "Remote",
                "experience": "Fresher / 0–2 yr",
                "amount_min": 700_000 / 12,
                "amount_max": 1_000_000 / 12,
                "deadline": (today + timedelta(days=28)).isoformat(),
                "tags": ["React", "Node.js", "MongoDB", "IoT", "REST APIs"],
                "documents_required": ["Resume", "Portfolio / GitHub"],
                "eligibility_rules": {
                    "required_skills": ["JavaScript", "Node.js", "React"],
                },
            },
            {
                "external_id": "wellfound-growth-hacker-2026",
                "source": "wellfound",
                "source_url": "https://wellfound.com/jobs/growth-marketing-india",
                "title": "Growth Hacker / Marketing Analyst",
                "description": (
                    "Run paid acquisition experiments on Meta and Google, "
                    "optimise onboarding funnels, and grow our monthly active users from 50k to 500k."
                ),
                "company": "UrbanNest PropTech",
                "location": "Gurgaon, Haryana",
                "work_type": "Hybrid",
                "experience": "0–1 yr",
                "amount_min": 500_000 / 12,
                "amount_max": 800_000 / 12,
                "deadline": (today + timedelta(days=10)).isoformat(),
                "tags": ["Growth Marketing", "SQL", "Meta Ads", "Google Ads", "Analytics"],
                "documents_required": ["Resume"],
                "eligibility_rules": {
                    "required_skills": ["Digital Marketing", "Analytics"],
                },
            },
            {
                "external_id": "wellfound-mobile-dev-2026",
                "source": "wellfound",
                "source_url": "https://wellfound.com/jobs/react-native-developer-india",
                "title": "React Native Developer",
                "description": (
                    "Build the consumer mobile app for a D2C health-tech brand serving 2M+ users. "
                    "Integrate Bluetooth health devices, in-app purchases, and real-time notifications."
                ),
                "company": "HealthOS",
                "location": "Bengaluru, Karnataka",
                "work_type": "Onsite",
                "experience": "0–2 yr",
                "amount_min": 800_000 / 12,
                "amount_max": 1_200_000 / 12,
                "deadline": (today + timedelta(days=15)).isoformat(),
                "tags": ["React Native", "TypeScript", "iOS", "Android", "Redux"],
                "documents_required": ["Resume", "App Store / Play Store links (if any)"],
                "eligibility_rules": {
                    "required_skills": ["React Native", "JavaScript"],
                },
            },
            {
                "external_id": "wellfound-founding-eng-2026",
                "source": "wellfound",
                "source_url": "https://wellfound.com/jobs/founding-engineer-edtech",
                "title": "Founding Engineer — EdTech Platform",
                "description": (
                    "Join as one of the first 5 engineers at a YC-backed edtech startup. "
                    "Build the AI tutoring engine, live classroom infrastructure, and mobile app from scratch."
                ),
                "company": "LearnSpark AI (YC W26)",
                "location": "Remote (India preferred)",
                "work_type": "Remote",
                "experience": "Fresher / Any",
                "amount_min": 1_000_000 / 12,
                "amount_max": 1_600_000 / 12,
                "deadline": (today + timedelta(days=35)).isoformat(),
                "tags": ["Python", "FastAPI", "React", "WebRTC", "AI", "Startup"],
                "documents_required": ["Resume", "GitHub Profile", "Brief Intro (loom/video)"],
                "eligibility_rules": {
                    "required_skills": ["Full-Stack", "Problem Solving"],
                },
            },
        ]

    def normalize_and_store(self, raw_records: List[Dict[str, Any]]) -> int:
        count = 0
        for item in raw_records:
            upsert_placement(self.db, item)
            count += 1
        self.db.commit()
        return count
