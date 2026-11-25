"""
TRUSTLENS AI - Phase 2.4 Campaign Dossier Sync Tests
Tests RBAC on /campaigns/sync, dry-run, idempotent repeat sync, verified-DB protection, and DB-backed GET /campaigns.
"""

import pytest
from httpx import AsyncClient, ASGITransport

from backend.app.main import app
from backend.app.database.manager import db_manager
from backend.app.database.collections import get_campaigns_collection
from backend.app.security.jwt import create_access_token


@pytest.fixture(autouse=True)
async def setup_db():
    await db_manager.connect()
    yield
    await db_manager.disconnect()


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


def _headers(user_id: str, role: str) -> dict:
    token = create_access_token(data={"sub": user_id, "role": role})
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_campaign_sync_rbac_and_idempotency(client: AsyncClient):
    h_user = _headers("f57955fd-7d26-4695-86d4-9c930eb15370", "user")
    h_admin = _headers("a22d3504-399f-4b0c-ac20-1a334aa1da22", "admin")

    # 1. RBAC: unauthenticated -> 401, regular user -> 403
    assert (await client.post("/api/v1/campaigns/sync")).status_code == 401
    assert (await client.post("/api/v1/campaigns/sync", headers=h_user)).status_code == 403

    # 2. Dry-run by admin
    dry = await client.post("/api/v1/campaigns/sync?dry_run=true", headers=h_admin)
    assert dry.status_code == 200
    assert dry.json()["dry_run"] is True
    assert dry.json()["failed"] == 0

    # 3. Real sync & repeat sync idempotency
    s1 = await client.post("/api/v1/campaigns/sync", headers=h_admin)
    assert s1.status_code == 200 and s1.json()["failed"] == 0
    s2 = await client.post("/api/v1/campaigns/sync", headers=h_admin)
    assert s2.status_code == 200
    assert s2.json()["inserted"] == 0 and s2.json()["updated"] == 0 and s2.json()["skipped"] == 47

    # 4. DB count is exactly 47 and GET /campaigns returns DB records
    count = await get_campaigns_collection().count_documents({})
    assert count == 47

    list_res = await client.get("/api/v1/campaigns?limit=50")
    assert list_res.status_code == 200 and len(list_res.json()) == 47

    det_res = await client.get("/api/v1/campaigns/11")
    assert det_res.status_code == 200
    det = det_res.json()
    assert det["cluster_id"] == 11
    assert det["source_provenance"] == "ml/artifacts/campaign_detection/campaign_dossiers.json"
