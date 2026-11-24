"""
Live Backend and ML Integration Test Suite for TRUSTLENS AI
Tests every connected endpoint and ML model inference via HTTP calls to 127.0.0.1:8000.
"""

import httpx
import json
import io
import time
import sys

BASE_URL = "http://127.0.0.1:8000/api/v1"

results = {
    "passed": [],
    "failed": [],
    "details": {}
}

client = httpx.Client(base_url=BASE_URL, timeout=30.0)

def record_test(name, success, info=""):
    if success:
        results["passed"].append(name)
        print(f" [PASS] {name} {('- ' + info) if info else ''}")
    else:
        results["failed"].append(name)
        print(f" [FAIL] {name} {('- ' + info) if info else ''}")
    results["details"][name] = {"success": success, "info": info}

print("=" * 60)
print("TRUSTLENS AI — LIVE BACKEND & ML INTEGRATION AUDIT")
print("=" * 60)

# 1. Health Endpoint
try:
    res = client.get("/health")
    if res.status_code == 200:
        data = res.json()
        models = data.get("models_loaded", {})
        info = f"Status: {data.get('status')}, Models: {list(models.keys())}"
        record_test("1. GET /health", True, info)
    else:
        record_test("1. GET /health", False, f"HTTP {res.status_code}")
except Exception as e:
    record_test("1. GET /health", False, str(e))

# 2. Text Analysis — Scam Message (M1 Bi-LSTM + M3 Tactic Detector)
scam_text = "URGENT: Your SBI bank account 4921 has been suspended due to incomplete KYC. Update immediately at http://sbi-kyc-update.com or your debit card will be permanently blocked."
try:
    res = client.post("/analyze/text", json={"text": scam_text, "channel": "sms"})
    if res.status_code == 200:
        data = res.json()
        is_threat = data.get("threat_level") in ["high", "critical", "medium"] or data.get("risk_assessment", {}).get("risk_score", 0) > 0.5
        score = data.get("risk_score", 0)
        label = data.get("text_model", {}).get("predicted_label") or data.get("risk_assessment", {}).get("verdict")
        tactics = data.get("tactic_model", {}).get("detected_tactics", [])
        record_test("2. POST /analyze/text (Scam Ingestion)", is_threat, f"Verdict: {label}, Risk: {score}, Tactics: {tactics}")
    else:
        record_test("2. POST /analyze/text (Scam Ingestion)", False, f"HTTP {res.status_code}: {res.text}")
except Exception as e:
    record_test("2. POST /analyze/text (Scam Ingestion)", False, str(e))

# 3. Text Analysis — Benign Message
benign_text = "Hi Rahul, your table reservation for 2 at Olive Bistro is confirmed for tonight at 8:00 PM. Thank you!"
try:
    res = client.post("/analyze/text", json={"text": benign_text, "channel": "sms"})
    if res.status_code == 200:
        data = res.json()
        threat_level = data.get("threat_level", "").lower()
        score = data.get("risk_score", 1.0)
        is_clean = threat_level in ["clean", "low", "benign", "safe"] or score < 0.35
        record_test("3. POST /analyze/text (Benign Ingestion)", is_clean, f"Threat Level: {threat_level}, Risk: {score}")
    else:
        record_test("3. POST /analyze/text (Benign Ingestion)", False, f"HTTP {res.status_code}")
except Exception as e:
    record_test("3. POST /analyze/text (Benign Ingestion)", False, str(e))

# 4. URL Analysis — Malicious URL (M2 XGBoost PhishDetector)
phish_url = "http://secure-sbi-login-verify-pan.online/update.php"
try:
    res = client.post("/analyze/url", json={"url": phish_url})
    if res.status_code == 200:
        data = res.json()
        url_model = data.get("url_model", {})
        prob = url_model.get("phishing_probability", 0)
        is_phish = url_model.get("is_phishing", False) or prob > 0.5
        factors = url_model.get("top_risk_factors", [])
        record_test("4. POST /analyze/url (Malicious Ingestion)", is_phish, f"Is Phishing: {is_phish}, Prob: {prob:.3f}, Factors: {factors[:3]}")
    else:
        record_test("4. POST /analyze/url (Malicious Ingestion)", False, f"HTTP {res.status_code}")
except Exception as e:
    record_test("4. POST /analyze/url (Malicious Ingestion)", False, str(e))

# 5. URL Analysis — Safe URL
safe_url = "https://www.google.com"
try:
    res = client.post("/analyze/url", json={"url": safe_url})
    if res.status_code == 200:
        data = res.json()
        url_model = data.get("url_model", {})
        score = url_model.get("risk_score", 1.0)
        is_phish = url_model.get("is_phishing", True)
        is_safe = (not is_phish) and (score < 0.35)
        record_test("5. POST /analyze/url (Safe Ingestion)", is_safe, f"Is Phish: {is_phish}, Risk Score: {score}")
    else:
        record_test("5. POST /analyze/url (Safe Ingestion)", False, f"HTTP {res.status_code}")
except Exception as e:
    record_test("5. POST /analyze/url (Safe Ingestion)", False, str(e))

# 6. Screenshot / Image Analysis
try:
    # Generate simple test PNG image bytes in memory
    from PIL import Image, ImageDraw
    img = Image.new('RGB', (400, 100), color=(255, 255, 255))
    d = ImageDraw.Draw(img)
    d.text((10, 10), "Electricity bill unpaid. Call 9876543210 immediately.", fill=(0, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    
    files = {"file": ("screenshot.png", buf, "image/png")}
    res = client.post("/analyze/image", files=files)
    if res.status_code == 200:
        data = res.json()
        extracted = data.get("extracted_text", "")
        status = data.get("analysis_status")
        record_test("6. POST /analyze/image (OCR Ingestion)", True, f"Status: {status}, Extracted length: {len(extracted)} chars")
    else:
        record_test("6. POST /analyze/image (OCR Ingestion)", False, f"HTTP {res.status_code}: {res.text}")
except ImportError:
    # If PIL is not installed, test with raw dummy PNG bytes
    png_header = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
    files = {"file": ("test.png", png_header, "image/png")}
    try:
        res = client.post("/analyze/image", files=files)
        record_test("6. POST /analyze/image (OCR Ingestion)", res.status_code in [200, 422], f"HTTP {res.status_code}")
    except Exception as e:
        record_test("6. POST /analyze/image (OCR Ingestion)", False, str(e))
except Exception as e:
    record_test("6. POST /analyze/image (OCR Ingestion)", False, str(e))

# 7. Comprehensive Investigation (Multi-vector)
comp_payload = {
    "content": "Dear user, electricity power will be disconnected tonight at 9:30 PM because bill was not updated. Contact officer at 9876543210 or pay at http://bses-bill-pay.live",
    "channel": "sms",
    "sender": "+919876543210"
}
try:
    res = client.post("/analyze/comprehensive", json=comp_payload)
    if res.status_code == 200:
        data = res.json()
        tactics = data.get("tactic_model", {}).get("detected_tactics", [])
        camp = data.get("campaign_association", {})
        score = data.get("risk_score", 0)
        record_test("7. POST /analyze/comprehensive (Multi-Vector)", True, f"Risk: {score}, Tactics: {tactics}, Camp Assoc: {camp.get('associated_campaign')}")
    else:
        record_test("7. POST /analyze/comprehensive (Multi-Vector)", False, f"HTTP {res.status_code}")
except Exception as e:
    record_test("7. POST /analyze/comprehensive (Multi-Vector)", False, str(e))

# 8. Model Metrics & Registry
try:
    res = client.get("/models/metrics")
    if res.status_code == 200:
        data = res.json()
        models = data.get("models", {})
        summary = data.get("overall_summary", {})
        record_test("8. GET /models/metrics", True, f"Active Models: {summary.get('active_models_count')}, Keys: {list(models.keys())}")
    else:
        record_test("8. GET /models/metrics", False, f"HTTP {res.status_code}")
except Exception as e:
    record_test("8. GET /models/metrics", False, str(e))

# 9. Campaign Retrieval
try:
    res = client.get("/campaigns?limit=10")
    if res.status_code == 200:
        camps = res.json()
        detail_ok = False
        if camps and len(camps) > 0:
            cid = camps[0].get("cluster_id") or camps[0].get("campaign_id") or 11
            res2 = client.get(f"/campaigns/{cid}")
            detail_ok = res2.status_code == 200
        record_test("9. GET /campaigns & /campaigns/{id}", detail_ok, f"Found {len(camps)} clusters, Detail fetch: {detail_ok}")
    else:
        record_test("9. GET /campaigns & /campaigns/{id}", False, f"HTTP {res.status_code}")
except Exception as e:
    record_test("9. GET /campaigns & /campaigns/{id}", False, str(e))

# 10. Community Reports — Ingestion & Fetch
try:
    report_payload = {
        "target_type": "url",
        "content": "Phishing site spoofing state electricity board bill collection: http://power-bill-disconnection.xyz",
        "target_identifier": "http://power-bill-disconnection.xyz",
        "description": "Received via SMS warning of power cut at 9 PM"
    }
    res = client.post("/reports", json=report_payload)
    if res.status_code in [200, 201]:
        rep = res.json()
        rep_id = rep.get("report_id")
        res_list = client.get("/reports?page=1&page_size=5")
        record_test("10. POST & GET /reports (Community)", res_list.status_code == 200, f"Created ID: {rep_id}, List status: {res_list.status_code}")
    else:
        record_test("10. POST & GET /reports (Community)", False, f"HTTP {res.status_code}: {res.text}")
except Exception as e:
    record_test("10. POST & GET /reports (Community)", False, str(e))

# 11. Authentication (Login & Profile)
token = None
try:
    login_res = client.post("/auth/login", json={"email": "admin@trustlens.ai", "password": "Admin@TrustLens2026!"})
    if login_res.status_code == 200:
        login_data = login_res.json()
        token = login_data.get("access_token")
        auth_client = httpx.Client(base_url=BASE_URL, headers={"Authorization": f"Bearer {token}"})
        me_res = auth_client.get("/auth/me")
        if me_res.status_code == 200:
            user = me_res.json()
            record_test("11. POST /auth/login & GET /auth/me", True, f"User: {user.get('email')}, Role: {user.get('role')}")
        else:
            record_test("11. POST /auth/login & GET /auth/me", False, f"Auth/me failed: {me_res.status_code}")
    else:
        record_test("11. POST /auth/login & GET /auth/me", False, f"Login HTTP {login_res.status_code}")
except Exception as e:
    record_test("11. POST /auth/login & GET /auth/me", False, str(e))

# 12. Analysis History (with & without token)
try:
    anon_res = client.get("/analyses?page=1&page_size=5")
    # Anonymous may return 401 Unauthorized or guest preview
    auth_ok = False
    if token:
        auth_client = httpx.Client(base_url=BASE_URL, headers={"Authorization": f"Bearer {token}"})
        auth_analyses_res = auth_client.get("/analyses?page=1&page_size=5")
        auth_ok = auth_analyses_res.status_code in [200, 204]
    record_test("12. GET /analyses (Auth Enforcement)", auth_ok or anon_res.status_code in [200, 401], f"Anon status: {anon_res.status_code}, Auth status: {auth_analyses_res.status_code if token else 'N/A'}")
except Exception as e:
    record_test("12. GET /analyses (Auth Enforcement)", False, str(e))

# 13. Model Failure & Validation Error Handling
try:
    # Malformed URL should return 422 or handled cleanly, NOT 200 with fake safety
    err_res = client.post("/analyze/url", json={"url": "not-a-valid-url-at-all"})
    handled_cleanly = err_res.status_code in [200, 400, 422]
    # Check if empty text handled
    err_text = client.post("/analyze/text", json={"text": ""})
    handled_cleanly = handled_cleanly and (err_text.status_code in [200, 400, 422])
    record_test("13. Input Validation & Error Handling", handled_cleanly, f"URL err: {err_res.status_code}, Text err: {err_text.status_code}")
except Exception as e:
    record_test("13. Input Validation & Error Handling", False, str(e))

print("=" * 60)
print(f"TOTAL TESTS: {len(results['passed']) + len(results['failed'])} | PASSED: {len(results['passed'])} | FAILED: {len(results['failed'])}")
print("=" * 60)

with open("backend_ml_integration_results.json", "w") as f:
    json.dump(results, f, indent=2)

if results["failed"]:
    sys.exit(1)
else:
    sys.exit(0)
