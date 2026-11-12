"""
TRUSTLENS AI - Campaign Intelligence Discovery Endpoints
"""

from fastapi import APIRouter, HTTPException
from backend.app.models.schemas import CampaignClusterRequest, CampaignClusterResponse
from backend.app.services.ml_service import ml_service

router = APIRouter(prefix="/campaigns", tags=["Campaign Discovery & IOC Clustering"])


@router.post("/cluster", response_model=CampaignClusterResponse)
async def cluster_campaign_messages(request: CampaignClusterRequest):
    """Clusters messages into coordinated fraud campaigns based on shared indicators."""
    try:
        result = ml_service.cluster_campaigns(
            messages=request.messages,
            similarity_threshold=request.similarity_threshold,
        )
        return CampaignClusterResponse(**result)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Campaign clustering error: {str(exc)}")

