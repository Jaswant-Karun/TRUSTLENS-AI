# TRUSTLENS AI — ML & FRAUD INTELLIGENCE AUDIT (PHASE 0)

> **Sources Inspected:** `backend/app/ml_engine/engine.py`, `backend/app/services/ml_service.py`, `backend/app/services/risk_service.py`, `ml/artifacts/model_dashboard_data.json`, `data/processed/dataset_manifest.json`

---

## 1. Model Inventory & Actual Evaluation Status

| Track | Architecture & Artifact | Dataset & Split | Verified Metrics | Known Limitations |
| :--- | :--- | :--- | :--- | :--- |
| **1. Text Scam** | Feature Union (Word+Char TF-IDF) + Calibrated LinearSVC (`ml/artifacts/text_detection/best_model.joblib`) | `text_train/val/test` (`StratifiedGroupKFold`, `text_group_id`) | Benchmark (`n=8,202`): Acc `0.9777`, Macro F1 `0.9760`, ROC-AUC `0.9960`. Phase 5.0 spot check (`n=300`): Acc `1.0000`, FP `0`, FN `0`. | Hindi recall is `0.5455` (`n=460`) vs English `0.9690` (`n=7,668`). |
| **2. Phishing URL** | 16 zero-hop lexical features + XGBoost + SHAP (`ml/artifacts/url_detection/`) | `urls_train/val/test` (`StratifiedGroupKFold`, `domain_group_id`) | Benchmark (`n=15,131`): Acc `0.9998`, F1 `0.9998`, ROC-AUC `1.0000`. Phase 5.0 `urls_test.parquet` (`n=300`): Acc `0.9233`, **FP `23` (`FPR=0.1533`)**, FN `0`. | Elevated `15.33%` FPR on balanced held-out URLs; no live DNS/HTML inspection. |
| **3. Tactic Detection** | OvR Calibrated LinearSVC (`ml/artifacts/tactic_detection/best_tactic_model.joblib`) | Cleaned multi-label tactic corpus | Micro F1 `0.9513`, Macro F1 `0.9313`, Hamming Loss `0.0039` (`9` active tactics). | `fake_investment` intentionally `UNAVAILABLE` (missing verified ground-truth positives). |
| **4. Campaign Clustering** | Multilingual MiniLM + HDBSCAN (`ml/artifacts/campaign_detection/`) | Multilingual scam corpus | `47` clusters; Silhouette `+0.2917` over DBSCAN (`0.0292`). | Unsupervised similarity only — not confirmed criminal attribution. |

## 2. Inference & Loader Findings
- **Real ML Predictions Confirmed:** Frontend & API predictions come from loaded `.joblib` / `.npy` / `SentenceTransformer` models verified via SHA-256 in `CentralModelLoader`, not hardcoded logic.
- **Duplicate Model Loading Defect:** `ProductionMLEngine` and `MLOrchestrationService` both load `paraphrase-multilingual-MiniLM-L12-v2`, inflating Python RSS memory to `958.96 MB`.
- **Risk Calibration:** `TransparentRiskAggregationService.assess_risk(None, None, None)` returns `"inconclusive"` cleanly.
