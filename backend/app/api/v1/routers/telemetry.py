"""
TRUSTLENS AI - Telemetry & SOC Dashboard Overview Endpoints
"""

from fastapi import APIRouter
from backend.app.models.schemas import TelemetrySummaryResponse

router = APIRouter(prefix="/telemetry", tags=["SOC Telemetry & Analytics"])


@router.get("/summary", response_model=TelemetrySummaryResponse)
async def get_telemetry_summary():
    """Returns high-level statistics and threat distribution for the SOC dashboard."""
    return TelemetrySummaryResponse(
        total_scans_analyzed=0,
        total_threats_blocked=0,
        active_campaigns_tracked=0,
        avg_inference_latency_ms=18.5,
        threat_breakdown={
            "phishing": 0,
            "smishing": 0,
            "spam": 0,
            "clean": 0,
        },
        top_tactics=[
            {"tactic": "Artificial Urgency", "percentage": 0},
            {"tactic": "Credential Harvesting", "percentage": 0},
            {"tactic": "Bank Impersonation", "percentage": 0},
        ],
        system_status="ACTIVE_MONITORING",
    )

