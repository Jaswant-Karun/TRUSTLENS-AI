"""
TRUSTLENS AI - Message Scam Scanning Endpoints
"""

from fastapi import APIRouter, HTTPException
from backend.app.models.schemas import TextScanRequest, TextScanResponse, CompositeScanRequest, CompositeScanResponse
from backend.app.services.ml_service import ml_service

router = APIRouter(prefix="/scans", tags=["Scam Message Scanning"])


@router.post("/text", response_model=TextScanResponse)
async def scan_text_message(request: TextScanRequest):
    """Classifies incoming text message for phishing, smishing, or scam deception."""
    try:
        result = ml_service.scan_text(
            text=request.text,
            sender=request.sender,
            channel=request.channel,
        )
        return TextScanResponse(**result)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Text classification error: {str(exc)}")


@router.post("/composite", response_model=CompositeScanResponse)
async def scan_composite_content(request: CompositeScanRequest):
    """Unified threat scan evaluating text, URLs, tactics, and IOC entities simultaneously."""
    try:
        result = ml_service.composite_scan(
            content=request.content,
            channel=request.channel,
            sender=request.sender,
        )
        return CompositeScanResponse(**result)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Composite scan error: {str(exc)}")
