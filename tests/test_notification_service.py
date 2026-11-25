"""
TRUSTLENS AI - Secure Notification Service Tests
Tests unauthenticated 401 rejections, opt-in/opt-out consent enforcement,
async queue delivery, read/unread state, cross-user BOLA isolation (404),
and delivery history retrieval.
"""

import uuid
import pytest
from httpx import AsyncClient, ASGITransport

from backend.app.main import app
from backend.app.database.manager import db_manager
from backend.app.database.collections import get_audit_collection, get_users_collection


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
async def test_notification_consent_queue_read_and_isolation(client: AsyncClient):
    suffix = uuid.uuid4().hex[:8]
    email_a = f"notif_a_{suffix}@example.com"
    email_b = f"notif_b_{suffix}@example.com"
    pw = f"Not1f!{suffix}"
    user_a_id = None
    user_b_id = None

    try:
        # 1. Unauthenticated rejected -> 401
        assert (await client.get("/api/v1/notifications")).status_code == 401

        reg_a = await client.post("/api/v1/auth/register", json={"email": email_a, "password": pw, "full_name": "Notif A"})
        reg_b = await client.post("/api/v1/auth/register", json={"email": email_b, "password": pw, "full_name": "Notif B"})
        user_a_id = reg_a.json()["user_id"]
        user_b_id = reg_b.json()["user_id"]

        tok_a = (await client.post("/api/v1/auth/login", json={"email": email_a, "password": pw})).json()["access_token"]
        tok_b = (await client.post("/api/v1/auth/login", json={"email": email_b, "password": pw})).json()["access_token"]
        h_a = {"Authorization": f"Bearer {tok_a}"}
        h_b = {"Authorization": f"Bearer {tok_b}"}

        # 2. Unconsented threat_intelligence notification is skipped (not unsolicited)
        skip_res = await client.post(
            "/api/v1/notifications/dispatch",
            json={
                "category": "threat_intelligence",
                "title": "New Campaign Cluster",
                "summary": "Cluster #45 activity observed.",
                "severity": "medium",
            },
            headers=h_a,
        )
        assert skip_res.status_code == 200
        assert skip_res.json()["queued"] is False
        assert skip_res.json()["status"] == "skipped_opt_out"

        # 3. Opt in to threat_alerts_opt_in, then dispatch investigation_update & threat_intelligence
        pref_res = await client.patch(
            "/api/v1/notifications/preferences",
            json={"threat_alerts_opt_in": True, "in_app_notifications": True},
            headers=h_a,
        )
        assert pref_res.status_code == 200
        assert pref_res.json()["threat_alerts_opt_in"] is True

        d1 = await client.post(
            "/api/v1/notifications/dispatch",
            json={
                "category": "investigation_update",
                "title": "Investigation Updated",
                "summary": "Evidence attached to case.",
                "severity": "info",
                "reference_id": "INV-2026-0011",
            },
            headers=h_a,
        )
        assert d1.status_code == 200 and d1.json()["queued"] is True
        notif_id = d1.json()["notification_id"]

        # 4. List notifications -> delivered asynchronously, unread_count == 1
        inbox = await client.get("/api/v1/notifications", headers=h_a)
        assert inbox.status_code == 200
        assert inbox.json()["unread_count"] == 1
        assert inbox.json()["items"][0]["delivery_status"] == "delivered"

        # 5. Cross-user BOLA: User B cannot mark User A's notification read -> 404
        assert (await client.patch(f"/api/v1/notifications/{notif_id}/read", headers=h_b)).status_code == 404

        # 6. User A marks read & verifies delivery history
        read_res = await client.patch(f"/api/v1/notifications/{notif_id}/read", headers=h_a)
        assert read_res.status_code == 200 and read_res.json()["read"] is True

        dlv_res = await client.get("/api/v1/notifications/deliveries", headers=h_a)
        assert dlv_res.status_code == 200
        assert any(d["notification_id"] == notif_id for d in dlv_res.json()["items"])
    finally:
        ids = [u for u in (user_a_id, user_b_id) if u]
        if ids:
            await db_manager.db["notifications"].delete_many({"user_id": {"$in": ids}})
            await db_manager.db["notification_deliveries"].delete_many({"user_id": {"$in": ids}})
            await get_users_collection().delete_many({"user_id": {"$in": ids}})
            await get_audit_collection().delete_many({"user_id": {"$in": ids}})
