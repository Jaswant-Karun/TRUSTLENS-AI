"""
TRUSTLENS AI - Main API v1 Router Aggregator
Combines all domain routers into a unified API v1 namespace.
"""

from fastapi import APIRouter
from backend.app.api.v1.routers import health, scans, urls, tactics, campaigns, telemetry

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(scans.router)
api_router.include_router(urls.router)
api_router.include_router(tactics.router)
api_router.include_router(campaigns.router)
api_router.include_router(telemetry.router)

