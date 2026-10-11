from typing import List, Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "EduPilot API"
    dev_mode: bool = True

    # Database
    database_url: str = "sqlite:///./edupilot.db"

    # Supabase / Auth
    supabase_url: Optional[str] = None
    supabase_jwt_secret: Optional[str] = None
    supabase_service_role_key: Optional[str] = None

    # LLM & AI
    groq_api_key: Optional[str] = None
    groq_model: str = "openai/gpt-oss-120b"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3:8b"
    tee_mode: str = "simulation"

    # Vector store & RAG
    chroma_path: str = "./data/chroma"

    # Notifications
    sendgrid_api_key: Optional[str] = None
    sendgrid_from_email: str = "noreply@edupilot.org"
    sender_email: str = "noreply@edupilot.org"
    notification_from_email: str = "noreply@edupilot.org"
    twilio_account_sid: Optional[str] = None
    twilio_auth_token: Optional[str] = None
    twilio_from_phone: str = "+15005550006"
    firebase_credentials_path: Optional[str] = None

    # Connectors
    enabled_connectors_list: List[str] = ["hackathons", "internships", "scholarships"]

    # Security
    kms_master_key: str = "edupilot-default-development-key-32b"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


_settings: Optional[Settings] = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
