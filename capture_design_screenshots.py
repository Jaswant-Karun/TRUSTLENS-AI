import subprocess
import os
import shutil

chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
artifact_dir = r"C:\Users\jaswant karun\.gemini\antigravity\brain\ccdc3978-e39e-4041-ac1a-6d43bb2834f7\screenshots"
docs_dir = r"c:\Users\jaswant karun\TRUSTLENS AI\docs\screenshots"

os.makedirs(artifact_dir, exist_ok=True)
os.makedirs(docs_dir, exist_ok=True)

targets = [
    {"name": "route_dashboard.png", "url": "http://localhost:3000/dashboard", "size": "1440,1100"},
    {"name": "route_analyze_text.png", "url": "http://localhost:3000/analyze/text", "size": "1440,1100"},
    {"name": "route_analyze_url.png", "url": "http://localhost:3000/analyze/url", "size": "1440,1100"},
    {"name": "route_analyze_image.png", "url": "http://localhost:3000/analyze/image", "size": "1440,1100"},
    {"name": "route_investigation.png", "url": "http://localhost:3000/investigation", "size": "1440,1100"},
    {"name": "route_intelligence_tactics.png", "url": "http://localhost:3000/intelligence/tactics", "size": "1440,1100"},
    {"name": "route_intelligence_campaigns.png", "url": "http://localhost:3000/intelligence/campaigns", "size": "1440,1100"},
    {"name": "route_intelligence_threats.png", "url": "http://localhost:3000/intelligence/threats", "size": "1440,1100"},
    {"name": "route_models.png", "url": "http://localhost:3000/models", "size": "1440,1100"},
    {"name": "route_history.png", "url": "http://localhost:3000/history", "size": "1440,1100"},
    {"name": "route_reports.png", "url": "http://localhost:3000/reports", "size": "1440,1100"},
    {"name": "route_settings.png", "url": "http://localhost:3000/settings", "size": "1440,1100"},
]

for t in targets:
    doc_out = os.path.join(docs_dir, t["name"])
    art_out = os.path.join(artifact_dir, t["name"])
    
    cmd = [
        chrome_path,
        "--headless=new",
        "--disable-gpu",
        f"--window-size={t['size']}",
        "--virtual-time-budget=3000",
        f"--screenshot={doc_out}",
        t["url"]
    ]
    
    print(f"Capturing {t['name']} from {t['url']}...")
    try:
        subprocess.run(cmd, check=True, timeout=20)
        if os.path.exists(doc_out):
            shutil.copyfile(doc_out, art_out)
            print(f"Saved: {doc_out} ({os.path.getsize(doc_out)} bytes)")
    except Exception as e:
        print(f"Error capturing {t['name']}: {e}")

print("Multi-page screenshot suite captured successfully!")
