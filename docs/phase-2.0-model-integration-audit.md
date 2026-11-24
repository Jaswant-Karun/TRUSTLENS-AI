# TRUSTLENS AI — PHASE 2.0: DATABASE PROVENANCE & BACKEND MODEL INTEGRATION AUDIT

> **Scope:** 138 MongoDB `analyses` Records, FastAPI ML Routes, `ProductionMLEngine`, and Registry Alignment  
> **Audit Date:** November 25, 2026  

---

## 1. MongoDB `analyses` Collection Provenance (138 Records)

Direct inspection of all 138 documents in `trustlens_ai.analyses` revealed the following breakdown:

- **Total Records:** `138`
- **User Provenance:**
  - `a22d3504-399f-4b0c-ac20-1a334aa1da22`: **96 records** (created `2026-11-12` during initial backend smoke/integration verification).
  - `anonymous`: **42 records** (created `2026-11-24` during QA and frontend route testing).
- **Analysis Types & Channels:**
  - `text`: 96 | `url`: 42
  - Channels: `sms` (74), `auto` (20), `whatsapp` (2), `None`/URL (42)
- **Threat Level Distribution:** `critical` (68), `clean` (38), `high` (17), `medium` (15)
- **Model Version Tracking:**
  - `text_model`: `trustlens-model1-v1.0` (96 records)
  - `url_model`: `trustlens-model2-xgboost-v1.0` (74 records)
  - `tactic_model`: `trustlens-model3-calibrated-linear-v1.0` (96 records)
- **Duplicate Input Finding:** Out of 138 documents, there are only **26 unique input payloads** (**112 duplicate submissions**). Top repeated test strings include `http://192.168.1.50/sbi-kyc/update.php` (12x) and `Aapka SBI khata turant band ho jayega...` (9x).
- **Conclusion:** Every record contains genuine ML model inference outputs traced to original inputs and model versions, **but** the corpus consists of developer/QA test runs rather than organic external user traffic.

---

## 2. Backend Model Loading & Inference Verification

Inspected `backend/app/ml_engine/engine.py` (`ProductionMLEngine`) and ran live safe inference checks against loaded artifacts:

| Model Track | Artifact Loaded by Backend | Live Safe Inference Result | Availability Guard |
|---|---|---|---|
| **Model 1: Text Scam** | `ml/artifacts/text_detection/best_model.joblib` + `best_vectorizer.joblib` | `is_threat=True, conf=0.941, ver=trustlens-model1-v1.0` | Returns `status: "unavailable"`, `is_threat: None` if unloaded |
| **Model 2: URL Phishing** | `ml/artifacts/url_detection/best_url_model.joblib` | `is_phishing=True, risk=0.9999, ver=trustlens-model2-xgboost-v1.0` | Returns `status: "unavailable"`, `is_phishing: None` if unloaded |
| **Model 3: Tactics** | `ml/artifacts/tactic_detection/best_tactic_model.joblib` + `vectorizer.joblib` | `count=2, tactics=['urgency_time_pressure', 'threats_intimidation']` | Returns `status: "unavailable"`, `tactics: []` if unloaded |
| **Model 4: Campaign** | `ml/artifacts/campaign_detection/cluster_artifacts.joblib` + `all-MiniLM-L6-v2` | `campaign_id=43, sim=0.9207` | Returns `status: "unavailable"`, `matched: False` if unloaded |

---

## 3. Metadata & Registry Discrepancies

1. **Supported Languages Claim (`model_registry.json`):** Claims Bengali and Tamil support for Model 1, whereas zero Bengali/Tamil training or evaluation samples exist.
2. **Silhouette Score Mismatch:** `model_dashboard_data.json` / UI reports `0.449` for Model 4, whereas `campaign_experiment_report.json` reports `0.3209`.
3. **Model 1 Transformer Absent:** `train_transformer.py` exists in source control, but no transformer weights are saved or loaded by `ProductionMLEngine`.
