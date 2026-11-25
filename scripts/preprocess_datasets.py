"""
TRUSTLENS AI - Phase 2.0.5: Reproducible Dataset Preprocessing & Quality Control
Safely ingests raw ScamShield, Mendeley SMS, and LegitPhish datasets using streaming/chunking.
Preserves raw datasets unchanged. Normalizes text & labels, extracts aligned URL features,
and assigns group IDs to prevent exact and near-duplicate leakage across splits.
"""

import os
import sys
import json
import hashlib
import unicodedata
from pathlib import Path
from urllib.parse import urlparse
from typing import Dict, Any, List

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
import numpy as np

from ml.preprocessing.text_preprocessor import text_preprocessor
from ml.url_detection.features import extract_url_features, FEATURE_COLUMNS


def remove_control_chars(text: str) -> str:
    """Removes invalid control characters while preserving newlines and tabs."""
    return "".join(
        ch for ch in text
        if ch in ("\n", "\t") or unicodedata.category(ch) != "Cc"
    )


def compute_group_hash(text: str) -> str:
    """Computes deterministic SHA-256 hash of normalized text for near-duplicate grouping."""
    norm = " ".join(text.lower().split())
    return hashlib.sha256(norm.encode("utf-8")).hexdigest()[:16]


def extract_domain_group(url: str) -> str:
    """Extracts canonical hostname/domain without port for group-aware URL splitting."""
    u = str(url).strip()
    if "://" not in u:
        u = "http://" + u
    try:
        netloc = urlparse(u).netloc.lower().split(":")[0]
        # Strip leading www. so www.example.com and example.com group together
        if netloc.startswith("www."):
            netloc = netloc[4:]
        return netloc or compute_group_hash(u)
    except Exception:
        return compute_group_hash(u)


def preprocess_text_corpora() -> Dict[str, Any]:
    """Streams and normalizes ScamShield (train/val/test) and Mendeley SMS datasets."""
    print("\n[1/2] Preprocessing Text Corpora (ScamShield + Mendeley SMS)...")
    records: List[Dict[str, Any]] = []
    stats = {
        "scamshield_raw_rows": 0,
        "mendeley_raw_rows": 0,
        "empty_or_malformed_dropped": 0,
        "missing_labels_dropped": 0,
        "exact_raw_duplicates_removed": 0,
        "mendeley_overlapping_with_scamshield": 0,
    }

    scamshield_raw_set = set()

    # 1. Stream ScamShield JSONL files
    for split in ["train", "val", "test"]:
        path = Path(f"data/raw/scamshield/{split}.jsonl")
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                stats["scamshield_raw_rows"] += 1
                item = json.loads(line)
                raw_text = item.get("text")
                if not raw_text or not str(raw_text).strip():
                    stats["empty_or_malformed_dropped"] += 1
                    continue

                if item.get("is_scam") is None:
                    stats["missing_labels_dropped"] += 1
                    continue

                raw_str = str(raw_text)
                cleaned_ctrl = remove_control_chars(raw_str)
                norm = text_preprocessor.preprocess(cleaned_ctrl, mask_personal_data=True)
                if not norm["cleaned_text"]:
                    stats["empty_or_malformed_dropped"] += 1
                    continue

                scamshield_raw_set.add(raw_str.strip().lower())

                is_scam = int(item["is_scam"])
                intent = str(item.get("head2_scam_intent", "Legitimate / Benign"))
                if is_scam == 0:
                    canonical_label = "legitimate"
                elif "spam" in intent.lower():
                    canonical_label = "spam"
                elif any(k in intent.lower() for k in ["kyc", "upi", "courier", "otp"]):
                    canonical_label = "smishing"
                else:
                    canonical_label = "scam"

                records.append({
                    "id": str(item.get("id")),
                    "raw_text": raw_str,
                    "cleaned_text": norm["cleaned_text"],
                    "extracted_urls": norm["extracted_urls"],
                    "url_count": len(norm["extracted_urls"]),
                    "language": norm["language"],
                    "raw_language": str(item.get("language", "Unknown")),
                    "original_label": intent,
                    "canonical_label": canonical_label,
                    "is_threat": is_scam,
                    "tactics": json.dumps(item.get("head1_social_engineering", {})),
                    "head2_scam_intent": intent,
                    "metadata_json": json.dumps(item.get("metadata", {})),
                    "source_dataset": f"ScamShield ({item.get('source_dataset', 'core')})",
                    "native_split": split,
                    "text_group_id": compute_group_hash(norm["cleaned_text"]),
                })

    # 2. Stream Mendeley SMS CSV
    sms_path = Path("data/raw/sms_phishing/Dataset_5971.csv")
    for chunk in pd.read_csv(sms_path, chunksize=2000):
        for idx, row in chunk.iterrows():
            stats["mendeley_raw_rows"] += 1
            raw_text = row.get("TEXT")
            raw_label = row.get("LABEL")
            if pd.isna(raw_text) or not str(raw_text).strip():
                stats["empty_or_malformed_dropped"] += 1
                continue
            if pd.isna(raw_label) or not str(raw_label).strip():
                stats["missing_labels_dropped"] += 1
                continue

            raw_str = str(raw_text)
            if raw_str.strip().lower() in scamshield_raw_set:
                stats["mendeley_overlapping_with_scamshield"] += 1

            cleaned_ctrl = remove_control_chars(raw_str)
            norm = text_preprocessor.preprocess(cleaned_ctrl, mask_personal_data=True)
            if not norm["cleaned_text"]:
                stats["empty_or_malformed_dropped"] += 1
                continue

            lbl_lower = str(raw_label).strip().lower()
            if lbl_lower == "ham":
                canonical_label = "legitimate"
                is_threat = 0
            elif lbl_lower == "spam":
                canonical_label = "spam"
                is_threat = 1
            elif lbl_lower == "smishing":
                canonical_label = "smishing"
                is_threat = 1
            else:
                canonical_label = "scam"
                is_threat = 1

            records.append({
                "id": f"mendeley_{idx:05d}",
                "raw_text": raw_str,
                "cleaned_text": norm["cleaned_text"],
                "extracted_urls": norm["extracted_urls"],
                "url_count": len(norm["extracted_urls"]),
                "language": norm["language"],
                "raw_language": "English",
                "original_label": str(raw_label).strip(),
                "canonical_label": canonical_label,
                "is_threat": is_threat,
                "tactics": "{}",
                "head2_scam_intent": str(raw_label).strip(),
                "metadata_json": "{}",
                "source_dataset": "Mendeley_SMS_Phishing",
                "native_split": "unassigned",
                "text_group_id": compute_group_hash(norm["cleaned_text"]),
            })

    df = pd.DataFrame(records)
    before_dedup = len(df)
    # Remove exact raw_text duplicates (preserving first occurrence)
    df["raw_text_norm"] = df["raw_text"].str.strip().str.lower()
    df = df.drop_duplicates(subset=["raw_text_norm"]).drop(columns=["raw_text_norm"]).reset_index(drop=True)
    stats["exact_raw_duplicates_removed"] = before_dedup - len(df)
    stats["final_clean_text_rows"] = len(df)
    stats["unique_near_duplicate_groups"] = int(df["text_group_id"].nunique())
    stats["near_duplicate_templates_count"] = len(df) - stats["unique_near_duplicate_groups"]
    stats["class_distribution"] = df["is_threat"].value_counts().to_dict()
    stats["language_distribution"] = df["language"].value_counts().to_dict()

    out_path = Path("data/processed/text_clean.parquet")
    df.to_parquet(out_path, index=False)
    print(f"  Saved {len(df):,} clean text rows ({stats['unique_near_duplicate_groups']:,} unique groups) -> {out_path}")
    return stats


def preprocess_url_corpus() -> Dict[str, Any]:
    """Chunk-loads LegitPhish CSV, drops malformed/duplicate URLs, aligns features, and assigns domain_group_id."""
    print("\n[2/2] Preprocessing URL Corpus (LegitPhish)...")
    csv_path = Path("data/raw/legitphish/url_features_extracted1.csv")

    stats = {
        "raw_rows": 0,
        "missing_labels_dropped": 0,
        "empty_urls_dropped": 0,
        "duplicate_urls_removed": 0,
    }

    chunks = []
    for chunk in pd.read_csv(csv_path, chunksize=25000):
        stats["raw_rows"] += len(chunk)
        # Check nulls
        null_lbl = chunk["ClassLabel"].isna().sum()
        stats["missing_labels_dropped"] += int(null_lbl)
        chunk = chunk.dropna(subset=["ClassLabel"]).copy()

        empty_u = chunk["URL"].isna() | (chunk["URL"].astype(str).str.strip() == "")
        stats["empty_urls_dropped"] += int(empty_u.sum())
        chunk = chunk[~empty_u].copy()
        chunks.append(chunk)

    df = pd.concat(chunks, ignore_index=True)
    before_dedup = len(df)
    df = df.drop_duplicates(subset=["URL"]).reset_index(drop=True)
    stats["duplicate_urls_removed"] = before_dedup - len(df)

    # Canonical label mapping: LegitPhish 0.0 = Phishing, 1.0 = Legitimate
    df["original_label"] = df["ClassLabel"].astype(float)
    df["canonical_label"] = df["original_label"].map({0.0: "phishing", 1.0: "legitimate"})
    df["is_phishing"] = df["original_label"].map({0.0: 1, 1.0: 0}).astype(int)
    df["source_dataset"] = "Mendeley_LegitPhish"

    # Extract deterministic aligned features without visiting URLs
    print("  Extracting aligned lexical/structural features (zero-hop)...")
    extracted_rows = [extract_url_features(u) for u in df["URL"]]
    feat_df = pd.DataFrame(extracted_rows)[FEATURE_COLUMNS]

    for col in FEATURE_COLUMNS:
        df[col] = feat_df[col].values

    # Assign domain_group_id for group-aware splitting
    df["domain_group_id"] = df["URL"].apply(extract_domain_group)

    stats["final_clean_url_rows"] = len(df)
    stats["unique_domain_groups"] = int(df["domain_group_id"].nunique())
    stats["class_distribution"] = df["is_phishing"].value_counts().to_dict()

    out_path = Path("data/processed/urls_clean.parquet")
    df.to_parquet(out_path, index=False)
    print(f"  Saved {len(df):,} clean URL rows ({stats['unique_domain_groups']:,} unique domain groups) -> {out_path}")
    return stats


def main():
    print("=" * 68)
    print("TRUSTLENS AI - PHASE 2.0.5: DATASET PREPROCESSING & QUALITY CONTROL")
    print("=" * 68)
    Path("data/processed").mkdir(parents=True, exist_ok=True)

    text_stats = preprocess_text_corpora()
    url_stats = preprocess_url_corpus()

    summary = {
        "text_preprocessing": text_stats,
        "url_preprocessing": url_stats,
    }
    with open("data/processed/preprocessing_stats.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, default=str)

    print("\nPreprocessing complete. Summary saved to data/processed/preprocessing_stats.json")


if __name__ == "__main__":
    main()
