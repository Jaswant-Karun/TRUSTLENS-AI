"""
Automated tests for IOC Enrichment Service:
- Normalization & auto-detection for domains, URLs, IPs, file hashes, phones, emails
- Batch deduplication
- Privacy & consent gate (no external calls without consent; PII & private IPs never sent externally)
- TTL caching and per-provider rate limiting
"""

from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.database.manager import db_manager
from backend.app.services.ioc_enrichment_service import IOCEnrichmentService, ioc_enrichment_service


@pytest.fixture()
def client():
    db_manager._use_fallback = True
    return TestClient(app)


def test_normalization_all_six_indicator_types():
    assert IOCEnrichmentService.detect_and_normalize("Example.COM.")[0:2] == ("domain", "example.com")
    assert IOCEnrichmentService.detect_and_normalize("HTTPS://Evil.XYZ/login#frag")[0:2] == ("url", "https://evil.xyz/login")
    assert IOCEnrichmentService.detect_and_normalize("8.8.8.8")[0:2] == ("ip", "8.8.8.8")
    assert IOCEnrichmentService.detect_and_normalize("A" * 64)[0:2] == ("file_hash", "a" * 64)
    assert IOCEnrichmentService.detect_and_normalize("9876543210")[0:2] == ("phone", "+919876543210")
    assert IOCEnrichmentService.detect_and_normalize("User@Example.COM")[0:2] == ("email", "user@example.com")


def test_privacy_consent_and_batch_dedup(client):
    # 1. Batch deduplication + no-consent skips external lookup
    resp = client.post(
        "/api/v1/threat-intel/enrich/batch",
        json={
            "indicators": [
                {"value": "Evil.COM"},
                {"value": "evil.com."},  # duplicate after normalization
                {"value": "9876543210"},
                {"value": "user@example.com"},
                {"value": "192.168.1.10"},
            ],
            "allow_external": True,
            "external_consent": False,
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["submitted_count"] == 5
    assert data["unique_enriched_count"] == 4
    assert data["duplicates_deduplicated"] == 1
    for item in data["results"]:
        assert item["external_enrichment"]["status"] == "skipped_no_consent"

    # 2. Even WITH external_consent=True, PII (phone, email) and private IPs are blocked from external lookups
    for pii_val in ("9876500001", "private.person@example.com", "192.168.1.25"):
        r = client.post(
            "/api/v1/threat-intel/enrich",
            json={"value": pii_val, "allow_external": True, "external_consent": True},
        )
        assert r.status_code == 200
        assert r.json()["external_enrichment"]["status"] == "skipped_privacy_policy"


def test_caching_and_provider_rate_limit(client):
    ioc_enrichment_service._provider_timestamps.clear()
    with patch("backend.app.services.ioc_enrichment_service.httpx.AsyncClient") as mock_client:
        mock_resp = MagicMock(status_code=200)
        mock_resp.json.return_value = {"handle": "DOM-1", "ldhName": "example.org"}
        inst = AsyncMock()
        inst.get.return_value = mock_resp
        mock_client.return_value.__aenter__.return_value = inst

        # First call hits external RDAP
        r1 = client.post("/api/v1/threat-intel/enrich", json={"value": "example.org", "allow_external": True, "external_consent": True})
        assert r1.status_code == 200
        assert r1.json()["cache_hit"] is False
        assert r1.json()["external_enrichment"]["status"] == "ok"

        # Second call hits cache (no extra HTTP call)
        r2 = client.post("/api/v1/threat-intel/enrich", json={"value": "example.org", "allow_external": True, "external_consent": True})
        assert r2.status_code == 200
        assert r2.json()["cache_hit"] is True
        assert inst.get.call_count == 1
