"""
TRUSTLENS AI - Phase 2.1 Investigation Authentication & Notes Test Suite
Tests BOLA/ownership, authenticated creation, note CRUD, empty-note rejection, 404s, and DB failure handling.
"""

import pytest
from httpx import AsyncClient, ASGITransport

from backend.app.main import app
from backend.app.database.manager import db_manager
from backend.app.database.collections import get_investigations_collection
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
async def test_unauthenticated_investigation_creation_rejected(client: AsyncClient):
    res = await client.post("/api/v1/investigations", json={"title": "Unauth Test Case", "severity": "high"})
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_authenticated_creation_owner_enforcement_and_private_isolation(client: AsyncClient):
    user_a_id = "f57955fd-7d26-4695-86d4-9c930eb15370"  # existing regular user
    user_b_id = "user-b-isolated-test"
    admin_id = "a22d3504-399f-4b0c-ac20-1a334aa1da22"   # existing admin

    h_user_a = _headers(user_a_id, "user")
    h_admin = _headers(admin_id, "admin")

    # 1. Create private investigation; attempt to spoof owner_id in payload
    create_res = await client.post(
        "/api/v1/investigations",
        json={
            "title": "Phase 2.1 Private Investigation",
            "description": "Testing ownership enforcement",
            "severity": "high",
            "visibility": "Private",
            "owner_id": "spoofed-admin-id",
        },
        headers=h_user_a,
    )
    assert create_res.status_code == 201, create_res.text
    created = create_res.json()
    inv_id = created["id"]
    assert created["owner_id"] == user_a_id, "owner_id must come from JWT, never request payload"

    try:
        # 2. Owner can access investigation, graph, timeline, and notes
        assert (await client.get(f"/api/v1/investigations/{inv_id}", headers=h_user_a)).status_code == 200
        assert (await client.get(f"/api/v1/investigations/{inv_id}/graph", headers=h_user_a)).status_code == 200
        assert (await client.get(f"/api/v1/investigations/{inv_id}/timeline", headers=h_user_a)).status_code == 200
        assert (await client.get(f"/api/v1/investigations/{inv_id}/notes", headers=h_user_a)).status_code == 200

        # 3. Admin retains RBAC access
        assert (await client.get(f"/api/v1/investigations/{inv_id}", headers=h_admin)).status_code == 200

        # 4. Unauthenticated user gets 401 on private investigation
        assert (await client.get(f"/api/v1/investigations/{inv_id}")).status_code == 401
        assert (await client.get(f"/api/v1/investigations/{inv_id}/graph")).status_code == 401

        # 5. Another ordinary user (User B) gets 403 on private investigation & notes
        # (Use unit check on service since get_current_user requires DB user for write; test service _check_read_access directly + GET with mock user)
        from backend.app.services.investigation_service import investigation_service
        doc = await get_investigations_collection().find_one({"investigation_id": inv_id})
        with pytest.raises(PermissionError):
            investigation_service._check_read_access(doc, {"user_id": user_b_id, "role": "user"})
        with pytest.raises(PermissionError):
            investigation_service._check_write_access(doc, {"user_id": user_b_id, "role": "user"})

        # 6. Note creation, empty rejection, retrieval, edit, and delete
        empty_note = await client.post(
            f"/api/v1/investigations/{inv_id}/notes",
            json={"content": "   "},
            headers=h_user_a,
        )
        assert empty_note.status_code == 422

        note_res = await client.post(
            f"/api/v1/investigations/{inv_id}/notes",
            json={"content": "Verified phishing domain indicator via header analysis."},
            headers=h_user_a,
        )
        assert note_res.status_code == 201, note_res.text
        note = note_res.json()
        assert note["author_id"] == user_a_id
        assert note["investigation_id"] == inv_id
        note_id = note["note_id"]

        list_res = await client.get(f"/api/v1/investigations/{inv_id}/notes", headers=h_user_a)
        assert list_res.status_code == 200
        assert any(n["note_id"] == note_id for n in list_res.json())

        # Cross-user note edit/delete rejected via service check
        with pytest.raises(PermissionError):
            await investigation_service.update_note(inv_id, note_id, "Tampered", {"user_id": user_b_id, "role": "user"})
        with pytest.raises(PermissionError):
            await investigation_service.delete_note(inv_id, note_id, {"user_id": user_b_id, "role": "user"})

        # Owner edits & deletes own note
        upd_res = await client.patch(
            f"/api/v1/investigations/{inv_id}/notes/{note_id}",
            json={"content": "Updated analyst finding."},
            headers=h_user_a,
        )
        assert upd_res.status_code == 200 and upd_res.json()["content"] == "Updated analyst finding."

        del_res = await client.delete(f"/api/v1/investigations/{inv_id}/notes/{note_id}", headers=h_user_a)
        assert del_res.status_code == 200
    finally:
        # Clean up isolated synthetic test investigation
        await get_investigations_collection().delete_one({"investigation_id": inv_id})


@pytest.mark.asyncio
async def test_invalid_investigation_id_returns_404(client: AsyncClient):
    h_user = _headers("f57955fd-7d26-4695-86d4-9c930eb15370", "user")
    assert (await client.get("/api/v1/investigations/INV-DOES-NOT-EXIST")).status_code == 404
    assert (await client.post("/api/v1/investigations/INV-DOES-NOT-EXIST/notes", json={"content": "hello"}, headers=h_user)).status_code == 404


@pytest.mark.asyncio
async def test_database_failure_handled_safely(monkeypatch):
    from backend.app.services.investigation_service import investigation_service

    class FailingColl:
        async def count_documents(self, *args, **kwargs):
            return 1

        async def find_one(self, *args, **kwargs):
            raise RuntimeError("Simulated MongoDB outage")

    monkeypatch.setattr("backend.app.services.investigation_service.get_investigations_collection", lambda: FailingColl())
    with pytest.raises(RuntimeError, match="Simulated MongoDB outage"):
        await investigation_service.list_notes("INV-2026-0011")
