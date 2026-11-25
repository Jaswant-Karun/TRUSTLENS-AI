"""
TRUSTLENS AI - Privacy & Data Protection Endpoints
GET  /api/v1/privacy/policy
GET  /api/v1/privacy/consent
PUT  /api/v1/privacy/consent
GET  /api/v1/privacy/access-logs
POST /api/v1/privacy/retention/preview
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from backend.app.security.dependencies import get_current_user, require_analyst_or_admin
from backend.app.services.privacy_service import privacy_service

router = APIRouter(prefix="/privacy", tags=["Privacy & Data Protection"])


class ConsentUpdateRequest(BaseModel):
    external_ioc_enrichment: Optional[bool] = None
    community_report_public_listing: Optional[bool] = None
    product_telemetry: Optional[bool] = None
    security_notifications: Optional[bool] = None


@router.get("/policy", response_model=Dict[str, Any])
async def get_privacy_policy_and_governance():
    """Returns data collection purposes, retention periods, user-rights endpoints, and DPDP/GDPR assessment."""
    return privacy_service.get_privacy_governance_summary()


@router.get("/consent", response_model=Dict[str, Any])
async def get_my_consent(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Retrieves the authenticated user's granular consent preferences."""
    return await privacy_service.get_consent(current_user["user_id"])


@router.put("/consent", response_model=Dict[str, Any])
async def update_my_consent(
    payload: ConsentUpdateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Updates granular consent preferences with audit logging."""
    prefs = {k: v for k, v in payload.model_dump().items() if v is not None}
    return await privacy_service.update_consent(current_user["user_id"], prefs)


@router.get("/access-logs", response_model=Dict[str, Any])
async def get_my_access_logs(
    limit: int = Query(default=50, ge=1, le=200),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Returns access and privacy audit logs for the authenticated user."""
    logs = await privacy_service.get_user_access_logs(current_user["user_id"], limit=limit)
    return {"total": len(logs), "logs": logs}


@router.post("/retention/preview", response_model=Dict[str, Any])
async def preview_retention_policy(
    reviewer: Dict[str, Any] = Depends(require_analyst_or_admin),
):
    """Dry-run evaluation of expired analyses and unverified reports under retention policy."""
    return await privacy_service.enforce_retention_policy(dry_run=True)
