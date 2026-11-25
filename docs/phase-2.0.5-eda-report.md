# TRUSTLENS AI — PHASE 2.0.5: EXPLORATORY DATA ANALYSIS (EDA) REPORT

> **Scope:** Clean Unified Text Corpus (`n=85,895`) & Clean URL Corpus (`n=100,872`)  
> **Visualizations:** `docs/screenshots/eda/*.png`  
> **Date:** November 25, 2026

---

## 1. Dataset Source Distribution
Across all raw ingested corpora (`192,870` total raw rows):
- **LegitPhish (Mendeley URL):** `101,219` raw records (52.48%)
- **ScamShield (HuggingFace):** `85,680` raw records (44.42%)
- **SMS Phishing (Mendeley 5971):** `5,971` raw records (3.10%)

![Dataset Source Distribution](file:///c:/Users/jaswant%20karun/TRUSTLENS%20AI/docs/screenshots/eda/dataset_source_distribution.png)

---

## 2. Canonical Class Distributions

### Text Corpus (`n=85,895`)
- **Legitimate (`is_threat=0`):** `54,724` (63.71%)
- **Threat (`is_threat=1`):** `31,171` (36.29%), decomposed into:
  - `scam`, `smishing`, and `spam` canonical categories.
- Balanced uniformly across Train (`36.29%`), Val (`36.29%`), and Test (`36.29%`).

### URL Corpus (`n=100,872`)
- **Phishing (`is_phishing=1`):** `63,492` (62.94%)
- **Legitimate (`is_phishing=0`):** `37,380` (37.06%)
- Balanced uniformly across Train (`62.94%`), Val (`62.94%`), and Test (`62.94%`).

![Class Distribution](file:///c:/Users/jaswant%20karun/TRUSTLENS%20AI/docs/screenshots/eda/class_distribution.png)

---

## 3. Language Coverage & Policy

Direct script and token-level language classification on all `85,895` clean text messages:

| Language | Total Records | Share (%) | Train | Val | Test | Support Policy |
|---|---|---|---|---|---|---|
| **English** | **78,255** | **91.11%** | 62,604 | 7,854 | 7,797 | Full Production Support |
| **Hindi (Devanagari)** | **6,342** | **7.38%** | 5,042 | 625 | 675 | Supported (Requires Transformer Fine-Tuning for high recall) |
| **Hinglish (Romanized)** | **1,298** | **1.51%** | 1,070 | 110 | 118 | Supported |
| **Tamil / Bengali** | **0** | **0.00%** | 0 | 0 | 0 | **Not Supported / Optional** (Zero validated samples) |

![Language Distribution](file:///c:/Users/jaswant%20karun/TRUSTLENS%20AI/docs/screenshots/eda/language_distribution.png)

---

## 4. Missing Values & Duplicate Audit

- **Missing Values:** Only `1` row in raw LegitPhish lacked `ClassLabel` (dropped). Both processed datasets have `0` missing values across all required fields.
- **Duplicates & Overlaps:**
  - `5,756` Mendeley SMS rows overlapped with ScamShield and were deduplicated.
  - `978` near-duplicate text templates were grouped under shared `text_group_id` hashes so templates cannot split across Train and Test.
  - `346` duplicate URLs were removed from LegitPhish, and `100,872` unique URLs were grouped across `63,962` unique domain hosts.

![Missing Values](file:///c:/Users/jaswant%20karun/TRUSTLENS%20AI/docs/screenshots/eda/missing_values.png)
![Duplicate Counts](file:///c:/Users/jaswant%20karun/TRUSTLENS%20AI/docs/screenshots/eda/duplicate_counts.png)
