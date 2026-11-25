"""
TRUSTLENS AI - System Health & Readiness Endpoints
"""

import time
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from fastapi import APIRouter

from backend.app.config.settings import settings
from backend.app.database.manager import db_manager
from backend.app.ml_engine.engine import ml_engine

router = APIRouter(tags=["Health & Diagnostics"])


@router.get("/health", response_model=Dict[str, Any])
async def health_check():
    """Returns live MongoDB ping latency, connectivity, model states, and platform readiness."""
    db_ok = db_manager.is_connected
    db_ping_ms: Optional[float] = None
    if db_ok and db_manager.client is not None:
        t0 = time.perf_counter()
        try:
            await db_manager.client.admin.command("ping")
            db_ping_ms = round((time.perf_counter() - t0) * 1000, 2)
        except Exception:
            db_ok = False

    return {
        "status": "healthy" if db_ok else "degraded",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV,
        "database_connected": db_ok,
        "db_ping_ms": db_ping_ms,
        "models_loaded": ml_engine.get_status(),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
