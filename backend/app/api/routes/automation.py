"""
TRUSTLENS AI - Automation & Integration Endpoints
POST /api/v1/automation/ingest-feed
POST /api/v1/automation/campaign-alerts
GET  /api/v1/automation/daily-summary
POST /api/v1/automation/log-execution
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from backend.app.services.automation_service import automation_service
from backend.app.security.dependencies import require_analyst_or_admin

router = APIRouter(prefix="/automation", tags=["n8n Automation & Feeds"])


class FeedIngestionRequest(BaseModel):
    source_name: str = Field(..., description="Approved feed name, e.g. URLhaus, PhishTank, Mendeley")
    feed_timestamp: Optional[str] = Field(None, description="ISO timestamp of feed extraction")
    indicators: List[Dict[str, Any]] = Field(..., description="List of indicators/URLs to ingest")
    workflow_id: Optional[str] = Field(None, description="n8n workflow execution ID")


class CampaignAlertRequest(BaseModel):
    cluster_id: int
    campaign_name: str
    targeted_entity: str
    cohesion_score: float
    indicators: List[str] = Field(default_factory=list)
    exemplar_message: Optional[str] = None


class ExecutionLogRequest(BaseModel):
    workflow_name: str
    trigger_event: str
    status: str = "success"
    payload_summary: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    duration_ms: float = 0.0


@router.post("/ingest-feed")
async def ingest_threat_feed(
    request: FeedIngestionRequest,
    current_user: Dict[str, Any] = Depends(require_analyst_or_admin),
):
    """
    Ingests external threat intelligence feed data with duplicate prevention.
    """
    try:
        return await automation_service.ingest_threat_feed(
            source_name=request.source_name,
            feed_timestamp=request.feed_timestamp,
            indicators=request.indicators,
            workflow_id=request.workflow_id,
        )
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))


@router.post("/campaign-alerts")
async def dispatch_campaign_alert(
    request: CampaignAlertRequest,
    current_user: Dict[str, Any] = Depends(require_analyst_or_admin),
):
    """
    Dispatches campaign alerts with 24h duplicate suppression and cohesion checks.
    """
    return await automation_service.dispatch_campaign_alert(
        cluster_id=request.cluster_id,
        campaign_name=request.campaign_name,
        targeted_entity=request.targeted_entity,
        cohesion_score=request.cohesion_score,
        indicators=request.indicators,
        exemplar_message=request.exemplar_message,
    )


@router.get("/daily-summary")
async def get_daily_summary(
    current_user: Dict[str, Any] = Depends(require_analyst_or_admin),
):
    """
    Aggregates verified daily metrics across scans, community reports,
    model performance, and emerging campaign clusters for executive reporting.
    """
    return await automation_service.get_daily_intelligence_summary()


@router.post("/log-execution")
async def log_workflow_execution(
    request: ExecutionLogRequest,
    current_user: Dict[str, Any] = Depends(require_analyst_or_admin),
):
    """
    Logs an n8n workflow execution record to the automation_logs collection.
    """
    log_id = await automation_service.record_execution_log(
        workflow_name=request.workflow_name,
        trigger_event=request.trigger_event,
        status=request.status,
        payload_summary=request.payload_summary,
        error_message=request.error_message,
        duration_ms=request.duration_ms,
    )
    return {"status": "logged", "log_id": log_id}

