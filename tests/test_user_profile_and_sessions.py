"""
TRUSTLENS AI - User Profile, Preferences, Sessions & Logout Tests
Tests authenticated profile retrieval, PATCH /api/v1/auth/me updates,
mass-assignment rejection, session history isolation, and logout revocation.
"""

import asyncio
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
async def test_profile_update_sessions_and_logout_revocation(client: AsyncClient):
    suffix = uuid.uuid4().hex[:8]
    email = f"profile_{suffix}@example.com"
    password = f"Prof1le!{suffix}"
    user_id = None

    try:
        # 1. Unauthenticated profile/sessions/logout rejected -> 401
        assert (await client.patch("/api/v1/auth/me", json={"full_name": "Anon"})).status_code == 401
        assert (await client.get("/api/v1/auth/sessions")).status_code == 401
        assert (await client.post("/api/v1/auth/logout")).status_code == 401

        # 2. Register & login
        reg = await client.post(
            "/api/v1/auth/register",
            json={"email": email, "password": password, "full_name": "Profile User"},
        )
        assert reg.status_code == 201
        user_id = reg.json()["user_id"]

        login = await client.post("/api/v1/auth/login", json={"email": email, "password": password})
        assert login.status_code == 200
        headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

        # 3. Update profile name, language, and notification settings
        patch_res = await client.patch(
            "/api/v1/auth/me",
            json={
                "full_name": "Updated Analyst Name",
                "preferred_language": "hi",
                "primary_focus": "investigations",
                "email_notifications": True,
                "in_app_notifications": True,
            },
            headers=headers,
        )
        assert patch_res.status_code == 200, patch_res.text
        updated = patch_res.json()
        assert updated["full_name"] == "Updated Analyst Name"
        assert updated["onboarding_preferences"]["preferred_language"] == "hi"
        assert updated["onboarding_preferences"]["email_notifications"] is True

        # 4. Mass assignment attempt (role escalation) rejected -> 422
        esc_res = await client.patch("/api/v1/auth/me", json={"role": "admin"}, headers=headers)
        assert esc_res.status_code == 422

        # 5. Active sessions returns own auth events
        sess_res = await client.get("/api/v1/auth/sessions", headers=headers)
        assert sess_res.status_code == 200
        assert sess_res.json()["user_id"] == user_id
        assert len(sess_res.json()["sessions"]) >= 2

        # 6. Logout revokes prior token
        await asyncio.sleep(1.1)  # ensure logout timestamp > token iat second
        out_res = await client.post("/api/v1/auth/logout", headers=headers)
        assert out_res.status_code == 200
        assert out_res.json()["logged_out"] is True

        revoked_check = await client.get("/api/v1/auth/me", headers=headers)
        assert revoked_check.status_code == 401
    finally:
        if user_id:
            await get_users_collection().delete_one({"user_id": user_id})
            await get_audit_collection().delete_many({"user_id": user_id})
