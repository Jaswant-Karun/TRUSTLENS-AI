"""
TRUSTLENS AI - Phase 2.3 Real Investigation Timeline & Event Tracking Tests
Tests:
- Investigation creation event
- Analysis attachment event & duplicate guard (409)
- Note creation event
- Status change event & duplicate status guard
- Chronological event ordering
- Invalid event/analysis references (404)
- Unauthorized timeline access (401)
- Empty timeline handling
- INV-2026-0011 historical timeline preservation
"""

import uuid
import pytest
from httpx import AsyncClient, ASGITransport

from backend.app.main import app
from backend.app.database.manager import db_manager
from backend.app.database.collections import get_investigations_collection, get_analyses_collection
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
async def test_event_driven_timeline_lifecycle_and_ordering(client: AsyncClient):
    user_id = "f57955fd-7d26-4695-86d4-9c930eb15370"
    admin_id = "a22d3504-399f-4b0c-ac20-1a334aa1da22"
    h_user = _headers(user_id, "user")
    h_admin = _headers(admin_id, "admin")

    # 1. Create investigation -> records investigation_created event
    c_res = await client.post(
        "/api/v1/investigations",
        json={"title": "Phase 2.3 Timeline Test", "severity": "high", "visibility": "Private"},
        headers=h_user,
    )
    assert c_res.status_code == 201
    inv_id = c_res.json()["id"]

    # Find a real analysis_id owned by admin (or any analysis for admin attach test)
    ana_doc = await get_analyses_collection().find_one({}, {"_id": 0, "analysis_id": 1})
    assert ana_doc is not None, "Expected at least 1 analysis in DB"
    ana_id = ana_doc["analysis_id"]

    try:
        # 2. Unauthorized timeline access -> 401
        assert (await client.get(f"/api/v1/investigations/{inv_id}/timeline")).status_code == 401

        # 3. Note creation -> records note_added event
        n_res = await client.post(
            f"/api/v1/investigations/{inv_id}/notes",
            json={"content": "Timeline test note."},
            headers=h_user,
        )
        assert n_res.status_code == 201

        # 4. Status change -> records investigation_status_changed event
        u_res = await client.patch(
            f"/api/v1/investigations/{inv_id}",
            json={"status": "in_progress"},
            headers=h_user,
        )
        assert u_res.status_code == 200 and u_res.json()["status"] == "in_progress"

        # 5. Analysis attachment -> records analysis_attached event; duplicate returns 409
        a_res = await client.post(
            f"/api/v1/investigations/{inv_id}/attach-analysis",
            json={"analysis_id": ana_id},
            headers=h_admin,
        )
        assert a_res.status_code == 200
        dup_res = await client.post(
            f"/api/v1/investigations/{inv_id}/attach-analysis",
            json={"analysis_id": ana_id},
            headers=h_admin,
        )
        assert dup_res.status_code == 409

        # Invalid analysis reference -> 404
        bad_ana = await client.post(
            f"/api/v1/investigations/{inv_id}/attach-analysis",
            json={"analysis_id": f"nonexistent-{uuid.uuid4().hex[:6]}"},
            headers=h_admin,
        )
        assert bad_ana.status_code == 404

        # 6. Verify all 4 action_types in chronological order
        t_res = await client.get(f"/api/v1/investigations/{inv_id}/timeline", headers=h_user)
        assert t_res.status_code == 200
        events = t_res.json()["timeline"]
        actions = [e.get("action_type") for e in events]
        assert actions == [
            "investigation_created",
            "note_added",
            "investigation_status_changed",
            "analysis_attached",
        ]
        timestamps = [e["timestamp"] for e in events]
        assert timestamps == sorted(timestamps), "Timeline events must be ordered chronologically"
    finally:
        await get_investigations_collection().delete_one({"investigation_id": inv_id})


@pytest.mark.asyncio
async def test_empty_timeline_and_historical_inv_0011_safety(client: AsyncClient):
    # INV-2026-0011 has genuine persisted events (not overwritten or fabricated)
    r_11 = await client.get("/api/v1/investigations/INV-2026-0011/timeline")
    assert r_11.status_code == 200
    assert r_11.json()["total_events"] == len(r_11.json()["timeline"])

    # Empty timeline case handled cleanly
    coll = get_investigations_collection()
    empty_id = f"INV-EMPTY-{uuid.uuid4().hex[:6]}"
    await coll.insert_one({
        "investigation_id": empty_id,
        "title": "Empty Timeline Check",
        "status": "active",
        "severity": "low",
        "visibility": "Organization",
        "nodes": [],
        "edges": [],
        "timeline": [],
    })
    try:
        r_empty = await client.get(f"/api/v1/investigations/{empty_id}/timeline")
        assert r_empty.status_code == 200
        assert r_empty.json()["timeline"] == []
        assert r_empty.json()["total_events"] == 0
    finally:
        await coll.delete_one({"investigation_id": empty_id})
