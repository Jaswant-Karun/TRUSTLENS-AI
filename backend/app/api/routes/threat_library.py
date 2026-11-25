"""
TRUSTLENS AI - Threat Library Endpoints
GET /api/v1/threat-library
GET /api/v1/threat-library/{item_id}
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, Query, HTTPException, status

from backend.app.services.threat_library_service import threat_library_service

router = APIRouter(prefix="/threat-library", tags=["Threat Library"])


@router.get("", response_model=Dict[str, Any])
async def query_threat_library(
    search: Optional[str] = Query(None, description="Search query across labels, summaries, and sources"),
    entity_type: Optional[str] = Query(
        None,
        description="all | suspicious_message | url | domain | indicator | tactic | similarity_cluster | community_report",
    ),
    severity: Optional[str] = Query(None, description="all | critical | high | medium | low | clean | inconclusive"),
    verification_status: Optional[str] = Query(
        None,
        description="all | verified | automated_inference | under_review | unverified",
    ),
    provenance: Optional[str] = Query(
        None,
        description="all | ml_model | threat_intel | human_review | unsupervised_clustering",
    ),
    sort_by: str = Query("created_at", description="created_at | severity | confidence | label"),
    sort_order: str = Query("desc", description="asc | desc"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """
    Searchable, filterable, sortable, and paginated repository of actual stored
    suspicious messages, URLs, domains, indicators, tactics, similarity clusters, and community reports.
    """
    return await threat_library_service.query_library(
        search=search,
        entity_type=entity_type,
        severity=severity,
        verification_status=verification_status,
        provenance=provenance,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        page_size=page_size,
    )


@router.get("/{item_id}", response_model=Dict[str, Any])
async def get_threat_library_item(item_id: str):
    """
    Retrieves full detail view, provenance, and verification status for a Threat Library record.
    """
    item = await threat_library_service.get_item_detail(item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Threat Library item '{item_id}' was not found.",
        )
    return item
