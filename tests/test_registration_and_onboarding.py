"""
TRUSTLENS AI - Registration, Consent, Onboarding & Email Verification Tests
Verifies password strength validation, privacy/terms consent enforcement,
duplicate-email prevention, bcrypt hashing (no plaintext), onboarding persistence,
and email verification endpoint.
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
async def test_registration_validation_duplicate_and_verification(client: AsyncClient):
    suffix = uuid.uuid4().hex[:8]
    email = f"onboard_{suffix}@example.com"
    strong_pw = f"Onb0ard!{suffix}"
    user_id = None

    try:
        # 1. Weak password rejected (no digits) -> 422
        weak_res = await client.post(
            "/api/v1/auth/register",
            json={
                "email": email,
                "password": "WeakPasswordOnlyLetters",
                "full_name": "Weak Test",
                "privacy_accepted": True,
                "terms_accepted": True,
            },
        )
        assert weak_res.status_code == 422

        # 2. Missing privacy/terms consent rejected -> 422
        no_consent = await client.post(
            "/api/v1/auth/register",
            json={
                "email": email,
                "password": strong_pw,
                "full_name": "Consent Test",
                "privacy_accepted": False,
                "terms_accepted": True,
            },
        )
        assert no_consent.status_code == 422

        # 3. Valid registration with onboarding preferences -> 201
        ok_res = await client.post(
            "/api/v1/auth/register",
            json={
                "email": email,
                "password": strong_pw,
                "full_name": "Onboard User",
                "privacy_accepted": True,
                "terms_accepted": True,
                "onboarding_preferences": {
                    "preferred_language": "hi",
                    "primary_focus": "url_shield",
                    "threat_alerts_opt_in": True,
                },
            },
        )
        assert ok_res.status_code == 201, ok_res.text
        data = ok_res.json()
        user_id = data["user_id"]
        ver_token = data["verification_token"]
        assert ver_token

        # Verify DB stores bcrypt hash, never plaintext password, plus onboarding prefs
        db_user = await get_users_collection().find_one({"user_id": user_id})
        assert db_user is not None
        assert db_user["hashed_password"].startswith("$2b$")
        assert strong_pw not in str(db_user)
        assert db_user["privacy_accepted"] is True
        assert db_user["terms_accepted"] is True
        assert db_user["onboarding_preferences"]["preferred_language"] == "hi"
        assert db_user["email_verified"] is False

        # 4. Duplicate registration prevented -> 400
        dup_res = await client.post(
            "/api/v1/auth/register",
            json={"email": email.upper(), "password": strong_pw, "full_name": "Dup User"},
        )
        assert dup_res.status_code == 400

        # 5. Invalid email verification token -> 400
        bad_ver = await client.post("/api/v1/auth/verify-email", json={"token": "invalid.token.value"})
        assert bad_ver.status_code == 400

        # 6. Valid email verification token -> 200 & DB updated
        good_ver = await client.post("/api/v1/auth/verify-email", json={"token": ver_token})
        assert good_ver.status_code == 200
        assert good_ver.json()["verified"] is True
        db_user_after = await get_users_collection().find_one({"user_id": user_id})
        assert db_user_after["email_verified"] is True
    finally:
        if user_id:
            await get_users_collection().delete_one({"user_id": user_id})
            await get_audit_collection().delete_many({"user_id": user_id})
