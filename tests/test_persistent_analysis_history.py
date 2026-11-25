"""
TRUSTLENS AI - Persistent Analysis History Tests
Tests real MongoDB persistence, pagination, sorting, filtering, detail retrieval,
cross-user delete isolation (403), authorized deletion (200), and zero fabricated UI data.
"""

from pathlib import Path
import uuid
import pytest
from httpx import AsyncClient, ASGITransport

from backend.app.main import app
from backend.app.database.manager import db_manager
from backend.app.database.collections import (
    get_analyses_collection,
    get_audit_collection,
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
async def test_persistent_history_sort_filter_detail_and_authorized_delete(client: AsyncClient):
    suffix = uuid.uuid4().hex[:8]
    email_a = f"hist_a_{suffix}@example.com"
    email_b = f"hist_b_{suffix}@example.com"
    pw = f"Hist0ry!{suffix}"
    user_a_id = None
    user_b_id = None
    created_ids = []

    try:
        reg_a = await client.post("/api/v1/auth/register", json={"email": email_a, "password": pw, "full_name": "Hist A"})
        reg_b = await client.post("/api/v1/auth/register", json={"email": email_b, "password": pw, "full_name": "Hist B"})
        user_a_id = reg_a.json()["user_id"]
        user_b_id = reg_b.json()["user_id"]

        tok_a = (await client.post("/api/v1/auth/login", json={"email": email_a, "password": pw})).json()["access_token"]
        tok_b = (await client.post("/api/v1/auth/login", json={"email": email_b, "password": pw})).json()["access_token"]
        h_a = {"Authorization": f"Bearer {tok_a}"}
        h_b = {"Authorization": f"Bearer {tok_b}"}

        # Create 2 real analyses for User A
        r1 = await client.post(
            "/api/v1/analyze/text",
            json={"text": "Hey, are we meeting at 2pm today?", "channel": "sms"},
            headers=h_a,
        )
        r2 = await client.post(
            "/api/v1/analyze/text",
            json={"text": "URGENT: SBI KYC suspended. Verify at http://sbi-kyc-trap.xyz now!", "channel": "sms"},
            headers=h_a,
        )
        assert r1.status_code == 200 and r2.status_code == 200
        id1 = r1.json()["analysis_id"]
        id2 = r2.json()["analysis_id"]
        created_ids.extend([id1, id2])

        # List with sorting (risk_score desc) & pagination
        list_res = await client.get("/api/v1/analyses?page=1&page_size=10&sort_by=risk_score&sort_order=desc", headers=h_a)
        assert list_res.status_code == 200
        items = list_res.json()["items"]
        assert len(items) == 2
        assert items[0]["risk_score"] >= items[1]["risk_score"]

        # Search filter by analysis_id
        search_res = await client.get(f"/api/v1/analyses?search={id2}", headers=h_a)
        assert search_res.status_code == 200
        assert search_res.json()["total_count"] == 1

        # Detail retrieval
        det_res = await client.get(f"/api/v1/analyses/{id2}", headers=h_a)
        assert det_res.status_code == 200
        assert det_res.json()["analysis_id"] == id2
        assert "risk_assessment" in det_res.json()

        # Cross-user delete rejected -> 403
        bad_del = await client.delete(f"/api/v1/analyses/{id2}", headers=h_b)
        assert bad_del.status_code == 403

        # Authorized delete by owner -> 200, then 404
        ok_del = await client.delete(f"/api/v1/analyses/{id2}", headers=h_a)
        assert ok_del.status_code == 200
        assert ok_del.json()["deleted"] is True
        assert (await client.get(f"/api/v1/analyses/{id2}", headers=h_a)).status_code == 404
    finally:
        if created_ids:
            await get_analyses_collection().delete_many({"analysis_id": {"$in": created_ids}})
        ids = [u for u in (user_a_id, user_b_id) if u]
        if ids:
            await get_users_collection().delete_many({"user_id": {"$in": ids}})
            await get_audit_collection().delete_many({"user_id": {"$in": ids}})


def test_history_ui_has_no_fabricated_backup_data():
    src = Path("frontend/app/history/page.tsx").read_text(encoding="utf-8")
    assert "BACKUP_HISTORY" not in src
    assert "bg-white" not in src
    assert "deleteAnalysis" in src
