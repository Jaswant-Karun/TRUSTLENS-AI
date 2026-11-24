import urllib.request
import json

base_url = "http://127.0.0.1:8000/api/v1"

def post_json(endpoint, data):
    req = urllib.request.Request(
        f"{base_url}{endpoint}",
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))

# 1. Text test
payload_text = {
    "text": "Aapka SBI khata turant band ho jayega. Urgent verify karein: http://192.168.1.50/sbi-kyc/update.php",
    "channel": "sms",
    "sender": "VK-SBIBNK"
}
try:
    data = post_json("/analyze/text", payload_text)
    print("=== TEXT STATUS === OK")
    print("threat_level:", data.get("threat_level"))
    print("confidence:", data.get("confidence"))
    print("risk_score:", data.get("risk_score"))
    print("text_model:", data.get("text_model"))
    print("url_model:", data.get("url_model"))
    print("tactic_model:", data.get("tactic_model"))
    print("campaign_association:", data.get("campaign_association"))
    print("risk_assessment:", data.get("risk_assessment"))
except Exception as e:
    print("Text error:", e)

# 2. URL test
payload_url = {"url": "http://192.168.1.50/sbi-kyc/update.php"}
try:
    data = post_json("/analyze/url", payload_url)
    print("\n=== URL STATUS === OK")
    print("threat_level:", data.get("threat_level"))
    print("confidence:", data.get("confidence"))
    print("risk_score:", data.get("risk_score"))
    print("url_model keys:", list(data.get("url_model", {}).keys()) if data.get("url_model") else None)
    if data.get("url_model"):
        print("url_model is_phishing:", data["url_model"].get("is_phishing"))
        print("url_model top_risk_factors:", data["url_model"].get("top_risk_factors"))
except Exception as e:
    print("URL error:", e)

# 3. Comprehensive test
payload_comp = {
    "content": "URGENT: Earn 5000 daily part-time job from home! Complete simple tasks. Send deposit to upi@fakebank",
    "url": "http://secure-login-hdfcbank-account-update.xyz/login.php",
    "channel": "whatsapp",
    "sender": "+91 98402 11928"
}
try:
    data = post_json("/analyze/comprehensive", payload_comp)
    print("\n=== COMPREHENSIVE STATUS === OK")
    print("threat_level:", data.get("threat_level"))
    print("confidence:", data.get("confidence"))
    print("risk_score:", data.get("risk_score"))
    print("text_model:", bool(data.get("text_model")))
    print("url_model:", bool(data.get("url_model")))
    print("tactic_model:", bool(data.get("tactic_model")))
    print("campaign_association:", bool(data.get("campaign_association")))
except Exception as e:
    print("Comprehensive error:", e)

# 4. Image test
boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
img_data = open("docs/screenshots/dashboard_intelligence_top.png", "rb").read()
body = (
    f"--{boundary}\r\n"
    f"Content-Disposition: form-data; name=\"file\"; filename=\"test_screenshot.png\"\r\n"
    f"Content-Type: image/png\r\n\r\n"
).encode("utf-8") + img_data + f"\r\n--{boundary}--\r\n".encode("utf-8")

req_img = urllib.request.Request(
    f"{base_url}/analyze/image",
    data=body,
    headers={"Content-Type": f"multipart/form-data; boundary={boundary}"}
)
try:
    with urllib.request.urlopen(req_img) as resp:
        data_img = json.loads(resp.read().decode("utf-8"))
        print("\n=== IMAGE STATUS === OK")
        print("analysis_status:", data_img.get("analysis_status"))
        print("ocr_confidence:", data_img.get("ocr_confidence"))
        print("extracted_text length:", len(data_img.get("extracted_text", "")))
        print("has analysis_result:", bool(data_img.get("analysis_result")))
except Exception as e:
    print("Image test error:", e)
