"""
TRUSTLENS AI - API Routes Aggregator
Assembles all official v1 routers under a centralized router.
"""

from fastapi import APIRouter

from backend.app.api.routes import (
    auth,
    analyze,
    analyses,
    campaigns,
    models,
    reports,
    health,
    training,
    automation,
    investigations,
    threat_library,
    analytics,
    exports,
    notifications,
    threat_intel,
    ioc_enrichment,
    privacy,
    security_ops,
)

api_v1_router = APIRouter()

# Include all required functional routers
api_v1_router.include_router(health.router)
api_v1_router.include_router(auth.router)
api_v1_router.include_router(analyze.router)
api_v1_router.include_router(analyses.router)
api_v1_router.include_router(campaigns.router)
api_v1_router.include_router(models.router)
api_v1_router.include_router(reports.router)
api_v1_router.include_router(training.router)
api_v1_router.include_router(automation.router)
api_v1_router.include_router(investigations.router)
api_v1_router.include_router(threat_library.router)
api_v1_router.include_router(analytics.router)
api_v1_router.include_router(exports.router)
api_v1_router.include_router(notifications.router)
api_v1_router.include_router(threat_intel.router)
api_v1_router.include_router(ioc_enrichment.router)
api_v1_router.include_router(privacy.router)
api_v1_router.include_router(security_ops.router)

__all__ = ["api_v1_router"]

