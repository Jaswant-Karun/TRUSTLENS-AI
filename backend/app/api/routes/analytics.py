"""
TRUSTLENS AI - Database-Backed Analytics Endpoints
GET /api/v1/analytics/overview
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, Query

from backend.app.services.analytics_service import analytics_service

router = APIRouter(prefix="/analytics", tags=["SOC Analytics"])


@router.get("/overview", response_model=Dict[str, Any])
async def get_analytics_overview(
    start_date: Optional[str] = Query(None, description="Filter start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Filter end date (YYYY-MM-DD)"),
    source: Optional[str] = Query(None, description="all | text | url | image | comprehensive | community_report"),
):
    """
    Returns live analytics aggregated from MongoDB records and verified model evaluation artifacts.
    """
    return await analytics_service.get_overview(
        start_date=start_date,
        end_date=end_date,
        source=source,
    )
