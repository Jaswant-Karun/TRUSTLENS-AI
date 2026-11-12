"""
TRUSTLENS AI - Core Analysis Endpoints
POST /api/v1/analyze/text
POST /api/v1/analyze/url
POST /api/v1/analyze/image
POST /api/v1/analyze/comprehensive
"""

import time
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, Request, UploadFile, File, Form, HTTPException, status

from backend.app.schemas.analysis import (
    TextAnalysisRequest,
    URLAnalysisRequest,
    ComprehensiveAnalysisRequest,
    AnalysisResultResponse,
    ImageAnalysisResponse,
)
from backend.app.services.analysis_service import threat_analysis_service
from backend.app.services.ocr_service import ocr_service
from backend.app.security.dependencies import get_optional_current_user

router = APIRouter(prefix="/analyze", tags=["Threat Analysis"])


@router.post("/text", response_model=AnalysisResultResponse)
async def analyze_text(
    payload: TextAnalysisRequest,
    request: Request,
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user),
):
    """
    Classifies suspicious digital communication (SMS, WhatsApp, Email).
    Runs Model 1 (Scam Text), Model 3 (Tactics), Model 4 (Campaigns), and Risk Calibration.
    """
    client_ip = request.client.host if request.client else "unknown"
    user_id = current_user.get("user_id") if current_user else "anonymous"

    return await threat_analysis_service.analyze_text(
        text=payload.text,
        channel=payload.channel or "sms",
        sender=payload.sender,
        user_id=user_id,
        client_ip=client_ip,
    )


@router.post("/url", response_model=AnalysisResultResponse)
async def analyze_url(
    payload: URLAnalysisRequest,
    request: Request,
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user),
):
    """
    Performs zero-hop offline inspection of suspicious URLs using Model 2 (XGBoost) and SHAP.
    Never connects to target endpoint.
    """
    client_ip = request.client.host if request.client else "unknown"
    user_id = current_user.get("user_id") if current_user else "anonymous"

    return await threat_analysis_service.analyze_url(
        url=payload.url,
        user_id=user_id,
        client_ip=client_ip,
    )


@router.post("/image", response_model=ImageAnalysisResponse)
async def analyze_image(
    request: Request,
    file: UploadFile = File(..., description="Screenshot evidence (JPEG, PNG, WebP; max 10MB)"),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user),
):
    """
    Extracts text from uploaded screenshot and runs end-to-end multi-model threat analysis.
    If image has no readable text, returns structured 'insufficient-evidence' status without failing.
    """
    start_time = time.perf_counter()
    client_ip = request.client.host if request.client else "unknown"
    user_id = current_user.get("user_id") if current_user else "anonymous"

    # Validate image format and file size
    raw_bytes, pil_image = await ocr_service.validate_and_read_image(file)

    # Perform OCR extraction
    ocr_result = ocr_service.extract_text(pil_image)
    text = ocr_result["extracted_text"]
    now = datetime.now(timezone.utc)

    if not ocr_result["has_readable_text"]:
        processing_time = round((time.perf_counter() - start_time) * 1000, 2)
        return {
            "analysis_id": f"img-{int(time.time())}",
            "extracted_text": text,
            "ocr_confidence": ocr_result["ocr_confidence"],
            "analysis_status": "insufficient-evidence",
            "analysis_result": None,
            "processing_time_ms": processing_time,
            "created_at": now,
        }

    # If readable text was found, run complete multi-model scan
    scan_res = await threat_analysis_service.analyze_text(
        text=text,
        channel="screenshot",
        sender=None,
        user_id=user_id,
        client_ip=client_ip,
    )

    processing_time = round((time.perf_counter() - start_time) * 1000, 2)
    return {
        "analysis_id": scan_res["analysis_id"],
        "extracted_text": text,
        "ocr_confidence": ocr_result["ocr_confidence"],
        "analysis_status": "completed",
        "analysis_result": scan_res,
        "processing_time_ms": processing_time,
        "created_at": now,
    }


@router.post("/comprehensive", response_model=AnalysisResultResponse)
async def analyze_comprehensive(
    payload: ComprehensiveAnalysisRequest,
    request: Request,
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user),
):
    """
    Unified multi-vector threat intelligence scan.
    Correlates text messages, standalone URLs, social engineering tactics, and campaign clusters.
    """
    client_ip = request.client.host if request.client else "unknown"
    user_id = current_user.get("user_id") if current_user else "anonymous"

    # If payload is purely a URL, route to URL analyzer
    if payload.content.startswith(("http://", "https://", "www.")) and not payload.url:
        return await threat_analysis_service.analyze_url(
            url=payload.content.strip(),
            user_id=user_id,
            client_ip=client_ip,
        )

    # Otherwise route to comprehensive text & embedded URL analysis
    combined_text = payload.content
    if payload.url and payload.url not in combined_text:
        combined_text = f"{combined_text} {payload.url}"

    return await threat_analysis_service.analyze_text(
        text=combined_text,
        channel=payload.channel or "auto",
        sender=payload.sender,
        user_id=user_id,
        client_ip=client_ip,
    )
