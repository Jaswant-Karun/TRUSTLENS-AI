"""
TRUSTLENS AI - Phase 2.5 End-to-End Workflow, RBAC & Security Integration Suite
Executes the complete user journey and security checks against the real FastAPI app & MongoDB,
cleaning up only its own synthetic test records.
"""

from datetime import datetime, timedelta
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


def _auth_headers(user_id: str, role: str, expires_delta: timedelta | None = None) -> dict:
    token = create_access_token(data={"sub": user_id, "role": role}, expires_delta=expires_delta)
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_phase2_5_complete_e2e_workflow_and_security(client: AsyncClient):
    uid_suffix = uuid.uuid4().hex[:8]
    user_a_email = f"e2e_user_a_{uid_suffix}@example.com"
    user_b_email = f"e2e_user_b_{uid_suffix}@example.com"
    password = f"Str0ngP@ss!{uid_suffix}"
    admin_id = "a22d3504-399f-4b0c-ac20-1a334aa1da22"  # existing admin in DB
    reviewer_id = f"e2e-reviewer-{uid_suffix}"

    user_a_id = None
    user_b_id = None
    created_inv_id = None
    created_analysis_id = None

    try:
        # 1. User A registers and logs in (real authentication flow)
        reg_a = await client.post(
            "/api/v1/auth/register",
            json={"email": user_a_email, "password": password, "full_name": "E2E User A", "role": "user"},
        )
        assert reg_a.status_code == 201, reg_a.text
        user_a_id = reg_a.json()["user_id"]

        login_a = await client.post(
            "/api/v1/auth/login",
            json={"email": user_a_email, "password": password},
        )
        assert login_a.status_code == 200, login_a.text
        token_a = login_a.json()["access_token"]
        h_user_a = {"Authorization": f"Bearer {token_a}"}

        me_res = await client.get("/api/v1/auth/me", headers=h_user_a)
        assert me_res.status_code == 200
        assert me_res.json()["email"] == user_a_email

        # Register & login User B for cross-user BOLA tests
        reg_b = await client.post(
            "/api/v1/auth/register",
            json={"email": user_b_email, "password": password, "full_name": "E2E User B", "role": "user"},
        )
        assert reg_b.status_code == 201, reg_b.text
        user_b_id = reg_b.json()["user_id"]
        login_b = await client.post("/api/v1/auth/login", json={"email": user_b_email, "password": password})
        assert login_b.status_code == 200
        h_user_b = {"Authorization": f"Bearer {login_b.json()['access_token']}"}

        h_reviewer = _auth_headers(reviewer_id, "reviewer")
        h_admin = _auth_headers(admin_id, "admin")
        h_expired = _auth_headers(user_a_id, "user", expires_delta=timedelta(seconds=-10))
        h_invalid = {"Authorization": "Bearer invalid.jwt.token"}

        # Token validation: expired & invalid tokens rejected
        assert (await client.post("/api/v1/investigations", json={"title": "Expired Token"}, headers=h_expired)).status_code == 401
        assert (await client.post("/api/v1/investigations", json={"title": "Invalid Token"}, headers=h_invalid)).status_code == 401

        # 2. Submit suspicious text for ML analysis
        analyze_res = await client.post(
            "/api/v1/analyze/text",
            json={
                "text": "URGENT: Your SBI KYC is suspended. Verify immediately at http://sbi-kyc-update-alert.com or account will be blocked in 2 hours.",
                "language": "en",
            },
            headers=h_user_a,
        )
        assert analyze_res.status_code == 200, analyze_res.text
        analysis_data = analyze_res.json()
        created_analysis_id = analysis_data["analysis_id"]
        assert "risk_score" in analysis_data
        assert "threat_level" in analysis_data

        # 3. Verify analysis is persisted in history (/api/v1/analyses)
        hist_res = await client.get("/api/v1/analyses?page=1&page_size=20", headers=h_user_a)
        assert hist_res.status_code == 200, hist_res.text
        hist_items = hist_res.json().get("items", [])
        assert any(item.get("analysis_id") == created_analysis_id for item in hist_items)

        detail_res = await client.get(f"/api/v1/analyses/{created_analysis_id}", headers=h_user_a)
        assert detail_res.status_code == 200
        assert detail_res.json()["analysis_id"] == created_analysis_id

        # 4. Create a Private investigation (testing mass assignment protection for owner_id)
        inv_res = await client.post(
            "/api/v1/investigations",
            json={
                "title": f"Phase 2.5 E2E KYC Case {uid_suffix}",
                "description": "End-to-end verification of analysis attachment, notes, timeline, and persistence",
                "severity": "high",
                "visibility": "Private",
                "owner_id": "spoofed-owner",
            },
            headers=h_user_a,
        )
        assert inv_res.status_code == 201, inv_res.text
        inv_data = inv_res.json()
        created_inv_id = inv_data["id"]
        assert inv_data["owner_id"] == user_a_id

        # 5. Attach the analysis to the investigation
        attach_res = await client.post(
            f"/api/v1/investigations/{created_inv_id}/attach-analysis",
            json={"analysis_id": created_analysis_id},
            headers=h_user_a,
        )
        assert attach_res.status_code == 200, attach_res.text

        # Duplicate attachment must return 409 Conflict
        dup_attach_res = await client.post(
            f"/api/v1/investigations/{created_inv_id}/attach-analysis",
            json={"analysis_id": created_analysis_id},
            headers=h_user_a,
        )
        assert dup_attach_res.status_code == 409

        # 6. Add an investigation note
        note_res = await client.post(
            f"/api/v1/investigations/{created_inv_id}/notes",
            json={"content": "Verified phishing domain indicator from Phase 2.5 E2E test."},
            headers=h_user_a,
        )
        assert note_res.status_code == 201, note_res.text
        note_id = note_res.json()["note_id"]

        # 7. Verify timeline records real chronological events
        tl_res = await client.get(f"/api/v1/investigations/{created_inv_id}/timeline", headers=h_user_a)
        assert tl_res.status_code == 200
        events = tl_res.json()["timeline"]
        action_types = [e.get("action_type") for e in events]
        assert "investigation_created" in action_types
        assert "analysis_attached" in action_types
        assert "note_added" in action_types
        timestamps = [datetime.fromisoformat(e["timestamp"].replace("Z", "+00:00")) for e in events]
        assert timestamps == sorted(timestamps)

        # 8. Re-fetch investigation (simulating refresh) & verify persisted notes + attached evidence
        refreshed_inv = await client.get(f"/api/v1/investigations/{created_inv_id}", headers=h_user_a)
        assert refreshed_inv.status_code == 200
        refreshed_notes = await client.get(f"/api/v1/investigations/{created_inv_id}/notes", headers=h_user_a)
        assert refreshed_notes.status_code == 200
        assert any(n["note_id"] == note_id for n in refreshed_notes.json())

        # 9. Campaign intelligence available from MongoDB
        camps_res = await client.get("/api/v1/campaigns")
        assert camps_res.status_code == 200
        assert len(camps_res.json()) == 47
        camp11_res = await client.get("/api/v1/campaigns/11")
        assert camp11_res.status_code == 200
        assert camp11_res.json()["cluster_id"] == 11

        # 10. Cross-user BOLA & RBAC checks on Private investigation
        assert (await client.get(f"/api/v1/investigations/{created_inv_id}", headers=h_user_b)).status_code == 403
        assert (await client.post(
            f"/api/v1/investigations/{created_inv_id}/notes",
            json={"content": "Unauthorized note"},
            headers=h_user_b,
        )).status_code == 403
        assert (await client.post(
            f"/api/v1/investigations/{created_inv_id}/attach-analysis",
            json={"analysis_id": created_analysis_id},
            headers=h_user_b,
        )).status_code == 403
        assert (await client.post(
            f"/api/v1/investigations/{created_inv_id}/notes",
            json={"content": "Unauthenticated note"},
        )).status_code == 401

        # Non-admin user cannot sync campaigns (admin-only); unauthenticated -> 401; admin -> 200
        assert (await client.post("/api/v1/campaigns/sync?dry_run=true")).status_code == 401
        assert (await client.post("/api/v1/campaigns/sync?dry_run=true", headers=h_user_b)).status_code == 403
        admin_sync = await client.post("/api/v1/campaigns/sync?dry_run=true", headers=h_admin)
        assert admin_sync.status_code == 200
        assert admin_sync.json()["total_source_records"] == 47

        # Admin can read private investigation
        assert (await client.get(f"/api/v1/investigations/{created_inv_id}", headers=h_admin)).status_code == 200

        # 11. NoSQL injection / malformed ID safety checks
        inj_res = await client.get("/api/v1/investigations/{'$ne':''}", headers=h_admin)
        assert inj_res.status_code in (400, 404, 422)
        inj_camp = await client.get("/api/v1/campaigns/{'$ne':''}")
        assert inj_camp.status_code in (400, 404, 422)

    finally:
        if created_inv_id:
            await get_investigations_collection().delete_one({"investigation_id": created_inv_id})
        if created_analysis_id:
            await get_analyses_collection().delete_one({"analysis_id": created_analysis_id})
        cleanup_ids = [uid for uid in [user_a_id, user_b_id] if uid]
        if cleanup_ids:
            await get_users_collection().delete_many({"user_id": {"$in": cleanup_ids}})
        await get_audit_collection().delete_many({"user_id": {"$in": cleanup_ids + [reviewer_id]}})
