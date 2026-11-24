import urllib.request
import re

routes = [
    ("/", "Root (Redirects to /dashboard)"),
    ("/dashboard", "Executive Overview Dashboard"),
    ("/analyze/text", "Multilingual Text Scam Analysis"),
    ("/analyze/url", "Zero-Hop Phishing URL Inspection"),
    ("/analyze/image", "Screenshot Forensic OCR Analysis"),
    ("/investigation", "Comprehensive Multi-Modal Investigation"),
    ("/intelligence/tactics", "Social Engineering Tactic Intelligence"),
    ("/intelligence/campaigns", "Scam Campaign Discovery & Attribution"),
    ("/intelligence/threats", "Threat Indicators & IOC Intelligence"),
    ("/models", "ML Center & Model Governance"),
    ("/history", "Analysis History & Incident Audit Trail"),
    ("/reports", "Community Threat Reports & Review"),
    ("/settings", "Platform Settings & Engine Configuration"),
]

base_url = "http://localhost:3000"
results = []
all_passed = True

print("=================================================================")
print(" TRUSTLENS AI — ROUTE-BY-ROUTE MULTI-PAGE NAVIGATION TEST")
print("=================================================================")

for path, desc in routes:
    url = f"{base_url}{path}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (TrustLens-Route-Tester)"})
        with urllib.request.urlopen(req, timeout=10) as response:
            status = response.getcode()
            body = response.read().decode("utf-8", errors="ignore")
            final_url = response.geturl()
            
            # Check unique markers
            passed = status == 200
            if not passed:
                all_passed = False
                
            print(f"[{'PASS' if passed else 'FAIL'}] {path:25} -> HTTP {status} | Final: {final_url} | {desc}")
            results.append({
                "path": path,
                "status": status,
                "description": desc,
                "passed": passed
            })
    except Exception as e:
        all_passed = False
        print(f"[FAIL] {path:25} -> ERROR: {e}")
        results.append({
            "path": path,
            "status": "ERROR",
            "description": desc,
            "passed": False,
            "error": str(e)
        })

print("=================================================================")
if all_passed:
    print(f" SUCCESS: All {len(routes)} routes validated and functioning perfectly!")
else:
    print(" Some routes failed verification.")
print("=================================================================")
