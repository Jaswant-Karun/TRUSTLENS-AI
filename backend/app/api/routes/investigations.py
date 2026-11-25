"""
TRUSTLENS AI - Cyber Threat Investigation Graph API Endpoints
Implements the 7 official investigation graph endpoints.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, Query, HTTPException, status

from backend.app.schemas.investigation import (
    InvestigationSummary,
    InvestigationDetail,
    InvestigationCreate,
    InvestigationGraphResponse,
    InvestigationTimelineResponse,
    ObjectDetailResponse,
    ObjectRelationshipsResponse,
    InvestigationNoteCreate,
    InvestigationNoteUpdate,
    InvestigationNoteResponse,
    InvestigationUpdate,
    AttachAnalysisRequest,
)
from backend.app.services.investigation_service import investigation_service
from backend.app.security.dependencies import get_current_user, get_optional_current_user

router = APIRouter(prefix="/investigations", tags=["Threat Investigations"])


def _handle_access_error(exc: PermissionError, current_user: Optional[Dict[str, Any]]):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))


@router.get("", response_model=List[InvestigationSummary])
async def list_investigations(
    status_filter: Optional[str] = Query(None, alias="status", description="active | in_progress | mitigated | archived"),
    severity: Optional[str] = Query(None, description="critical | high | medium | low"),
    limit: int = Query(50, ge=1, le=100),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user),
):
    """
    Lists persisted investigation dossiers visible to the caller.
    """
    return await investigation_service.list_investigations(
        status=status_filter,
        severity=severity,
        limit=limit,
        current_user=current_user,
    )


@router.post("", response_model=InvestigationDetail, status_code=status.HTTP_201_CREATED)
async def create_investigation(
    payload: InvestigationCreate,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Creates and persists a new cyber threat investigation dossier owned by the authenticated user.
    """
    try:
        return await investigation_service.create_investigation(
            payload.model_dump(),
            current_user=current_user,
        )
    except ValueError as verr:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(verr))


@router.get("/{investigation_id}", response_model=InvestigationDetail)
async def get_investigation(
    investigation_id: str,
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user),
):
    """
    Retrieves metadata, attribution, sources, and summary statistics for a specific investigation.
    """
    try:
        doc = await investigation_service.get_investigation_by_id(investigation_id, current_user=current_user)
    except PermissionError as exc:
        _handle_access_error(exc, current_user)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Investigation with ID '{investigation_id}' was not found.",
        )
    return doc


@router.get("/{investigation_id}/graph", response_model=InvestigationGraphResponse)
async def get_investigation_graph(
    investigation_id: str,
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user),
):
    """
    Retrieves all graph nodes, technical properties, and evidence-backed edges for the investigation.
    """
    try:
        graph = await investigation_service.get_investigation_graph(investigation_id, current_user=current_user)
    except PermissionError as exc:
        _handle_access_error(exc, current_user)
    if not graph:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Investigation graph for ID '{investigation_id}' was not found.",
        )
    return graph


@router.get("/{investigation_id}/timeline", response_model=InvestigationTimelineResponse)
async def get_investigation_timeline(
    investigation_id: str,
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user),
):
    """
    Retrieves chronological multi-track timeline events for the investigation.
    """
    try:
        timeline = await investigation_service.get_investigation_timeline(investigation_id, current_user=current_user)
    except PermissionError as exc:
        _handle_access_error(exc, current_user)
    if not timeline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Investigation timeline for ID '{investigation_id}' was not found.",
        )
    return timeline


@router.get("/{investigation_id}/objects/{object_id}", response_model=ObjectDetailResponse)
async def get_investigation_object(
    investigation_id: str,
    object_id: str,
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user),
):
    """
    Retrieves details and metadata for a specific object within an investigation.
    """
    try:
        obj_data = await investigation_service.get_object_by_id(investigation_id, object_id, current_user=current_user)
    except PermissionError as exc:
        _handle_access_error(exc, current_user)
    if not obj_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Object '{object_id}' in investigation '{investigation_id}' was not found.",
        )
    return obj_data


@router.get("/{investigation_id}/objects/{object_id}/relationships", response_model=ObjectRelationshipsResponse)
async def get_investigation_object_relationships(
    investigation_id: str,
    object_id: str,
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user),
):
    """
    One-Hop Relationship Expansion:
    Returns existing connected entities plus discovers new real entities matching shared IOCs from MongoDB.
    """
    try:
        rels = await investigation_service.get_object_relationships(investigation_id, object_id, current_user=current_user)
    except PermissionError as exc:
        _handle_access_error(exc, current_user)
    if not rels:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Relationships for object '{object_id}' in investigation '{investigation_id}' were not found.",
        )
    return rels


@router.get("/{investigation_id}/notes", response_model=List[InvestigationNoteResponse])
async def list_investigation_notes(
    investigation_id: str,
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user),
):
    """Retrieves persistent notes attached to an investigation."""
    try:
        notes = await investigation_service.list_notes(investigation_id, current_user=current_user)
    except PermissionError as exc:
        _handle_access_error(exc, current_user)
    if notes is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Investigation with ID '{investigation_id}' was not found.",
        )
    return notes


@router.post("/{investigation_id}/notes", response_model=InvestigationNoteResponse, status_code=status.HTTP_201_CREATED)
async def add_investigation_note(
    investigation_id: str,
    payload: InvestigationNoteCreate,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Adds a persistent analyst/owner note to an investigation."""
    try:
        note = await investigation_service.add_note(
            investigation_id=investigation_id,
            content=payload.content,
            current_user=current_user,
        )
    except PermissionError as exc:
        _handle_access_error(exc, current_user)
    except ValueError as verr:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(verr))
    if note is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Investigation with ID '{investigation_id}' was not found.",
        )
    return note


@router.patch("/{investigation_id}/notes/{note_id}", response_model=InvestigationNoteResponse)
async def update_investigation_note(
    investigation_id: str,
    note_id: str,
    payload: InvestigationNoteUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Edits an existing investigation note (author or admin only)."""
    try:
        note = await investigation_service.update_note(
            investigation_id=investigation_id,
            note_id=note_id,
            content=payload.content,
            current_user=current_user,
        )
    except PermissionError as exc:
        _handle_access_error(exc, current_user)
    except ValueError as verr:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(verr))
    if note is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note '{note_id}' in investigation '{investigation_id}' was not found.",
        )
    return note


@router.delete("/{investigation_id}/notes/{note_id}")
async def delete_investigation_note(
    investigation_id: str,
    note_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Deletes an investigation note (author or admin only)."""
    try:
        deleted = await investigation_service.delete_note(
            investigation_id=investigation_id,
            note_id=note_id,
            current_user=current_user,
        )
    except PermissionError as exc:
        _handle_access_error(exc, current_user)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note '{note_id}' in investigation '{investigation_id}' was not found.",
        )
    return {"status": "deleted", "note_id": note_id}


@router.patch("/{investigation_id}", response_model=InvestigationDetail)
async def update_investigation(
    investigation_id: str,
    payload: InvestigationUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Updates investigation status, visibility, or metadata and records timeline + audit events."""
    try:
        updated = await investigation_service.update_investigation(
            investigation_id=investigation_id,
            payload=payload.model_dump(exclude_none=True),
            current_user=current_user,
        )
    except PermissionError as exc:
        _handle_access_error(exc, current_user)
    except ValueError as verr:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(verr))
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Investigation with ID '{investigation_id}' was not found.",
        )
    return updated


@router.post("/{investigation_id}/attach-analysis", response_model=InvestigationDetail)
async def attach_analysis_to_investigation(
    investigation_id: str,
    payload: AttachAnalysisRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Attaches an existing analysis record to an investigation without mutating the original analysis."""
    try:
        updated = await investigation_service.attach_analysis(
            investigation_id=investigation_id,
            analysis_id=payload.analysis_id,
            current_user=current_user,
        )
    except PermissionError as exc:
        _handle_access_error(exc, current_user)
    except RuntimeError as rerr:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(rerr))
    except LookupError as lerr:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(lerr))
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Investigation with ID '{investigation_id}' was not found.",
        )
    return updated
