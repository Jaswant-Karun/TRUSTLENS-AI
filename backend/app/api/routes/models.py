"""
TRUSTLENS AI - Model Governance & Metrics Endpoints
GET /api/v1/models
GET /api/v1/models/metrics
GET /api/v1/models/experiments
"""

from typing import Dict, Any
from fastapi import APIRouter

from backend.app.schemas.common import ModelRegistryResponse
from backend.app.services.model_service import model_service

router = APIRouter(prefix="/models", tags=["Model Governance"])


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
