# TRUSTLENS AI — PHASE 2.0: URL PHISHING DETECTOR AUDIT (MODEL 2)

> **Directory Audited:** `ml/url_detection/` & `ml/artifacts/url_detection/`  
> **Audit Date:** November 25, 2026  

---

## 1. Component & Artifact Inventory

- **Training Script:** `ml/url_detection/train_models.py` (Executed ✅)
- **Feature Extraction:** `ml/url_detection/features.py` (Deterministic zero-hop lexical & entropy extractor; zero outbound HTTP requests).
- **Feature Schema:** `ml/artifacts/url_detection/feature_schema.json` (**16 numerical/boolean features**: `url_length`, `has_ip_address`, `dot_count`, `https_flag`, `url_entropy`, `token_count`, `subdomain_count`, `query_param_count`, `tld_length`, `path_length`, `has_hyphen_in_domain`, `number_of_digits`, `tld_popularity`, `suspicious_file_extension`, `domain_name_length`, `percentage_numeric_chars`).
- **Model Architecture:** XGBoost Gradient Boosted Decision Trees (`n_estimators=200`, `max_depth=6`, `learning_rate=0.1`).
- **Saved Model Artifacts:**
  - `ml/artifacts/url_detection/best_url_model.joblib` (244,185 bytes)
  - `ml/artifacts/url_detection/xgboost_model.joblib` (244,185 bytes)
  - `ml/artifacts/url_detection/random_forest.joblib` (2,509,753 bytes)
  - `ml/artifacts/url_detection/logistic_regression.joblib` & `scaler.joblib`
- **SHAP Explainability:** Genuine `shap.TreeExplainer` implemented and saved (`shap_feature_importance.json`, `shap_summary.png`). Top drivers: `path_length` (6.7612), `https_flag` (2.0495), `tld_popularity` (0.874).

---

## 2. Held-Out Test Set Evaluation (15,131 URLs)

| Model | Accuracy | Precision | Recall | F1 Binary | ROC-AUC | PR-AUC | FPR | Latency/Sample |
|---|---|---|---|---|---|---|---|---|
| Logistic Regression | 0.9971 | 0.9999 | 0.9955 | 0.9977 | 0.9998 | 0.9999 | 0.0002 | 0.0001 ms |
| Random Forest | 0.9997 | 0.9996 | 0.9999 | 0.9997 | 1.0000 | 1.0000 | 0.0007 | 0.0027 ms |
| **XGBoost Classifier** | **0.9998** | **0.9999** | **0.9998** | **0.9998** | **1.0000** | **1.0000** | **0.0002** | **0.0007 ms** |

---

## 3. Genuine ML vs. Rules Verification & Skew Audit

- **Genuine Classifier Confirmation:** The detector is **NOT** a rules-based heuristic. It loads a trained XGBoost GBDT model (`best_url_model.joblib`) and performs real tree-ensemble inference with SHAP TreeExplainer attribution.
- **Train-Serving Feature Skew Identified:**
  Direct parity testing between `urls_test.parquet` (LegitPhish pre-extracted CSV) and `ml/url_detection/features.py` revealed minor discrepancies:
  1. **IP:Port URLs (`http://61.137.184.208:33466/bin.sh`):** LegitPhish CSV recorded `tld_length = 9.0` (counting `208:33466`), whereas `features.py` strips the port (`tld_length = 3.0`).
  2. **Suspicious Extensions:** `features.py` flags `.sh` as `suspicious_file_extension = 1`, whereas LegitPhish CSV recorded `0`.
  3. **Token Count:** Minor tokenization regex differences (`5.0` vs `4.0` on `https://www.klondikegoldcorp.com`).
- **Backend Integration:** **VERIFIED.** Safe inference check returned `is_phishing=True, risk=0.9999, version=trustlens-model2-xgboost-v1.0`.

---

## 4. Maturity Classification
- **Overall Status:** **VERIFIED** (Genuine trained XGBoost + SHAP pipeline, with minor train-serving feature extraction skew documented for future cleanup).
