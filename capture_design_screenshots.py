import subprocess
import time
import os
import shutil

chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
artifact_dir = r"C:\Users\jaswant karun\.gemini\antigravity\brain\ccdc3978-e39e-4041-ac1a-6d43bb2834f7\screenshots"
docs_dir = r"c:\Users\jaswant karun\TRUSTLENS AI\docs\screenshots"

os.makedirs(artifact_dir, exist_ok=True)
os.makedirs(docs_dir, exist_ok=True)

targets = [
    {
        "name": "design_overview_cockpit.png",
        "url": "http://localhost:3000?tab=overview",
        "window_size": "1440,1100",
        "delay": 4
    },
    {
        "name": "design_workbench_scan.png",
        "url": "http://localhost:3000?tab=scan",
        "window_size": "1440,1100",
        "delay": 4
    },
    {
        "name": "design_campaign_intelligence.png",
        "url": "http://localhost:3000?tab=campaigns",
        "window_size": "1440,1100",
        "delay": 4
    },
    {
        "name": "design_model_governance.png",
        "url": "http://localhost:3000?tab=models",
        "window_size": "1440,1200",
        "delay": 4
    },
    {
        "name": "design_tablet.png",
        "url": "http://localhost:3000?tab=overview",
        "window_size": "768,1024",
        "delay": 3
    },
    {
        "name": "design_mobile.png",
        "url": "http://localhost:3000?tab=overview",
        "window_size": "390,844",
        "delay": 3
    }
]

for t in targets:
    doc_out = os.path.join(docs_dir, t["name"])
    art_out = os.path.join(artifact_dir, t["name"])
    
    cmd = [
        chrome_path,
        "--headless=new",
        "--disable-gpu",
        f"--window-size={t['window_size']}",
        f"--virtual-time-budget={t['delay'] * 1000}",
        f"--screenshot={doc_out}",
        t["url"]
    ]
    
    print(f"Capturing {t['name']}...")
    try:
        subprocess.run(cmd, check=True, timeout=25)
        if os.path.exists(doc_out):
            shutil.copyfile(doc_out, art_out)
            print(f"Saved: {doc_out} ({os.path.getsize(doc_out)} bytes)")
    except Exception as e:
        print(f"Error capturing {t['name']}: {e}")

print("All screenshots successfully captured!")
