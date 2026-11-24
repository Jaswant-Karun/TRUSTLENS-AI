# TRUSTLENS AI — PHASE 2.0: HARDWARE-CONSTRAINED TRAINING ROADMAP & SUMMARY

> **Target Local Hardware:** Intel Core i5-12450H, 16 GB RAM, Integrated Intel UHD Graphics, Python 3.12  
> **Audit Policy:** No training was executed during Phase 2.0.  

---

## 1. Master Audit Summary Table

| ML Component | Dataset Ready | Training Executed | Evaluation Complete | Artifact Exists | Backend Integrated |
|---|---|---|---|---|---|
| **Text** | **PARTIAL** *(En/Hi/Hinglish only; 0 Bn/Ta)* | **PARTIAL** *(LinearSVC trained; MuRIL Transformer NOT trained)* | **VERIFIED** *(8,202 test set)* | **VERIFIED** *(LinearSVC + TF-IDF)* | **VERIFIED** |
| **URL** | **VERIFIED** *(100,872 unique URLs)* | **VERIFIED** *(LR, RF, XGBoost)* | **VERIFIED** *(15,131 test set + SHAP)* | **VERIFIED** *(XGBoost + SHAP)* | **VERIFIED** |
| **Tactics** | **PARTIAL** *(9/10 labels real; `fake_investment` missing)* | **PARTIAL** *(9/10 trained; 1 blocked)* | **VERIFIED** *(8,202 test set, 9 labels)* | **VERIFIED** *(OvR LinearSVC)* | **VERIFIED** |
| **Campaign** | **VERIFIED** *(5,715 threat texts)* | **VERIFIED** *(HDBSCAN & DBSCAN)* | **PARTIAL** *(Silhouette metric mismatch in dashboard)* | **VERIFIED** *(47 centroids + embeddings)* | **VERIFIED** |

---

## 2. Hardware-Aware Training & Remediation Roadmap (Phase 2.1+)

Given the **16 GB RAM** and **CPU-only (Intel i5-12450H, Integrated UHD)** local constraint:

### Priority 1: Multilingual Transformer Fine-Tuning (Google Colab / Kaggle GPU)
- **Problem:** Local TF-IDF LinearSVC only achieves **54.55% threat recall on Hindi** (`460` test samples). Local CPU fine-tuning of `google/muril-base-cased` is slow and risks OOM under 16 GB RAM.
- **Recommendation:**
  - Execute `ml/text_detection/train_transformer.py` on **Google Colab T4 (16 GB VRAM)** or **Kaggle P100**.
  - Use `fp16=True`, `batch_size=16`, `max_length=128`, gradient accumulation steps `= 2`.
  - Export quantized ONNX / PyTorch weights (`< 500 MB`) back to `ml/artifacts/text_detection/transformer/` for fast CPU inference (`torch.set_num_threads(8)`).

### Priority 2: Multilingual Campaign Embeddings (Local CPU Compatible)
- **Problem:** Model 4 uses `all-MiniLM-L6-v2` (English-centric).
- **Recommendation:**
  - Upgrade `CampaignEmbeddingEngine` to `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (384 dimensions, ~470 MB).
  - Run locally on i5-12450H with `batch_size=64` (~2–3 minutes for 5,715 samples, < 2 GB RAM peak).
  - Re-run HDBSCAN and synchronize `campaign_experiment_report.json` with `model_dashboard_data.json` so Silhouette scores match identically.

### Priority 3: URL Feature Extraction Alignment (Local CPU)
- **Problem:** Minor train-serving feature extraction skew on IP:port URLs (`tld_length`) and `.sh` extensions (`suspicious_file_extension`).
- **Recommendation:**
  - Re-extract features across all 100,872 URLs using `ml/url_detection/features.py` directly before retraining XGBoost (`< 15 seconds` on i5-12450H CPU).

### Priority 4: Tactic #10 (`fake_investment`) Data Acquisition
- **Status:** **BLOCKED** until genuine multi-label human-annotated investment/crypto scam records are acquired. Do **not** synthesize labels with keyword rules.

### Priority 5: Registry & Metadata Hygiene
- Remove unsupported languages (`Bengali`, `Tamil`) from `model_registry.json` until verified datasets are added.
