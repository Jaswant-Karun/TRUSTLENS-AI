"""
TRUSTLENS AI - User, Organization, Role Assignment & Account Lifecycle Tests
Verifies organization membership, admin RBAC, account deactivation/deletion,
personal data export isolation, and cross-user private analysis/investigation isolation.
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
async def test_user_organization_lifecycle_and_cross_user_isolation(client: AsyncClient):
    suffix = uuid.uuid4().hex[:8]
    email_a = f"org_a_{suffix}@example.com"
    email_b = f"org_b_{suffix}@example.com"
    password = f"OrgTest!{suffix}"
    admin_id = "a22d3504-399f-4b0c-ac20-1a334aa1da22"
    h_admin = {"Authorization": f"Bearer {create_access_token(data={'sub': admin_id, 'role': 'admin'})}"}

    user_a_id = None
    user_b_id = None
    org_id = None
    inv_a_id = None
    ana_a_id = None

    try:
        # 1. Register & login User A and User B
        reg_a = await client.post("/api/v1/auth/register", json={"email": email_a, "password": password, "full_name": "Org User A"})
        reg_b = await client.post("/api/v1/auth/register", json={"email": email_b, "password": password, "full_name": "Org User B"})
        assert reg_a.status_code == 201 and reg_b.status_code == 201
        user_a_id = reg_a.json()["user_id"]
        user_b_id = reg_b.json()["user_id"]

        tok_a = (await client.post("/api/v1/auth/login", json={"email": email_a, "password": password})).json()["access_token"]
        tok_b = (await client.post("/api/v1/auth/login", json={"email": email_b, "password": password})).json()["access_token"]
        h_a = {"Authorization": f"Bearer {tok_a}"}
        h_b = {"Authorization": f"Bearer {tok_b}"}

        # 2. User A creates an organization & assigns User B as analyst
        org_res = await client.post("/api/v1/auth/organizations", json={"name": f"SecOps Team {suffix}"}, headers=h_a)
        assert org_res.status_code == 201, org_res.text
        org_id = org_res.json()["organization_id"]

        # Non-member User B cannot assign membership -> 403
        bad_mem = await client.post(
            f"/api/v1/auth/users/{user_b_id}/organization",
            json={"organization_id": org_id, "organization_role": "org_admin"},
            headers=h_b,
        )
        assert bad_mem.status_code == 403

        # User A (org_admin) assigns User B as member
        ok_mem = await client.post(
            f"/api/v1/auth/users/{user_b_id}/organization",
            json={"organization_id": org_id, "organization_role": "member"},
            headers=h_a,
        )
        assert ok_mem.status_code == 200
        assert ok_mem.json()["organization_id"] == org_id

        # 3. Role assignment is admin-only
        assert (await client.patch(f"/api/v1/auth/users/{user_b_id}/role", json={"role": "analyst"}, headers=h_a)).status_code == 403
        role_res = await client.patch(f"/api/v1/auth/users/{user_b_id}/role", json={"role": "reviewer"}, headers=h_admin)
        assert role_res.status_code == 200 and role_res.json()["role"] == "reviewer"

        # 4. Cross-user isolation on Private investigation and personal analysis
        ana_res = await client.post(
            "/api/v1/analyze/text",
            json={"text": "URGENT: Your KYC is blocked. Verify at http://kyc-test-trap.xyz"},
            headers=h_a,
        )
        assert ana_res.status_code == 200
        ana_a_id = ana_res.json()["analysis_id"]

        inv_res = await client.post(
            "/api/v1/investigations",
            json={"title": f"Private Case {suffix}", "severity": "high", "visibility": "Private"},
            headers=h_a,
        )
        assert inv_res.status_code == 201
        inv_a_id = inv_res.json()["id"]

        # User B cannot access User A's private investigation (403) or private analysis (404)
        assert (await client.get(f"/api/v1/investigations/{inv_a_id}", headers=h_b)).status_code == 403
        assert (await client.get(f"/api/v1/analyses/{ana_a_id}", headers=h_b)).status_code == 404

        # User B's personal data export must NOT contain User A's analysis or investigation
        exp_b = await client.get("/api/v1/auth/export-data", headers=h_b)
        assert exp_b.status_code == 200
        assert all(a.get("analysis_id") != ana_a_id for a in exp_b.json()["analyses"])
        assert all(i.get("investigation_id") != inv_a_id for i in exp_b.json()["investigations"])

        # 5. Admin can deactivate & reactivate User B
        deact = await client.patch(f"/api/v1/auth/users/{user_b_id}/status", json={"is_active": False, "reason": "Audit test"}, headers=h_admin)
        assert deact.status_code == 200 and deact.json()["is_active"] is False
        assert (await client.get("/api/v1/auth/me", headers=h_b)).status_code == 403

        react = await client.patch(f"/api/v1/auth/users/{user_b_id}/status", json={"is_active": True}, headers=h_admin)
        assert react.status_code == 200 and react.json()["is_active"] is True

        # 6. Self-service account deletion requires valid password & revokes access
        bad_del = await client.request("DELETE", "/api/v1/auth/account", json={"password": "WrongPassword!"}, headers=h_a)
        assert bad_del.status_code == 401

        ok_del = await client.request("DELETE", "/api/v1/auth/account", json={"password": password}, headers=h_a)
        assert ok_del.status_code == 200 and ok_del.json()["deleted"] is True
        assert (await client.get("/api/v1/auth/me", headers=h_a)).status_code == 403
    finally:
        if inv_a_id:
            await get_investigations_collection().delete_one({"investigation_id": inv_a_id})
        if ana_a_id:
            await get_analyses_collection().delete_one({"analysis_id": ana_a_id})
        if org_id:
            await db_manager.db["organizations"].delete_one({"organization_id": org_id})
        ids = [uid for uid in (user_a_id, user_b_id) if uid]
        if ids:
            await get_users_collection().delete_many({"user_id": {"$in": ids}})
            await get_audit_collection().delete_many({"user_id": {"$in": ids + [admin_id]}, "resource_id": {"$in": ids + ([org_id] if org_id else [])}})
