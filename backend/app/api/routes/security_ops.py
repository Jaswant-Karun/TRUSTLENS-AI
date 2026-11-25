"""
TRUSTLENS AI - Abuse Monitoring & Operational Alerts Endpoints
GET /api/v1/security/abuse-monitoring
"""

from typing import Dict, Any
from fastapi import APIRouter, Depends, Query

from backend.app.security.dependencies import require_analyst_or_admin
from backend.app.services.abuse_service import abuse_service

router = APIRouter(prefix="/security", tags=["Abuse Protection & Operations"])


@router.get("/abuse-monitoring", response_model=Dict[str, Any])
async def get_abuse_monitoring(
    limit: int = Query(default=50, ge=1, le=200),
    reviewer: Dict[str, Any] = Depends(require_analyst_or_admin),
):
    """Returns active brute-force lockouts, suspicious request events, and operational alerts."""
    return await abuse_service.get_monitoring_summary(limit=limit)
