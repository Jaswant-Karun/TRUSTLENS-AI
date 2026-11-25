"""
Automated tests for Community Threat Reporting System:
- PII & sensitive content redaction (phone, email, PAN, Aadhaar) + reporter privacy
- Duplicate detection (content_sha256, duplicate_count, is_duplicate)
- Abuse prevention (429 rate limit)
- Moderation & verification workflow (pending, reviewed, rejected, confirmed)
- Strict gating: only confirmed reports enter threat_indicators or verified-training-candidates
"""

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.database.manager import db_manager
from backend.app.database.collections import get_indicators_collection
from backend.app.security.dependencies import require_analyst_or_admin
from backend.app.services.report_service import report_service


@pytest.fixture()
def client():
    db_manager._use_fallback = True
    report_service._rate_windows.clear()
    return TestClient(app)


def test_pii_redaction_duplicate_detection_and_verification_gating(client):
    # 1. Submit report with PII (phone, email, PAN, Aadhaar) and a malicious URL
    payload = {
        "target_type": "sms",
        "content": "My PAN ABCDE1234F and Aadhaar 1234 5678 9012, call 9876543210 or visit http://evil-comm-test.xyz/kyc",
        "target_identifier": "9876543210",
        "description": "Email me at victim@example.com",
    }
    r1 = client.post("/api/v1/reports", json=payload)
    assert r1.status_code == 201
    d1 = r1.json()
    assert d1["status"] == "pending"
    assert d1["is_duplicate"] is False
    assert d1["eligible_for_threat_intel"] is False
    assert d1["eligible_for_ml_training"] is False
    # Verify PII redacted
    assert "9876543210" not in d1["content"]
    assert "ABCDE1234F" not in d1["content"]
    assert "1234 5678 9012" not in d1["content"]
    assert "victim@example.com" not in (d1["description"] or "")

    # 2. Duplicate submission returns is_duplicate=True and increments duplicate_count
    r2 = client.post("/api/v1/reports", json=payload)
    assert r2.status_code == 201
    assert r2.json()["is_duplicate"] is True
    assert r2.json()["duplicate_count"] == 2

    # 3. Public listing redacts reporter_user_id
    lst = client.get("/api/v1/reports").json()
    assert all(it["reporter_user_id"] == "redacted" for it in lst["items"])

    # 4. Moderation: reviewed -> rejected -> confirmed
    app.dependency_overrides[require_analyst_or_admin] = lambda: {"user_id": "mod-1", "role": "analyst"}
    try:
        rid = d1["report_id"]
        rev = client.post(f"/api/v1/reports/{rid}/review", json={"verdict": "reviewed", "notes": "Under triage"})
        assert rev.status_code == 200
        assert rev.json()["eligible_for_ml_training"] is False

        rej = client.post(f"/api/v1/reports/{rid}/review", json={"verdict": "rejected", "notes": "Spam noise"})
        assert rej.status_code == 200
        assert rej.json()["eligible_for_threat_intel"] is False
        assert client.get("/api/v1/reports/verified-training-candidates").json()["total"] == 0

        conf = client.post(f"/api/v1/reports/{rid}/review", json={"verdict": "confirmed", "notes": "Verified phishing"})
        assert conf.status_code == 200
        assert conf.json()["eligible_for_threat_intel"] is True
        assert conf.json()["eligible_for_ml_training"] is True
        assert client.get("/api/v1/reports/verified-training-candidates").json()["total"] == 1
    finally:
        app.dependency_overrides.pop(require_analyst_or_admin, None)


def test_abuse_rate_limit_enforced(client):
    for i in range(report_service.SUBMISSION_LIMIT_PER_MIN):
        r = client.post("/api/v1/reports", json={"target_type": "url", "content": f"http://spam-site-{i}.xyz/login"})
        assert r.status_code == 201

    blocked = client.post("/api/v1/reports", json={"target_type": "url", "content": "http://spam-site-overflow.xyz/login"})
    assert blocked.status_code == 429
