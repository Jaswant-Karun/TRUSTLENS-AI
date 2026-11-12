"""
TRUSTLENS AI - Scam Tactic Detection Endpoints
"""

from fastapi import APIRouter, HTTPException
from backend.app.models.schemas import TacticScanRequest, TacticScanResponse
from backend.app.services.ml_service import ml_service

router = APIRouter(prefix="/tactics", tags=["Scam Tactic Detection"])


@router.post("/scan", response_model=TacticScanResponse)
async def scan_tactics(request: TacticScanRequest):
    """Scans message for psychological urgency, OTP requests, and entity impersonation."""
    try:
        result = ml_service.scan_tactics(text=request.text)
        return TacticScanResponse(**result)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Tactic detection error: {str(exc)}")
