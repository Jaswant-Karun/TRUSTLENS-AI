"""
TRUSTLENS AI - Python Training Orchestrator Endpoints
POST /api/v1/training/jobs
GET  /api/v1/training/jobs/{job_id}
GET  /api/v1/training/jobs
POST /api/v1/training/jobs/{job_id}/compare
POST /api/v1/training/jobs/{job_id}/promote
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from backend.app.services.training_service import training_orchestrator
from backend.app.security.dependencies import require_analyst_or_admin, require_admin

router = APIRouter(prefix="/training", tags=["ML Training Orchestration"])


class TrainingJobRequest(BaseModel):
    model_name: str = Field(..., description="model1_text | model2_url | model3_tactics | model4_campaigns")
    dataset_version: str = Field("v1.2-cleaned", description="Cleaned dataset version to train on")
    hyperparameters: Optional[Dict[str, Any]] = Field(default_factory=dict)


class PromotionRequest(BaseModel):
    approved_by: str = Field(..., description="Analyst or Admin username who approved promotion")
    approval_token: str = Field(..., min_length=8, description="Human security approval verification token")


@router.post("/jobs", status_code=status.HTTP_202_ACCEPTED)
async def submit_training_job(
    request: TrainingJobRequest,
    current_user: Dict[str, Any] = Depends(require_analyst_or_admin),
):
    """
    Submits a training/retraining job to the Python training worker.
    Rejects duplicate jobs if the model is currently training.
    """
    try:
        job = await training_orchestrator.submit_training_job(
            model_name=request.model_name,
            dataset_version=request.dataset_version,
            hyperparameters=request.hyperparameters,
            requested_by=current_user.get("username", "analyst"),
        )
        return job
    except RuntimeError as rerr:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(rerr))
    except ValueError as verr:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(verr))
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))


@router.get("/jobs/{job_id}")
async def get_training_job(
    job_id: str,
    current_user: Dict[str, Any] = Depends(require_analyst_or_admin),
):
    """Retrieves status, progress, and evaluation metrics for a training job."""
    job = await training_orchestrator.get_job_status(job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Job '{job_id}' not found.")
    return job


@router.get("/jobs")
async def list_training_jobs(
    limit: int = 20,
    current_user: Dict[str, Any] = Depends(require_analyst_or_admin),
):
    """Lists recent training jobs and statuses."""
    return await training_orchestrator.list_jobs(limit=limit)


@router.post("/jobs/{job_id}/compare")
async def compare_candidate_model(
    job_id: str,
    current_user: Dict[str, Any] = Depends(require_analyst_or_admin),
):
    """
    Compares candidate model metrics against production baselines.
    Ensures candidate does not regress system performance.
    """
    try:
        return await training_orchestrator.compare_candidate_with_production(job_id)
    except ValueError as verr:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(verr))
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))


@router.post("/jobs/{job_id}/promote")
async def promote_model_to_production(
    job_id: str,
    request: PromotionRequest,
    current_user: Dict[str, Any] = Depends(require_admin),
):
    """
    Promotes an approved candidate model to production.
    Strictly requires Admin role, verified approval token, and updates audit trail.
    """
    try:
        return await training_orchestrator.promote_model_to_production(
            job_id=job_id,
            approved_by=request.approved_by,
            approval_token=request.approval_token,
        )
    except ValueError as verr:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(verr))
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))
