"""
TRUSTLENS AI - Community Scam Reports Endpoints
POST /api/v1/reports
GET /api/v1/reports
POST /api/v1/reports/{id}/review
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, Query, Request, HTTPException, status

from backend.app.schemas.common import (
    CreateReportRequest,
    ReviewReportRequest,
    ReportResponse,
    PaginatedResponse,
)
from backend.app.services.report_service import report_service
from backend.app.security.dependencies import (
    get_optional_current_user,
    require_analyst_or_admin,
)

router = APIRouter(prefix="/reports", tags=["Community Reporting"])


@router.post("", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
async def submit_scam_report(
    payload: CreateReportRequest,
    request: Request,
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user),
):
    """
    Submits a new community scam report. Open to public or registered users.
    """
    client_ip = request.client.host if request.client else "unknown"
    user_id = current_user.get("user_id") if current_user else "anonymous"

    return await report_service.create_report(
        target_type=payload.target_type,
        content=payload.content,
        target_identifier=payload.target_identifier,
        description=payload.description,
        evidence_urls=payload.evidence_urls,
        reporter_user_id=user_id,
        client_ip=client_ip,
    )


@router.get("", response_model=PaginatedResponse)
async def list_reports(
    status: Optional[str] = Query(None, description="pending | under_review | verified_scam | benign"),
    target_type: Optional[str] = Query(None, description="sms | whatsapp | url | call | upi"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """
    Retrieves paginated community threat submissions.
    """
    return await report_service.list_reports(
        status_filter=status,
        target_type=target_type,
        page=page,
        page_size=page_size,
    )


@router.post("/{report_id}/review", response_model=ReportResponse)
async def review_scam_report(
    report_id: str,
    payload: ReviewReportRequest,
    request: Request,
    reviewer: Dict[str, Any] = Depends(require_analyst_or_admin),
):
    """
    SOC Analyst / Admin action: verifies scam report and triggers threat indicator extraction.
    """
    client_ip = request.client.host if request.client else "unknown"

    return await report_service.review_report(
        report_id=report_id,
        verdict=payload.verdict,
        notes=payload.notes,
        assigned_tactics=payload.assigned_tactics,
        reviewer_id=reviewer["user_id"],
        client_ip=client_ip,
    )
