# TRUSTLENS AI — Threat Intelligence Data Repository

**Stage:** Day 2 — Automated Dataset Download, Ingestion & Verification  
**Platform:** TRUSTLENS AI (Multilingual Digital Fraud Intelligence & Prevention Platform)  
**Memory & Architecture Policy:** Streaming 1MB chunk processing, immutable raw stores, cryptographic verification.

---

## 1. Directory Structure

```
data/
├── dataset_manifest.json          # Machine-readable inventory of all sources, URLs, licenses & hashes
├── dataset_verification_results.json # Full verification audit report with row counts & class statistics
├── README.md                      # This repository documentation
├── raw/                           # IMMUTABLE raw datasets (read-only original files)
│   ├── scamshield/
│   │   ├── train.jsonl            # 69,286 rows (35.80 MB, SHA-256: 418b1d7a...)
│   │   ├── val.jsonl              # 8,192 rows  (4.17 MB, SHA-256: 12a8a8dc...)
│   │   └── test.jsonl             # 8,202 rows  (4.19 MB, SHA-256: a3a569a6...)
│   ├── sms_phishing/
│   │   ├── Dataset_5971.zip       # Original Mendeley archive (244.70 KB, SHA-256: 9bbf3188...)
│   │   └── Dataset_5971.csv       # Extracted CSV, 5,971 rows (595.99 KB, SHA-256: 649844f1...)
│   └── legitphish/
│       └── url_features_extracted1.csv # 101,219 rows (8.55 MB, SHA-256: 8685e790...)
├── processed/                     # Preprocessed, deduplicated Parquet splits for ML models
└── external/                      # Threat intelligence feeds (URLhaus, OpenPhish) cache
```

---

## 2. Acquired Datasets & Provenance

### 2.1 ScamShield: Multilingual Smishing & Social Engineering Corpus
- **Source:** Hugging Face (`sidzzz07/scamshield-dataset`)
- **Direct URL:** [https://huggingface.co/datasets/sidzzz07/scamshield-dataset](https://huggingface.co/datasets/sidzzz07/scamshield-dataset)
- **Version:** 1.0.0
- **License:** MIT License (Permissive open source)
- **Authors / Creators:** sidzzz07
- **Corpus Size:** 85,680 total samples across 3 splits:
  - `train.jsonl`: 69,286 records (44,221 legit, 25,065 scam)
  - `val.jsonl`: 8,192 records (5,186 legit, 3,006 scam)
  - `test.jsonl`: 8,202 records (5,191 legit, 3,011 scam)
- **Languages:** English (76,323 / 89.08%), Hindi (6,352 / 7.41%), Hinglish (3,005 / 3.51%).
- **Primary Schema:** `id`, `text`, `language`, `source_dataset`, `is_scam`, `head1_social_engineering`, `head2_scam_intent`, `split_group`, `metadata`.

### 2.2 SMS Phishing Dataset for Machine Learning
- **Source:** Mendeley Data
- **DOI:** `10.17632/f45bkkt8pr.1`
- **Direct URL:** [https://data.mendeley.com/datasets/f45bkkt8pr/1](https://data.mendeley.com/datasets/f45bkkt8pr/1)
- **Version:** 1
- **License:** Creative Commons Attribution 4.0 International (CC BY 4.0)
- **Authors:** Sandhya Mishra, Devpriya Soni
- **Records:** 5,971 SMS records
- **Columns (5):** `LABEL`, `TEXT`, `URL`, `EMAIL`, `PHONE`
- **Raw Label Distribution:** `ham`: 4,844, `Smishing`: 616, `spam`: 466, `Spam`: 23, `smishing`: 22.

### 2.3 LegitPhish Dataset
- **Source:** Mendeley Data
- **DOI:** `10.17632/hx4m73v2sf.2`
- **Direct URL:** [https://data.mendeley.com/datasets/hx4m73v2sf/2](https://data.mendeley.com/datasets/hx4m73v2sf/2)
- **Version:** 2
- **License:** Creative Commons Attribution 4.0 International (CC BY 4.0)
- **Authors:** Rachana Potpelwar, Uday Kulkarni, Jaishri Waghmare
- **Records:** 101,219 URL records
- **Columns (18):** `URL`, `url_length`, `has_ip_address`, `dot_count`, `https_flag`, `url_entropy`, `token_count`, `subdomain_count`, `query_param_count`, `tld_length`, `path_length`, `has_hyphen_in_domain`, `number_of_digits`, `tld_popularity`, `suspicious_file_extension`, `domain_name_length`, `percentage_numeric_chars`, `ClassLabel`.
- **Raw Label Distribution:** Phishing (`0`): 63,678, Legitimate (`1`): 37,540, Empty (`''`): 1.

---

## 3. Cryptographic Verification & File Integrity

All downloaded files are verified against SHA-256 checksums computed using streaming 1MB buffers:

| Dataset | File | Size (Bytes) | Size (MB) | Format | SHA-256 Checksum |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **ScamShield** | `train.jsonl` | 37,541,871 | 35.80 MB | JSONL | `418b1d7af29945135284d4293230c75b26c3bccd3dda5382caf730fbc0e49cbf` |
| **ScamShield** | `val.jsonl` | 4,377,027 | 4.17 MB | JSONL | `12a8a8dc62de78aeb4881a902bb0e829134f1e6f277ade90b02743134112789f` |
| **ScamShield** | `test.jsonl` | 4,393,460 | 4.19 MB | JSONL | `a3a569a69529fe3398445bdd31046bfbcc19755c6b87f1133c8ed6c0134cdd6c` |
| **SMS Phishing** | `Dataset_5971.zip` | 244,698 | 0.23 MB | ZIP | `9bbf3188fdad81495d8e82825648b9b63b53fc86841a3d26c02629990b233cc3` |
| **SMS Phishing** | `Dataset_5971.csv` | 595,987 | 0.57 MB | CSV | `649844f1c62a6b27e145eaf17a65f7010c56c390e11a794ea8329993a05ba71e` |
| **LegitPhish** | `url_features_extracted1.csv` | 8,963,838 | 8.55 MB | CSV | `8685e7901c3b4e73eb43c106cb166cc932dd14f76960a032c713c2c32f09dbcd` |

---

## 4. Immutability & Security Policy

1. **Read-Only Raw Store:** Files inside `data/raw/` must NEVER be modified, cleaned, or overwritten in-place.
2. **Safe Extraction:** Archives are extracted with Zip Slip path-traversal guards and CRC integrity validation.
3. **Memory Safety:** Streaming operations (1MB chunks) ensure full compatibility with 16 GB RAM developer workstations.
4. **Anti-Fabrication:** Synthetic samples or simulated rows are strictly prohibited. Missing records, empty labels, and casing variations are documented truthfully as observed.

---

## 5. Reproduction Commands

To re-run dataset download and update the manifest:
```bash
python scripts/download_datasets.py
```

To re-run cryptographic verification and dataset schema audit:
```bash
python scripts/verify_datasets.py
```
