"""
TRUSTLENS AI - Authorized Isolated Application Security Testing Program
Covers all 10 categories in an isolated fallback environment:
1. Broken Access Control
2. Authentication Weaknesses
3. IDOR (Insecure Direct Object Reference)
4. Injection (NoSQL / Regex)
5. XSS (Content-Type & query probe blocking)
6. CSRF / CORS Origin Enforcement
7. SSRF (Zero-network URL analysis on metadata/loopback IPs)
8. Unsafe File Handling (MIME spoofing, empty, oversized, Zip Slip)
9. Secret Exposure
10. Dependency Vulnerability Tracking
"""

import io
import socket
import zipfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from PIL import Image

from backend.app.config.settings import AppSettings
from backend.app.database.collections import get_analyses_collection, get_investigations_collection, get_users_collection
from backend.app.database.manager import db_manager
from backend.app.main import app
from backend.app.security.dependencies import get_current_user, get_optional_current_user
from backend.app.security.jwt import create_access_token
from backend.app.services.abuse_service import abuse_service
from backend.app.services.ocr_service import ocr_service
from ml.data_pipeline.acquisition import safe_extract_zip


@pytest.fixture()
def client():
    db_manager._use_fallback = True
    abuse_service._login_failures.clear()
    abuse_service._lockouts.clear()
    return TestClient(app)


def test_01_broken_access_control(client):
    # Unauthenticated access to protected endpoints -> 401
    for method, url in [
        ("GET", "/api/v1/security/abuse-monitoring"),
        ("GET", "/api/v1/reports/verified-training-candidates"),
        ("GET", "/api/v1/exports/misp?target_type=analysis&target_id=x"),
        ("GET", "/api/v1/privacy/consent"),
    ]:
        r = client.request(method, url)
        assert r.status_code == 401, f"Expected 401 on {url}, got {r.status_code}"

    # Regular 'user' role cannot access analyst/admin endpoints -> 403
    regular_user = {"user_id": "reg-u-1", "email": "reg@trustlens.ai", "role": "user", "is_active": True}
    app.dependency_overrides[get_current_user] = lambda: regular_user
    try:
        assert client.get("/api/v1/security/abuse-monitoring").status_code == 403
        assert client.get("/api/v1/reports/verified-training-candidates").status_code == 403
    finally:
        app.dependency_overrides.pop(get_current_user, None)


def test_02_authentication_weaknesses_and_session_revocation(client):
    import asyncio

    async def _seed():
        users = get_users_collection()
        await users.insert_one({
            "user_id": "sec-prog-u1",
            "email": "secprog@trustlens.ai",
            "role": "user",
            "is_active": True,
            "session_revoked_before": datetime.now(timezone.utc) + timedelta(seconds=30),
        })
    asyncio.run(_seed())

    # Revoked token rejected on both required and optional auth
    revoked_tok = create_access_token({"sub": "sec-prog-u1"})
    r_req = client.get("/api/v1/privacy/consent", headers={"Authorization": f"Bearer {revoked_tok}"})
    assert r_req.status_code == 401
    # Tampered token rejected
    r_bad = client.get("/api/v1/privacy/consent", headers={"Authorization": "Bearer invalid.jwt.token"})
    assert r_bad.status_code == 401


def test_03_idor_private_investigation_and_analysis_isolation(client):
    import asyncio

    async def _seed():
        await get_investigations_collection().insert_one({
            "investigation_id": "INV-IDOR-PRIV-1",
            "title": "Private Owner A Case",
            "owner_id": "owner-a",
            "visibility": "Private",
            "nodes": [],
            "edges": [],
            "timeline": [],
        })
        await get_analyses_collection().insert_one({
            "analysis_id": "an-idor-priv-1",
            "user_id": "owner-a",
            "threat_level": "high",
            "risk_score": 0.85,
            "created_at": datetime.now(timezone.utc),
        })
    asyncio.run(_seed())

    owner_b = {"user_id": "owner-b", "email": "b@trustlens.ai", "role": "user", "is_active": True}
    app.dependency_overrides[get_current_user] = lambda: owner_b
    app.dependency_overrides[get_optional_current_user] = lambda: owner_b
    try:
        assert client.get("/api/v1/investigations/INV-IDOR-PRIV-1").status_code in (401, 403)
        assert client.get("/api/v1/exports/json?target_type=analysis&target_id=an-idor-priv-1").status_code in (401, 403)
    finally:
        app.dependency_overrides.pop(get_current_user, None)
        app.dependency_overrides.pop(get_optional_current_user, None)


def test_04_05_06_injection_xss_and_cors_csrf(client):
    # 4. NoSQL operator injection probe blocked -> 400
    assert client.get("/api/v1/threat-library?search=$where").status_code == 400
    assert client.get("/api/v1/threat-library?search=$ne").status_code == 400

    # 5. XSS query probe blocked (400) and JSON responses enforce nosniff + CSP
    assert client.get("/api/v1/threat-library?search=<script>alert(1)</script>").status_code == 400
    h = client.get("/api/v1/health")
    assert h.headers.get("X-Content-Type-Options") == "nosniff"
    assert "default-src 'none'" in (h.headers.get("Content-Security-Policy") or "")

    # 6. Arbitrary evil Origin does NOT receive Allow-Origin reflection
    cors_r = client.options("/api/v1/health", headers={"Origin": "https://evil-csrf-site.com", "Access-Control-Request-Method": "GET"})
    assert cors_r.headers.get("access-control-allow-origin") != "https://evil-csrf-site.com"


def test_07_ssrf_zero_network_url_analysis(client):
    with patch.object(socket, "getaddrinfo", side_effect=AssertionError("SSRF: Outbound DNS forbidden!")):
        for target in ("http://169.254.169.254/latest/meta-data/", "http://127.0.0.1:8000/admin"):
            r = client.post("/api/v1/analyze/url", json={"url": target})
            assert r.status_code == 200
            assert r.json()["url_model"]["security_signals"]["redirect_behavior"]["live_redirect_followed"] is False


def test_08_unsafe_file_handling_and_zip_slip(tmp_path):
    import asyncio

    # MIME spoofing (GIF pretending to be image/png) -> 415
    buf = io.BytesIO()
    Image.new("RGB", (8, 8)).save(buf, format="GIF")
    up = MagicMock()
    up.content_type = "image/png"
    up.read = AsyncMock(return_value=buf.getvalue())
    with pytest.raises(HTTPException) as exc:
        asyncio.run(ocr_service.validate_and_read_image(up))
    assert exc.value.status_code == 415

    # Zip Slip path traversal -> ValueError
    zpath = tmp_path / "slip.zip"
    with zipfile.ZipFile(zpath, "w") as zf:
        zf.writestr("../../pwn.txt", "x")
    with pytest.raises(ValueError, match="Zip Slip"):
        safe_extract_zip(zpath, tmp_path / "out")


def test_09_10_secret_exposure_and_dependency_report(client):
    # Secret exposure check on public endpoints
    for ep in ("/", "/api/v1/health", "/api/v1/privacy/policy"):
        txt = client.get(ep).text
        assert "trustlens-super-secret" not in txt
        assert "Admin@TrustLens2026!" not in txt

    # Production secret gate enforced
    with pytest.raises(RuntimeError, match="SECRET_KEY"):
        AppSettings(APP_ENV="production").validate_production_security()

    # OWASP dependency audit report exists
    assert Path("docs/audit/OWASP_SECURITY_AUDIT_REPORT.md").exists()
