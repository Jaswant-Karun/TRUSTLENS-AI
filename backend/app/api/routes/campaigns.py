"""
TRUSTLENS AI - Campaign Intelligence Endpoints
GET /api/v1/campaigns
GET /api/v1/campaigns/{id}
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Query, HTTPException, status

from backend.app.schemas.common import CampaignSummary, CampaignDetailResponse
from backend.app.services.campaign_service import campaign_service

router = APIRouter(prefix="/campaigns", tags=["Campaign Intelligence"])


@router.get("", response_model=List[CampaignSummary])
async def list_campaigns(
    status: Optional[str] = Query(None, description="active | dormant | mitigated"),
    target: Optional[str] = Query(None, description="Filter by targeted institution / brand"),
    limit: int = Query(50, ge=1, le=100),
):
    """
    Lists discovered scam campaign clusters, sizes, cohesion, and targets.
    """
    return await campaign_service.list_campaigns(
        status=status,
        target=target,
        limit=limit,
    )


@router.get("/{campaign_id}", response_model=CampaignDetailResponse)
async def get_campaign(campaign_id: int):
    """
    Retrieves full intelligence dossier for a specific campaign cluster.
    Includes shared IOCs, exemplar message, and mandatory legal attribution disclaimer.
    """
    dossier = await campaign_service.get_campaign_by_id(campaign_id)
    if not dossier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Campaign Cluster #{campaign_id} was not found.",
        )
    return dossier
