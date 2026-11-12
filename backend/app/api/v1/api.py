"""
TRUSTLENS AI - Main API v1 Router Aggregator
Combines official specification routers with backward-compatible legacy routes.
"""

from fastapi import APIRouter
from backend.app.api.routes import api_v1_router
from backend.app.api.v1.routers import health, scans, urls, tactics, campaigns, telemetry

api_router = APIRouter()

# 1. Mount official v1 domain routes
api_router.include_router(api_v1_router)

# 2. Mount legacy endpoints for backwards compatibility
api_router.include_router(scans.router)
api_router.include_router(urls.router)
api_router.include_router(tactics.router)
api_router.include_router(telemetry.router)
