"""
TRUSTLENS AI - n8n Automation & Training Orchestration Test Suite
Tests:
1. Workflow JSON schema integrity & node documentation completeness.
2. Threat feed ingestion & duplicate prevention.
3. Asynchronous ML training job dispatch, duplicate job locking, and evaluation comparison.
4. Gated human promotion with approval tokens.
5. Campaign alert dispatch, cohesion thresholds, and 24h duplicate suppression.
6. Daily executive intelligence summary generation.
7. Automation audit logging.
"""

import pytest
import json
import glob
from pathlib import Path
from httpx import AsyncClient, ASGITransport
import asyncio

from backend.app.main import app
from backend.app.database.manager import db_manager


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


@pytest.fixture
async def admin_auth_token(client: AsyncClient):
    """Seeds default admin and logs in to get a verified Administrator JWT."""
    from backend.app.services.auth_service import auth_service
    await auth_service.seed_initial_admin()

    login_res = await client.post(
        "/api/v1/auth/login",
        json={"email": "admin@trustlens.ai", "password": "Admin@TrustLens2026!"},
    )
    assert login_res.status_code == 200, f"Login failed: {login_res.text}"
    token = login_res.json()["access_token"]
    return token


def test_n8n_workflow_json_schema_and_documentation():
    """Validates that all 6 workflow JSON files exist, parse cleanly, and document every node."""
    workflow_files = glob.glob("n8n/workflows/0*.json")
    assert len(workflow_files) == 6, f"Expected 6 numbered workflows, found {len(workflow_files)}"

    for filepath in workflow_files:
        path = Path(filepath)
        with open(path, "r", encoding="utf-8") as f:
            wf = json.load(f)

        assert "name" in wf, f"{path.name} missing 'name'"
        assert "nodes" in wf, f"{path.name} missing 'nodes'"
        assert "connections" in wf, f"{path.name} missing 'connections'"
        assert len(wf["nodes"]) >= 5, f"{path.name} has fewer than 5 nodes"

        # Verify every node has a descriptive 'notes' or documentation field
        for node in wf["nodes"]:
            assert "name" in node, f"Node missing name in {path.name}"
            assert "type" in node, f"Node {node['name']} missing type in {path.name}"
            assert "notes" in node and len(node["notes"]) > 10, (
                f"Node '{node['name']}' in {path.name} must contain descriptive documentation notes."
            )


@pytest.mark.asyncio
async def test_threat_feed_ingestion_and_deduplication(client: AsyncClient, admin_auth_token: str):
    """Tests Workflow 1 target: Feed ingestion with strict duplicate prevention."""
    headers = {"Authorization": f"Bearer {admin_auth_token}"}
    import uuid
    run_id = uuid.uuid4().hex[:6]
    
    feed_payload = {
        "source_name": f"Test_URLhaus_Feed_{run_id}",
        "feed_timestamp": "2026-11-13T00:00:00Z",
        "indicators": [
            {
                "indicator_type": "url",
                "indicator_value": f"http://fraud-portal-test-{run_id}.xyz/login.html",
                "confidence": 0.94,
                "tags": ["phishing", "banking"],
            },
            {
                "indicator_type": "domain",
                "indicator_value": f"pan-card-verification-{run_id}.online",
                "confidence": 0.88,
                "tags": ["kyc_fraud"],
            },
        ],
        "workflow_id": f"n8n-exec-test-{run_id}",
    }

    # 1. First Ingestion: both records should be ingested
    res1 = await client.post("/api/v1/automation/ingest-feed", json=feed_payload, headers=headers)
    assert res1.status_code == 200, f"Ingestion failed: {res1.text}"
    data1 = res1.json()
    assert data1["status"] == "success"
    assert data1["ingested_count"] == 2
    assert data1["duplicates_skipped"] == 0

    # 2. Second Ingestion: duplicates should be safely skipped
    res2 = await client.post("/api/v1/automation/ingest-feed", json=feed_payload, headers=headers)
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["status"] == "success"
    assert data2["ingested_count"] == 0
    assert data2["duplicates_skipped"] == 2


@pytest.mark.asyncio
async def test_automated_ml_training_lifecycle_and_locks(client: AsyncClient, admin_auth_token: str):
    """
    Tests Workflow 2 & 3 targets:
    - Background job enqueueing
    - Duplicate training lock prevention (HTTP 409)
    - Asynchronous job completion polling
    - Candidate vs production model comparison
    - Human-approved production promotion
    """
    headers = {"Authorization": f"Bearer {admin_auth_token}"}

    train_payload = {
        "model_name": "model2_url",
        "dataset_version": "v1.2-cleaned",
        "hyperparameters": {"n_estimators": 100, "max_depth": 6},
    }

    # 1. Enqueue Training Job
    res = await client.post("/api/v1/training/jobs", json=train_payload, headers=headers)
    assert res.status_code == 202, f"Training job rejected: {res.text}"
    job = res.json()
    job_id = job["job_id"]
    assert job["status"] in ["queued", "running"]

    # 2. Concurrency Lock: Immediate duplicate request for model2_url must be rejected with 409
    dup_res = await client.post("/api/v1/training/jobs", json=train_payload, headers=headers)
    assert dup_res.status_code == 409, "Duplicate training job was not locked out!"

    # 3. Poll until completed (worker processes asynchronously)
    for _ in range(15):
        await asyncio.sleep(0.3)
        poll_res = await client.get(f"/api/v1/training/jobs/{job_id}", headers=headers)
        assert poll_res.status_code == 200
        poll_data = poll_res.json()
        if poll_data["status"] == "completed":
            break

    assert poll_data["status"] == "completed"
    assert poll_data["progress"] == 1.0
    assert "roc_auc" in poll_data["metrics"]

    # 4. Compare Candidate Model with Production Baseline
    comp_res = await client.post(f"/api/v1/training/jobs/{job_id}/compare", headers=headers)
    assert comp_res.status_code == 200
    comp_data = comp_res.json()
    assert comp_data["passed_criteria"] is True
    assert comp_data["requires_human_approval"] is True
    assert comp_data["recommendation"] == "PROCEED_TO_HUMAN_APPROVAL"

    # 5. Production Promotion without valid token must fail validation
    bad_prom = await client.post(
        f"/api/v1/training/jobs/{job_id}/promote",
        json={"approved_by": "analyst", "approval_token": "short"},
        headers=headers,
    )
    assert bad_prom.status_code in [400, 422]

    # 6. Production Promotion with valid human approval token
    prom_res = await client.post(
        f"/api/v1/training/jobs/{job_id}/promote",
        json={
            "approved_by": "security_lead_analyst",
            "approval_token": "AUTH-HUMAN-LEAD-2026-CONFIRM",
        },
        headers=headers,
    )
    assert prom_res.status_code == 200
    prom_data = prom_res.json()
    assert prom_data["status"] == "promoted_successfully"
    assert "audit_id" in prom_data


@pytest.mark.asyncio
async def test_campaign_alerts_cohesion_and_duplicate_suppression(client: AsyncClient, admin_auth_token: str):
    """Tests Workflow 4 target: Cohesion validation and 24h alert deduplication."""
    headers = {"Authorization": f"Bearer {admin_auth_token}"}

    alert_payload = {
        "cluster_id": 99,
        "campaign_name": "Campaign Cluster #99 — Fake Electricity Bill Cut",
        "targeted_entity": "State Electricity Board",
        "cohesion_score": 0.78,
        "indicators": ["http://electricity-bill-pay.site", "9812345678"],
        "exemplar_message": "Electricity will be disconnected tonight. Call officer immediately.",
    }

    # 1. Low cohesion score (< 0.60) must be rejected
    low_cohesion_payload = dict(alert_payload)
    low_cohesion_payload["cluster_id"] = 100
    low_cohesion_payload["cohesion_score"] = 0.45
    low_res = await client.post("/api/v1/automation/campaign-alerts", json=low_cohesion_payload, headers=headers)
    assert low_res.status_code == 200
    assert low_res.json()["status"] == "rejected_low_confidence"

    # 2. First alert dispatch: succeeds
    res1 = await client.post("/api/v1/automation/campaign-alerts", json=alert_payload, headers=headers)
    assert res1.status_code == 200
    data1 = res1.json()
    assert data1["status"] == "dispatched"
    assert data1["is_duplicate"] is False
    assert data1["recipients_notified"] >= 1

    # 3. Duplicate dispatch within 24 hours: suppressed
    res2 = await client.post("/api/v1/automation/campaign-alerts", json=alert_payload, headers=headers)
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["status"] == "suppressed_duplicate"
    assert data2["is_duplicate"] is True


@pytest.mark.asyncio
async def test_daily_summary_and_execution_logging(client: AsyncClient, admin_auth_token: str):
    """Tests Workflow 6 targets: Daily summary generation and execution logging."""
    headers = {"Authorization": f"Bearer {admin_auth_token}"}

    # 1. Fetch Daily Executive Summary
    summary_res = await client.get("/api/v1/automation/daily-summary", headers=headers)
    assert summary_res.status_code == 200
    summary = summary_res.json()
    assert "telemetry_24h" in summary
    assert "model_health" in summary
    assert "top_emerging_threats" in summary
    assert summary["telemetry_24h"]["total_threat_scans"] >= 0

    # 2. Log n8n execution telemetry
    log_payload = {
        "workflow_name": "daily_intelligence_report",
        "trigger_event": "daily_cron_0800_utc",
        "status": "success",
        "payload_summary": {"total_scans": summary["telemetry_24h"]["total_threat_scans"]},
        "duration_ms": 230.5,
    }
    log_res = await client.post("/api/v1/automation/log-execution", json=log_payload, headers=headers)
    assert log_res.status_code == 200
    assert log_res.json()["status"] == "logged"
    assert "log_id" in log_res.json()

