import httpx
import json

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json"
}

datasets = [
    ("f45bkkt8pr", "1", "sms_phishing"),
    ("hx4m73v2sf", "2", "legitphish")
]

for ds_id, ver, name in datasets:
    ep = f"https://data.mendeley.com/public-api/datasets/{ds_id}/files?folder_id=root&version={ver}"
    r = httpx.get(ep, headers=headers, timeout=15)
    files = r.json()
    print(f"=== {name} ({ds_id} v{ver}) ===")
    for f in files:
        fname = f.get("filename")
        fid = f.get("id")
        cd = f.get("content_details", {})
        size = cd.get("size", 0)
        dl_url = cd.get("download_url")
        print(f"File: {fname} | Size: {size} bytes ({size/(1024*1024):.2f} MB)")
        print(f"  ID: {fid}")
        print(f"  Download URL: {dl_url}")

