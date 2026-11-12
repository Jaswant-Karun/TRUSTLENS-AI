import httpx
import json

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json"
}

endpoints = [
    "https://data.mendeley.com/public-api/datasets/f45bkkt8pr/files?folder_id=root&version=1",
    "https://data.mendeley.com/public-api/datasets/f45bkkt8pr/files?version=1",
    "https://data.mendeley.com/api/datasets/f45bkkt8pr/files?version=1",
    "https://data.mendeley.com/public-api/datasets/f45bkkt8pr/1/files",
    "https://data.mendeley.com/datasets/f45bkkt8pr/1/files",
    "https://prod-mendeley-data-platform.mendeley.com/public-api/datasets/f45bkkt8pr/files?version=1"
]

for ep in endpoints:
    try:
        r = httpx.get(ep, headers=headers, follow_redirects=True, timeout=10)
        print(f"{ep} -> {r.status_code}")
        if r.status_code == 200:
            print("Content:", r.text[:300])
    except Exception as e:
        print(f"{ep} -> Error: {e}")
