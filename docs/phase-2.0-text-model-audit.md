# TRUSTLENS AI — PHASE 2.0: TEXT SCAM CLASSIFIER AUDIT (MODEL 1)

> **Directory Audited:** `ml/text_detection/` & `ml/artifacts/text_detection/`  
> **Audit Date:** November 25, 2026  

---

## 1. Component & Artifact Inventory

- **Training Scripts:**
  - `ml/text_detection/train_baselines.py` (Executed ✅)
  - `ml/text_detection/train_transformer.py` (`google/muril-base-cased` — **NOT EXECUTED** ❌)
- **Preprocessing & Vectorization:**
  - `ml/preprocessing/text_preprocessor.py`
  - `FeatureUnion` combining Word TF-IDF (`ngram_range=(1,3)`, `sublinear_tf=True`) and Character TF-IDF (`ngram_range=(2,5)`), max 100,000 features (`best_vectorizer.joblib`, 1.81 MB).
- **Model Architecture (Production):**
  - `LinearSVC` (`C=1.0`, `penalty='l2'`, `loss='squared_hinge'`) wrapped in `CalibratedClassifierCV` (Platt scaling, 3-fold CV).
- **Saved Model Artifacts:**
  - `ml/artifacts/text_detection/best_model.joblib` (1,202,133 bytes)
  - `ml/artifacts/text_detection/best_vectorizer.joblib` (1,806,240 bytes)
  - `ml/artifacts/multilingual_text_model.joblib` & `tfidf_vectorizer.joblib` (mirrors)
- **Label Mapping:** `0` = `legitimate`, `1` = `threat`.
- **Evaluation & Inference:**
  - `ml/artifacts/text_detection/experiment_report.json` (4 baseline models evaluated on 8,202 held-out test samples).
  - `ml/text_detection/infer.py` and `ml/text_detection/classifier.py`.

---

## 2. Held-Out Test Set Evaluation (8,202 Samples)

| Model | Accuracy | Macro F1 | Weighted F1 | ROC-AUC | FPR | FNR |
|---|---|---|---|---|---|---|
| Word TF-IDF + Logistic Regression | 0.9684 | 0.9661 | 0.9685 | 0.9933 | 0.0287 | 0.0365 |
| Char TF-IDF + Logistic Regression | 0.9718 | 0.9698 | 0.9719 | 0.9943 | 0.0270 | 0.0302 |
| FeatureUnion + Logistic Regression | 0.9763 | 0.9746 | 0.9764 | 0.9958 | 0.0208 | 0.0286 |
| **FeatureUnion + Calibrated LinearSVC** | **0.9777** | **0.9760** | **0.9777** | **0.9960** | **0.0168** | **0.0319** |

### Per-Language Breakdown (Winning LinearSVC Model)
- **English (7,668 samples):** Accuracy `97.68%`, Macro F1 `0.9754`, Threat Recall `96.90%`
- **Hinglish (74 samples):** Accuracy `100.0%`, Macro F1 `1.000`, Threat Recall `100.0%`
- **Hindi (460 samples):** Accuracy `98.91%`, Macro F1 **`0.8502`**, **Threat Recall `54.55%`**

---

## 3. Critical Findings & Gaps

1. **Hindi Threat Recall Deficiency:** While overall accuracy looks high due to class imbalance in the Hindi subset, the TF-IDF LinearSVC model misses **45.45% of Hindi scam messages** (`recall_threat = 0.5455`).
2. **Transformer Not Trained:** `train_transformer.py` (`google/muril-base-cased`) was written to address multilingual Devanagari/transliterated semantics, but **no transformer artifacts exist** in `ml/artifacts/text_detection/transformer/`.
3. **Registry Over-Claim:** `model_registry.json` lists Bengali and Tamil as supported languages, despite zero training or test samples for those languages.
4. **Backend Integration:** **VERIFIED.** `ProductionMLEngine` loads `best_model.joblib` and `best_vectorizer.joblib` and executed live safe inference (`is_threat=True, conf=0.941, version=trustlens-model1-v1.0`).

---

## 4. Maturity Classification
- **Overall Status:** **VERIFIED** for English/Hinglish baseline; **PARTIAL** for true multilingual (Hindi/Bengali/Tamil) coverage.
- **Stage:** Stage 6 (Integrated into FastAPI and tested through frontend).
