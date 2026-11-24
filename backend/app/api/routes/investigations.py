"""
TRUSTLENS AI - Cyber Threat Investigation Graph API Endpoints
Implements the 7 official investigation graph endpoints.
"""

from typing import List, Optional
from fastapi import APIRouter, Query, HTTPException, status

from backend.app.schemas.investigation import (
    InvestigationSummary,
    InvestigationDetail,
    InvestigationCreate,
    InvestigationGraphResponse,
    InvestigationTimelineResponse,
    ObjectDetailResponse,
    ObjectRelationshipsResponse,
)
from backend.app.services.investigation_service import investigation_service

router = APIRouter(prefix="/investigations", tags=["Threat Investigations"])


@router.get("", response_model=List[InvestigationSummary])
async def list_investigations(
    status_filter: Optional[str] = Query(None, alias="status", description="active | in_progress | mitigated | archived"),
    severity: Optional[str] = Query(None, description="critical | high | medium | low"),
    limit: int = Query(50, ge=1, le=100),
):
    """
    Lists persisted investigation dossiers with node/task counters and severity.
    """
    return await investigation_service.list_investigations(
        status=status_filter,
        severity=severity,
        limit=limit,
    )


@router.post("", response_model=InvestigationDetail, status_code=status.HTTP_201_CREATED)
async def create_investigation(payload: InvestigationCreate):
    """
    Creates and persists a new cyber threat investigation dossier.
    """
    return await investigation_service.create_investigation(payload.model_dump())


@router.get("/{investigation_id}", response_model=InvestigationDetail)
async def get_investigation(investigation_id: str):
    """
    Retrieves metadata, attribution, sources, and summary statistics for a specific investigation.
    """
    doc = await investigation_service.get_investigation_by_id(investigation_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Investigation with ID '{investigation_id}' was not found.",
        )
    return doc


@router.get("/{investigation_id}/graph", response_model=InvestigationGraphResponse)
async def get_investigation_graph(investigation_id: str):
    """
    Retrieves all graph nodes, technical properties, and evidence-backed edges for the investigation.
    """
    graph = await investigation_service.get_investigation_graph(investigation_id)
    if not graph:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Investigation graph for ID '{investigation_id}' was not found.",
        )
    return graph


@router.get("/{investigation_id}/timeline", response_model=InvestigationTimelineResponse)
async def get_investigation_timeline(investigation_id: str):
    """
    Retrieves chronological multi-track timeline events for the investigation.
    """
    timeline = await investigation_service.get_investigation_timeline(investigation_id)
    if not timeline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Investigation timeline for ID '{investigation_id}' was not found.",
        )
    return timeline


@router.get("/{investigation_id}/objects/{object_id}", response_model=ObjectDetailResponse)
async def get_investigation_object(investigation_id: str, object_id: str):
    """
    Retrieves details and metadata for a specific object within an investigation.
    """
    obj_data = await investigation_service.get_object_by_id(investigation_id, object_id)
    if not obj_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Object '{object_id}' in investigation '{investigation_id}' was not found.",
        )
    return obj_data


@router.get("/{investigation_id}/objects/{object_id}/relationships", response_model=ObjectRelationshipsResponse)
async def get_investigation_object_relationships(investigation_id: str, object_id: str):
    """
    One-Hop Relationship Expansion:
    Returns existing connected entities plus discovers new real entities matching shared IOCs from MongoDB.
    """
    rels = await investigation_service.get_object_relationships(investigation_id, object_id)
    if not rels:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Relationships for object '{object_id}' in investigation '{investigation_id}' were not found.",
        )
    return rels
