"""FastAPI application entrypoint for EduPilot."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.db.session import engine, Base, ensure_notification_schema
# Import models so SQLAlchemy metadata registers all tables
import app.db.models  # noqa: F401

from app.api.routes.scholarships import router as scholarships_router
from app.api.routes.internships import router as internships_router
from app.api.routes.hackathons import router as hackathons_router
from app.api.routes.profile import router as profile_router
from app.api.routes.notifications import router as notifications_router
from app.api.routes.notification_prefs import router as notification_prefs_router
from app.api.routes.workflow import router as workflow_router
from app.api.routes.feedback import router as feedback_router
from app.api.routes.experiments import router as experiments_router
from app.api.routes.admin import router as admin_router
from app.api.routes.documents_api import router as documents_router
from app.api.routes.connectors import router as connectors_router
from app.api.routes.chat import router as chat_router
from app.api.routes.search_api import router as search_router
from app.api.routes.eval import router as eval_router
from app.api.routes.consent import router as consent_router
from app.api.routes.placements import router as placements_router
from app.api.routes.simulation import router as simulation_router
import os

settings = get_settings()

# Initialize DB tables automatically on startup
Base.metadata.create_all(bind=engine)
ensure_notification_schema()

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="RozgarLink Backend Microservice API",
)

# CORS Middleware config

ALLOWED_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount all v1 routers
API_V1_PREFIX = "/api/v1"

app.include_router(scholarships_router, prefix=API_V1_PREFIX)
app.include_router(internships_router, prefix=API_V1_PREFIX)
app.include_router(hackathons_router, prefix=API_V1_PREFIX)
app.include_router(profile_router, prefix=API_V1_PREFIX)
app.include_router(notifications_router, prefix=API_V1_PREFIX)
app.include_router(notification_prefs_router, prefix=API_V1_PREFIX)
app.include_router(consent_router, prefix=API_V1_PREFIX)
app.include_router(workflow_router, prefix=API_V1_PREFIX)
app.include_router(feedback_router, prefix=API_V1_PREFIX)
app.include_router(experiments_router, prefix=API_V1_PREFIX)
app.include_router(admin_router, prefix=API_V1_PREFIX)
app.include_router(documents_router, prefix=API_V1_PREFIX)
app.include_router(connectors_router, prefix=API_V1_PREFIX)
app.include_router(chat_router, prefix=API_V1_PREFIX)
app.include_router(search_router, prefix=API_V1_PREFIX)
app.include_router(eval_router, prefix=API_V1_PREFIX)
app.include_router(placements_router, prefix=API_V1_PREFIX)
app.include_router(simulation_router, prefix=API_V1_PREFIX)


@app.get("/health")
def health_check():
    return {"status": "ok", "app": settings.app_name}
