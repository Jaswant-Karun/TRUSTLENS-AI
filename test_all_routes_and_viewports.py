"""
Comprehensive Route & Responsive Testing Suite for TRUSTLENS AI
Tests all 13 routes via HTTP GET and captures screenshots across Desktop, Laptop, Tablet, and Mobile.
"""

import os
import sys
import json
import httpx
import subprocess
import shutil

BASE_URL = "http://localhost:3000"

chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
if not os.path.exists(chrome_path):
    chrome_path = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"

qa_docs_dir = r"c:\Users\jaswant karun\TRUSTLENS AI\docs\screenshots\qa"
qa_art_dir = r"C:\Users\jaswant karun\.gemini\antigravity\brain\ccdc3978-e39e-4041-ac1a-6d43bb2834f7\screenshots\qa"
os.makedirs(qa_docs_dir, exist_ok=True)
os.makedirs(qa_art_dir, exist_ok=True)

routes = [
    {"path": "/", "name": "home_redirect"},
    {"path": "/dashboard", "name": "dashboard"},
    {"path": "/analyze/text", "name": "analyze_text"},
    {"path": "/analyze/url", "name": "analyze_url"},
    {"path": "/analyze/image", "name": "analyze_image"},
    {"path": "/investigation", "name": "investigation"},
    {"path": "/intelligence/tactics", "name": "intel_tactics"},
    {"path": "/intelligence/campaigns", "name": "intel_campaigns"},
    {"path": "/intelligence/threats", "name": "intel_threats"},
    {"path": "/models", "name": "models"},
    {"path": "/history", "name": "history"},
    {"path": "/reports", "name": "reports"},
    {"path": "/settings", "name": "settings"}
]

viewports = [
    {"label": "desktop", "size": "1440,900"},
    {"label": "laptop", "size": "1280,800"},
    {"label": "tablet", "size": "768,1024"},
    {"label": "mobile", "size": "375,667"}
]

results = {
    "http_checks": {},
    "responsive_checks": {},
    "errors": []
}

client = httpx.Client(base_url=BASE_URL, timeout=15.0)

print("=" * 65)
print("TRUSTLENS AI — ROUTE & VIEWPORT QUALITY ASSURANCE AUDIT")
print("=" * 65)

# Part 1: HTTP & Content Validation
for r in routes:
    url = f"{BASE_URL}{r['path']}"
    try:
        res = client.get(r['path'])
        is_ok = res.status_code in [200, 307, 308]
        results["http_checks"][r['path']] = {
            "status_code": res.status_code,
            "success": is_ok,
            "content_length": len(res.text)
        }
        status_str = "PASS" if is_ok else "FAIL"
        print(f"[{status_str}] Route: {r['path']:<26} -> HTTP {res.status_code} ({len(res.text)} bytes)")
    except Exception as e:
        results["http_checks"][r['path']] = {"success": False, "error": str(e)}
        print(f"[FAIL] Route: {r['path']:<26} -> Exception: {e}")
        results["errors"].append(f"{r['path']}: {e}")

# Part 2: Responsive Rendering with Headless Chrome
print("\n" + "-" * 65)
print("RESPONSIVE MULTI-DEVICE RENDERING TEST")
print("-" * 65)

sample_routes = [
    {"path": "/dashboard", "name": "dashboard"},
    {"path": "/analyze/url", "name": "analyze_url"},
    {"path": "/models", "name": "models"},
    {"path": "/reports", "name": "reports"}
]

for sr in sample_routes:
    target_url = f"{BASE_URL}{sr['path']}"
    results["responsive_checks"][sr['name']] = {}
    for vp in viewports:
        img_name = f"{sr['name']}_{vp['label']}.png"
        doc_path = os.path.join(qa_docs_dir, img_name)
        art_path = os.path.join(qa_art_dir, img_name)
        
        cmd = [
            chrome_path,
            "--headless=new",
            "--disable-gpu",
            f"--window-size={vp['size']}",
            "--virtual-time-budget=3000",
            f"--screenshot={doc_path}",
            target_url
        ]
        
        try:
            sub = subprocess.run(cmd, capture_output=True, timeout=25)
            if os.path.exists(doc_path) and os.path.getsize(doc_path) > 1000:
                shutil.copyfile(doc_path, art_path)
                file_size = os.path.getsize(doc_path)
                results["responsive_checks"][sr['name']][vp['label']] = {
                    "success": True,
                    "size_bytes": file_size,
                    "file": img_name
                }
                print(f"[PASS] {sr['name']:<14} @ {vp['label']:<8} ({vp['size']:<9}) -> {file_size} bytes")
            else:
                results["responsive_checks"][sr['name']][vp['label']] = {"success": False, "error": "Empty screenshot"}
                print(f"[FAIL] {sr['name']:<14} @ {vp['label']:<8} -> Failed to generate image")
        except Exception as e:
            results["responsive_checks"][sr['name']][vp['label']] = {"success": False, "error": str(e)}
            print(f"[FAIL] {sr['name']:<14} @ {vp['label']:<8} -> {e}")

with open("route_and_viewport_qa_results.json", "w") as f:
    json.dump(results, f, indent=2)

print("=" * 65)
passed_routes = sum(1 for v in results["http_checks"].values() if v.get("success"))
total_routes = len(routes)
print(f"ROUTE CHECKS: {passed_routes}/{total_routes} PASSED")
passed_responsive = sum(1 for page in results["responsive_checks"].values() for vp in page.values() if vp.get("success"))
total_responsive = len(sample_routes) * len(viewports)
print(f"RESPONSIVE CHECKS: {passed_responsive}/{total_responsive} PASSED")
print("=" * 65)
