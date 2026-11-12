import httpx
import re
import json

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

datasets = [
    ("f45bkkt8pr", "1", "sms_phishing"),
    ("hx4m73v2sf", "2", "legitphish")
]

for ds_id, ver, name in datasets:
    page_url = f"https://data.mendeley.com/datasets/{ds_id}/{ver}"
    try:
        r = httpx.get(page_url, headers=headers, follow_redirects=True, timeout=15)
        print(f"[{name}] HTTP {r.status_code}")
        # Search for direct download links
        links = re.findall(r'href="([^"]+)"', r.text)
        download_links = [l for l in links if "download" in l.lower() or "files" in l.lower()]
        print(f"[{name}] Download links found: {len(download_links)}")
        for dl in download_links[:5]:
            print("  ->", dl)
            
        # Check for embedded state / json
        scripts = re.findall(r'<script[^>]*>(.*?)</script>', r.text, re.DOTALL)
        for s in scripts:
            if "files" in s and ("downloadUrl" in s or "download_url" in s or "direct_download" in s):
                matches = re.findall(r'https?://[^\s",\']+(?:download|files)[^\s",\']+', s)
                if matches:
                    print(f"[{name}] Script download matches: {matches[:3]}")
    except Exception as e:
        print(f"[{name}] Error: {e}")

