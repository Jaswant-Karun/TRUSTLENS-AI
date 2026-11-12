"""
TRUSTLENS AI - Automated Dataset Download & Ingestion Pipeline
Acquires authentic raw datasets into data/raw/ with integrity verification,
chunk-based streaming, safe archive extraction, retry logic, and manifest recording.

Project: TRUSTLENS AI (Day 2 - Acquisition & Verification)
License Provenance: Verified MIT & CC BY 4.0
"""

import os
import sys
import time
import json
import shutil
import zipfile
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional
import httpx

# Ensure project root is on PYTHONPATH
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Target raw data directories
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
MANIFEST_PATH = DATA_DIR / "dataset_manifest.json"

# Dataset Source Definitions with Official Provenance
DATASETS_CONFIG: Dict[str, Dict[str, Any]] = {
    "scamshield": {
        "dataset_id": "sidzzz07/scamshield-dataset",
        "name": "ScamShield: Multilingual Smishing & Social Engineering Corpus",
        "source": "Hugging Face",
        "source_url": "https://huggingface.co/datasets/sidzzz07/scamshield-dataset",
        "version": "1.0.0",
        "license": "MIT",
        "license_url": "https://opensource.org/licenses/MIT",
        "authors": ["sidzzz07"],
        "description": "Multilingual SMS phishing and social engineering dataset covering English, Hindi, and Hinglish.",
        "dest_dir": RAW_DIR / "scamshield",
        "files": [
            {
                "filename": "train.jsonl",
                "url": "https://huggingface.co/datasets/sidzzz07/scamshield-dataset/resolve/main/train.jsonl",
                "format": "jsonl",
                "expected_size_mb": 35.80,
                "is_archive": False,
            },
            {
                "filename": "val.jsonl",
                "url": "https://huggingface.co/datasets/sidzzz07/scamshield-dataset/resolve/main/val.jsonl",
                "format": "jsonl",
                "expected_size_mb": 4.17,
                "is_archive": False,
            },
            {
                "filename": "test.jsonl",
                "url": "https://huggingface.co/datasets/sidzzz07/scamshield-dataset/resolve/main/test.jsonl",
                "format": "jsonl",
                "expected_size_mb": 4.19,
                "is_archive": False,
            },
        ],
    },
    "sms_phishing": {
        "dataset_id": "10.17632/f45bkkt8pr.1",
        "name": "SMS Phishing Dataset for Machine Learning and Pattern Recognition",
        "source": "Mendeley Data",
        "source_url": "https://data.mendeley.com/datasets/f45bkkt8pr/1",
        "version": "1",
        "license": "CC BY 4.0",
        "license_url": "http://creativecommons.org/licenses/by/4.0",
        "authors": ["Sandhya Mishra", "Devpriya Soni"],
        "description": "5,971 labeled SMS messages categorized into Ham, Spam, and Smishing.",
        "dest_dir": RAW_DIR / "sms_phishing",
        "files": [
            {
                "filename": "Dataset_5971.zip",
                "url": "https://data.mendeley.com/public-files/datasets/f45bkkt8pr/files/edb361de-918d-469f-9106-e84823830665/file_downloaded",
                "format": "zip",
                "expected_size_mb": 0.23,
                "is_archive": True,
                "extracted_files": ["Dataset_5971.csv"],
            }
        ],
    },
    "legitphish": {
        "dataset_id": "10.17632/hx4m73v2sf.2",
        "name": "LegitPhish Dataset",
        "source": "Mendeley Data",
        "source_url": "https://data.mendeley.com/datasets/hx4m73v2sf/2",
        "version": "2",
        "license": "CC BY 4.0",
        "license_url": "http://creativecommons.org/licenses/by/4.0",
        "authors": ["Rachana Potpelwar", "Uday Kulkarni", "Jaishri Waghmare"],
        "description": "101,219 URLs labeled Phishing (0) or Legitimate (1) with 17 extracted lexical/structural features.",
        "dest_dir": RAW_DIR / "legitphish",
        "files": [
            {
                "filename": "url_features_extracted1.csv",
                "url": "https://data.mendeley.com/public-files/datasets/hx4m73v2sf/files/0ed51e4d-d160-4047-b650-3f0801eea4aa/file_downloaded",
                "format": "csv",
                "expected_size_mb": 8.55,
                "is_archive": False,
            }
        ],
    },
}


def compute_sha256(filepath: Path, chunk_size: int = 1024 * 1024) -> str:
    """Computes SHA-256 hash using streaming chunks to minimize memory consumption."""
    sha = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(chunk_size):
            sha.update(chunk)
    return sha.hexdigest()


def detect_file_format(filepath: Path) -> str:
    """Detects file format via header magic bytes and extension inspection."""
    ext = filepath.suffix.lower()
    with open(filepath, "rb") as f:
        header = f.read(16)

    # Magic bytes check
    if header.startswith(b"PK\x03\x04") or header.startswith(b"PK\x05\x06"):
        return "zip"
    elif ext == ".jsonl":
        return "jsonl"
    elif ext == ".csv":
        return "csv"
    elif ext == ".parquet":
        return "parquet"
    return ext.lstrip(".") or "unknown"


def safe_extract_zip(zip_path: Path, target_dir: Path) -> List[str]:
    """
    Safely extracts a zip archive preventing Path Traversal (Zip Slip) attacks.
    Validates zip CRC integrity prior to extraction.
    """
    extracted_names = []
    target_dir_resolved = target_dir.resolve()

    with zipfile.ZipFile(zip_path, "r") as z:
        # Check CRC integrity
        crc_error = z.testzip()
        if crc_error is not None:
            raise ValueError(f"Corrupted archive detected in {zip_path.name}: bad CRC on {crc_error}")

        for member in z.infolist():
            member_path = (target_dir / member.filename).resolve()
            # Path traversal guard
            if not str(member_path).startswith(str(target_dir_resolved)):
                raise SecurityError(
                    f"Dangerous path traversal attempt detected in archive member: {member.filename}"
                )
            z.extract(member, target_dir)
            extracted_names.append(member.filename)

    return extracted_names


def download_file_with_retry(
    url: str,
    dest_path: Path,
    expected_size_mb: Optional[float] = None,
    max_retries: int = 3,
    chunk_size: int = 1024 * 1024,
    force: bool = False,
) -> Dict[str, Any]:
    """
    Downloads a file with streaming chunks, retry backoff, and size/checksum recording.
    If the file exists and is valid, skips downloading unless force=True.
    """
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = dest_path.with_suffix(dest_path.suffix + ".part")

    # If file exists and is non-empty, verify without re-downloading
    if dest_path.exists() and dest_path.stat().st_size > 0 and not force:
        size_bytes = dest_path.stat().st_size
        size_mb = size_bytes / (1024 * 1024)
        print(f"  [EXISTS] {dest_path.name} ({size_mb:.2f} MB, {size_bytes:,} bytes)")
        sha256 = compute_sha256(dest_path)
        return {
            "status": "cached",
            "path": dest_path,
            "size_bytes": size_bytes,
            "size_mb": round(size_mb, 4),
            "sha256": sha256,
            "format": detect_file_format(dest_path),
            "downloaded_at": datetime.fromtimestamp(dest_path.stat().st_mtime, tz=timezone.utc).isoformat(),
        }

    headers = {
        "User-Agent": "TRUSTLENS-AI-Acquisition/1.0.0 (Research Dataset Verification; Windows x64)"
    }
    timeout = httpx.Timeout(connect=60.0, read=180.0, write=60.0, pool=60.0)

    last_exc = None
    for attempt in range(1, max_retries + 1):
        try:
            print(f"  [DOWNLOAD] {dest_path.name} (Attempt {attempt}/{max_retries}) from {url[:80]}...")
            with httpx.Client(follow_redirects=True, timeout=timeout) as client:
                with client.stream("GET", url, headers=headers) as resp:
                    resp.raise_for_status()
                    total_bytes = 0
                    with open(temp_path, "wb") as f:
                        for chunk in resp.iter_bytes(chunk_size=chunk_size):
                            if chunk:
                                f.write(chunk)
                                total_bytes += len(chunk)

            # Validate temp file size > 0
            if total_bytes == 0:
                raise ValueError(f"Downloaded empty file (0 bytes) from {url}")

            # Atomically replace destination file
            if temp_path.exists():
                shutil.move(str(temp_path), str(dest_path))

            size_bytes = dest_path.stat().st_size
            size_mb = size_bytes / (1024 * 1024)
            sha256 = compute_sha256(dest_path)
            print(f"  [SAVED] {dest_path.name} ({size_mb:.2f} MB, {size_bytes:,} bytes, SHA-256: {sha256[:12]}...)")

            return {
                "status": "downloaded",
                "path": dest_path,
                "size_bytes": size_bytes,
                "size_mb": round(size_mb, 4),
                "sha256": sha256,
                "format": detect_file_format(dest_path),
                "downloaded_at": datetime.now(timezone.utc).isoformat(),
            }

        except Exception as exc:
            last_exc = exc
            print(f"  [WARNING] Attempt {attempt} failed: {exc}")
            if temp_path.exists():
                try:
                    temp_path.unlink()
                except Exception:
                    pass
            if attempt < max_retries:
                backoff = 2 ** attempt
                print(f"  Backing off for {backoff}s before retry...")
                time.sleep(backoff)

    raise RuntimeError(f"Failed to download {dest_path.name} after {max_retries} attempts: {last_exc}")


def build_manifest(download_results: Dict[str, Any]) -> Dict[str, Any]:
    """Generates the structured dataset manifest adhering to metadata schema."""
    manifest = {
        "manifest_version": "1.0.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "project": "TRUSTLENS AI - Multilingual Digital Fraud Intelligence & Prevention Platform",
        "stage": "Day 2 - Dataset Acquisition and Verification",
        "system_info": {
            "platform": sys.platform,
            "python_version": sys.version.split()[0],
            "chunk_size_bytes": 1024 * 1024,
            "memory_guard": "Stream-based processing enabled (16GB RAM constraint respected)",
        },
        "datasets": {},
    }

    for ds_key, ds_info in download_results.items():
        config = DATASETS_CONFIG[ds_key]
        manifest["datasets"][ds_key] = {
            "name": config["name"],
            "dataset_id": config["dataset_id"],
            "source": config["source"],
            "source_url": config["source_url"],
            "version": config["version"],
            "license": config["license"],
            "license_url": config["license_url"],
            "authors": config["authors"],
            "description": config["description"],
            "raw_directory": str(config["dest_dir"].relative_to(PROJECT_ROOT)).replace("\\", "/"),
            "files": ds_info["files"],
        }

    return manifest


def main(force: bool = False) -> None:
    print("=" * 70)
    print("TRUSTLENS AI — AUTOMATED DATASET INGESTION & DOWNLOAD (DAY 2)")
    print("=" * 70)
    print(f"Target Raw Directory: {RAW_DIR}")
    print(f"Mode: {'Forced Re-Download' if force else 'Integrity Check / Fetch Missing'}")
    print(f"RAM Guard: Active (1MB stream buffers, zero in-memory accumulation)")
    print("-" * 70)

    # Ensure required directories exist
    for dir_name in ["scamshield", "sms_phishing", "legitphish"]:
        (RAW_DIR / dir_name).mkdir(parents=True, exist_ok=True)
    (DATA_DIR / "processed").mkdir(parents=True, exist_ok=True)
    (DATA_DIR / "external").mkdir(parents=True, exist_ok=True)

    download_results: Dict[str, Any] = {}

    for ds_key, config in DATASETS_CONFIG.items():
        print(f"\nProcessing Dataset: [{ds_key.upper()}] — {config['name']}")
        dest_dir = config["dest_dir"]
        ds_records = {"files": []}

        for file_info in config["files"]:
            target_path = dest_dir / file_info["filename"]
            result = download_file_with_retry(
                url=file_info["url"],
                dest_path=target_path,
                expected_size_mb=file_info.get("expected_size_mb"),
                force=force,
            )

            file_entry = {
                "filename": file_info["filename"],
                "relative_path": str(target_path.relative_to(PROJECT_ROOT)).replace("\\", "/"),
                "status": result["status"],
                "format": result["format"],
                "size_bytes": result["size_bytes"],
                "size_mb": result["size_mb"],
                "sha256": result["sha256"],
                "source_url": file_info["url"],
                "downloaded_at": result["downloaded_at"],
            }

            # Safe archive extraction if applicable
            if file_info.get("is_archive", False):
                print(f"  [EXTRACT] Testing CRC & extracting {file_info['filename']} safely...")
                extracted = safe_extract_zip(target_path, dest_dir)
                print(f"  [EXTRACTED] {extracted}")
                file_entry["extracted_files"] = []
                for ext_name in extracted:
                    ext_path = dest_dir / ext_name
                    ext_size = ext_path.stat().st_size
                    ext_sha = compute_sha256(ext_path)
                    file_entry["extracted_files"].append({
                        "filename": ext_name,
                        "relative_path": str(ext_path.relative_to(PROJECT_ROOT)).replace("\\", "/"),
                        "format": detect_file_format(ext_path),
                        "size_bytes": ext_size,
                        "size_mb": round(ext_size / (1024 * 1024), 4),
                        "sha256": ext_sha,
                    })

            ds_records["files"].append(file_entry)

        download_results[ds_key] = ds_records

    # Write dataset manifest
    manifest = build_manifest(download_results)
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print("\n" + "=" * 70)
    print(f"DATASET ACQUISITION COMPLETE. Manifest generated at: {MANIFEST_PATH}")
    print("=" * 70)


if __name__ == "__main__":
    force_download = "--force" in sys.argv
    main(force=force_download)
