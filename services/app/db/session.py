from typing import Generator
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from app.config import get_settings

settings = get_settings()

db_url = settings.database_url
connect_args = {}
if db_url.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(db_url, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def ensure_notification_schema() -> None:
    """Add notification fields required by newer app versions to existing databases."""
    inspector = inspect(engine)
    if "notification_preferences" not in inspector.get_table_names():
        return
    columns = {column["name"] for column in inspector.get_columns("notification_preferences")}
    if "voice_enabled" not in columns:
        with engine.begin() as connection:
            connection.execute(text(
                "ALTER TABLE notification_preferences "
                "ADD COLUMN voice_enabled BOOLEAN NOT NULL DEFAULT 0"
            ))


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
