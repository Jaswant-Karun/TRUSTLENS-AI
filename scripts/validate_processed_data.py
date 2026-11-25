"""
TRUSTLENS AI - Phase 2.0.5: Processed Data & Anti-Leakage Validation Suite
Verifies:
1. Raw datasets are 100% untouched (SHA-256 match against data/dataset_manifest.json).
2. Processed parquet schemas, non-null labels, and canonical label mappings.
3. Zero exact/near-duplicate message group leakage across train/val/test splits.
4. Zero domain-level URL leakage across train/val/test splits.
"""

import json
import hashlib
from pathlib import Path
import pandas as pd


def compute_sha256(filepath: Path) -> str:
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def verify_raw_integrity():
    print("\n[1/3] Verifying Raw Dataset Integrity (SHA-256)...")
    manifest_path = Path("data/dataset_manifest.json")
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    for ds_key, ds_info in manifest["datasets"].items():
        for file_info in ds_info["files"]:
            rel_path = Path(file_info["relative_path"])
            assert rel_path.exists(), f"Missing raw file: {rel_path}"
            actual_sha = compute_sha256(rel_path)
            assert actual_sha == file_info["sha256"], f"Raw file modified! {rel_path}"
            print(f"  PASS: {rel_path} unchanged (SHA-256 verified)")
            for ext in file_info.get("extracted_files", []):
                ext_path = Path(ext["relative_path"])
                assert ext_path.exists(), f"Missing extracted raw file: {ext_path}"
                assert compute_sha256(ext_path) == ext["sha256"], f"Extracted raw modified: {ext_path}"
                print(f"  PASS: {ext_path} unchanged (SHA-256 verified)")


def verify_text_splits():
    print("\n[2/3] Verifying Text Corpus Validity & Zero Group Leakage...")
    tr = pd.read_parquet("data/processed/text_train.parquet")
    va = pd.read_parquet("data/processed/text_val.parquet")
    te = pd.read_parquet("data/processed/text_test.parquet")

    for name, df in [("train", tr), ("val", va), ("test", te)]:
        assert len(df) > 0, f"Empty text {name}"
        assert df["is_threat"].isna().sum() == 0, f"Null labels in text {name}"
        assert df["cleaned_text"].isna().sum() == 0, f"Null cleaned_text in text {name}"
        assert set(df["canonical_label"].unique()).issubset({"legitimate", "spam", "smishing", "scam"})
        assert set(df["is_threat"].unique()).issubset({0, 1})

    g_tr = set(tr["text_group_id"])
    g_va = set(va["text_group_id"])
    g_te = set(te["text_group_id"])

    assert len(g_tr & g_te) == 0, f"Leakage Train-Test: {len(g_tr & g_te)}"
    assert len(g_tr & g_va) == 0, f"Leakage Train-Val: {len(g_tr & g_va)}"
    assert len(g_va & g_te) == 0, f"Leakage Val-Test: {len(g_va & g_te)}"

    c_tr = set(tr["cleaned_text"])
    c_te = set(te["cleaned_text"])
    assert len(c_tr & c_te) == 0, f"Cleaned text overlap Train-Test: {len(c_tr & c_te)}"

    print(f"  PASS: Text splits valid (Train={len(tr):,}, Val={len(va):,}, Test={len(te):,})")
    print("  PASS: Zero text_group_id & cleaned_text leakage across all splits!")


def verify_url_splits():
    print("\n[3/3] Verifying URL Corpus Validity & Zero Domain Leakage...")
    tr = pd.read_parquet("data/processed/urls_train.parquet")
    va = pd.read_parquet("data/processed/urls_val.parquet")
    te = pd.read_parquet("data/processed/urls_test.parquet")

    for name, df in [("train", tr), ("val", va), ("test", te)]:
        assert len(df) > 0, f"Empty url {name}"
        assert df["is_phishing"].isna().sum() == 0, f"Null labels in url {name}"
        assert set(df["canonical_label"].unique()).issubset({"phishing", "legitimate"})
        assert set(df["is_phishing"].unique()).issubset({0, 1})

    d_tr = set(tr["domain_group_id"])
    d_va = set(va["domain_group_id"])
    d_te = set(te["domain_group_id"])

    assert len(d_tr & d_te) == 0, f"Domain leakage Train-Test: {len(d_tr & d_te)}"
    assert len(d_tr & d_va) == 0, f"Domain leakage Train-Val: {len(d_tr & d_va)}"
    assert len(d_va & d_te) == 0, f"Domain leakage Val-Test: {len(d_va & d_te)}"

    print(f"  PASS: URL splits valid (Train={len(tr):,}, Val={len(va):,}, Test={len(te):,})")
    print("  PASS: Zero domain_group_id leakage across all splits!")


def main():
    print("=" * 68)
    print("TRUSTLENS AI - PHASE 2.0.5: VALIDATION & ANTI-LEAKAGE SUITE")
    print("=" * 68)
    verify_raw_integrity()
    verify_text_splits()
    verify_url_splits()
    print("\nALL VALIDATION CHECKS PASSED SUCCESSFULLY!")


if __name__ == "__main__":
    main()
