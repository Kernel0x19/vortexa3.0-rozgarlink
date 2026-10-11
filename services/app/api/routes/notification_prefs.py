from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime

from app.api.deps import get_current_user
from app.db.models import User, NotificationPreference
from app.db.session import get_db

router = APIRouter(prefix="/notifications/preferences", tags=["notifications"])


class NotificationPreferencesSchema(BaseModel):
    email_enabled: bool = True
    sms_enabled: bool = False
    push_enabled: bool = True
    voice_enabled: bool = False
    deadline_reminders: bool = True
    new_matches: bool = True
    status_updates: bool = True


@router.get("", response_model=NotificationPreferencesSchema)
def get_preferences(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    pref = db.query(NotificationPreference).filter_by(user_id=user.id).first()
    if not pref:
        return NotificationPreferencesSchema()
    return NotificationPreferencesSchema(
        email_enabled=pref.email_enabled,
        sms_enabled=pref.sms_enabled,
        push_enabled=pref.push_enabled,
        voice_enabled=pref.voice_enabled,
        deadline_reminders=pref.deadline_reminders,
        new_matches=pref.new_matches,
        status_updates=pref.status_updates,
    )


@router.put("", response_model=NotificationPreferencesSchema)
def update_preferences(
    body: NotificationPreferencesSchema,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    pref = db.query(NotificationPreference).filter_by(user_id=user.id).first()
    if not pref:
        pref = NotificationPreference(user_id=user.id)
        db.add(pref)

    pref.email_enabled = body.email_enabled
    pref.sms_enabled = body.sms_enabled
    pref.push_enabled = body.push_enabled
    pref.voice_enabled = body.voice_enabled
    pref.deadline_reminders = body.deadline_reminders
    pref.new_matches = body.new_matches
    pref.status_updates = body.status_updates
    pref.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(pref)

    return NotificationPreferencesSchema(
        email_enabled=pref.email_enabled,
        sms_enabled=pref.sms_enabled,
        push_enabled=pref.push_enabled,
        voice_enabled=pref.voice_enabled,
        deadline_reminders=pref.deadline_reminders,
        new_matches=pref.new_matches,
        status_updates=pref.status_updates,
    )
