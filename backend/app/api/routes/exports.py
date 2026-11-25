"""
TRUSTLENS AI - Investigation Reporting & JSON / STIX 2.1 Export Endpoints
GET /api/v1/intelligence-reports/generate
GET /api/v1/exports/json
GET /api/v1/exports/stix
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

from backend.app.services.reporting_service import reporting_service
from backend.app.services.ti_sharing_service import ti_sharing_service
from backend.app.security.dependencies import get_optional_current_user, get_current_user

router = APIRouter(tags=["Reports & Exports"])


class ImportValidationRequest(BaseModel):
    format: str
    payload: Dict[str, Any]


@router.get("/intelligence-reports/generate", response_model=Dict[str, Any])
async def generate_intelligence_report(
    report_type: str = Query(
        ...,
        description="message_analysis | url_analysis | comprehensive_investigation | campaign_similarity | model_evaluation",
    ),
    target_id: Optional[str] = Query(None, description="analysis_id, investigation_id, or campaign_id"),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user),
):
    """
    Generates an auditable investigation or model evaluation report with sources,
    evidence, model versions, predictions, review status, and limitations.
    """
    try:
        return await reporting_service.generate_report(
            report_type=report_type,
            target_id=target_id,
            current_user=current_user,
        )
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.get("/exports/json")
async def export_investigation_json(
    target_type: str = Query(..., description="investigation | analysis | campaign | report"),
    target_id: str = Query(..., description="Record identifier"),
    download: bool = Query(False, description="Set true to include Content-Disposition attachment header"),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user),
):
    """
    Exports investigation, analysis, campaign, or report data as structured JSON.
    """
    try:
        payload = await reporting_service.export_json(
            target_type=target_type,
            target_id=target_id,
            current_user=current_user,
        )
        headers = {}
        if download:
            headers["Content-Disposition"] = f'attachment; filename="trustlens-{target_type}-{target_id}.json"'
        return JSONResponse(content=jsonable_encoder(payload), headers=headers)
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.get("/exports/stix")
async def export_investigation_stix(
    target_type: str = Query(..., description="investigation | analysis | campaign"),
    target_id: str = Query(..., description="Record identifier"),
    download: bool = Query(False, description="Set true to include Content-Disposition attachment header"),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user),
):
    """
    Exports a strictly validated STIX 2.1 Bundle for supported object types and relationships.
    """
    try:
        bundle = await reporting_service.export_stix_21(
            target_type=target_type,
            target_id=target_id,
            current_user=current_user,
        )
        await ti_sharing_service.log_sharing_audit(
            "export_stix",
            (current_user or {}).get("user_id") or "anonymous",
            "stix21",
            target_id,
            {"target_type": target_type, "schema_valid": bundle.get("x_trustlens_stix_validation", {}).get("schema_valid")},
        )
        headers = {}
        if download:
            headers["Content-Disposition"] = f'attachment; filename="trustlens-{target_type}-{target_id}.stix.json"'
        return JSONResponse(content=jsonable_encoder(bundle), headers=headers)
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.get("/exports/misp")
async def export_investigation_misp(
    target_type: str = Query(..., description="investigation | analysis | campaign"),
    target_id: str = Query(..., description="Record identifier"),
    download: bool = Query(False, description="Set true to include Content-Disposition attachment header"),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Exports an authorized, PII-scrubbed MISP Core Format Event JSON with audit logging."""
    try:
        misp_event = await ti_sharing_service.export_misp_event(
            target_type=target_type,
            target_id=target_id,
            current_user=current_user,
            reporting_svc=reporting_service,
        )
        headers = {}
        if download:
            headers["Content-Disposition"] = f'attachment; filename="trustlens-{target_type}-{target_id}.misp.json"'
        return JSONResponse(content=jsonable_encoder(misp_event), headers=headers)
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.post("/exports/validate-import", response_model=Dict[str, Any])
async def validate_threat_intel_import(
    req: ImportValidationRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Validates incoming STIX 2.1 or MISP payloads for schema compliance and PII leakage."""
    try:
        uid = current_user.get("user_id") or current_user.get("email") or "analyst"
        return await ti_sharing_service.validate_import(req.format, req.payload, user_id=uid)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
