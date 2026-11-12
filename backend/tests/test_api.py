"""
TRUSTLENS AI - Backend API Integration & Health Tests
"""

import pytest
from httpx import ASGITransport, AsyncClient
from backend.app.main import app


@pytest.mark.asyncio
async def test_root_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["platform"] == "TRUSTLENS AI"
    assert "tagline" in data
    assert data["health"] == "/api/v1/health"


@pytest.mark.asyncio
async def test_health_check_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "models_loaded" in data
    assert isinstance(data["models_loaded"], dict)


@pytest.mark.asyncio
async def test_url_scan_feature_extraction():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {"url": "http://192.168.1.1/secure-login-kyc/update.php?id=99281"}
        response = await client.post("/api/v1/urls/scan", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "features" in data
    features = data["features"]
    assert features["has_ip_address"] is True
    assert features["has_suspicious_keywords"] is True
    assert "url_entropy" in features
    assert "domain_entropy" in features


@pytest.mark.asyncio
async def test_text_scan_multilingual():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Hindi / Hinglish urgent message
        payload = {"text": "Aapka SBI khata turant band ho jayega, KYC update karein immediately"}
        response = await client.post("/api/v1/scans/text", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "predicted_label" in data
    assert "detected_language" in data
    assert data["detected_language"] in ["Hinglish (Romanized Hindi)", "English", "Hindi (Devanagari)"]


@pytest.mark.asyncio
async def test_tactic_detection():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {"text": "URGENT: Submit your OTP within 24 hours to prevent SBI account blocked"}
        response = await client.post("/api/v1/tactics/scan", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "tactics" in data
    assert data["tactic_count"] >= 1


@pytest.mark.asyncio
async def test_composite_scan():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "content": "Dear customer, your bank account is suspended. Verify immediately at http://192.168.1.1/kyc",
            "channel": "sms"
        }
        response = await client.post("/api/v1/scans/composite", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "scan_id" in data
    assert data["detected_type"] == "text"
    assert data["url_analysis"] is not None
    assert data["tactics_analysis"] is not None

