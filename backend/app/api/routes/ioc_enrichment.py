"""
TRUSTLENS AI - IOC Enrichment Endpoints
POST /api/v1/threat-intel/enrich
POST /api/v1/threat-intel/enrich/batch
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from backend.app.services.ioc_enrichment_service import ioc_enrichment_service

router = APIRouter(prefix="/threat-intel", tags=["IOC Enrichment"])


class IOCEnrichRequest(BaseModel):
    value: str = Field(..., min_length=1, max_length=2048)
    indicator_type: Optional[str] = Field(default=None, description="domain | url | ip | file_hash | phone | email")
    allow_external: bool = Field(default=False)
    external_consent: bool = Field(default=False, description="Explicit user consent required for external lookups")


class IOCBatchItem(BaseModel):
    value: str = Field(..., min_length=1, max_length=2048)
    indicator_type: Optional[str] = None


class IOCBatchEnrichRequest(BaseModel):
    indicators: List[IOCBatchItem] = Field(..., min_length=1, max_length=50)
    allow_external: bool = Field(default=False)
    external_consent: bool = Field(default=False)


@router.post("/enrich", response_model=Dict[str, Any])
async def enrich_single_ioc(payload: IOCEnrichRequest):
    try:
        return await ioc_enrichment_service.enrich_indicator(
            value=payload.value,
            indicator_type=payload.indicator_type,
            allow_external=payload.allow_external,
            external_consent=payload.external_consent,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))


@router.post("/enrich/batch", response_model=Dict[str, Any])
async def enrich_batch_iocs(payload: IOCBatchEnrichRequest):
    try:
        return await ioc_enrichment_service.enrich_batch(
            indicators=[i.model_dump() for i in payload.indicators],
            allow_external=payload.allow_external,
            external_consent=payload.external_consent,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))
