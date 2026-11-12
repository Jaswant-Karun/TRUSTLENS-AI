"""
TRUSTLENS AI - System Health & Readiness Endpoints
"""

from typing import Dict, Any
from datetime import datetime, timezone
from fastapi import APIRouter

from backend.app.config.settings import settings
from backend.app.database.manager import db_manager
from backend.app.ml_engine.engine import ml_engine

router = APIRouter(tags=["Health & Diagnostics"])


@router.get("/health", response_model=Dict[str, Any])
async def health_check():
    """Returns database connectivity, model states, and platform readiness."""
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV,
        "database_connected": db_manager.is_connected,
        "models_loaded": ml_engine.get_status(),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
