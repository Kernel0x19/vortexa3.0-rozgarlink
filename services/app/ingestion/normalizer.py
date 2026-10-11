"""Normalizer and deduplication utility for RozgarLink data ingestion pipeline."""

from datetime import date, datetime
import logging
from typing import Any, Dict, Optional
from sqlalchemy.orm import Session

from app.db.models import Hackathon, Opportunity, OpportunityCategory

logger = logging.getLogger(__name__)


def upsert_hackathon(db: Session, data: Dict[str, Any]) -> Hackathon:
    """Normalize, deduplicate, and upsert a hackathon record."""
    source = data.get("source", "unstop")
    ext_id = str(data.get("external_id") or data.get("id") or "")

    reg_deadline = data.get("registration_deadline")
    if isinstance(reg_deadline, str) and reg_deadline:
        try:
            reg_deadline = datetime.strptime(reg_deadline[:10], "%Y-%m-%d").date()
        except Exception:
            reg_deadline = None

    start_date = data.get("start_date")
    if isinstance(start_date, str) and start_date:
        try:
            start_date = datetime.strptime(start_date[:10], "%Y-%m-%d").date()
        except Exception:
            start_date = None

    end_date = data.get("end_date")
    if isinstance(end_date, str) and end_date:
        try:
            end_date = datetime.strptime(end_date[:10], "%Y-%m-%d").date()
        except Exception:
            end_date = None

    existing = db.query(Hackathon).filter_by(source=source, external_id=ext_id).first()

    if existing:
        existing.title = data.get("title", existing.title)
        existing.organizer = data.get("organizer", existing.organizer)
        existing.mode = data.get("mode", existing.mode)
        existing.location = data.get("location", existing.location)
        existing.team_size = data.get("team_size", existing.team_size)
        existing.prize_pool = int(data.get("prize_pool", existing.prize_pool or 0))
        if reg_deadline:
            existing.registration_deadline = reg_deadline
        if start_date:
            existing.start_date = start_date
        if end_date:
            existing.end_date = end_date
        existing.themes = data.get("themes", existing.themes or [])
        existing.apply_link = data.get("apply_link", existing.apply_link)
        existing.is_active = data.get("is_active", True)
        existing.last_synced_at = datetime.utcnow()
        obj = existing
    else:
        obj = Hackathon(
            external_id=ext_id,
            source=source,
            title=data.get("title", "Untitled Hackathon"),
            organizer=data.get("organizer"),
            mode=data.get("mode", "online"),
            location=data.get("location"),
            team_size=data.get("team_size", "1-4 Members"),
            prize_pool=int(data.get("prize_pool", 0)),
            registration_deadline=reg_deadline,
            start_date=start_date,
            end_date=end_date,
            themes=data.get("themes", []),
            apply_link=data.get("apply_link"),
            posted_date=date.today(),
            is_active=True,
            last_synced_at=datetime.utcnow(),
        )
        db.add(obj)

    return obj


def upsert_internship(db: Session, data: Dict[str, Any]) -> Opportunity:
    """Normalize, deduplicate, and upsert an internship opportunity."""
    source = data.get("source", "internshala")
    ext_id = str(data.get("external_id") or data.get("id") or "")
    source_url = data.get("source_url") or data.get("application_url")

    deadline = data.get("deadline")
    if isinstance(deadline, str) and deadline:
        try:
            deadline = datetime.strptime(deadline[:10], "%Y-%m-%d").date()
        except Exception:
            deadline = None

    q = db.query(Opportunity).filter_by(source=source, external_id=ext_id)
    existing = q.first()
    if not existing and source_url:
        existing = db.query(Opportunity).filter_by(source_url=source_url).first()

    raw_data = data.get("raw_data") or {
        "company": data.get("company"),
        "location": data.get("location"),
        "duration": data.get("duration"),
        "stipend": data.get("stipend"),
        "work_type": data.get("work_type", "Remote"),
    }

    if existing:
        existing.title = data.get("title", existing.title)
        existing.description = data.get("description", existing.description)
        existing.amount_min = float(data.get("amount_min", existing.amount_min or 0))
        existing.amount_max = float(data.get("amount_max", existing.amount_max or 0))
        if deadline:
            existing.deadline = deadline
        existing.eligibility_rules = data.get("eligibility_rules", existing.eligibility_rules or {})
        existing.documents_required = data.get("documents_required", existing.documents_required or [])
        if source_url and source_url != existing.source_url:
            taken = db.query(Opportunity).filter_by(source_url=source_url).first()
            if not taken or taken.id == existing.id:
                existing.source_url = source_url
        existing.application_url = source_url or existing.application_url
        existing.tags = data.get("tags", existing.tags or [])
        existing.raw_data = raw_data
        existing.is_active = True
        existing.last_synced_at = datetime.utcnow()
        obj = existing
    else:
        obj = Opportunity(
            external_id=ext_id,
            source=source,
            source_url=source_url,
            category=OpportunityCategory.INTERNSHIP,
            title=data.get("title", "Untitled Internship"),
            description=data.get("description", ""),
            amount_min=float(data.get("amount_min", 0)),
            amount_max=float(data.get("amount_max", 0)),
            deadline=deadline,
            eligibility_rules=data.get("eligibility_rules", {}),
            documents_required=data.get("documents_required", ["Resume", "College ID"]),
            application_url=source_url,
            tags=data.get("tags", []),
            raw_data=raw_data,
            is_active=True,
            last_synced_at=datetime.utcnow(),
        )
        db.add(obj)

    # Index in Chroma vector store if possible
    try:
        from app.knowledge.hybrid_rag import HybridRAG
        rag = HybridRAG()
        rag.index_opportunity(obj)
    except Exception as e:
        logger.debug(f"Vector indexing skipped: {e}")

    return obj


def upsert_placement(db: Session, data: Dict[str, Any]) -> Opportunity:
    """Normalize, deduplicate, and upsert a full-time job (placement) opportunity."""
    source = data.get("source", "naukri")
    ext_id = str(data.get("external_id") or data.get("id") or "")
    source_url = data.get("source_url") or data.get("application_url")

    deadline = data.get("deadline")
    if isinstance(deadline, str) and deadline:
        try:
            deadline = datetime.strptime(deadline[:10], "%Y-%m-%d").date()
        except Exception:
            deadline = None

    q = db.query(Opportunity).filter_by(source=source, external_id=ext_id)
    existing = q.first()
    if not existing and source_url:
        existing = db.query(Opportunity).filter_by(source_url=source_url).first()

    raw_data = data.get("raw_data") or {
        "company": data.get("company"),
        "location": data.get("location"),
        "work_type": data.get("work_type", "Onsite"),
        "experience": data.get("experience", "Fresher"),
        "organization": data.get("company"),
    }

    if existing:
        existing.title = data.get("title", existing.title)
        existing.description = data.get("description", existing.description)
        existing.amount_min = float(data.get("amount_min", existing.amount_min or 0))
        existing.amount_max = float(data.get("amount_max", existing.amount_max or 0))
        if deadline:
            existing.deadline = deadline
        existing.eligibility_rules = data.get("eligibility_rules", existing.eligibility_rules or {})
        existing.documents_required = data.get("documents_required", existing.documents_required or [])
        if source_url and source_url != existing.source_url:
            taken = db.query(Opportunity).filter_by(source_url=source_url).first()
            if not taken or taken.id == existing.id:
                existing.source_url = source_url
        existing.application_url = source_url or existing.application_url
        existing.tags = data.get("tags", existing.tags or [])
        existing.raw_data = raw_data
        existing.is_active = True
        existing.last_synced_at = datetime.utcnow()
        obj = existing
    else:
        obj = Opportunity(
            external_id=ext_id,
            source=source,
            source_url=source_url,
            category=OpportunityCategory.PLACEMENT,
            title=data.get("title", "Untitled Job"),
            description=data.get("description", ""),
            amount_min=float(data.get("amount_min", 0)),
            amount_max=float(data.get("amount_max", 0)),
            deadline=deadline,
            eligibility_rules=data.get("eligibility_rules", {}),
            documents_required=data.get("documents_required", ["Resume"]),
            application_url=source_url,
            tags=data.get("tags", []),
            raw_data=raw_data,
            is_active=True,
            last_synced_at=datetime.utcnow(),
        )
        db.add(obj)

    # Index in Chroma vector store if possible
    try:
        from app.knowledge.hybrid_rag import HybridRAG
        rag = HybridRAG()
        rag.index_opportunity(obj)
    except Exception as e:
        logger.debug(f"Vector indexing (placement) skipped: {e}")

    return obj
