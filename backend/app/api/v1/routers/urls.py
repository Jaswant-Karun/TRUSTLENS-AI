"""
TRUSTLENS AI - Phishing URL Analysis Endpoints
"""

from fastapi import APIRouter, HTTPException
from backend.app.models.schemas import URLScanRequest, URLScanResponse
from backend.app.services.ml_service import ml_service

router = APIRouter(prefix="/urls", tags=["Phishing URL Analysis"])


@router.post("/scan", response_model=URLScanResponse)
async def scan_url(request: URLScanRequest):
    """Extracts 17 lexical and structural features and predicts phishing risk."""
    try:
        result = ml_service.scan_url(url=request.url)
        return URLScanResponse(**result)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"URL evaluation error: {str(exc)}")

