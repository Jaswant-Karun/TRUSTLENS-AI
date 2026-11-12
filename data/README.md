# TRUSTLENS AI — Threat Data Repository

This directory contains the training, evaluation, and live threat intelligence datasets used by TRUSTLENS AI.

## Directory Structure
- `raw/scamshield/`: Raw Sidzzz07 ScamShield multilingual corpus (Hugging Face). Immutable raw store.
- `raw/sms_phishing/`: Raw SMS Phishing Dataset for Machine Learning (Mendeley Data, 5,971 records). Immutable raw store.
- `raw/legitphish/`: Raw LegitPhish Dataset (Mendeley Data, 101,219 labelled URLs with 17 features). Immutable raw store.
- `processed/`: Deduplicated, validated, and normalized splits (train/val/test) in Parquet format.
- `external/`: Cached threat feeds (URLhaus, OpenPhish, PhishTank) metadata.

## Provenance & Integrity Policy
1. Files placed in `raw/` are **read-only** and must never be altered in-place.
2. All data cleaning, deduplication, and label standardization must be executed via automated preprocessing pipelines in `ml/`.
3. Processed splits are saved with cryptographic SHA-256 checksums to ensure reproducibility.

