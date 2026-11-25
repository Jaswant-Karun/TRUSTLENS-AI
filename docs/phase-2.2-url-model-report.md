# TRUSTLENS AI — PHASE 2.2: PHISHING URL CLASSIFICATION ENGINE REPORT

> **Dataset Version:** `2.0.5` (LegitPhish CC BY 4.0, `100,872` unique URLs, `63,962` domain groups, `StratifiedGroupKFold`, `random_seed=42`)  
> **Candidate Artifacts Directory:** `ml/artifacts/url_detection/v2.2_candidate/` *(Production artifacts preserved untouched)*  
> **Scripts Created/Updated:** `ml/url_detection/features.py`, `train.py`, `evaluate.py`, `predict.py`, `tests/test_url_features.py`  
> **Date:** November 25, 2026

---

## 1. Safe Feature Extraction & Unit Tests

- **Zero-Hop Guarantee:** `ml/url_detection/features.py` performs deterministic lexical, structural, and Shannon entropy extraction without making any DNS, TCP, or HTTP requests.
- **Unit Test Verification (`tests/test_url_features.py`):** **5 / 5 tests passed in `0.002s`**, including mocked `socket.getaddrinfo` assertion confirming zero network resolution.
- **Train-Serving Alignment:** All 16 core features in `FEATURE_COLUMNS` were re-extracted identically across `urls_{train,val,test}.parquet`, eliminating the Phase 2.0 IP:port `tld_length` and `.sh` skew.

---

## 2. Model Comparison on Untouched Held-Out Test Set (`n = 14,411` URLs, `9,076` Unseen Domains)

| Model | Accuracy | Precision | Recall | F1 Binary | Macro F1 | ROC-AUC | PR-AUC | FPR | FNR | Latency (ms) | Size (MB) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Logistic Regression (Scaled, Balanced) | 0.9966 | 0.9992 | 0.9954 | 0.9973 | 0.9964 | 0.9997 | 0.9999 | **0.0013** | 0.0046 | 0.00016 ms | 0.0009 MB |
| Random Forest (100 Trees, Balanced) | 0.9970 | 0.9953 | 1.0000 | 0.9977 | 0.9968 | 1.0000 | 1.0000 | 0.0081 | 0.0000 | 0.00772 ms | 2.3531 MB |
| **XGBoost Classifier (GBDT)** | **0.9990** | **0.9983** | **1.0000** | **0.9992** | **0.9989** | **1.0000** | **1.0000** | 0.0028 | **0.0000** | 0.00261 ms | 0.2999 MB |

### Confusion Matrix (`xgboost_model`, `[legitimate, phishing]`)
```
[[5325,   15],
 [   0, 9071]]
```

---

## 3. Domain & Scheme Generalization Analysis (`xgboost_model`)

Evaluated across completely unseen domain groups in `urls_test.parquet`:
- **Popular TLDs (`.com/.org/.net/.in`, `5,598` URLs):** Macro F1 `0.9970`, Phishing Recall `1.0000`
- **Non-Popular / Long-Tail TLDs (`8,813` URLs):** Macro F1 `1.0000`, Phishing Recall `1.0000`
- **HTTPS Scheme URLs (`5,654` URLs):** Macro F1 `0.9876`, Phishing Recall `1.0000`
- **HTTP / Non-HTTPS URLs (`8,757` URLs):** Macro F1 `1.0000`, Phishing Recall `1.0000`

---

## 4. SHAP Explainability & Safety Limitations

Implemented via `shap.TreeExplainer` in `ml/url_detection/evaluate.py` and `predict.py`.
- **Top Global SHAP Drivers (`mean(|SHAP|)`):**
  1. `path_length` (`4.3603`)
  2. `https_flag` (`3.6260`)
  3. `percentage_numeric_chars` (`1.1429`)
  4. `tld_popularity` (`0.9468`)
  5. `dot_count` (`0.6443`)
- **Mandatory Safety Disclaimer (Returned by `predict.py`):**
  > *"Lexical and structural features alone do not constitute definitive proof that a URL is malicious. A missing threat-intelligence match or low lexical risk score does not automatically classify a URL as safe."*

---

## 5. Saved Artifacts & SHA-256 Checksums (`ml/artifacts/url_detection/v2.2_candidate/`)

| Artifact | Size (MB) | SHA-256 |
|---|---|---|
| `xgboost_model.joblib` | 0.2999 MB | `b7ed50c6fe1a3c8aa79bd87c129b8a969cd320a057b111e41ad30be63d52cd3f` |
| `random_forest.joblib` | 2.3531 MB | `55c74f3c82a0292c90135f4ab039af398f74099f40651767050de5f499e9257d` |
| `logistic_regression.joblib` | 0.0009 MB | `0abc712c75db7aed5a2cebf75ef0ac1bef0b7a746b5196f5e0a6ed2357aaf6e8` |
| `scaler.joblib` | 0.0009 MB | `15983600df7c772983ec5b63b05d0301c80dba82730e9e2144ab5fefa5749e10` |

> **Stop Condition Honored:** Existing production backend routes and production artifacts were not modified.
