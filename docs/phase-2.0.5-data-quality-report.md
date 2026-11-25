# TRUSTLENS AI — PHASE 2.0.5: DATA QUALITY CONTROL & ANTI-LEAKAGE REPORT

> **Pipelines Executed:** `scripts/preprocess_datasets.py`, `scripts/create_dataset_splits.py`, `scripts/validate_processed_data.py`  
> **Random Seed:** `42`  
> **Manifest:** [`data/processed/dataset_manifest.json`](file:///c:/Users/jaswant%20karun/TRUSTLENS%20AI/data/processed/dataset_manifest.json)  
> **Date:** November 25, 2026

---

## 1. Raw Dataset Preservation Audit

All raw files were verified **100% unchanged** via SHA-256 cryptographic checksum validation against `data/dataset_manifest.json`:

| Raw File | Format | Raw Rows | Integrity Status |
|---|---|---|---|
| `data/raw/scamshield/train.jsonl` | JSONL | 69,286 | ✅ SHA-256 Verified Unchanged |
| `data/raw/scamshield/val.jsonl` | JSONL | 8,192 | ✅ SHA-256 Verified Unchanged |
| `data/raw/scamshield/test.jsonl` | JSONL | 8,202 | ✅ SHA-256 Verified Unchanged |
| `data/raw/sms_phishing/Dataset_5971.csv` | CSV | 5,971 | ✅ SHA-256 Verified Unchanged |
| `data/raw/legitphish/url_features_extracted1.csv` | CSV | 101,219 | ✅ SHA-256 Verified Unchanged |

---

## 2. Cleaning, Normalization & Deduplication Summary

### 2.1 Text Corpus (`ScamShield` + `Mendeley SMS Phishing`)
- **Total Raw Rows Ingested:** `91,651` (`85,680` ScamShield + `5,971` Mendeley SMS)
- **Empty / Malformed Rows Dropped:** `0`
- **Missing Labels Dropped:** `0`
- **Cross-Dataset Overlap Detected:** `5,756` Mendeley SMS rows matched existing ScamShield raw texts.
- **Exact Raw Duplicates Removed:** `5,756`
- **Final Clean Text Records (`text_clean.parquet`):** **`85,895`**
- **Near-Duplicate Template Groups (`text_group_id`):** `84,917` unique groups (`978` near-duplicate templates normalized by `[URL]`, `[PHONE]`, `[OTP]`, `[EMAIL]`, `[UPI_ID]`).
- **Text Preprocessing Guarantees:**
  - Applied `NFKC` Unicode normalization (preserving Devanagari ligatures).
  - Stripped invalid Unicode control characters (`Cc` category) while preserving newlines and tabs.
  - Preserved meaningful punctuation and extracted URLs into separate `extracted_urls` column.
  - Preserved original labels (`original_label`) alongside normalized `canonical_label` (`legitimate`, `spam`, `smishing`, `scam`) and binary `is_threat`.

### 2.2 URL Corpus (`Mendeley LegitPhish`)
- **Total Raw Rows Ingested:** `101,219` (chunked `chunksize=25000`)
- **Corrupted Rows Dropped (Missing `ClassLabel`):** `1`
- **Empty URLs Dropped:** `0`
- **Duplicate URLs Removed:** `346`
- **Final Clean URL Records (`urls_clean.parquet`):** **`100,872`**
- **Unique Host Domain Groups (`domain_group_id`):** `63,962`
- **Zero-Hop Feature Alignment:** Re-extracted all 16 lexical/structural features directly via `ml/url_detection/features.py` without visiting or downloading any URL, eliminating the train-serving skew identified in Phase 2.0.
- **Label Mapping:** `original_label` (`0.0` -> `phishing` / `is_phishing=1`, `1.0` -> `legitimate` / `is_phishing=0`).

---

## 3. Leakage Prevention & Group-Aware Splitting

Prior to Phase 2.0.5, the existing splits exhibited **76 normalized text template leaks** and **3,373 domain-level URL leaks** between Train and Test.

To eliminate leakage permanently, `scripts/create_dataset_splits.py` uses **`StratifiedGroupKFold`** (`random_state=42`):

| Corpus | Split | Records | Positive Class % | Group Key | Cross-Split Leakage |
|---|---|---|---|---|---|
| **Text** | `text_train.parquet` | **68,716** | 36.29% (`is_threat=1`) | `text_group_id` | **0** |
| **Text** | `text_val.parquet` | **8,589** | 36.29% (`is_threat=1`) | `text_group_id` | **0** |
| **Text** | `text_test.parquet` | **8,590** | 36.29% (`is_threat=1`) | `text_group_id` | **0** |
| **URL** | `urls_train.parquet` | **72,051** | 62.94% (`is_phishing=1`) | `domain_group_id` | **0** |
| **URL** | `urls_val.parquet` | **14,410** | 62.94% (`is_phishing=1`) | `domain_group_id` | **0** |
| **URL** | `urls_test.parquet` | **14,411** | 62.94% (`is_phishing=1`) | `domain_group_id` | **0** |

---

## 4. Verification Test Results (`scripts/validate_processed_data.py`)

- ✅ **Raw Integrity:** All 6 raw dataset files passed SHA-256 verification.
- ✅ **Schema & Label Consistency:** Zero null labels, zero null cleaned texts, 100% canonical label compliance.
- ✅ **Reproducibility:** Deterministic `StratifiedGroupKFold` with fixed `RANDOM_SEED = 42` recorded in `data/processed/dataset_manifest.json`.
- ✅ **Zero Group Leakage:** Verified `0` overlap of `text_group_id`, `cleaned_text`, and `domain_group_id` across Train, Val, and Test.
