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


@router.get("/health/slo", response_model=Dict[str, Any])
async def launch_slo_and_telemetry():
    """Returns launch availability SLOs, usage/cost counters, and strict scope guardrails."""
    analyses_count = 0
    users_count = 0
    if db_manager.db is not None:
        try:
            analyses_count = await db_manager.db["analyses"].count_documents({})
            users_count = await db_manager.db["users"].count_documents({})
        except Exception:
            pass

    return {
        "service_availability": {
            "database_connected": db_manager.is_connected,
            "models_loaded": ml_engine.get_status(),
            "availability_slo": "99.9%",
            "p95_inference_target_ms": 1500,
        },
        "usage_and_cost_telemetry": {
            "total_analyses_recorded": analyses_count,
            "total_registered_users": users_count,
            "worker_memory_limit_gb": 4,
            "workers_per_replica": 1,
        },
        "launch_scope_guardrails": {
            "evaluated_languages": ["English", "Hindi", "Hinglish"],
            "unsupported_languages": ["Tamil", "Bengali"],
            "auto_expand_scope": False,
            "claim_universal_fraud_detection": False,
        },
        "incident_and_support_contacts": {
            "security_email": "security@trustlens.ai",
            "feedback_endpoint": "/api/v1/models/feedback",
            "transparency_endpoint": "/api/v1/privacy/transparency",
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
