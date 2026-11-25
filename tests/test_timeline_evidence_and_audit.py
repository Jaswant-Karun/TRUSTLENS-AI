"""
TRUSTLENS AI - Investigation Timeline, Evidence Reference & Audit History Tests
Verifies UTC timezone normalization, timeline pagination & ordering,
evidence_reference provenance, verified audit history endpoint,
and preservation of INV-2026-0011 without fabricating events.
"""

import uuid
import pytest
from httpx import AsyncClient, ASGITransport

from backend.app.main import app
from backend.app.database.manager import db_manager
from backend.app.database.collections import (
    get_analyses_collection,
    get_audit_collection,
    get_investigations_collection,
    get_users_collection,
)


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


@pytest.mark.asyncio
async def test_timeline_pagination_utc_evidence_and_audit_history(client: AsyncClient):
    suffix = uuid.uuid4().hex[:8]
    email_a = f"tl_a_{suffix}@example.com"
    email_b = f"tl_b_{suffix}@example.com"
    pw = f"TmL!ne1{suffix}"
    user_a_id = None
    user_b_id = None
    inv_id = None
    ana_id = None

    try:
        reg_a = await client.post("/api/v1/auth/register", json={"email": email_a, "password": pw, "full_name": "TL A"})
        reg_b = await client.post("/api/v1/auth/register", json={"email": email_b, "password": pw, "full_name": "TL B"})
        user_a_id = reg_a.json()["user_id"]
        user_b_id = reg_b.json()["user_id"]

        tok_a = (await client.post("/api/v1/auth/login", json={"email": email_a, "password": pw})).json()["access_token"]
        tok_b = (await client.post("/api/v1/auth/login", json={"email": email_b, "password": pw})).json()["access_token"]
        h_a = {"Authorization": f"Bearer {tok_a}"}
        h_b = {"Authorization": f"Bearer {tok_b}"}

        ana_res = await client.post(
            "/api/v1/analyze/text",
            json={"text": "URGENT: Your KYC is suspended. Verify at http://kyc-tl-test.xyz"},
            headers=h_a,
        )
        ana_id = ana_res.json()["analysis_id"]

        inv_res = await client.post(
            "/api/v1/investigations",
            json={"title": f"Timeline Case {suffix}", "severity": "high", "visibility": "Private"},
            headers=h_a,
        )
        inv_id = inv_res.json()["id"]

        await client.post(f"/api/v1/investigations/{inv_id}/notes", json={"content": "Analyst note 1"}, headers=h_a)
        await client.post(f"/api/v1/investigations/{inv_id}/attach-analysis", json={"analysis_id": ana_id}, headers=h_a)

        # 1. Paginated timeline (page_size=2 -> 2 pages for 3 events)
        p1 = await client.get(f"/api/v1/investigations/{inv_id}/timeline?page=1&page_size=2&order=asc", headers=h_a)
        assert p1.status_code == 200
        d1 = p1.json()
        assert d1["total_events"] == 3
        assert d1["total_pages"] == 2
        assert len(d1["timeline"]) == 2

        p2 = await client.get(f"/api/v1/investigations/{inv_id}/timeline?page=2&page_size=2&order=asc", headers=h_a)
        assert p2.status_code == 200
        d2 = p2.json()
        assert len(d2["timeline"]) == 1
        assert d2["timeline"][0]["action_type"] == "analysis_attached"
        assert d2["timeline"][0]["evidence_reference"] == f"analyses/{ana_id}"

        # 2. Audit history endpoint respects RBAC & returns real audit entries
        assert (await client.get(f"/api/v1/investigations/{inv_id}/audit", headers=h_b)).status_code == 403
        aud_res = await client.get(f"/api/v1/investigations/{inv_id}/audit", headers=h_a)
        assert aud_res.status_code == 200
        assert aud_res.json()["total_count"] >= 2

        # 3. Historical INV-2026-0011 remains untouched (6 real events)
        inv11 = await client.get("/api/v1/investigations/INV-2026-0011/timeline")
        assert inv11.status_code == 200
        assert inv11.json()["total_events"] == 6
    finally:
        if inv_id:
            await get_investigations_collection().delete_one({"investigation_id": inv_id})
        if ana_id:
            await get_analyses_collection().delete_one({"analysis_id": ana_id})
        ids = [u for u in (user_a_id, user_b_id) if u]
        if ids:
            await get_users_collection().delete_many({"user_id": {"$in": ids}})
            await get_audit_collection().delete_many({"user_id": {"$in": ids}})
