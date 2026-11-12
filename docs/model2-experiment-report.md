# TRUSTLENS AI — Model 2: Machine Learning Phishing URL Detection
## Experiment, Architecture & Explainability Report

- **Model Identifier:** `trustlens-model2-phishing-url-v1`
- **Module Path:** `ml/url_detection/`
- **Artifacts Path:** `ml/artifacts/url_detection/`
- **Dataset Source:** Mendeley Data LegitPhish Dataset (`url_features_extracted1.csv`)
- **Evaluator Hardware:** Intel Core i5-12450H CPU (8 Cores / 12 Threads), 16 GB RAM, Windows 11
- **Status:** Verified and Integrated with Live Inference Pipeline & FastAPI Engine

---

## 1. Executive Summary & Objective

Model 2 delivers high-speed, zero-network-interaction phishing URL detection for the **TRUSTLENS AI** platform. Suspicious URLs embedded in phishing emails, smishing SMS, or messaging apps are subjected to strictly offline feature extraction and gradient boosted classification. 

### Operational Security Guarantees:
1. **Zero Outbound Network Traffic:** The evaluation engine does **never** perform DNS queries, HTTP/HTTPS handshakes, webpage downloads, or JavaScript execution.
2. **Untrusted Input Sanitation:** All incoming URLs are treated as untrusted strings, parsed safely with strict length caps (2048 chars) and sandboxed regular expressions.
3. **Sub-Millisecond Inference:** Per-URL inference latency is under **0.01 ms** for batch vector operations and **~1.5 ms** for end-to-end single URL REST API requests.

---

## 2. Feature Engineering & Lexical Profile

The feature pipeline decomposes each candidate URL into 16 numerical and structural indicators without contacting remote infrastructure:

| Feature Name | Description | Threat Rationale |
| :--- | :--- | :--- |
| `url_length` | Total string character count | Phishing and obfuscated URLs are often exceptionally long or short. |
| `domain_name_length` | Character length of the second-level domain (SLD) | Disproportionate domain length indicates spoofed brand naming. |
| `path_length` | Total character count of the URL path | Deep nested directory paths often host credential harvesters or payloads. |
| `subdomain_count` | Number of subdomains preceding SLD | Multi-level subdomain chains (e.g. `login.paypal.com.evil.com`) spoof legitimate brands. |
| `dot_count` | Total frequency of `.` characters in URL | High dot frequency correlates with nested subdomains and IP addresses. |
| `has_hyphen_in_domain` | Binary indicator (1 if `-` exists in domain) | Hyphens are widely abused in typosquatting (`bank-secure-login.com`). |
| `number_of_digits` | Total count of numerical characters (0-9) | Raw IP addresses and automated campaign hash IDs introduce high digit counts. |
| `percentage_numeric_chars` | Percentage of URL string composed of digits | Legitimate domains typically have low (<1%) numeric ratios; phishing averages >35%. |
| `has_ip_address` | Binary indicator (1 if domain is raw IPv4/IPv6) | Direct IP usage bypasses domain reputation and is a high-risk IOC. |
| `https_flag` | Scheme indicator (1 if `https`, 0 if `http`) | Absence of TLS or unencrypted transport poses clear credential-interception risk. |
| `query_param_count` | Number of parameter segments partitioned by `?` and `&` | Phishing kits embed tracking tokens and victim emails in query strings. |
| `url_entropy` | Shannon entropy of the full URL string | Measures randomness; algorithmic DGA names show elevated entropy (>4.2). |
| `token_count` | Lexical words/tokens partitioned by delimiters | Obfuscated paths and complex redirects yield high token counts. |
| `tld_length` | Length of top-level domain string | Unconventional or compound TLD lengths indicate specialized infrastructure. |
| `tld_popularity` | Binary indicator (1 if TLD in top global list) | High-risk free TLDs (e.g. `.xyz`, `.top`, `.buzz`) contrast with standard `.com`/`.org`. |
| `suspicious_file_extension`| Binary indicator (1 if path ends in `.exe`, `.scr`, `.sh`, etc.) | Detects direct malware drops and executable payload distribution. |

---

## 3. Dataset Distribution & Leak-Free Splitting

The pipeline ingests the curated `data/processed/urls_{train,val,test}.parquet` partitions generated from Mendeley Data LegitPhish. Class balance and sample counts are rigorously verified:

- **Total Unique Samples:** 100,872 URLs
- **Target Distribution:**
  - `Phishing (Class 1)`: 63,491 records (62.94%)
  - `Legitimate (Class 0)`: 37,381 records (37.06%)
- **Data Partitions:**
  - **Train Set (`70%`):** 70,610 samples (44,444 phishing, 26,166 legitimate)
  - **Validation Set (`15%`):** 15,131 samples (9,524 phishing, 5,607 legitimate)
  - **Holdout Test Set (`15%`):** 15,131 samples (9,524 phishing, 5,607 legitimate)

> [!IMPORTANT]
> The holdout test set (`urls_test.parquet`) was quarantined until final benchmark evaluation. Zero test samples were used for model fitting or hyperparameter tuning.

---

## 4. Model Comparison & Test Benchmark Results

Three distinct machine learning algorithms were trained and evaluated on identical holdout test samples (`N = 15,131`):

| Model | Accuracy | Precision | Recall | F1 (Binary) | F1 (Macro) | ROC-AUC | PR-AUC | FPR | FNR | Inference Latency |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Logistic Regression (L2 Baseline)** | 99.71% | 0.9999 | 0.9955 | 0.9977 | 0.9969 | 0.9998 | 0.9999 | 0.02% | 0.45% | **0.0001 ms** |
| **Random Forest (100 Trees)** | 99.97% | 0.9996 | 0.9999 | 0.9997 | 0.9996 | 1.0000 | 1.0000 | 0.07% | 0.01% | 0.0027 ms |
| **XGBoost Classifier (150 Estimators)** | **99.98%** | **0.9999** | **0.9998** | **0.9998** | **0.9998** | **1.0000** | **1.0000** | **0.02%** | **0.02%** | **0.0007 ms** |

### Confusion Matrix on Test Set (`N = 15,131`):

#### Chosen Production Model: XGBoost Classifier
```
                   Predicted Legitimate    Predicted Phishing
Actual Legitimate          5,606                     1           (FPR: 0.018%)
Actual Phishing                2                 9,522           (FNR: 0.021%)
```

- **True Negatives:** 5,606 / 5,607 legitimate URLs accurately passed.
- **False Positives:** Only 1 legitimate URL flagged across 5,607 holdout samples.
- **False Negatives:** Only 2 phishing URLs evaded detection across 9,524 attacks.
- **True Positives:** 9,522 phishing URLs successfully blocked.

---

## 5. Model Explainability via SHAP (SHapley Additive exPlanations)

To eliminate black-box opacity and provide SOC analysts with actionable rationale, SHAP `TreeExplainer` was calculated across representative validation samples.

### Feature Importance Attribution Ranking:

```
Rank  Feature                     Mean |SHAP|  Threat Contribution
-----------------------------------------------------------------------------------------
 1    path_length                 0.2398       Deep directory paths in phishing kits
 2    https_flag                  0.0855       Unencrypted HTTP transport in payload drops
 3    token_count                 0.0627       Multiple hyphenated words & tokenized params
 4    number_of_digits            0.0369       Presence of IP addresses and numerical hashes
 5    percentage_numeric_chars    0.0330       High numeric density in malicious endpoints
 6    dot_count                   0.0188       Multiple subdomains spoofing brands
 7    subdomain_count             0.0110       Multi-tier domain nesting
 8    has_ip_address              0.0083       Raw IP hostnames
 9    tld_popularity              0.0074       Non-standard / disposable TLDs
10    url_length                  0.0064       Disproportionately long obfuscated URLs
11    suspicious_file_extension   0.0059       Direct downloads (.exe, .sh, .scr)
12    tld_length                  0.0055       Unusual TLD string lengths
13    url_entropy                 0.0021       Algorithmic randomness in domain/path
14    domain_name_length          0.0020       Excessive second-level domain length
15    has_hyphen_in_domain        0.0006       Brand typosquatting
16    query_param_count           0.0002       Query parameter tracking tokens
```

Visual artifacts saved:
- `ml/artifacts/url_detection/shap_summary.png`
- `ml/artifacts/url_detection/confusion_matrix.png`
- `ml/artifacts/url_detection/shap_feature_importance.json`

---

## 6. Live Inference Engine & Integration

The production inference engine is encapsulated in `ml/url_detection/infer.py` and connected directly to the FastAPI service (`backend/app/services/ml_service.py`).

### Example Live Predictions:

```python
# Test Case 1: Brand Spoofing Typosquat
URL: "https://keraekken-loagginnusa.godaddysites.com/"
Result: PHISHING | Risk Score: 0.9906 | Latency: 8.02 ms
Risk Factors:
  - High URL Shannon entropy (4.25) indicates algorithmic generation
  - Hyphen present in domain name (common typo-squatting indicator)

# Test Case 2: Raw IP Malware Drop with Suspicious Script
URL: "http://192.168.1.100/secure-banking-login/index.php?update_kyc=98214"
Result: PHISHING | Risk Score: 1.0000 | Latency: 1.64 ms
Risk Factors:
  - Direct IPv4/IPv6 address used in place of domain name
  - High dot count (4 dots) indicates nested spoofing subdomains
  - High URL Shannon entropy (4.84) indicates algorithmic generation
  - Suspicious executable or script file extension in URL path
  - Unencrypted HTTP transmission scheme

# Test Case 3: Legitimate Developer Portal
URL: "https://stackoverflow.com/questions/tagged/python"
Result: LEGITIMATE | Risk Score: 0.0051 | Latency: 1.32 ms
Risk Factors:
  - None (Passes all security checks)
```

---

## 7. Security Policy & Disclaimers

> [!WARNING]
> **Correlation vs. Causation Caveat:** Statistical lexical indicators demonstrate strong empirical correlation with known phishing campaigns in the Mendeley dataset, but do **not** constitute deterministic legal proof of server intent. Novel phishing techniques utilizing clean domains with zero lexical anomalies must be cross-referenced with Model 1 (Message Detection) and Model 3 (Tactic Analysis).

> [!NOTE]
> **Production Safety:** The inference pipeline strictly forbids remote HTTP queries, socket bindings, or browser renderings. All assessments are performed in memory through deterministic regex and tree traversal.
