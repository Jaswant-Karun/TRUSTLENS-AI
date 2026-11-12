"""
TRUSTLENS AI - Analysis History Endpoints
GET /api/v1/analyses
GET /api/v1/analyses/{id}
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status

from backend.app.schemas.common import PaginatedResponse
from backend.app.services.analysis_service import threat_analysis_service
from backend.app.security.dependencies import get_current_user

router = APIRouter(prefix="/analyses", tags=["Analysis History"])


@router.get("", response_model=PaginatedResponse)
async def list_analyses(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    threat_level: Optional[str] = Query(None, description="clean | low | medium | high | critical | inconclusive"),
    channel: Optional[str] = Query(None, description="sms | email | url | screenshot"),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Retrieves paginated scan history. Users see own scans; analysts/admins see all scans.
    """
    user_id = current_user["user_id"]
    role = current_user.get("role", "user")

    return await threat_analysis_service.get_analyses_history(
        user_id=user_id,
        role=role,
        threat_level=threat_level,
        channel=channel,
        page=page,
        page_size=page_size,
    )


@router.get("/{analysis_id}", response_model=Dict[str, Any])
async def get_analysis(
    analysis_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Retrieves a single detailed analysis record by UUID.
    """
    user_id = current_user["user_id"]
    role = current_user.get("role", "user")

    doc = await threat_analysis_service.get_analysis_by_id(
        analysis_id=analysis_id,
        user_id=user_id,
        role=role,
    )
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis with ID '{analysis_id}' was not found.",
        )
    return doc

