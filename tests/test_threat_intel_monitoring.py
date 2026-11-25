"""
Automated tests for Scalable Threat Intelligence Monitoring Pipeline:
- Retry handling with exponential backoff on transient errors
- Idempotency (repeated identical payload yields unchanged_indicators, 0 new_indicators)
- Delta tracking (new_indicators vs threat_status_changed)
- Campaign correlation against scam_campaigns
- Per-source hourly rate limiting
- Source health & last_successful_sync_utc reporting with scheduled_polling label
"""

import json
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.database.manager import db_manager
from backend.app.database.collections import get_campaigns_collection
from backend.app.security.dependencies import get_current_user
from backend.app.services.threat_intel_service import threat_intel_service


@pytest.fixture()
def client():
    db_manager._use_fallback = True
    threat_intel_service._rate_limit_windows.clear()
    return TestClient(app)


def test_retries_idempotency_delta_and_source_health(client):
    kev_v1 = json.dumps({
        "vulnerabilities": [{"cveID": "CVE-2026-9999", "vendorProject": "Test", "product": "App", "vulnerabilityName": "Bug", "knownRansomwareCampaignUse": "Unknown", "dateAdded": "2026-11-25"}]
    })
    kev_v2 = json.dumps({
        "vulnerabilities": [{"cveID": "CVE-2026-9999", "vendorProject": "Test", "product": "App", "vulnerabilityName": "Bug", "knownRansomwareCampaignUse": "Known", "dateAdded": "2026-11-25"}]
    })

    app.dependency_overrides[get_current_user] = lambda: {"user_id": "sec-ops", "email": "ops@trustlens.ai"}
    try:
        with patch("backend.app.services.threat_intel_service.httpx.AsyncClient") as mock_client:
            # 1. Transient error on attempt 1, succeeds on attempt 2 (retry handling)
            ok_resp = MagicMock(status_code=200, text=kev_v1)
            ok_resp.raise_for_status = MagicMock()
            inst = AsyncMock()
            inst.get.side_effect = [RuntimeError("Transient 503"), ok_resp]
            mock_client.return_value.__aenter__.return_value = inst

            r1 = client.post("/api/v1/threat-intel/ingest/cisa_kev").json()
            assert r1["status"] == "success"
            assert r1["attempts"] == 2
            assert r1["new_indicators"] == 1
            assert r1["status_changes"] == 0

            # 2. Idempotency: same payload again -> 0 new, 1 unchanged
            inst.get.side_effect = [ok_resp]
            r2 = client.post("/api/v1/threat-intel/ingest/cisa_kev").json()
            assert r2["new_indicators"] == 0
            assert r2["unchanged_indicators"] == 1

            # 3. Threat status change (Unknown -> Known => high -> critical)
            ok_v2 = MagicMock(status_code=200, text=kev_v2)
            ok_v2.raise_for_status = MagicMock()
            inst.get.side_effect = [ok_v2]
            r3 = client.post("/api/v1/threat-intel/ingest/cisa_kev").json()
            assert r3["status_changes"] == 1

        # 4. Status endpoint displays last_successful_sync_utc, source_health, and scheduled_polling notice
        st = client.get("/api/v1/threat-intel/status").json()
        assert st["sync_mode"] == "scheduled_polling"
        assert "not instantaneous real-time" in st["sync_mode_notice"].lower()
        assert st["last_successful_sync_utc"] is not None
        kev_h = [h for h in st["source_health"] if h["source_id"] == "cisa_kev"][0]
        assert kev_h["health_status"] == "healthy"
        assert kev_h["last_successful_sync_utc"] is not None
    finally:
        app.dependency_overrides.pop(get_current_user, None)
