"""
TRUSTLENS AI - Sign-In & Authentication Security Tests
Tests invalid credentials, expired sessions, unauthorized access,
and real successful login against FastAPI + MongoDB, plus login UI contracts.
"""

from datetime import timedelta
from pathlib import Path
import uuid
import pytest
from httpx import AsyncClient, ASGITransport

from backend.app.main import app
from backend.app.database.manager import db_manager
from backend.app.database.collections import get_audit_collection, get_users_collection
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


@pytest.mark.asyncio
async def test_signin_invalid_expired_unauthorized_and_success(client: AsyncClient):
    suffix = uuid.uuid4().hex[:8]
    email = f"signin_test_{suffix}@example.com"
    password = f"ValidP@ss!{suffix}"
    user_id = None

    try:
        # 1. Unauthorized access without token -> 401
        assert (await client.get("/api/v1/auth/me")).status_code == 401
        assert (await client.get("/api/v1/analyses")).status_code == 401

        # 2. Invalid credentials (non-existent email) -> 401
        bad_user = await client.post(
            "/api/v1/auth/login",
            json={"email": f"missing_{suffix}@example.com", "password": password},
        )
        assert bad_user.status_code == 401

        # 3. Register real user
        reg = await client.post(
            "/api/v1/auth/register",
            json={"email": email, "password": password, "full_name": "SignIn Test", "role": "user"},
        )
        assert reg.status_code == 201, reg.text
        user_id = reg.json()["user_id"]

        # 4. Invalid credentials (wrong password) -> 401
        wrong_pw = await client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": "WrongPassword123!"},
        )
        assert wrong_pw.status_code == 401

        # 5. Expired session token -> 401
        expired_token = create_access_token(
            data={"sub": user_id, "role": "user"},
            expires_delta=timedelta(seconds=-15),
        )
        exp_res = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {expired_token}"},
        )
        assert exp_res.status_code == 401

        # 6. Successful authentication -> 200 + valid JWT accepted by /auth/me
        ok_res = await client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": password},
        )
        assert ok_res.status_code == 200, ok_res.text
        token = ok_res.json()["access_token"]
        me_res = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert me_res.status_code == 200
        assert me_res.json()["email"] == email
        assert me_res.json()["user_id"] == user_id
    finally:
        if user_id:
            await get_users_collection().delete_one({"user_id": user_id})
            await get_audit_collection().delete_many({"user_id": user_id})


def test_login_page_security_and_ux_contracts():
    login_src = Path("frontend/app/login/page.tsx").read_text(encoding="utf-8")
    for token in [
        "sanitizeNextPath",
        "clearStoredToken",
        "getCurrentUser",
        "loginUser",
        "/forgot-password",
        "showPassword",
        "AUTHENTICATING...",
        "session_expired",
    ]:
        assert token in login_src, f"Missing expected sign-in feature: {token}"
