"""
Automated tests for Privacy-First Data Protection Architecture:
- /api/v1/privacy/policy exposes purposes, retention, user rights, and non-claim of regulatory compliance
- Granular consent defaults (opt-in False), update, and audit logging
- /api/v1/privacy/access-logs returns user's own audit trail
- Fernet field-level encryption roundtrip & PII redaction
- Retention policy dry-run preview
"""

from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.database.manager import db_manager
from backend.app.security.dependencies import get_current_user, require_analyst_or_admin
from backend.app.services.privacy_service import privacy_service


def test_privacy_policy_consent_encryption_retention_and_logs():
    db_manager._use_fallback = True
    client = TestClient(app)

    # 1. Public privacy policy & DPDP/GDPR summary (explicitly does not claim unverified compliance)
    pol = client.get("/api/v1/privacy/policy")
    assert pol.status_code == 200
    pdata = pol.json()
    assert len(pdata["data_collection_purposes"]) >= 5
    assert pdata["data_retention_policy"]["analyses"]["retention_days"] == 90
    assert pdata["jurisdictional_assessment"]["regulatory_compliance_claim"] is False
    assert "india_dpdp_act_2023" in pdata["jurisdictional_assessment"]
    assert "eu_gdpr" in pdata["jurisdictional_assessment"]

    # 2. Field-level encryption roundtrip & PII redaction
    secret_note = "Sensitive victim reference 12345"
    enc = privacy_service.encrypt_sensitive_field(secret_note)
    assert enc != secret_note
    assert privacy_service.decrypt_sensitive_field(enc) == secret_note
    assert "9876543210" not in privacy_service.redact_pii("Call 9876543210 or PAN ABCDE1234F")

    # 3. Consent defaults, update, and access logs
    user = {"user_id": "priv-u-1", "email": "priv@trustlens.ai", "role": "analyst"}
    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[require_analyst_or_admin] = lambda: user
    try:
        c0 = client.get("/api/v1/privacy/consent").json()
        assert c0["external_ioc_enrichment"] is False
        assert c0["community_report_public_listing"] is False

        c1 = client.put("/api/v1/privacy/consent", json={"external_ioc_enrichment": True}).json()
        assert c1["external_ioc_enrichment"] is True
        assert c1["updated_at_utc"] is not None

        logs = client.get("/api/v1/privacy/access-logs").json()
        assert logs["total"] >= 1
        assert logs["logs"][0]["action"] == "update_privacy_consent"

        ret = client.post("/api/v1/privacy/retention/preview").json()
        assert ret["dry_run"] is True
    finally:
        app.dependency_overrides.pop(get_current_user, None)
        app.dependency_overrides.pop(require_analyst_or_admin, None)
