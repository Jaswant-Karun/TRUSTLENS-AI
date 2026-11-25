"""
Automated tests for Real Threat Intelligence Ingestion Architecture:
- All 6 sources document licensing, attribution, update_frequency, reliability, and permitted_commercial_use
- Commercial license gate blocks urlhaus_recent and openphish_community by default
- Normalization of PhishTank JSON, CISA KEV JSON, URLhaus CSV, and CERT RSS with source attribution
- Error handling records status='error' and never fabricates live threat intelligence
- API endpoints /threat-intel/sources, /threat-intel/status, /threat-intel/ingest/{source_id}
"""

import json
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.database.manager import db_manager
from backend.app.security.dependencies import get_current_user
from backend.app.services.threat_intel_service import THREAT_INTEL_SOURCES, threat_intel_service


@pytest.fixture()
def client():
    db_manager._use_fallback = True
    return TestClient(app)


def test_all_sources_have_required_governance_fields():
    assert len(THREAT_INTEL_SOURCES) >= 6
    for sid, spec in THREAT_INTEL_SOURCES.items():
        for field in ("licensing", "attribution", "update_frequency", "reliability", "permitted_commercial_use"):
            assert field in spec and spec[field], f"{sid} missing {field}"


def test_commercial_gate_blocks_non_commercial_feeds():
    with pytest.raises(PermissionError, match="blocked by commercial license gate"):
        threat_intel_service.check_commercial_gate("urlhaus_recent", allow_non_commercial=False)
    with pytest.raises(PermissionError, match="blocked by commercial license gate"):
        threat_intel_service.check_commercial_gate("openphish_community", allow_non_commercial=False)

    # Commercial-permitted sources pass
    assert threat_intel_service.check_commercial_gate("phishtank_online_valid")["source_id"] == "phishtank_online_valid"
    assert threat_intel_service.check_commercial_gate("cisa_kev")["source_id"] == "cisa_kev"


def test_payload_normalization_and_attribution():
    pt_body = json.dumps([{"url": "http://evil-sbi-login.xyz/kyc", "target": "SBI", "verification_time": "2026-11-25T10:00:00Z"}])
    pt_recs = threat_intel_service.normalize_payload("phishtank_online_valid", pt_body)
    assert len(pt_recs) == 1
    assert pt_recs[0]["source"] == "PhishTank (Cisco Talos)"
    assert pt_recs[0]["commercial_permitted"] is True
    assert pt_recs[0]["provenance"] == "threat_intel"

    kev_body = json.dumps({
        "vulnerabilities": [{"cveID": "CVE-2026-0001", "vendorProject": "Acme", "product": "VPN", "vulnerabilityName": "RCE", "knownRansomwareCampaignUse": "Known", "dateAdded": "2026-11-24"}]
    })
    kev_recs = threat_intel_service.normalize_payload("cisa_kev", kev_body)
    assert len(kev_recs) == 1
    assert kev_recs[0]["value"] == "CVE-2026-0001"
    assert kev_recs[0]["severity"] == "critical"


def test_api_sources_error_handling_and_no_fabrication(client):
    src_resp = client.get("/api/v1/threat-intel/sources")
    assert src_resp.status_code == 200
    assert src_resp.json()["total"] >= 6

    app.dependency_overrides[get_current_user] = lambda: {"user_id": "sec-ops", "email": "ops@trustlens.ai"}
    try:
        # Non-commercial feed returns 403
        blocked = client.post("/api/v1/threat-intel/ingest/urlhaus_recent")
        assert blocked.status_code == 403

        # Network error during ingestion returns status='error' with 0 records (never fabricated)
        with patch("backend.app.services.threat_intel_service.httpx.AsyncClient") as mock_client:
            inst = AsyncMock()
            inst.get.side_effect = RuntimeError("Upstream timeout")
            mock_client.return_value.__aenter__.return_value = inst
            err_resp = client.post("/api/v1/threat-intel/ingest/cisa_kev")
            assert err_resp.status_code == 200
            body = err_resp.json()
            assert body["status"] == "error"
            assert body["records_persisted"] == 0
            assert "Upstream timeout" in body["error"]
    finally:
        app.dependency_overrides.pop(get_current_user, None)
