from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import date, datetime


class StudentProfileBase(BaseModel):
    full_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None
    category: Optional[str] = None
    income_annual: Optional[float] = None
    college: Optional[str] = None
    university: Optional[str] = None
    stream: Optional[str] = None
    degree: Optional[str] = None
    year_of_study: Optional[int] = None
    cgpa: Optional[float] = None
    percentage_12th: Optional[float] = None
    percentage_10th: Optional[float] = None
    backlogs: Optional[int] = None
    skills: Optional[List[str]] = Field(default_factory=list)
    documents: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    preferences: Optional[Dict[str, Any]] = Field(default_factory=dict)
    domicile_state: Optional[str] = None
    academic_level: Optional[str] = None
    institution_type: Optional[str] = None
    previous_year_marks_percentage: Optional[float] = None
    is_single_girl_child: Optional[bool] = False
    is_orphan: Optional[bool] = False
    is_pwd: Optional[bool] = False
    pwd_percentage: Optional[float] = None
    is_ward_of_defense_personnel: Optional[bool] = False
    bank_account_seeded_aadhaar: Optional[bool] = False


class StudentProfileCreate(StudentProfileBase):
    pass


class StudentProfileResponse(StudentProfileBase):
    id: str
    user_id: str
    readiness_score: float = 0.0
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class NotificationResponse(BaseModel):
    id: str
    user_id: str
    title: str
    body: str
    channel: str = "in_app"
    read: bool = False
    sent_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True
