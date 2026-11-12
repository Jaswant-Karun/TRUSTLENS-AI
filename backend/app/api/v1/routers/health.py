"""
TRUSTLENS AI - System Health & Diagnostics Endpoint
"""

from fastapi import APIRouter
from backend.app.core.config import settings
from backend.app.core.database import db_manager
from backend.app.services.ml_service import ml_service
from backend.app.models.schemas import SystemHealthResponse

router = APIRouter(tags=["Health & Status"])


@router.get("/health", response_model=SystemHealthResponse)
async def get_system_health():
    """Returns application health, database connectivity, and ML engine status."""
    return SystemHealthResponse(
        status="healthy",
        app_name=settings.APP_NAME,
        version=settings.APP_VERSION,
        database_connected=db_manager.is_connected,
        models_loaded=ml_service.get_models_status(),
    )
