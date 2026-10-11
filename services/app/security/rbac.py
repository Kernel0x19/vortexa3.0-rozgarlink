from typing import Optional
from sqlalchemy.orm import Session
from app.db.models import User, UserRole


def ensure_user(db: Session, user_id: str, email: str = "") -> User:
    """Ensure a user record exists in the database and return it."""
    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        if not email:
            email = f"user_{user_id[:8]}@example.com"
        user = User(
            id=user_id,
            email=email,
            role=UserRole.STUDENT,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


def can_admin(user: Optional[User]) -> bool:
    """Check if user has admin privileges."""
    if not user:
        return False
    return user.role == UserRole.ADMIN or str(getattr(user, "role", "")).lower() == "admin"


def can_review(user: Optional[User]) -> bool:
    """Check if user has reviewer or admin privileges."""
    if not user:
        return False
    return user.role in (UserRole.REVIEWER, UserRole.ADMIN) or str(getattr(user, "role", "")).lower() in ("reviewer", "admin")
