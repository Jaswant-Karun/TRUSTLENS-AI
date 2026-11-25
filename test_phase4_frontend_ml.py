import json
import urllib.request

FRONTEND = "http://localhost:3000"
BACKEND = "http://127.0.0.1:8000"

routes = [
    "/analyze/text",
    "/analyze/url",
    "/analyze/image",
    "/investigation",
    "/investigations",
    "/investigations/INV-2026-0011",
    "/models",
    "/dashboard",
]

print("=== 1. FRONTEND ROUTE VERIFICATION ===")
for r in routes:
    res = urllib.request.urlopen(f"{FRONTEND}{r}", timeout=10)
    html = res.read().decode("utf-8")
    assert res.status == 200 and len(html) > 5000
    print(f"  PASS: {r} -> HTTP {res.status} ({len(html):,} bytes)")

print("\n=== 2. FRONTEND PROXY -> FASTAPI ML PARITY ===")
def post_api(base, path, payload):
    req = urllib.request.Request(
        f"{base}/api/v1{path}",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    res = urllib.request.urlopen(req, timeout=15)
    return res.status, json.loads(res.read().decode("utf-8"))

for path, payload in [
    ("/analyze/text", {"text": "URGENT: Your SBI KYC expired today. Update at http://sbi-kyc.xyz", "channel": "sms"}),
    ("/analyze/url", {"url": "http://192.168.1.50:8080/sbi-kyc/update.php"}),
    ("/analyze/comprehensive", {"content": "Earn Rs 5000 daily liking YouTube videos!", "channel": "whatsapp"}),
]:
    st_f, res_f = post_api(FRONTEND, path, payload)
    st_b, res_b = post_api(BACKEND, path, payload)
    assert st_f == 200 and st_b == 200
    assert res_f["threat_level"] == res_b["threat_level"]
    print(f"  PASS: {path} -> Proxy & Backend match (threat_level={res_f['threat_level']}, risk={res_f['risk_score']})")

print("\nALL PHASE 4.0 INTEGRATION CHECKS PASSED!")
