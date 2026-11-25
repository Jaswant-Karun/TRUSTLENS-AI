"""
TRUSTLENS AI - Phase 2.0.5: Group-Aware Leak-Free Dataset Splitting
Creates reproducible Train / Validation / Test Parquet splits using StratifiedGroupKFold
to guarantee zero exact/near-duplicate message leakage and zero domain-level URL leakage.
Generates data/processed/dataset_manifest.json with SHA-256 checksums.
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone

import pandas as pd
import numpy as np
from sklearn.model_selection import StratifiedGroupKFold

RANDOM_SEED = 42


def compute_sha256(filepath: Path) -> str:
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def split_text_corpus(out_dir: Path) -> dict:
    print("\n[1/2] Splitting Text Corpus (StratifiedGroupKFold on text_group_id)...")
    df = pd.read_parquet(out_dir / "text_clean.parquet")

    # 10-fold StratifiedGroupKFold -> 80% Train (folds 0-7), 10% Val (fold 8), 10% Test (fold 9)
    sgkf = StratifiedGroupKFold(n_splits=10, shuffle=True, random_state=RANDOM_SEED)
    fold_assignments = np.zeros(len(df), dtype=int)
    for fold_idx, (_, test_idx) in enumerate(sgkf.split(df, df["is_threat"], df["text_group_id"])):
        fold_assignments[test_idx] = fold_idx

    df["split_assignment"] = np.where(
        fold_assignments == 9, "test",
        np.where(fold_assignments == 8, "val", "train")
    )

    train_df = df[df["split_assignment"] == "train"].reset_index(drop=True)
    val_df = df[df["split_assignment"] == "val"].reset_index(drop=True)
    test_df = df[df["split_assignment"] == "test"].reset_index(drop=True)

    train_df.to_parquet(out_dir / "text_train.parquet", index=False)
    val_df.to_parquet(out_dir / "text_val.parquet", index=False)
    test_df.to_parquet(out_dir / "text_test.parquet", index=False)

    print(f"  text_train.parquet: {len(train_df):,} rows | Threat%: {train_df['is_threat'].mean():.2%}")
    print(f"  text_val.parquet:   {len(val_df):,} rows | Threat%: {val_df['is_threat'].mean():.2%}")
    print(f"  text_test.parquet:  {len(test_df):,} rows | Threat%: {test_df['is_threat'].mean():.2%}")

    return {
        "method": "StratifiedGroupKFold(n_splits=10, shuffle=True)",
        "group_key": "text_group_id",
        "random_seed": RANDOM_SEED,
        "train_rows": len(train_df),
        "val_rows": len(val_df),
        "test_rows": len(test_df),
        "train_threat_ratio": round(float(train_df["is_threat"].mean()), 4),
        "val_threat_ratio": round(float(val_df["is_threat"].mean()), 4),
        "test_threat_ratio": round(float(test_df["is_threat"].mean()), 4),
        "language_distribution": {
            "train": train_df["language"].value_counts().to_dict(),
            "val": val_df["language"].value_counts().to_dict(),
            "test": test_df["language"].value_counts().to_dict(),
        },
    }


def split_url_corpus(out_dir: Path) -> dict:
    print("\n[2/2] Splitting URL Corpus (StratifiedGroupKFold on domain_group_id)...")
    df = pd.read_parquet(out_dir / "urls_clean.parquet")

    # 7-fold StratifiedGroupKFold -> ~71.4% Train (folds 0-4), ~14.3% Val (fold 5), ~14.3% Test (fold 6)
    sgkf = StratifiedGroupKFold(n_splits=7, shuffle=True, random_state=RANDOM_SEED)
    fold_assignments = np.zeros(len(df), dtype=int)
    for fold_idx, (_, test_idx) in enumerate(sgkf.split(df, df["is_phishing"], df["domain_group_id"])):
        fold_assignments[test_idx] = fold_idx

    df["split_assignment"] = np.where(
        fold_assignments == 6, "test",
        np.where(fold_assignments == 5, "val", "train")
    )

    train_df = df[df["split_assignment"] == "train"].reset_index(drop=True)
    val_df = df[df["split_assignment"] == "val"].reset_index(drop=True)
    test_df = df[df["split_assignment"] == "test"].reset_index(drop=True)

    train_df.to_parquet(out_dir / "urls_train.parquet", index=False)
    val_df.to_parquet(out_dir / "urls_val.parquet", index=False)
    test_df.to_parquet(out_dir / "urls_test.parquet", index=False)

    print(f"  urls_train.parquet: {len(train_df):,} rows | Phish%: {train_df['is_phishing'].mean():.2%}")
    print(f"  urls_val.parquet:   {len(val_df):,} rows | Phish%: {val_df['is_phishing'].mean():.2%}")
    print(f"  urls_test.parquet:  {len(test_df):,} rows | Phish%: {test_df['is_phishing'].mean():.2%}")

    return {
        "method": "StratifiedGroupKFold(n_splits=7, shuffle=True)",
        "group_key": "domain_group_id",
        "random_seed": RANDOM_SEED,
        "train_rows": len(train_df),
        "val_rows": len(val_df),
        "test_rows": len(test_df),
        "train_phishing_ratio": round(float(train_df["is_phishing"].mean()), 4),
        "val_phishing_ratio": round(float(val_df["is_phishing"].mean()), 4),
        "test_phishing_ratio": round(float(test_df["is_phishing"].mean()), 4),
    }


def main():
    print("=" * 68)
    print("TRUSTLENS AI - PHASE 2.0.5: GROUP-AWARE SPLIT GENERATION")
    print("=" * 68)
    out_dir = Path("data/processed")

    text_info = split_text_corpus(out_dir)
    url_info = split_url_corpus(out_dir)

    checksums = {}
    for p in sorted(out_dir.glob("*.parquet")):
        checksums[p.name] = {
            "sha256": compute_sha256(p),
            "size_bytes": p.stat().st_size,
        }

    manifest = {
        "manifest_version": "2.0.5",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "random_seed": RANDOM_SEED,
        "leakage_prevention": "Group-aware splitting enforced via text_group_id and domain_group_id",
        "text_corpus": text_info,
        "url_corpus": url_info,
        "processed_files": checksums,
    }

    with open(out_dir / "dataset_manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(f"\nManifest saved to {out_dir / 'dataset_manifest.json'}")


if __name__ == "__main__":
    main()
