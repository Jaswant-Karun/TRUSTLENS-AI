"""
TRUSTLENS AI - Model Governance & Metrics Endpoints
GET /api/v1/models
GET /api/v1/models/metrics
GET /api/v1/models/experiments
"""

from typing import Dict, Any, Optional
from pathlib import Path
import json
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from backend.app.security.dependencies import get_current_user
from backend.app.schemas.common import ModelRegistryResponse
from backend.app.services.model_service import model_service
from backend.app.services.monitoring_service import monitoring_service

router = APIRouter(prefix="/models", tags=["Model Governance"])


class ModelFeedbackCreate(BaseModel):
    analysis_id: str = Field(..., min_length=1, max_length=128)
    feedback_type: str = Field(..., pattern="^(false_positive|false_negative)$")
    suggested_label: str = Field(..., min_length=1, max_length=64)
    comment: Optional[str] = Field(default=None, max_length=1000)
    detected_language: Optional[str] = Field(default=None, max_length=64)
    model_version: Optional[str] = Field(default=None, max_length=128)


class ModelFeedbackReview(BaseModel):
    decision: str = Field(..., pattern="^(verified_ground_truth|rejected)$")
    verified_label: Optional[str] = Field(default=None, max_length=64)
    reviewer_notes: Optional[str] = Field(default=None, max_length=1000)


@router.get("", response_model=Dict[str, Any])
async def get_models():
    """
    Retrieves production model registry, semantic versions (v1.0.0), and artifact SHA256 hashes.
    """
    return model_service.get_models_registry()


@router.get("/metrics", response_model=Dict[str, Any])
async def get_model_metrics():
    """
    Retrieves held-out test evaluation benchmarks across all 4 tracks for SOC dashboard display.
    """
    return model_service.get_models_metrics()


@router.get("/experiments", response_model=Dict[str, Any])
async def get_experiments():
    """
    Retrieves full experimental lineage tracking baseline vs champion model progressions.
    """
    return model_service.get_experiment_history()


@router.get("/monitoring", response_model=Dict[str, Any])
async def get_model_monitoring(limit: int = Query(default=1000, ge=1, le=5000)):
    """
    Retrieves live production ML monitoring metrics from real MongoDB analyses and human-reviewed feedback.
    """
    return await monitoring_service.get_monitoring_snapshot(limit=limit)


@router.post("/feedback", status_code=status.HTTP_201_CREATED, response_model=Dict[str, Any])
async def submit_model_feedback(
    payload: ModelFeedbackCreate,
):
    """
    Submits user FP/FN feedback strictly as 'pending_review' (never automatically treated as ground truth).
    """
    return await monitoring_service.submit_feedback(
        analysis_id=payload.analysis_id,
        feedback_type=payload.feedback_type,
        suggested_label=payload.suggested_label,
        submitted_by="user_report",
        comment=payload.comment,
        detected_language=payload.detected_language,
        model_version=payload.model_version,
    )


@router.get("/feedback", response_model=Dict[str, Any])
async def list_model_feedback(
    review_status: Optional[str] = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
):
    """Lists submitted model feedback separated by review_status."""
    items = await monitoring_service.list_feedback(review_status=review_status, limit=limit)
    return {"total": len(items), "items": items}


@router.post("/feedback/{feedback_id}/review", response_model=Dict[str, Any])
async def review_model_feedback(
    feedback_id: str,
    payload: ModelFeedbackReview,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Human-review gate required before any user report becomes a verified ground-truth label."""
    if payload.decision == "verified_ground_truth" and not payload.verified_label:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="verified_label is required when approving feedback as verified_ground_truth.",
        )
    reviewer = current_user.get("email") or current_user.get("user_id") or "analyst"
    updated = await monitoring_service.review_feedback(
        feedback_id=feedback_id,
        decision=payload.decision,
        reviewed_by=reviewer,
        verified_label=payload.verified_label,
        reviewer_notes=payload.reviewer_notes,
    )
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feedback record not found.")
    return updated


@router.get("/{model_id}", response_model=Dict[str, Any])
async def get_model_by_id(model_id: str):
    """
    Retrieves detailed registry metadata, SHA-256 checksum, and status for a specific model ID.
    """
    reg_v2 = Path("ml/registry/models_registry_v2.json")
    if reg_v2.exists():
        data = json.loads(reg_v2.read_text(encoding="utf-8"))
        if model_id in data.get("models", {}):
            return data["models"][model_id]
    reg_v1 = model_service.get_models_registry()
    if model_id in reg_v1.get("models", {}):
        return reg_v1["models"][model_id]
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Model ID '{model_id}' not found in registry.",
    )

