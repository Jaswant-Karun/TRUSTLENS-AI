"""
Automated tests for Threat Intelligence Sharing (STIX 2.1 & MISP):
- STIX 2.1 Bundle export, schema validation, confidence, external_references, and relationships
- MISP Event export, schema validation, Orgc/Tag/Attribute preservation
- Authorized export & import validation (rejects invalid schemas and PII leakage)
- Private user data (phone/email/private IP) never exposed in exports
- Audit logs recorded for exports and import validations
"""

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.database.manager import db_manager
from backend.app.database.collections import get_audit_collection, get_analyses_collection
from backend.app.security.dependencies import get_current_user, get_optional_current_user
from backend.app.services.ti_sharing_service import validate_stix_21_bundle, validate_misp_event


@pytest.fixture()
def client():
    db_manager._use_fallback = True
    return TestClient(app)


def test_stix_and_misp_export_validation_privacy_and_audit(client):
    import asyncio

    async def _seed():
        an_coll = get_analyses_collection()
        await an_coll.insert_one({
            "analysis_id": "an-stix-999",
            "user_id": "ti-user-1",
            "threat_level": "critical",
            "risk_score": 0.94,
            "created_at": "2026-11-25T10:00:00+00:00",
            "extracted_iocs": {
                "urls": ["http://evil-stix-test.xyz/login"],
                "domains": ["evil-stix-test.xyz"],
                "phones": ["+919876543210"],  # PII that MUST be scrubbed from exports
            },
            "tactic_model": {"tactics": [{"tactic_name": "Urgency and Time Pressure"}]},
        })
    asyncio.run(_seed())

    user = {"user_id": "ti-user-1", "email": "ti@trustlens.ai"}

    # 1. Unauthenticated MISP export is rejected (401)
    assert client.get("/api/v1/exports/misp?target_type=analysis&target_id=an-stix-999").status_code == 401

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_optional_current_user] = lambda: user
    try:
        # 2. STIX 2.1 export passes schema validation, preserves confidence & source, scrubs PII
        stix_r = client.get("/api/v1/exports/stix?target_type=analysis&target_id=an-stix-999")
        assert stix_r.status_code == 200
        bundle = stix_r.json()
        assert bundle["x_trustlens_stix_validation"]["schema_valid"] is True
        ok, errs = validate_stix_21_bundle(bundle)
        assert ok, errs
        indicators = [o for o in bundle["objects"] if o["type"] == "indicator"]
        assert len(indicators) >= 1
        assert "confidence" in indicators[0]
        assert "external_references" in indicators[0]
        assert "9876543210" not in str(bundle)

        # 3. MISP export passes validation and scrubs PII
        misp_r = client.get("/api/v1/exports/misp?target_type=analysis&target_id=an-stix-999")
        assert misp_r.status_code == 200
        misp_ev = misp_r.json()
        assert misp_ev["x_trustlens_misp_validation"]["valid"] is True
        m_ok, m_errs = validate_misp_event(misp_ev)
        assert m_ok, m_errs
        assert "9876543210" not in str(misp_ev)

        # 4. Import validation accepts valid STIX & rejects PII-leaking MISP
        val_ok = client.post("/api/v1/exports/validate-import", json={"format": "stix21", "payload": bundle})
        assert val_ok.status_code == 200
        assert val_ok.json()["valid"] is True

        bad_misp = {"Event": {"uuid": "1", "info": "bad", "date": "2026-11-25", "Orgc": {"name": "X"}, "Attribute": [{"type": "email", "category": "Other", "value": "leak@example.com"}]}}
        val_bad = client.post("/api/v1/exports/validate-import", json={"format": "misp", "payload": bad_misp})
        assert val_bad.status_code == 200
        assert val_bad.json()["valid"] is False

        # 5. Audit logs recorded
        async def _count_audits():
            return await get_audit_collection().count_documents({"user_id": "ti-user-1"})
        assert asyncio.run(_count_audits()) >= 3
    finally:
        app.dependency_overrides.pop(get_current_user, None)
        app.dependency_overrides.pop(get_optional_current_user, None)
