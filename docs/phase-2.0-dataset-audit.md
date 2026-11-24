# TRUSTLENS AI — PHASE 2.0: FORENSIC DATASET AUDIT

> **Audit Scope:** `data/raw/`, `data/processed/`, `data/external/`, `data/dataset_manifest.json`  
> **Verification Method:** Direct inspection of all CSV, JSONL, and Parquet files via Python/Pandas.  
> **Audit Date:** November 25, 2026

---

## 1. Raw Datasets Inventory

### 1.1 ScamShield: Multilingual Smishing & Social Engineering Corpus
- **Actual Source:** Hugging Face (`sidzzz07/scamshield-dataset`)
- **License & Provenance:** MIT License
- **Local File Paths & Record Counts:**
  - `data/raw/scamshield/train.jsonl` (JSONL, 35.80 MB): **69,286** rows × 9 cols
  - `data/raw/scamshield/val.jsonl` (JSONL, 4.17 MB): **8,192** rows × 9 cols
  - `data/raw/scamshield/test.jsonl` (JSONL, 4.19 MB): **8,202** rows × 9 cols
  - **Total Raw Records:** **85,680**
- **Columns:** `id`, `text`, `language`, `source_dataset`, `is_scam`, `head1_social_engineering`, `head2_scam_intent`, `split_group`, `metadata`
- **Label Columns:** `is_scam` (binary), `head1_social_engineering` (multi-label dict), `head2_scam_intent` (categorical intent)
- **Language Distribution (Raw Splits):**
  - Train: English (61,058), Hindi (5,436), Hinglish (2,792)
  - Val: English (7,631), Hindi (456), Hinglish (105)
  - Test: English (7,634), Hindi (460), Hinglish (108)
  - **Important Finding:** Zero Bengali or Tamil records exist in the dataset.
- **Missing Values:** `0` missing values across all splits.
- **Usability:** **VERIFIED** for English & Hinglish binary scam detection and 9-label tactic detection; **PARTIAL** for Hindi (5,436 train samples, 460 test samples with low threat-class support).

### 1.2 SMS Phishing Dataset for Machine Learning and Pattern Recognition
- **Actual Source:** Mendeley Data (`10.17632/f45bkkt8pr.1`, Mishra & Soni)
- **License & Provenance:** CC BY 4.0
- **Local File Path:** `data/raw/sms_phishing/Dataset_5971.csv` (CSV, 595,987 bytes)
- **Actual Record Count:** **5,971** rows × 5 cols
- **Columns:** `LABEL`, `TEXT`, `URL`, `EMAIL`, `PHONE`
- **Label Column & Class Distribution:** `LABEL`: `ham` (4,844), `Smishing` (616), `spam` (466), `Spam` (23), `smishing` (22)
- **Missing Values:** `0` missing in CSV (URL/EMAIL/PHONE columns contain `"no"` string flags rather than nulls).
- **Duplicates:** **17** exact row duplicates; **22** duplicate `TEXT` values.
- **Overlap Finding:** 5,756 records overlap with ScamShield; only **215 novel records** were added during preprocessing.
- **Usability:** **VERIFIED** (deduplicated into unified `text_train.parquet`).

### 1.3 LegitPhish Dataset
- **Actual Source:** Mendeley Data (`10.17632/hx4m73v2sf.2`, Potpelwar et al.)
- **License & Provenance:** CC BY 4.0
- **Local File Path:** `data/raw/legitphish/url_features_extracted1.csv` (CSV, 8.96 MB)
- **Actual Record Count:** **101,219** rows × 18 cols
- **Columns:** `URL`, `url_length`, `has_ip_address`, `dot_count`, `https_flag`, `url_entropy`, `token_count`, `subdomain_count`, `query_param_count`, `tld_length`, `path_length`, `has_hyphen_in_domain`, `number_of_digits`, `tld_popularity`, `suspicious_file_extension`, `domain_name_length`, `percentage_numeric_chars`, `ClassLabel`
- **Missing Values:** `1` corrupted row with missing `ClassLabel`.
- **Duplicates:** **346** exact row duplicates / duplicate `URL` strings.
- **Usability:** **VERIFIED** (cleaned to 100,872 unique URLs).

### 1.4 External Datasets (`data/external/`)
- Directory contains only `.gitkeep` (0 datasets).

---

## 2. Processed Datasets Inventory (`data/processed/*.parquet`)

| File | Rows × Cols | Class Distribution | Language Distribution | Missing Values | Duplicates |
|---|---|---|---|---|---|
| `text_train.parquet` | **69,501 × 15** | `0`: 44,347 (63.8%)<br>`1`: 25,154 (36.2%) | En: 62,929, Hi: 5,426, Hinglish: 1,146 | `raw_language`: 215, `split`: 215 (from Mendeley) | 0 `raw_text` dups; **758** `cleaned_text` dups |
| `text_val.parquet` | **8,192 × 14** | `0`: 5,186 (63.3%)<br>`1`: 3,006 (36.7%) | En: 7,658, Hi: 456, Hinglish: 78 | 0 | 0 |
| `text_test.parquet` | **8,202 × 14** | `0`: 5,191 (63.3%)<br>`1`: 3,011 (36.7%) | En: 7,668, Hi: 460, Hinglish: 74 | 0 | 0 |
| `urls_train.parquet` | **70,610 × 21** | `1` (Phish): 44,444 (62.9%)<br>`0` (Legit): 26,166 (37.1%) | N/A | 0 | 0 |
| `urls_val.parquet` | **15,131 × 21** | `1`: 9,524 (62.9%)<br>`0`: 5,607 (37.1%) | N/A | 0 | 0 |
| `urls_test.parquet` | **15,131 × 21** | `1`: 9,524 (62.9%)<br>`0`: 5,607 (37.1%) | N/A | 0 | 0 |
| `sms_phishing_clean.parquet` | **5,971 × 11** | Canonical Ham/Spam/Smishing | En: 5,967, Hinglish: 4 | 0 | 17 row dups |

---

## 3. Audit Conclusions
- All raw and processed datasets exist locally with verified SHA-256 checksums in `dataset_inventory.json`.
- **Minor Discrepancy:** `text_train.parquet` contains 758 duplicate `cleaned_text` strings after URL normalization (`<URL>` token replacement), which is expected when identical scam templates differ only by URL.
- **Language Gap:** Dataset only covers English, Hindi, and Hinglish. Claims of Bengali and Tamil support in `model_registry.json` are unsupported by training data.
