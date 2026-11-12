"""
TRUSTLENS AI - API Routes Aggregator
Assembles all official v1 routers under a centralized router.
"""

from fastapi import APIRouter

from backend.app.api.routes import auth, analyze, analyses, campaigns, models, reports, health

api_v1_router = APIRouter()

# Include all required functional routers
api_v1_router.include_router(health.router)
api_v1_router.include_router(auth.router)
api_v1_router.include_router(analyze.router)
api_v1_router.include_router(analyses.router)
api_v1_router.include_router(campaigns.router)
api_v1_router.include_router(models.router)
api_v1_router.include_router(reports.router)

__all__ = ["api_v1_router"]

