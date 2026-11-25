# TRUSTLENS AI — REAL-WORLD DATA ACQUISITION & GOVERNANCE STRATEGY

> **Phase:** 3.0 Strategy (No Datasets Downloaded or Retrained Yet)  
> **Guiding Rule:** Never assume public accessibility grants commercial/training rights; never visit suspicious URLs; never mix training and evaluation splits.

---

## 1. Data Gaps Identified in Phase 3.0 Audit

1. **Hindi & Regional Indian Language Scam Coverage:** Current text model has only `460` Hindi test samples and `0.5455` recall; Bengali and Tamil have zero verified test coverage.
2. **Modern Benign URL Calibration:** `LegitPhish` (`101,219` URLs) causes a `15.33%` false-positive rate on modern legitimate URLs with long paths, subdomains, or SaaS query strings.
3. **Fake Investment / Crypto / Pig-Butchering Tactics:** Currently `UNAVAILABLE` due to zero verified ground-truth training annotations.

---

## 2. Vetted Real-World Data Sources (By Licensing & Intended Use)

| Source | Data Type | Languages | License / Terms | Intended Use | Quality & Legal Notes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **ScamShield (`sidzzz07/scamshield-dataset`)** *(existing)* | SMS/smishing + tactic heads | EN, HI, Hinglish | **MIT** | Training, Val, Test | Baseline corpus; expand Hindi slice via stratified sampling/curation |
| **SMS Phishing (`10.17632/f45bkkt8pr.1`)** *(existing)* | SMS Ham/Spam/Smishing | EN | **CC BY 4.0** | Training, Val, Test | Requires attribution; deduplicate against ScamShield |
| **LegitPhish (`10.17632/hx4m73v2sf.2`)** *(existing)* | URL lexical features | Language-agnostic | **CC BY 4.0** | Training, Val | Over-represents older phishing/benign patterns; rebalance with modern benign URLs |
| **Tranco Top-1M Domain/URL List** (`tranco-list.eu`) | Benign popular domains/URLs | Global | **Open research list** (verify ToS) | **Benign URL Calibration & FPR Testing** | Ideal for reducing 15.33% URL FPR on legitimate SaaS/banking/news domains |
| **URLhaus (abuse.ch)** | Active malware/phishing URLs | Global | **CC0 (Public Domain)** | **Threat Intel Feed & Evaluation** | High-confidence malicious URLs; update daily via n8n; never visit URLs |
| **OpenPhish (Community) / PhishTank** | Verified phishing URLs | Global | **Feed ToS (check commercial terms)** | **Threat Intel & Evaluation Only** | Verify commercial license before using in model training weights |
| **CERT-In / RBI / Chakshu / FTC Scam Advisories** | Official scam templates & advisories | EN, HI, regional | **Public Government Advisories** | **Evaluation & Tactic Taxonomy Grounding** | Use published advisory patterns for benchmark validation & user education |
| **Hugging Face Multilingual Toxic/Spam/Scam Corpora** *(e.g. IndicNLP / AI4Bharat benign text)* | Clean Hindi, Tamil, Bengali benign text | HI, TA, BN | **CC BY / MIT / Apache-2.0** *(verify per dataset)* | **Negative (Benign) Class Balancing** | Prevents over-flagging normal Hindi/Tamil/Bengali messages as scams |
| **Consented User Community Reports (`scam_reports`)** | User-submitted scam reports | Multilingual | **Explicit User Opt-In Consent** | **Human-Reviewed Evaluation -> Training** | Strict PII redaction (phone numbers, OTPs, names) & reviewer approval required before any ML use |

---

## 3. Anti-Leakage & Governance Pipeline

1. **Deduplication by Canonical Hash & MinHash/SimHash:** Group near-identical messages and root domains (`domain_group_id`) via `StratifiedGroupKFold` before splitting.
2. **Strict Golden Evaluation Holdout:** Maintain a frozen, time-separated evaluation set (`data/golden_eval/`) that is never touched during feature engineering or hyperparameter tuning.
3. **PII Redaction Gate:** Strip phone numbers, Aadhaar/PAN patterns, account numbers, and personal names before storing consented community reports for ML review.
4. **Dataset Manifest Provenance:** Every new dataset must be registered in `data/dataset_manifest.json` with SHA-256, license, source URL, and allowed usage (`train | eval | threat_intel_only`).
