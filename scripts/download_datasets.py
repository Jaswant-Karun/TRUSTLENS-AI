"""
TRUSTLENS AI - Dataset Ingestion & Download Pipeline
Downloads authentic, original datasets into data/raw/ without modifying them.
"""

import os
import sys
import zipfile
import hashlib
from pathlib import Path
import httpx

DATASETS_CONFIG = {
    "scamshield": {
        "dest_dir": Path("data/raw/scamshield"),
        "files": [
            {
                "name": "train.jsonl",
                "url": "https://huggingface.co/datasets/sidzzz07/scamshield-dataset/resolve/main/train.jsonl",
                "expected_size_mb": 35.8,
            },
            {
                "name": "val.jsonl",
                "url": "https://huggingface.co/datasets/sidzzz07/scamshield-dataset/resolve/main/val.jsonl",
                "expected_size_mb": 4.17,
            },
            {
                "name": "test.jsonl",
                "url": "https://huggingface.co/datasets/sidzzz07/scamshield-dataset/resolve/main/test.jsonl",
                "expected_size_mb": 4.19,
            },
        ],
    },
    "sms_phishing": {
        "dest_dir": Path("data/raw/sms_phishing"),
        "files": [
            {
                "name": "Dataset_5971.zip",
                "url": "https://data.mendeley.com/public-files/datasets/f45bkkt8pr/files/edb361de-918d-469f-9106-e84823830665/file_downloaded",
                "expected_size_mb": 0.23,
                "is_zip": True,
            }
        ],
    },
    "legitphish": {
        "dest_dir": Path("data/raw/legitphish"),
        "files": [
            {
                "name": "url_features_extracted1.csv",
                "url": "https://data.mendeley.com/public-files/datasets/hx4m73v2sf/files/0ed51e4d-d160-4047-b650-3f0801eea4aa/file_downloaded",
                "expected_size_mb": 8.55,
            }
        ],
    },
}


def download_file(url: str, dest_path: Path) -> None:
    """Downloads a file with streaming and progress reporting."""
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    if dest_path.exists() and dest_path.stat().st_size > 0:
        print(f"  [EXISTS] {dest_path.name} ({dest_path.stat().st_size / (1024*1024):.2f} MB)")
        return

    print(f"  Downloading {dest_path.name} from {url}...")
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    with httpx.Client(follow_redirects=True, timeout=120) as client:
        with client.stream("GET", url, headers=headers) as resp:
            resp.raise_for_status()
            with open(dest_path, "wb") as f:
                for chunk in resp.iter_bytes(chunk_size=1024 * 1024):
                    if chunk:
                        f.write(chunk)
    
    size_mb = dest_path.stat().st_size / (1024 * 1024)
    print(f"  [SAVED] {dest_path.name} ({size_mb:.2f} MB)")


def main():
    print("=" * 60)
    print("TRUSTLENS AI - DATASET DOWNLOAD & INGESTION")
    print("=" * 60)

    for ds_name, config in DATASETS_CONFIG.items():
        print(f"\nProcessing Dataset: {ds_name.upper()}")
        dest_dir = config["dest_dir"]
        dest_dir.mkdir(parents=True, exist_ok=True)

        for file_info in config["files"]:
            file_path = dest_dir / file_info["name"]
            download_file(file_info["url"], file_path)

            if file_info.get("is_zip", False):
                print(f"  Extracting {file_info['name']}...")
                with zipfile.ZipFile(file_path, "r") as zip_ref:
                    zip_ref.extractall(dest_dir)
                print(f"  [EXTRACTED] Contents of {file_info['name']}")

    print("\n" + "=" * 60)
    print("ALL RAW DATASETS DOWNLOADED AND PRESERVED!")
    print("=" * 60)


if __name__ == "__main__":
    main()

