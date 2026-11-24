import subprocess
import time
import urllib.request
import json
import os
import shutil

chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
if not os.path.exists(chrome_path):
    chrome_path = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"

# Launch headless Chrome with remote debugging
port = 9222
proc = subprocess.Popen([
    chrome_path,
    "--headless=new",
    "--disable-gpu",
    f"--remote-debugging-port={port}",
    "--window-size=1536,960",
    "http://localhost:3000/investigations/INV-2026-0881"
])

print("Launched Chrome on port", port)
time.sleep(3)

try:
    # Query targets
    targets = json.loads(urllib.request.urlopen(f"http://127.0.0.1:{port}/json").read().decode("utf-8"))
    page_target = next((t for t in targets if t.get("type") == "page"), None)
    print("Found page target:", page_target["id"] if page_target else "None")
finally:
    proc.terminate()
    proc.wait()
