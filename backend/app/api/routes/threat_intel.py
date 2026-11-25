"""
TRUSTLENS AI - Threat Intelligence Ingestion Endpoints
GET  /api/v1/threat-intel/sources
GET  /api/v1/threat-intel/status
POST /api/v1/threat-intel/ingest/{source_id}
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from backend.app.security.dependencies import get_current_user
from backend.app.services.threat_intel_service import threat_intel_service

router = APIRouter(prefix="/threat-intel", tags=["Threat Intelligence Ingestion"])


@router.get("/sources", response_model=Dict[str, Any])
async def list_threat_intel_sources(commercial_only: Optional[bool] = Query(default=None)):
    """Lists all evaluated threat intelligence sources with licensing, attribution, reliability, and commercial terms."""
    sources = threat_intel_service.list_sources(commercial_only=commercial_only)
    return {"total": len(sources), "sources": sources}


@router.get("/status", response_model=Dict[str, Any])
async def get_threat_intel_status(limit: int = Query(default=20, ge=1, le=100)):
    """Returns normalized indicator counts, recent ingestion runs, and error logs."""
    return await threat_intel_service.get_status(limit=limit)


@router.post("/ingest/{source_id}", response_model=Dict[str, Any])
async def trigger_threat_intel_ingestion(
    source_id: str,
    allow_non_commercial: bool = Query(default=False),
    max_items: int = Query(default=250, ge=1, le=2000),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Triggers a live ingestion run for a permitted source. Blocked for non-commercial feeds unless explicitly overridden."""
    try:
        return await threat_intel_service.ingest_source(
            source_id=source_id,
            allow_non_commercial=allow_non_commercial,
            max_items=max_items,
        )
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
