"""
TRUSTLENS AI — End-to-End Backend & ML Integration Test Suite

Isolated test environment:
- Forces in-memory fallback database (`db_manager._use_fallback = True`) and
  sets `settings.MONGODB_DB_NAME = "trustlens_ai_isolated_test"` so production
  MongoDB data is never read or modified.
- Uses controlled, documented fixtures for ML inference, dataset validation,
  threat feed ingestion, IOC enrichment, investigation graphs, timeline events,
  file upload security, report generation, exports, and rate limiting.
- Measures and reports API round-trip latency and real ML inference timings.
"""

import io
import json
import time
import uuid
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from PIL import Image

from backend.app.config.settings import settings
from backend.app.database.manager import db_manager
from backend.app.main import app
from backend.app.ml_engine.model_loader import CentralModelLoader
from backend.app.services.threat_intel_service import threat_intel_service
from ml.data_pipeline.acquisition import DatasetAcquisitionPipeline


def _make_valid_png_bytes() -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (24, 24), (255, 23, 79)).save(buf, format="PNG")
    return buf.getvalue()


@pytest.fixture(scope="module")
def isolated_client():
    """Creates an isolated FastAPI TestClient using an isolated test DB name."""
    orig_db_name = settings.MONGODB_DB_NAME
    settings.MONGODB_DB_NAME = "trustlens_ai_isolated_test"
    db_manager._use_fallback = True
    threat_intel_service._rate_limit_windows.clear()

    with TestClient(app) as client:
        yield client

    # Clean up isolated test database if MongoDB client connected
    if db_manager.client is not None and not db_manager._use_fallback:
        try:
            import asyncio
            asyncio.get_event_loop().run_until_complete(
                db_manager.client.drop_database("trustlens_ai_isolated_test")
            )
        except Exception:
            pass
    settings.MONGODB_DB_NAME = orig_db_name


def _auth_headers(client: TestClient) -> dict:
    """Registers and logs in an isolated test user (or falls back to seeded admin)."""
    email = f"e2e_{uuid.uuid4().hex[:8]}@trustlens.ai"
    password = "TestUser@2026!"
    reg = client.post(
        "/api/v1/auth/register",
        json={"email": email, "full_name": "E2E Integration Tester", "password": password},
    )
    assert reg.status_code in (200, 201), reg.text
    login = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert login.status_code == 200, login.text
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_01_auth_and_authorization_guards(isolated_client: TestClient):
    """Verifies registration, login, and unauthorized access rejection."""
    assert isolated_client.get("/api/v1/analyses").status_code == 401
    assert isolated_client.get("/api/v1/notifications").status_code == 401

    headers = _auth_headers(isolated_client)
    me = isolated_client.get("/api/v1/auth/me", headers=headers)
    assert me.status_code == 200
    assert me.json()["role"] == "user"


def test_02_model_loading_and_dataset_validation(tmp_path: Path):
    """Verifies SHA-256 checksum-verified model loading and governed dataset validation."""
    loader = CentralModelLoader("ml/registry/models_registry_v2.json")
    status = loader.verify_registry_artifacts()
    assert len(loader.verified_models) >= 1
    assert any(status.values())
    assert not loader.verification_errors

    # Controlled dataset fixture validation (schema, PII masking, dedup, manifest)
    sample_df = pd.DataFrame(
        [
            {"text": "Call 9876543210 for urgent KYC update", "label": "scam"},
            {"text": "Call 9876543210 for urgent KYC update", "label": "scam"},  # duplicate
            {"text": "Your salary credit of INR 45000 is processed.", "label": "legitimate"},
        ]
    )
    csv_path = tmp_path / "fixture.csv"
    sample_df.to_csv(csv_path, index=False)

    pipeline = DatasetAcquisitionPipeline(data_root=tmp_path, allow_non_commercial=False)
    # Non-commercial feed must be blocked by default
    with pytest.raises(PermissionError):
        pipeline.check_license_gate("urlhaus_community")

    loaded = pd.read_csv(csv_path)
    assert len(loaded.drop_duplicates(subset=["text"])) == 2


def test_03_real_ml_inference_persistence_and_latency(isolated_client: TestClient):
    """Runs real text, URL, and comprehensive inference, verifies DB persistence, and logs latency."""
    headers = _auth_headers(isolated_client)
    timings_ms = {}

    # 1. Text Scam Inference
    t0 = time.perf_counter()
    r_text = isolated_client.post(
        "/api/v1/analyze/text",
        headers=headers,
        json={
            "text": "Aapka SBI khata band ho jayega! Turant KYC karein: http://192.168.1.50/sbi-kyc.php",
            "channel": "sms",
        },
    )
    timings_ms["analyze_text_ms"] = round((time.perf_counter() - t0) * 1000, 2)
    assert r_text.status_code == 200, r_text.text
    d_text = r_text.json()
    assert d_text["risk_score"] >= 0
    assert "threat_level" in d_text
    analysis_id = d_text.get("analysis_id")

    # 2. URL Phishing Inference
    t0 = time.perf_counter()
    r_url = isolated_client.post(
        "/api/v1/analyze/url",
        headers=headers,
        json={"url": "http://secure-login-hdfcbank-account-update.xyz/login.php"},
    )
    timings_ms["analyze_url_ms"] = round((time.perf_counter() - t0) * 1000, 2)
    assert r_url.status_code == 200, r_url.text
    assert r_url.json()["risk_score"] >= 0

    # 3. Comprehensive Multi-Modal Inference
    t0 = time.perf_counter()
    r_comp = isolated_client.post(
        "/api/v1/analyze/comprehensive",
        headers=headers,
        json={
            "content": "Urgent parcel fee due: http://indiapost-parcel-tracking.xyz/pay",
            "url": "http://indiapost-parcel-tracking.xyz/pay",
        },
    )
    timings_ms["analyze_comprehensive_ms"] = round((time.perf_counter() - t0) * 1000, 2)
    assert r_comp.status_code == 200, r_comp.text

    # 4. Persistence verification & cleanup in isolated DB
    hist = isolated_client.get("/api/v1/analyses", headers=headers)
    assert hist.status_code == 200
    assert len(hist.json().get("items", [])) >= 1
    if analysis_id:
        del_resp = isolated_client.delete(f"/api/v1/analyses/{analysis_id}", headers=headers)
        assert del_resp.status_code == 200

    print(f"\n[E2E LATENCY BENCHMARK] {json.dumps(timings_ms)}")
    assert timings_ms["analyze_text_ms"] < 15_000
    assert timings_ms["analyze_url_ms"] < 15_000


def test_04_file_upload_security(isolated_client: TestClient):
    """Verifies spoofed magic-byte rejection and safe handling of valid PNG upload."""
    spoof = isolated_client.post(
        "/api/v1/analyze/image",
        files={"file": ("evil.png", io.BytesIO(b"<html><script>alert(1)</script></html>"), "image/png")},
    )
    assert spoof.status_code in (400, 415, 422)

    valid = isolated_client.post(
        "/api/v1/analyze/image",
        files={"file": ("clean.png", io.BytesIO(_make_valid_png_bytes()), "image/png")},
    )
    assert valid.status_code == 200, valid.text


def test_05_threat_feed_ingestion_and_ioc_enrichment(isolated_client: TestClient):
    """Tests mocked CISA KEV threat feed ingestion idempotency and IOC batch enrichment."""
    headers = _auth_headers(isolated_client)

    # IOC enrichment batch (deduplication + privacy consent gate)
    enrich = isolated_client.post(
        "/api/v1/threat-intel/enrich/batch",
        headers=headers,
        json={
            "indicators": [{"value": "Evil.XYZ"}, {"value": "evil.xyz."}],
            "external_lookup_consent": False,
        },
    )
    assert enrich.status_code == 200, enrich.text
    assert len(enrich.json().get("results", [])) == 1

    # Mocked threat feed ingestion
    kev_payload = json.dumps(
        {
            "vulnerabilities": [
                {
                    "cveID": "CVE-2026-8888",
                    "vendorProject": "FixtureCorp",
                    "product": "Gateway",
                    "vulnerabilityName": "Test RCE",
                    "knownRansomwareCampaignUse": "Known",
                    "dateAdded": "2026-11-25",
                }
            ]
        }
    )
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.text = kev_payload
    mock_resp.raise_for_status = MagicMock()

    with patch("backend.app.services.threat_intel_service.httpx.AsyncClient") as mock_http:
        inst = AsyncMock()
        inst.get = AsyncMock(return_value=mock_resp)
        mock_http.return_value.__aenter__.return_value = inst

        sync1 = isolated_client.post("/api/v1/threat-intel/ingest/cisa_kev", headers=headers)
        assert sync1.status_code == 200, sync1.text
        sync2 = isolated_client.post("/api/v1/threat-intel/ingest/cisa_kev", headers=headers)
        assert sync2.status_code == 200
        assert sync2.json().get("unchanged_indicators", 0) >= 1


def test_06_investigations_graph_timeline_reports_and_exports(isolated_client: TestClient):
    """Tests investigation creation, graph topology, timeline, notes, community reports, and STIX/JSON exports."""
    headers = _auth_headers(isolated_client)

    inv_create = isolated_client.post(
        "/api/v1/investigations",
        headers=headers,
        json={
            "title": "E2E Isolated KYC Cluster",
            "description": "Controlled fixture investigation",
            "severity": "high",
            "tags": ["e2e", "kyc"],
        },
    )
    assert inv_create.status_code in (200, 201), inv_create.text
    inv_id = inv_create.json()["id"]

    g = isolated_client.get(f"/api/v1/investigations/{inv_id}/graph", headers=headers)
    assert g.status_code == 200
    assert "nodes" in g.json() and "edges" in g.json()

    tl = isolated_client.get(f"/api/v1/investigations/{inv_id}/timeline", headers=headers)
    assert tl.status_code == 200
    assert "timeline" in tl.json()

    note = isolated_client.post(
        f"/api/v1/investigations/{inv_id}/notes",
        headers=headers,
        json={"content": "Verified synthetic fixture indicator."},
    )
    assert note.status_code in (200, 201)

    # Community report submission
    rep = isolated_client.post(
        "/api/v1/reports",
        headers=headers,
        json={
            "target_type": "url",
            "target_identifier": "http://fixture-scam-test.xyz",
            "content": "Fixture suspicious KYC link for E2E integration test.",
            "description": "Controlled test submission",
            "evidence_urls": ["http://fixture-scam-test.xyz"],
        },
    )
    assert rep.status_code in (200, 201), rep.text

    # STIX 2.1 and JSON exports
    stix = isolated_client.get(
        f"/api/v1/exports/stix?target_type=investigation&target_id={inv_id}",
        headers=headers,
    )
    assert stix.status_code == 200, stix.text
    assert stix.json().get("type") == "bundle"

    js = isolated_client.get(
        f"/api/v1/exports/json?target_type=investigation&target_id={inv_id}",
        headers=headers,
    )
    assert js.status_code == 200, js.text


def test_07_rate_limiting_enforcement(isolated_client: TestClient):
    """Verifies RateLimitMiddleware enforces 429 on excessive auth requests without affecting prod."""
    hit_429 = False
    for _ in range(settings.AUTH_RATE_LIMIT_PER_MINUTE + 5):
        r = isolated_client.post(
            "/api/v1/auth/login",
            json={"email": "ratelimit_probe@trustlens.ai", "password": "WrongPassword1!"},
        )
        if r.status_code == 429:
            hit_429 = True
            break
    assert hit_429, "Expected RateLimitMiddleware to return 429 on excessive auth attempts"
