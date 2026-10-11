from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime

from app.api.deps import get_current_user
from app.db.models import User, ConsentRecord
from app.db.session import get_db

router = APIRouter(prefix="/consent", tags=["consent"])


class ConsentItem(BaseModel):
    purpose: str
    granted: bool
    granted_at: Optional[str] = None


class ConsentUpdate(BaseModel):
    purpose: str
    granted: bool


@router.get("", response_model=List[ConsentItem])
def get_consents(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    records = db.query(ConsentRecord).filter_by(user_id=user.id).all()
    # Default standard consent purposes if none recorded
    standard_purposes = [
        "data_processing",
        "notification_delivery",
        "document_verification",
        "recommendation_personalization",
    ]
    recorded_map = {r.purpose: r for r in records}

    results = []
    for purpose in standard_purposes:
        if purpose in recorded_map:
            rec = recorded_map[purpose]
            results.append(
                ConsentItem(
                    purpose=rec.purpose,
                    granted=rec.granted,
                    granted_at=rec.granted_at.isoformat() if rec.granted_at else None,
                )
            )
        else:
            results.append(
                ConsentItem(
                    purpose=purpose,
                    granted=False,
                    granted_at=None,
                )
            )
    return results


@router.post("", response_model=ConsentItem)
def set_consent(
    body: ConsentUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    rec = db.query(ConsentRecord).filter_by(user_id=user.id, purpose=body.purpose).first()
    now = datetime.utcnow()
    if not rec:
        rec = ConsentRecord(
            user_id=user.id,
            purpose=body.purpose,
            granted=body.granted,
            granted_at=now if body.granted else None,
            revoked_at=now if not body.granted else None,
        )
        db.add(rec)
    else:
        rec.granted = body.granted
        if body.granted:
            rec.granted_at = now
            rec.revoked_at = None
        else:
            rec.revoked_at = now

    db.commit()
    db.refresh(rec)

    return ConsentItem(
        purpose=rec.purpose,
        granted=rec.granted,
        granted_at=rec.granted_at.isoformat() if rec.granted_at else None,
    )
