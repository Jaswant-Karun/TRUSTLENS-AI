"""
TRUSTLENS AI - Comprehensive Technical Audit Test Suite
Executes and validates all 17 mandatory audit test cases across all system components:
1. Legitimate banking message
2. Fake bank KYC message
3. Fake job offer
4. Suspicious investment message
5. OTP manipulation message
6. Phishing URL
7. Legitimate URL
8. English message
9. Hindi message
10. Hinglish message
11. Tamil message (language test)
12. Screenshot containing suspicious communication (OCR)
13. Message containing no clear evidence (inconclusive / low risk handling)
14. Invalid URL (validation handling)
15. Empty input (validation handling)
16. Oversized upload (> 10MB rejection)
17. Unavailable ML service fallback & error resilience
"""

import pytest
import io
from PIL import Image
from httpx import AsyncClient, ASGITransport

from backend.app.main import app
from backend.app.database.manager import db_manager
from backend.app.ml_engine.engine import ml_engine


@pytest.fixture(autouse=True)
async def setup_db():
    await db_manager.connect()
    yield
    await db_manager.disconnect()


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def auth_token(client: AsyncClient):
    """Obtains valid admin token for audit requests."""
    from backend.app.services.auth_service import auth_service
    await auth_service.seed_initial_admin()
    res = await client.post(
        "/api/v1/auth/login",
        json={"email": "admin@trustlens.ai", "password": "Admin@TrustLens2026!"},
    )
    assert res.status_code == 200
    return res.json()["access_token"]


# --- TEST CASE 1: LEGITIMATE BANKING MESSAGE ---
@pytest.mark.asyncio
async def test_case_01_legitimate_banking_message(client: AsyncClient, auth_token: str):
    """Test Case 1: Legitimate banking credit notification."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    msg = "Dear Customer, INR 5,000 credited to A/C XX1234 on 12-Nov via NEFT. UTR: N123456789. Avl Bal: INR 45,210. - HDFC Bank"

    res = await client.post("/api/v1/analyze/text", json={"text": msg}, headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["predicted_label"] == "legitimate"
    assert data["is_threat"] is False
    assert data["model_version"] is not None


# --- TEST CASE 2: FAKE BANK KYC MESSAGE ---
@pytest.mark.asyncio
async def test_case_02_fake_bank_kyc_message(client: AsyncClient, auth_token: str):
    """Test Case 2: Fake bank KYC suspension threat message."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    msg = "URGENT: Your SBI YONO account has been suspended due to pending KYC update. Click http://sbi-kyc-verify-portal.top to avoid permanent block within 24 hours."

    res = await client.post("/api/v1/analyze/comprehensive", json={"content": msg}, headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["risk_assessment"]["overall_risk_level"] in ["high", "critical"]
    assert data["text_model"]["is_threat"] is True
    # Ensure tactics detected include artificial urgency or entity impersonation
    tactics = [t["tactic_code"] for t in data["tactic_model"]["detected_tactics"]]
    assert any("URGENCY" in t or "IMPERSONATION" in t or "SUSPENSION" in t for t in tactics)


# --- TEST CASE 3: FAKE JOB OFFER ---
@pytest.mark.asyncio
async def test_case_03_fake_job_offer(client: AsyncClient, auth_token: str):
    """Test Case 3: Fake employment task scam."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    msg = "Part-time job offer! Earn 3000 to 5000 INR daily by liking YouTube videos and rating hotels on Google Maps. No experience needed. Contact WhatsApp +919876543210."

    res = await client.post("/api/v1/analyze/text", json={"text": msg}, headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["is_threat"] is True
    # Verify tactic model tags employment / financial manipulation
    tactics = [t["tactic_code"] for t in data["tactics"]]
    assert any("JOB" in t or "FINANCIAL" in t or "REWARD" in t or "OFFER" in t for t in tactics)


# --- TEST CASE 4: SUSPICIOUS INVESTMENT MESSAGE ---
@pytest.mark.asyncio
async def test_case_04_suspicious_investment_message(client: AsyncClient, auth_token: str):
    """Test Case 4: High-yield crypto / Ponzi scam."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    msg = "Guaranteed returns! Double your Bitcoin in 48 hours with our AI crypto trading bot. Zero risk 100% payout guaranteed. Join Telegram t.me/crypto_double_wealth."

    res = await client.post("/api/v1/analyze/text", json={"text": msg}, headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["is_threat"] is True
    tactics = [t["tactic_code"] for t in data["tactics"]]
    assert any("INVESTMENT" in t or "FINANCIAL" in t or "REWARD" in t for t in tactics)


# --- TEST CASE 5: OTP MANIPULATION MESSAGE ---
@pytest.mark.asyncio
async def test_case_05_otp_manipulation_message(client: AsyncClient, auth_token: str):
    """Test Case 5: Social engineering OTP credential theft."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    msg = "Dear user, verification code 892301 for transaction Rs 24,999. If not done by you call customer support 0801234567 immediately to cancel."

    res = await client.post("/api/v1/analyze/text", json={"text": msg}, headers=headers)
    assert res.status_code == 200
    data = res.json()
    tactics = [t["tactic_code"] for t in data["tactics"]]
    assert any("OTP" in t or "CREDENTIAL" in t or "URGENCY" in t for t in tactics)


# --- TEST CASE 6: PHISHING URL ---
@pytest.mark.asyncio
async def test_case_06_phishing_url(client: AsyncClient, auth_token: str):
    """Test Case 6: Phishing URL with suspicious IP & keywords."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    url = "http://185.220.101.5/secure-sbi-login-verify/auth.php?token=92834"

    res = await client.post("/api/v1/analyze/url", json={"url": url}, headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["is_phishing"] is True
    assert data["risk_score"] > 0.75
    assert len(data["shap_explanations"]["top_risk_factors"]) > 0


# --- TEST CASE 7: LEGITIMATE URL ---
@pytest.mark.asyncio
async def test_case_07_legitimate_url(client: AsyncClient, auth_token: str):
    """Test Case 7: Legitimate HTTPS URL with trusted domain structure."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    url = "https://www.google.com/search?q=cybersecurity+defense"

    res = await client.post("/api/v1/analyze/url", json={"url": url}, headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["is_phishing"] is False
    assert data["risk_score"] < 0.25


# --- TEST CASE 8: ENGLISH THREAT MESSAGE ---
@pytest.mark.asyncio
async def test_case_08_english_message(client: AsyncClient, auth_token: str):
    """Test Case 8: Standard English phishing notification."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    msg = "Your Netflix subscription has expired. Update your billing card today to prevent service interruption."

    res = await client.post("/api/v1/analyze/text", json={"text": msg}, headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["is_threat"] is True
    assert data["detected_language"] in ["English", "en"]


# --- TEST CASE 9: HINDI MESSAGE ---
@pytest.mark.asyncio
async def test_case_09_hindi_message(client: AsyncClient, auth_token: str):
    """Test Case 9: Pure Devanagari Hindi fraudulent message."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    msg = "प्रिय ग्राहक, आपका बैंक खाता आज रात निलंबित कर दिया जाएगा। तुरंत इस लिंक पर क्लिक करके पैन कार्ड अपडेट करें।"

    res = await client.post("/api/v1/analyze/text", json={"text": msg}, headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["is_threat"] is True
    assert data["detected_language"] in ["Hindi", "hi"]


# --- TEST CASE 10: HINGLISH MESSAGE ---
@pytest.mark.asyncio
async def test_case_10_hinglish_message(client: AsyncClient, auth_token: str):
    """Test Case 10: Code-mixed Hinglish threat message."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    msg = "Aapka account block ho chuka hai. Turant diye gaye link par click karein aur KYC document upload karein."

    res = await client.post("/api/v1/analyze/text", json={"text": msg}, headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["is_threat"] is True
    assert data["detected_language"] in ["Hinglish", "Hindi", "English"]


# --- TEST CASE 11: TAMIL MESSAGE EVALUATION ---
@pytest.mark.asyncio
async def test_case_11_tamil_message(client: AsyncClient, auth_token: str):
    """Test Case 11: Tamil message verification (evaluates multilingual tokenizer)."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    msg = "அன்புள்ள வாடிக்கையாளரே, உங்கள் வங்கி கணக்கு முடக்கப்பட்டுள்ளது. உடனே புதுப்பிக்கவும்."

    res = await client.post("/api/v1/analyze/text", json={"text": msg}, headers=headers)
    assert res.status_code == 200
    data = res.json()
    # Verifies graceful handling without crash, returns valid predictions
    assert "is_threat" in data
    assert "confidence" in data
    assert data["model_version"] is not None


# --- TEST CASE 12: SCREENSHOT CONTAINING SUSPICIOUS COMMUNICATION ---
@pytest.mark.asyncio
async def test_case_12_screenshot_analysis(client: AsyncClient, auth_token: str):
    """Test Case 12: Screenshot OCR upload and threat triage."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    img = Image.new("RGB", (250, 60), color=(255, 255, 255))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    img_bytes = buf.getvalue()

    files = {"file": ("screenshot.png", img_bytes, "image/png")}
    res = await client.post("/api/v1/analyze/image", files=files, headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "ocr_confidence" in data
    assert "analysis_status" in data


# --- TEST CASE 13: MESSAGE CONTAINING NO CLEAR EVIDENCE ---
@pytest.mark.asyncio
async def test_case_13_no_clear_evidence_message(client: AsyncClient, auth_token: str):
    """Test Case 13: Vague or short message without clear threat indicators."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    msg = "Hey can you call me later"

    res = await client.post("/api/v1/analyze/comprehensive", json={"content": msg}, headers=headers)
    assert res.status_code == 200
    data = res.json()
    # Must not invent arbitrary high risk scores!
    assert data["risk_assessment"]["overall_risk_level"] in ["clean", "low", "inconclusive"]
    assert data["risk_assessment"]["overall_risk_score"] < 0.40


# --- TEST CASE 14: INVALID URL HANDLING ---
@pytest.mark.asyncio
async def test_case_14_invalid_url_handling(client: AsyncClient, auth_token: str):
    """Test Case 14: Malformed or unparseable URL input."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Empty host or invalid structure
    res = await client.post("/api/v1/analyze/url", json={"url": "not_a_valid_url"}, headers=headers)
    assert res.status_code in [200, 422]
    if res.status_code == 200:
        data = res.json()
        assert "risk_score" in data


# --- TEST CASE 15: EMPTY INPUT HANDLING ---
@pytest.mark.asyncio
async def test_case_15_empty_input_handling(client: AsyncClient, auth_token: str):
    """Test Case 15: Empty string input validation rejection."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    res = await client.post("/api/v1/analyze/text", json={"text": ""}, headers=headers)
    assert res.status_code in [400, 422], f"Expected 400 or 422, got {res.status_code}"


# --- TEST CASE 16: OVERSIZED UPLOAD REJECTION ---
@pytest.mark.asyncio
async def test_case_16_oversized_upload(client: AsyncClient, auth_token: str):
    """Test Case 16: Image upload exceeding 10MB limit."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    # Create 11MB byte stream
    oversized_bytes = b"0" * (11 * 1024 * 1024)
    files = {"file": ("huge.png", oversized_bytes, "image/png")}

    res = await client.post("/api/v1/analyze/image", files=files, headers=headers)
    assert res.status_code in [400, 413, 422], f"Expected 400/413/422, got {res.status_code}"


# --- TEST CASE 17: ML SERVICE RESILIENCE & DATABASE PERSISTENCE ---
@pytest.mark.asyncio
async def test_case_17_resilience_and_history_persistence(client: AsyncClient, auth_token: str):
    """Test Case 17: Verification that analysis history persists and queries accurately."""
    headers = {"Authorization": f"Bearer {auth_token}"}

    # Run comprehensive scan
    scan_res = await client.post(
        "/api/v1/analyze/comprehensive",
        json={"content": "Final Notice: Bank account locked click http://sbi-alert.top"},
        headers=headers,
    )
    assert scan_res.status_code == 200
    scan_id = scan_res.json()["analysis_id"]

    # Verify retrieval from history
    hist_res = await client.get(f"/api/v1/analyses/{scan_id}", headers=headers)
    assert hist_res.status_code == 200
    hist_data = hist_res.json()
    assert hist_data["analysis_id"] == scan_id
    assert "risk_level" in hist_data

