import subprocess
import os
import shutil

chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
if not os.path.exists(chrome_path):
    chrome_path = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"

artifact_dir = r"C:\Users\jaswant karun\.gemini\antigravity\brain\ccdc3978-e39e-4041-ac1a-6d43bb2834f7\screenshots"
docs_dir = r"c:\Users\jaswant karun\TRUSTLENS AI\docs\screenshots"

os.makedirs(artifact_dir, exist_ok=True)
os.makedirs(docs_dir, exist_ok=True)

targets = [
    {"name": "dashboard_intelligence_top.png", "url": "http://localhost:3000/dashboard", "size": "1440,1100"},
    {"name": "dashboard_intelligence_full.png", "url": "http://localhost:3000/dashboard", "size": "1440,2400"},
    {"name": "route_dashboard.png", "url": "http://localhost:3000/dashboard", "size": "1440,1100"},
]

for t in targets:
    doc_out = os.path.join(docs_dir, t["name"])
    art_out = os.path.join(artifact_dir, t["name"])
    
    cmd = [
        chrome_path,
        "--headless=new",
        "--disable-gpu",
        f"--window-size={t['size']}",
        "--virtual-time-budget=4000",
        f"--screenshot={doc_out}",
        t["url"]
    ]
    
    print(f"Capturing {t['name']} from {t['url']}...")
    try:
        subprocess.run(cmd, check=True, timeout=25)
        if os.path.exists(doc_out):
            shutil.copyfile(doc_out, art_out)
            print(f"Saved: {doc_out} ({os.path.getsize(doc_out)} bytes)")
        else:
            print(f"Warning: {doc_out} was not generated.")
    except Exception as e:
        print(f"Error capturing {t['name']}: {e}")

print("Dashboard screenshot suite complete!")
