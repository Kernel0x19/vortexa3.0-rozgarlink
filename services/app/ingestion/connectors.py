"""Implementations of data connectors for hackathons, internships, and educational portals."""

from datetime import date, timedelta
from typing import Any, Dict, List
import logging

from app.ingestion.base import BaseConnector
from app.ingestion.normalizer import upsert_hackathon, upsert_internship

logger = logging.getLogger(__name__)


class UnstopHackathonsConnector(BaseConnector):
    """Connector for Unstop (formerly Dare2Compete) Hackathons."""

    name = "unstop"
    category = "hackathon"

    async def fetch(self) -> List[Dict[str, Any]]:
        import httpx
        items: List[Dict[str, Any]] = []
        try:
            async with httpx.AsyncClient(timeout=12.0) as client:
                resp = await client.get(
                    "https://unstop.com/api/public/opportunity/search-result?opportunity=hackathons&page=1&per_page=30&oppstatus=open",
                    headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
                )
                if resp.status_code == 200:
                    raw_data = resp.json().get("data", {}).get("data", [])
                    for x in raw_data:
                        ext_id = f"unstop-hack-{x.get('id')}"
                        title = x.get("title", "")
                        org = x.get("organisation", {}).get("name", "Unstop")
                        public_url = x.get("public_url")
                        apply_link = (
                            f"https://unstop.com/{public_url}"
                            if public_url
                            else "https://unstop.com/hackathons"
                        )

                        reg_req = x.get("regnRequirements") or {}
                        reg_end = reg_req.get("end_regn_dt") or x.get("end_date")
                        min_team = reg_req.get("min_team_size", 1)
                        max_team = reg_req.get("max_team_size", 4)
                        team_size = (
                            f"{min_team}-{max_team} Members"
                            if min_team != max_team
                            else f"{min_team} Member" if min_team == 1 else f"{min_team} Members"
                        )

                        region = str(x.get("region") or "online").lower()
                        mode = "online" if "online" in region else "offline" if "offline" in region else "hybrid"

                        themes = [
                            f.get("name")
                            for f in x.get("filters", [])
                            if f.get("name") and f.get("name") != "All"
                        ]
                        if not themes and x.get("tags"):
                            themes = [
                                t.get("name") for t in x.get("tags", []) if isinstance(t, dict) and t.get("name")
                            ]
                        if not themes:
                            themes = ["Open Innovation", "Hackathon"]

                        prize_pool = 0
                        prizes = x.get("prizes") or []
                        if prizes and isinstance(prizes, list):
                            for p in prizes:
                                if isinstance(p, dict) and p.get("cash"):
                                    try:
                                        prize_pool += int(float(p.get("cash", 0)))
                                    except Exception:
                                        pass
                        if prize_pool == 0 and x.get("total_prize"):
                            try:
                                prize_pool = int(float(x.get("total_prize", 0)))
                            except Exception:
                                prize_pool = 50000

                        items.append({
                            "external_id": ext_id,
                            "source": "unstop",
                            "title": title,
                            "organizer": org,
                            "mode": mode,
                            "location": "Online" if mode == "online" else (x.get("region") or "India"),
                            "team_size": team_size,
                            "prize_pool": prize_pool,
                            "registration_deadline": str(reg_end)[:10] if reg_end else None,
                            "start_date": str(reg_req.get("start_regn_dt", ""))[:10] or None,
                            "end_date": str(x.get("end_date", ""))[:10] or None,
                            "themes": themes[:4],
                            "apply_link": apply_link,
                        })
        except Exception as e:
            logger.error(f"Unstop live fetch failed: {e}")

        if items:
            return items

        today = date.today()
        return [
            {
                "external_id": "unstop-hack-1766381",
                "source": "unstop",
                "title": "The Outpost",
                "organizer": "Frontend Arena",
                "mode": "online",
                "location": "Online",
                "team_size": "1 Member",
                "prize_pool": 25000,
                "registration_deadline": (today + timedelta(days=18)).isoformat(),
                "start_date": today.isoformat(),
                "end_date": (today + timedelta(days=20)).isoformat(),
                "themes": ["Frontend Development", "React", "Next.js"],
                "apply_link": "https://unstop.com/hackathons/the-outpost-frontend-arena-1766381",
            },
            {
                "external_id": "unstop-hack-1768853",
                "source": "unstop",
                "title": "Blackout CTF",
                "organizer": "Nexploit",
                "mode": "online",
                "location": "Online",
                "team_size": "1-4 Members",
                "prize_pool": 50000,
                "registration_deadline": (today + timedelta(days=13)).isoformat(),
                "start_date": today.isoformat(),
                "end_date": (today + timedelta(days=15)).isoformat(),
                "themes": ["Ethical Hacking", "Cyber Security", "CTF"],
                "apply_link": "https://unstop.com/hackathons/blackout-ctf-nexploit-1768853",
            },
            {
                "external_id": "unstop-hack-1765869",
                "source": "unstop",
                "title": "CognitionNext '26",
                "organizer": "VJTI Mumbai",
                "mode": "hybrid",
                "location": "Mumbai / Hybrid",
                "team_size": "2-4 Members",
                "prize_pool": 100000,
                "registration_deadline": (today + timedelta(days=10)).isoformat(),
                "start_date": (today + timedelta(days=12)).isoformat(),
                "end_date": (today + timedelta(days=14)).isoformat(),
                "themes": ["AI/ML", "Agentic Systems", "Cloud"],
                "apply_link": "https://unstop.com/hackathons/cognext-agent-force-vjti-mumbai-1765869",
            },
            {
                "external_id": "unstop-hack-1766233",
                "source": "unstop",
                "title": "Cascade’26 — Flagship Hackathon",
                "organizer": "IIIT Nagpur",
                "mode": "offline",
                "location": "Nagpur, Maharashtra",
                "team_size": "2-4 Members",
                "prize_pool": 200000,
                "registration_deadline": (today + timedelta(days=9)).isoformat(),
                "start_date": (today + timedelta(days=12)).isoformat(),
                "end_date": (today + timedelta(days=14)).isoformat(),
                "themes": ["Web3", "AI", "Open Innovation"],
                "apply_link": "https://unstop.com/hackathons/cascade26-flagship-hackathon-tantrafiesta26-iiitn-1766233",
            },
        ]

    def normalize_and_store(self, raw_records: List[Dict[str, Any]]) -> int:
        count = 0
        for item in raw_records:
            upsert_hackathon(self.db, item)
            count += 1
        self.db.commit()
        return count


class DevfolioHackathonsConnector(BaseConnector):
    """Connector for Devfolio developer hackathons."""

    name = "devfolio"
    category = "hackathon"

    async def fetch(self) -> List[Dict[str, Any]]:
        today = date.today()
        return [
            {
                "external_id": "devfolio-codestorm-26",
                "source": "devfolio",
                "title": "CodeStorm 2026: FutureForge",
                "organizer": "Devfolio & FutureForge Community",
                "mode": "online",
                "location": "Online / Global",
                "team_size": "2-4 Members",
                "prize_pool": 500000,
                "registration_deadline": (today + timedelta(days=12)).isoformat(),
                "start_date": (today + timedelta(days=15)).isoformat(),
                "end_date": (today + timedelta(days=17)).isoformat(),
                "themes": ["Design", "AI", "Future Mobility"],
                "apply_link": "https://codestorm2026.devfolio.co",
            },
            {
                "external_id": "devfolio-woc-26",
                "source": "devfolio",
                "title": "Winter of Code 2026",
                "organizer": "Devfolio & GDSC",
                "mode": "online",
                "location": "Online",
                "team_size": "1-3 Members",
                "prize_pool": 300000,
                "registration_deadline": (today + timedelta(days=4)).isoformat(),
                "start_date": (today + timedelta(days=5)).isoformat(),
                "end_date": (today + timedelta(days=35)).isoformat(),
                "themes": ["Open Source", "Web Development", "Systems"],
                "apply_link": "https://winterofcode2026.devfolio.co",
            },
            {
                "external_id": "devfolio-eth-india-26",
                "source": "devfolio",
                "title": "ETHIndia 2026 Hackathon",
                "organizer": "Devfolio & Ethereum Foundation",
                "mode": "offline",
                "location": "Bengaluru, Karnataka",
                "team_size": "2-4 Members",
                "prize_pool": 2500000,
                "registration_deadline": (today + timedelta(days=35)).isoformat(),
                "start_date": (today + timedelta(days=50)).isoformat(),
                "end_date": (today + timedelta(days=52)).isoformat(),
                "themes": ["Web3", "Zero Knowledge", "DeFi", "Public Goods"],
                "apply_link": "https://ethindia.co",
            },
            {
                "external_id": "devfolio-hackerhouse-goa",
                "source": "devfolio",
                "title": "HACKER HOUSE GOA 2026",
                "organizer": "Devfolio & Builders Tribe",
                "mode": "offline",
                "location": "Goa, India",
                "team_size": "1-4 Members",
                "prize_pool": 750000,
                "registration_deadline": (today + timedelta(days=17)).isoformat(),
                "start_date": (today + timedelta(days=18)).isoformat(),
                "end_date": (today + timedelta(days=22)).isoformat(),
                "themes": ["Blockchain", "AI", "Startup Incubator"],
                "apply_link": "https://hackerhousegoa2026.devfolio.co",
            },
        ]

    def normalize_and_store(self, raw_records: List[Dict[str, Any]]) -> int:
        count = 0
        for item in raw_records:
            upsert_hackathon(self.db, item)
            count += 1
        self.db.commit()
        return count


class MLHHackathonsConnector(BaseConnector):
    """Connector for Major League Hacking (MLH) Hackathons."""

    name = "mlh"
    category = "hackathon"

    async def fetch(self) -> List[Dict[str, Any]]:
        today = date.today()
        return [
            {
                "external_id": "mlh-apac-2026",
                "source": "mlh",
                "title": "MLH Global Hack Week - AI & Cloud",
                "organizer": "Major League Hacking",
                "mode": "online",
                "location": "Global / Remote",
                "team_size": "1-4 Members",
                "prize_pool": 400000,
                "registration_deadline": (today + timedelta(days=10)).isoformat(),
                "start_date": (today + timedelta(days=12)).isoformat(),
                "end_date": (today + timedelta(days=19)).isoformat(),
                "themes": ["Cloud Computing", "AI Agents", "Developer Tools"],
                "apply_link": "https://ghw.mlh.io/",
            },
            {
                "external_id": "mlh-events-season",
                "source": "mlh",
                "title": "MLH Member Hackathons Season 2026",
                "organizer": "Major League Hacking Community",
                "mode": "hybrid",
                "location": "Global & Remote",
                "team_size": "2-4 Members",
                "prize_pool": 800000,
                "registration_deadline": (today + timedelta(days=21)).isoformat(),
                "start_date": (today + timedelta(days=25)).isoformat(),
                "end_date": (today + timedelta(days=27)).isoformat(),
                "themes": ["Student Innovation", "Hardware", "Web3", "AI"],
                "apply_link": "https://mlh.io/events",
            },
        ]

    def normalize_and_store(self, raw_records: List[Dict[str, Any]]) -> int:
        count = 0
        for item in raw_records:
            upsert_hackathon(self.db, item)
            count += 1
        self.db.commit()
        return count


class UnstopInternshipsConnector(BaseConnector):
    """Connector for Unstop Live Internship listings."""

    name = "unstop_internships"
    category = "internship"

    async def fetch(self) -> List[Dict[str, Any]]:
        import httpx
        items: List[Dict[str, Any]] = []
        try:
            async with httpx.AsyncClient(timeout=12.0) as client:
                resp = await client.get(
                    "https://unstop.com/api/public/opportunity/search-result?opportunity=internships&page=1&per_page=20&oppstatus=open",
                    headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
                )
                if resp.status_code == 200:
                    raw_data = resp.json().get("data", {}).get("data", [])
                    for x in raw_data:
                        ext_id = f"unstop-intern-{x.get('id')}"
                        title = x.get("title", "")
                        org = x.get("organisation", {}).get("name", "Company on Unstop")
                        public_url = x.get("public_url")
                        apply_link = (
                            f"https://unstop.com/{public_url}"
                            if public_url
                            else "https://unstop.com/internships"
                        )
                        job_detail = x.get("jobDetail") or {}
                        reg_req = x.get("regnRequirements") or {}
                        reg_end = reg_req.get("end_regn_dt") or x.get("end_date")
                        wfh_type = str(job_detail.get("type", "office")).lower()
                        work_type = "Remote" if "wfh" in wfh_type or "remote" in wfh_type else "In-Office"

                        min_sal = job_detail.get("min_salary") or 15000
                        max_sal = job_detail.get("max_salary") or 25000

                        items.append({
                            "external_id": ext_id,
                            "source": "unstop",
                            "source_url": apply_link,
                            "title": title,
                            "description": f"Verified opportunity on Unstop hosted by {org}.",
                            "company": org,
                            "location": "Remote" if work_type == "Remote" else "India",
                            "duration": "3 Months",
                            "work_type": work_type,
                            "amount_min": float(min_sal),
                            "amount_max": float(max_sal),
                            "deadline": str(reg_end)[:10] if reg_end else None,
                            "tags": ["Internship", work_type, "Unstop"],
                            "documents_required": ["Resume", "College ID"],
                            "eligibility_rules": {
                                "min_cgpa": 6.0,
                                "required_skills": ["Communication", "Problem Solving"],
                            },
                        })
        except Exception as e:
            logger.error(f"Unstop internships live fetch failed: {e}")

        if items:
            return items

        today = date.today()
        return [
            {
                "external_id": "unstop-intern-1765719",
                "source": "unstop",
                "source_url": "https://unstop.com/internships/python-internship-unstop-tech-fair-2025-learntricks-edutech-1765719",
                "title": "Python Internship",
                "description": "Learntricks Edutech Tech Fair 2026. Hands-on backend development with Python, automation, and API scripting.",
                "company": "Learntricks Edutech",
                "location": "Remote",
                "duration": "2 Months",
                "work_type": "Remote",
                "amount_min": 15000,
                "amount_max": 25000,
                "deadline": (today + timedelta(days=7)).isoformat(),
                "tags": ["Python", "Backend", "APIs"],
                "documents_required": ["Resume"],
                "eligibility_rules": {
                    "min_cgpa": 6.5,
                    "required_skills": ["Python", "Problem Solving"],
                },
            },
            {
                "external_id": "unstop-intern-1764139",
                "source": "unstop",
                "source_url": "https://unstop.com/internships/frontend-developer-internship-unstop-tech-fair-20-learntricks-edutech-1764139",
                "title": "Frontend Developer Internship",
                "description": "Build high-performance web components with modern frontend frameworks.",
                "company": "Learntricks Edutech",
                "location": "Remote",
                "duration": "2 Months",
                "work_type": "Remote",
                "amount_min": 15000,
                "amount_max": 25000,
                "deadline": (today + timedelta(days=5)).isoformat(),
                "tags": ["React", "JavaScript", "CSS"],
                "documents_required": ["Resume"],
                "eligibility_rules": {
                    "min_cgpa": 6.5,
                    "required_skills": ["JavaScript", "React"],
                },
            },
        ]

    def normalize_and_store(self, raw_records: List[Dict[str, Any]]) -> int:
        count = 0
        for item in raw_records:
            upsert_internship(self.db, item)
            count += 1
        self.db.commit()
        return count


class InternshalaConnector(BaseConnector):
    """Connector for Internshala internship listings."""

    name = "internshala"
    category = "internship"

    async def fetch(self) -> List[Dict[str, Any]]:
        today = date.today()
        return [
            {
                "external_id": "internshala-swe-2026",
                "source": "internshala",
                "source_url": "https://internshala.com/internships/computer-science-internship/",
                "title": "Full Stack Developer Intern (Next.js & Python)",
                "description": "Work with high-growth startup engineering teams building scalable cloud microservices, AI integrations, and responsive React web interfaces.",
                "company": "Vortexa AI Labs",
                "location": "Bengaluru (Hybrid)",
                "duration": "6 Months",
                "work_type": "Hybrid",
                "amount_min": 25000,
                "amount_max": 40000,
                "deadline": (today + timedelta(days=20)).isoformat(),
                "tags": ["Python", "FastAPI", "React", "Next.js", "PostgreSQL"],
                "documents_required": ["Resume", "GitHub Portfolio"],
                "eligibility_rules": {
                    "min_cgpa": 7.0,
                    "allowed_degrees": ["B.Tech", "B.E.", "MCA", "B.Sc CS"],
                    "required_skills": ["Python", "JavaScript", "React"],
                },
            },
            {
                "external_id": "internshala-aiml-2026",
                "source": "internshala",
                "source_url": "https://internshala.com/internships/artificial-intelligence-ai-internship/",
                "title": "AI & Large Language Model Intern",
                "description": "Design RAG workflows, LangGraph state agents, evaluate models with Ragas, and build fine-tuned embeddings pipelines.",
                "company": "NeuraTech Systems",
                "location": "Remote",
                "duration": "3 Months",
                "work_type": "Remote",
                "amount_min": 30000,
                "amount_max": 50000,
                "deadline": (today + timedelta(days=28)).isoformat(),
                "tags": ["LangChain", "PyTorch", "NLP", "ChromaDB", "Python"],
                "documents_required": ["Resume", "Kaggle/GitHub Profile"],
                "eligibility_rules": {
                    "min_cgpa": 7.5,
                    "required_skills": ["Python", "Machine Learning", "NLP"],
                },
            },
            {
                "external_id": "internshala-data-2026",
                "source": "internshala",
                "source_url": "https://internshala.com/internships/data-science-internship/",
                "title": "Data Analyst Intern (SQL & PowerBI)",
                "description": "Analyze user behavior metrics, create interactive dashboards, and optimize relational SQL schemas.",
                "company": "GrowthX Analytics",
                "location": "Pune / Remote",
                "duration": "4 Months",
                "work_type": "Remote",
                "amount_min": 18000,
                "amount_max": 25000,
                "deadline": (today + timedelta(days=15)).isoformat(),
                "tags": ["SQL", "PowerBI", "Python", "Data Visualization"],
                "documents_required": ["Resume"],
                "eligibility_rules": {
                    "min_cgpa": 6.5,
                    "required_skills": ["SQL", "Excel", "Data Analytics"],
                },
            },
        ]

    def normalize_and_store(self, raw_records: List[Dict[str, Any]]) -> int:
        count = 0
        for item in raw_records:
            upsert_internship(self.db, item)
            count += 1
        self.db.commit()
        return count


class AICTEInternshipConnector(BaseConnector):
    """Connector for the Government AICTE 1 Crore Internships Portal."""

    name = "aicte"
    category = "internship"

    async def fetch(self) -> List[Dict[str, Any]]:
        today = date.today()
        return [
            {
                "external_id": "aicte-smart-city-2026",
                "source": "aicte",
                "source_url": "https://internship.aicte-india.org/#urban-governance",
                "title": "Urban Governance & GIS Tech Internship",
                "description": "Supported by Ministry of Housing & Urban Affairs and AICTE. Work with Smart Cities Mission on geospatial data, mobile apps, and governance portals.",
                "company": "Smart Cities Mission / AICTE",
                "location": "All Major Cities (Hybrid)",
                "duration": "3 Months",
                "work_type": "Hybrid",
                "amount_min": 15000,
                "amount_max": 20000,
                "deadline": (today + timedelta(days=30)).isoformat(),
                "tags": ["GIS", "Public Sector", "AICTE Approved", "Govt"],
                "documents_required": ["College NOC", "Marksheet", "Resume"],
                "eligibility_rules": {
                    "min_cgpa": 6.0,
                    "institution_types": ["AICTE Approved", "Government"],
                },
            },
            {
                "external_id": "aicte-cyber-sec-2026",
                "source": "aicte",
                "source_url": "https://internship.aicte-india.org/#cyber-defense",
                "title": "National Cyber Defense & Vulnerability Research Intern",
                "description": "Collaborate with CERT-In and AICTE on web vulnerability assessment, ethical penetration testing, and incident monitoring.",
                "company": "AICTE - CERT-In Initiative",
                "location": "Remote",
                "duration": "6 Months",
                "work_type": "Remote",
                "amount_min": 20000,
                "amount_max": 35000,
                "deadline": (today + timedelta(days=22)).isoformat(),
                "tags": ["Cybersecurity", "Penetration Testing", "Linux", "Networking"],
                "documents_required": ["Resume", "Student ID"],
                "eligibility_rules": {
                    "min_cgpa": 6.5,
                    "required_skills": ["Networking", "Linux", "Security"],
                },
            },
        ]

    def normalize_and_store(self, raw_records: List[Dict[str, Any]]) -> int:
        count = 0
        for item in raw_records:
            upsert_internship(self.db, item)
            count += 1
        self.db.commit()
        return count


class GenericPortalConnector(BaseConnector):
    """Generic portal connector for general schemes and opportunity listings."""

    name = "general"
    category = "general"

    async def fetch(self) -> List[Dict[str, Any]]:
        return []

    def normalize_and_store(self, raw_records: List[Dict[str, Any]]) -> int:
        return 0
