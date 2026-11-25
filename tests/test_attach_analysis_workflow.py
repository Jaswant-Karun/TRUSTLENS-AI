"""
TRUSTLENS AI - Attach Analysis to Investigation Workflow Tests
Verifies authenticated attachment to existing/new investigations,
provenance preservation (analysis_id, model_version, analysis_created_at, evidence_reference),
duplicate prevention (409), unauthorized protection (403), graph & timeline updates,
and frontend AttachToInvestigationModal wiring.
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
async def test_attach_analysis_provenance_duplicate_and_rbac(client: AsyncClient):
    suffix = uuid.uuid4().hex[:8]
    email_a = f"att_a_{suffix}@example.com"
    email_b = f"att_b_{suffix}@example.com"
    pw = f"Att@ch1!{suffix}"
    user_a_id = None
    user_b_id = None
    inv_id = None
    ana_id = None

    try:
        reg_a = await client.post("/api/v1/auth/register", json={"email": email_a, "password": pw, "full_name": "Attach A"})
        reg_b = await client.post("/api/v1/auth/register", json={"email": email_b, "password": pw, "full_name": "Attach B"})
        user_a_id = reg_a.json()["user_id"]
        user_b_id = reg_b.json()["user_id"]

        tok_a = (await client.post("/api/v1/auth/login", json={"email": email_a, "password": pw})).json()["access_token"]
        tok_b = (await client.post("/api/v1/auth/login", json={"email": email_b, "password": pw})).json()["access_token"]
        h_a = {"Authorization": f"Bearer {tok_a}"}
        h_b = {"Authorization": f"Bearer {tok_b}"}

        # 1. Run real analysis
        ana_res = await client.post(
            "/api/v1/analyze/text",
            json={"text": "URGENT: Verify SBI KYC at http://sbi-kyc-attach.xyz immediately."},
            headers=h_a,
        )
        assert ana_res.status_code == 200
        ana_id = ana_res.json()["analysis_id"]

        # 2. Create Private investigation
        inv_res = await client.post(
            "/api/v1/investigations",
            json={"title": f"Attach Case {suffix}", "severity": "high", "visibility": "Private"},
            headers=h_a,
        )
        assert inv_res.status_code == 201
        inv_id = inv_res.json()["id"]

        # 3. Unauthorized cross-user attach -> 403
        assert (await client.post(
            f"/api/v1/investigations/{inv_id}/attach-analysis",
            json={"analysis_id": ana_id},
            headers=h_b,
        )).status_code == 403

        # 4. Authorized attach -> 200
        att_res = await client.post(
            f"/api/v1/investigations/{inv_id}/attach-analysis",
            json={"analysis_id": ana_id},
            headers=h_a,
        )
        assert att_res.status_code == 200

        # 5. Duplicate attach -> 409 Conflict
        dup_res = await client.post(
            f"/api/v1/investigations/{inv_id}/attach-analysis",
            json={"analysis_id": ana_id},
            headers=h_a,
        )
        assert dup_res.status_code == 409

        # 6. Verify graph node provenance & timeline event
        graph_res = await client.get(f"/api/v1/investigations/{inv_id}/graph", headers=h_a)
        assert graph_res.status_code == 200
        nodes = graph_res.json()["nodes"]
        ana_nodes = [n for n in nodes if (n.get("properties") or {}).get("analysis_id") == ana_id]
        assert len(ana_nodes) == 1
        props = ana_nodes[0]["properties"]
        assert props["evidence_reference"] == f"analyses/{ana_id}"
        assert props["model_version"]
        assert props["analysis_created_at"]

        tl_res = await client.get(f"/api/v1/investigations/{inv_id}/timeline", headers=h_a)
        assert tl_res.status_code == 200
        assert any(e.get("action_type") == "analysis_attached" for e in tl_res.json()["timeline"])
    finally:
        if inv_id:
            await get_investigations_collection().delete_one({"investigation_id": inv_id})
        if ana_id:
            await get_analyses_collection().delete_one({"analysis_id": ana_id})
        ids = [u for u in (user_a_id, user_b_id) if u]
        if ids:
            await get_users_collection().delete_many({"user_id": {"$in": ids}})
            await get_audit_collection().delete_many({"user_id": {"$in": ids}})


def test_frontend_attach_modal_wired_into_results_and_history():
    modal = Path("frontend/components/investigation/AttachToInvestigationModal.tsx").read_text(encoding="utf-8")
    panel = Path("frontend/components/ui/AnalysisResultPanel.tsx").read_text(encoding="utf-8")
    history = Path("frontend/app/history/page.tsx").read_text(encoding="utf-8")
    assert "attachAnalysisToInvestigation" in modal
    assert "createInvestigation" in modal
    assert "AttachToInvestigationModal" in panel
    assert "AttachToInvestigationModal" in history
