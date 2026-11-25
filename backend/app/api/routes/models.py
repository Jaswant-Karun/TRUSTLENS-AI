"""
TRUSTLENS AI - Model Governance & Metrics Endpoints
GET /api/v1/models
GET /api/v1/models/metrics
GET /api/v1/models/experiments
"""

from typing import Dict, Any
from pathlib import Path
import json
from fastapi import APIRouter, HTTPException, status

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

