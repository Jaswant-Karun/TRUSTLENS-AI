# TRUSTLENS AI — PHASE 2.1: MULTILINGUAL TEXT SCAM DETECTION MODEL REPORT

> **Dataset Version:** `2.0.5` (Leak-free `StratifiedGroupKFold` splits on `text_group_id`, `random_seed=42`)  
> **Candidate Artifacts Directory:** `ml/artifacts/text_detection/v2.1_candidate/` *(Production artifacts preserved untouched)*  
> **Scripts Created:** `ml/text_detection/config.yaml`, `train.py`, `evaluate.py`, `predict.py`  
> **Date:** November 25, 2026

---

## 1. Task Definition & Label Mapping

- **Supported Multi-Class Taxonomy (`4` Classes):**
  - `0: legitimate` (Train: `43,779` | Val: `5,472` | Test: `5,473`)
  - `1: spam` (Train: `19,449` | Val: `2,422` | Test: `2,461`)
  - `2: smishing` (Train: `3,443` | Val: `468` | Test: `414`)
  - `3: scam` (Train: `2,045` | Val: `227` | Test: `242`)
- **Incompatible / Deferred Labels:**
  - Standalone `phishing` URLs are routed to Model 2 (`phishing_url`), while SMS/message URL phishing lures are mapped to `smishing`.
  - Tamil and Bengali remain unsupported (`0` validated samples).

---

## 2. Baseline Model Comparison (Untouched Test Set, `n=8,590`)

All 3 baselines were trained on `text_train.parquet` (`n=68,716`) with `class_weight="balanced"`, validated on `text_val.parquet` (`n=8,589`), and evaluated once on `text_test.parquet` (`n=8,590`):

| Model Pipeline | Accuracy | Macro F1 | Weighted F1 | ROC-AUC (OvR) | PR-AUC (OvR) | Threat FPR | Threat FNR | Latency (ms/msg) | Size (MB) |
|---|---|---|---|---|---|---|---|---|---|
| Word TF-IDF (1-2) + LogReg | 0.9601 | 0.9394 | 0.9603 | 0.9929 | 0.9708 | 0.0354 | 0.0263 | 0.0474 ms | 3.374 MB |
| Char_wb TF-IDF (3-5) + LogReg | 0.9683 | 0.9510 | 0.9685 | 0.9958 | 0.9774 | 0.0292 | **0.0209** | 0.2026 ms | 3.826 MB |
| **Word+Char FeatureUnion + Calibrated LinearSVC** | **0.9783** | **0.9629** | **0.9783** | **0.9974** | **0.9870** | **0.0139** | 0.0221 | 0.3166 ms | 10.184 MB |

---

## 3. Selected Model Breakdown (`union_tfidf_linearsvc`)

### Per-Class Held-Out Performance
| Class | Precision | Recall | F1 Score | Test Support |
|---|---|---|---|---|
| `legitimate` | 0.9874 | 0.9861 | **0.9867** | 5,473 |
| `spam` | 0.9614 | 0.9724 | **0.9669** | 2,461 |
| `smishing` | 0.9679 | 0.9469 | **0.9573** | 414 |
| `scam` | 0.9652 | 0.9174 | **0.9407** | 242 |

### Per-Language Held-Out Performance
- **English (`7,797` samples):** Accuracy `0.9765` | Macro F1 `0.9583` | Threat Recall `0.9771`
- **Hindi (`675` samples):** Accuracy `0.9956` | Macro F1 **`0.9653`** | Threat Recall **`0.9855`** *(Improved from 54.55% in Phase 2.0 by preserving Devanagari diacritics with `strip_accents=None` and balanced class weighting)*
- **Hinglish (`118` samples):** Accuracy `1.0000` | Macro F1 `1.0000` | Threat Recall `1.0000`

### Confusion Matrix (`[legitimate, spam, smishing, scam]`)
```
[[5397,   65,    6,    5],
 [  63, 2393,    4,    1],
 [   2,   18,  392,    2],
 [   4,   13,    3,  222]]
```

---

## 4. Multilingual Transformer Evaluation & GPU Notebook

- **Local Hardware Constraint:** Local machine (`Intel i5-12450H`, `16 GB RAM`, CPU-only) cannot fine-tune `google/muril-base-cased` across 68,716 samples without risking OOM.
- **Justification & Reproducible GPU Notebook:** Created [`ml/notebooks/02_train_muril_transformer_gpu.ipynb`](file:///c:/Users/jaswant%20karun/TRUSTLENS%20AI/ml/notebooks/02_train_muril_transformer_gpu.ipynb) configured for Google Colab T4 / Kaggle GPU (`fp16=True`, `max_length=128`, `seed=42`) using the exact same `text_{train,val,test}.parquet` splits.

---

## 5. Saved Artifacts & SHA-256 Checksums (`ml/artifacts/text_detection/v2.1_candidate/`)

| Artifact | Size (MB) | SHA-256 |
|---|---|---|
| `union_tfidf_linearsvc_vectorizer.joblib` | 2.857 MB | `d5b7d1fcfb018d6318256e1dc6f1450dfb8368852f7149c2b651c0a492f49225` |
| `union_tfidf_linearsvc_model.joblib` | 7.327 MB | `46b6f2235ccecc83224b611f8a7f195c2f064acdb10e1d0549f6e15d1df70b8b` |
| `word_tfidf_logreg_vectorizer.joblib` | 1.848 MB | `7b2c3e00d3067bc3b8271e6e64644a59f0043623f81ebda884f8714d10c297a3` |
| `word_tfidf_logreg_model.joblib` | 1.527 MB | `44d96c18f641326a7cc076f754a291c36ae06f97be8aedba4c86bda8a135c202` |
| `char_tfidf_logreg_vectorizer.joblib` | 1.994 MB | `cb70fc651f7c1215a3363c5824a29e3eb7ce3f9d019d288e3561c88cdbc60399` |
| `char_tfidf_logreg_model.joblib` | 1.832 MB | `6b3fe6ade6bbb2427a718528e03aa25c5fa98a54cb29e1feb33121e4478443f4` |

> **Stop Condition Honored:** Existing production artifacts (`best_model.joblib`) were not overwritten, and frontend/backend routes were not modified.
