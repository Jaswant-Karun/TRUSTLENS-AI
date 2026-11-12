"""
TRUSTLENS AI - Complete Backend Endpoints Test Suite
Validates all required FastAPI endpoints, security controls, models integration, and MongoDB storage.
"""

import io
import pytest
from httpx import ASGITransport, AsyncClient
from PIL import Image

from backend.app.main import app


@pytest.fixture
def test_image_bytes():
    """Generates simple in-memory PNG bytes for screenshot analysis tests."""
    img = Image.new("RGB", (200, 80), color=(255, 255, 255))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


@pytest.mark.asyncio
async def test_auth_full_lifecycle():
    """Tests user registration, login, JWT token issuance, and protected profile access."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Register new user
        reg_payload = {
            "email": "analyst.audit@trustlens.ai",
            "password": "SecurePassword123!",
            "full_name": "Senior SOC Analyst",
            "role": "analyst",
        }
        reg_res = await client.post("/api/v1/auth/register", json=reg_payload)
        assert reg_res.status_code == 201
        reg_data = reg_res.json()
        assert reg_data["email"] == "analyst.audit@trustlens.ai"
        assert reg_data["role"] == "analyst"
        assert "password" not in reg_data

        # 2. Login to receive JWT Bearer Token
        login_payload = {
            "email": "analyst.audit@trustlens.ai",
            "password": "SecurePassword123!",
        }
        login_res = await client.post("/api/v1/auth/login", json=login_payload)
        assert login_res.status_code == 200
        login_data = login_res.json()
        assert "access_token" in login_data
        assert login_data["token_type"] == "bearer"
        token = login_data["access_token"]

        # 3. Access protected /auth/me with Bearer Token
        headers = {"Authorization": f"Bearer {token}"}
        me_res = await client.get("/api/v1/auth/me", headers=headers)
        assert me_res.status_code == 200
        me_data = me_res.json()
        assert me_data["email"] == "analyst.audit@trustlens.ai"
        assert me_data["role"] == "analyst"

        # 4. Access protected /auth/me without token -> 401 Unauthorized
        unauth_res = await client.get("/api/v1/auth/me")
        assert unauth_res.status_code == 401


@pytest.mark.asyncio
async def test_text_analysis_endpoint():
    """Tests POST /api/v1/analyze/text and risk aggregation output."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "text": "FINAL WARNING: Your SBI account has been locked. Click http://sbi-secure.in to update your PAN immediately.",
            "channel": "sms",
            "sender": "VK-SBIBNK",
        }
        res = await client.post("/api/v1/analyze/text", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert "analysis_id" in data
        assert data["analysis_type"] == "text"
        assert data["threat_level"] in ["medium", "high", "critical"]
        assert "risk_assessment" in data
        assert "transparency_breakdown" in data["risk_assessment"]
        assert "extracted_iocs" in data
        assert "explainability" in data


@pytest.mark.asyncio
async def test_url_analysis_endpoint():
    """Tests POST /api/v1/analyze/url zero-hop inspection and SHAP evidence."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {"url": "http://185.220.101.5/banking/login.php?user=admin"}
        res = await client.post("/api/v1/analyze/url", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["analysis_type"] == "url"
        assert data["threat_level"] in ["high", "critical"]
        assert data["url_model"]["is_phishing"] is True
        assert data["url_model"]["risk_score"] > 0.80
        assert "explainability" in data


@pytest.mark.asyncio
async def test_image_screenshot_analysis_endpoint(test_image_bytes):
    """Tests POST /api/v1/analyze/image upload validation and handling."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Valid PNG upload
        files = {"file": ("screenshot.png", test_image_bytes, "image/png")}
        res = await client.post("/api/v1/analyze/image", files=files)
        assert res.status_code == 200
        data = res.json()
        assert "analysis_status" in data
        assert data["analysis_status"] in ["completed", "insufficient-evidence"]
        assert "ocr_confidence" in data

        # Invalid MIME type -> 415 Unsupported Media Type
        bad_files = {"file": ("malware.exe", b"MZ90...", "application/x-msdownload")}
        bad_res = await client.post("/api/v1/analyze/image", files=bad_files)
        assert bad_res.status_code == 415


@pytest.mark.asyncio
async def test_comprehensive_analysis_endpoint():
    """Tests POST /api/v1/analyze/comprehensive multi-vector pipeline."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "content": "Electricity bill unpaid of Rs 3,450. Power disconnection tonight at 9:30 PM. Call 9876543210 immediately.",
            "url": "http://192.168.1.1/pay-bill.php",
            "channel": "sms",
        }
        res = await client.post("/api/v1/analyze/comprehensive", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["threat_level"] in ["medium", "high", "critical"]
        assert data["tactic_model"] is not None
        assert data["tactic_model"]["tactic_count"] >= 1


@pytest.mark.asyncio
async def test_analyses_history_endpoints():
    """Tests GET /api/v1/analyses and GET /api/v1/analyses/{id}."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Login to obtain token
        login_res = await client.post("/api/v1/auth/login", json={"email": "analyst.audit@trustlens.ai", "password": "SecurePassword123!"})
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Trigger an analysis first to populate history
        scan_res = await client.post("/api/v1/analyze/text", json={"text": "Your lottery prize of Rs 25 Lakhs won in KBC lucky draw."}, headers=headers)
        scan_id = scan_res.json()["analysis_id"]

        # 2. List analyses
        history_res = await client.get("/api/v1/analyses", headers=headers)
        assert history_res.status_code == 200
        hist_data = history_res.json()
        assert "items" in hist_data
        assert hist_data["total_count"] >= 1

        # 3. Retrieve single analysis by ID
        detail_res = await client.get(f"/api/v1/analyses/{scan_id}", headers=headers)
        assert detail_res.status_code == 200
        detail_data = detail_res.json()
        assert detail_data["analysis_id"] == scan_id


@pytest.mark.asyncio
async def test_campaign_intelligence_endpoints():
    """Tests GET /api/v1/campaigns and GET /api/v1/campaigns/{id}."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. List campaigns
        res = await client.get("/api/v1/campaigns")
        assert res.status_code == 200
        campaigns = res.json()
        assert isinstance(campaigns, list)
        assert len(campaigns) > 0

        first_cid = campaigns[0]["cluster_id"]

        # 2. Get specific campaign dossier
        dossier_res = await client.get(f"/api/v1/campaigns/{first_cid}")
        assert dossier_res.status_code == 200
        dossier = dossier_res.json()
        assert dossier["cluster_id"] == first_cid
        assert "legal_disclaimer" in dossier


@pytest.mark.asyncio
async def test_model_management_endpoints():
    """Tests GET /api/v1/models, /metrics, and /experiments."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Models Registry
        models_res = await client.get("/api/v1/models")
        assert models_res.status_code == 200
        assert "models" in models_res.json()

        # 2. Metrics
        metrics_res = await client.get("/api/v1/models/metrics")
        assert metrics_res.status_code == 200
        assert "platform" in metrics_res.json()

        # 3. Experiments History
        exp_res = await client.get("/api/v1/models/experiments")
        assert exp_res.status_code == 200
        assert "experiments" in exp_res.json()


@pytest.mark.asyncio
async def test_community_scam_reports_flow():
    """Tests POST /api/v1/reports, GET /api/v1/reports, and POST /api/v1/reports/{id}/review."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Submit scam report
        report_payload = {
            "target_type": "sms",
            "content": "Fake courier message: Parcel on hold due to missing address. Pay Rs 25 at http://indiapost-update.top",
            "target_identifier": "+919876543210",
            "description": "SMS received claiming Indian Post parcel issue.",
        }
        create_res = await client.post("/api/v1/reports", json=report_payload)
        assert create_res.status_code == 201
        report_data = create_res.json()
        report_id = report_data["report_id"]
        assert report_data["status"] == "pending"

        # 2. List reports
        list_res = await client.get("/api/v1/reports")
        assert list_res.status_code == 200
        assert list_res.json()["total_count"] >= 1

        # 3. Review report as Analyst
        login_res = await client.post("/api/v1/auth/login", json={"email": "analyst.audit@trustlens.ai", "password": "SecurePassword123!"})
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        review_payload = {
            "verdict": "verified_scam",
            "notes": "Confirmed postal delivery smishing campaign.",
            "assigned_tactics": ["Urgency", "Financial Manipulation"],
        }
        review_res = await client.post(f"/api/v1/reports/{report_id}/review", json=review_payload, headers=headers)
        assert review_res.status_code == 200
        assert review_res.json()["status"] == "verified_scam"


@pytest.mark.asyncio
async def test_security_headers_and_correlation_id():
    """Verifies that security headers and correlation ID middleware are active."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/")
        assert res.status_code == 200
        assert res.headers.get("X-Content-Type-Options") == "nosniff"
        assert res.headers.get("X-Frame-Options") == "DENY"
        assert "X-Correlation-ID" in res.headers
        assert "X-Process-Time" in res.headers
