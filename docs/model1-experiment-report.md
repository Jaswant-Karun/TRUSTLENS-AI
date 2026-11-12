# TRUSTLENS AI — Model 1: Multilingual Scam Detection Experiment Report

> **Platform:** TRUSTLENS AI — Advanced Multilingual Digital Fraud Intelligence & Prevention Platform  
> **Mission:** *Detect the deception before people lose their money.*  
> **Model 1 Identity:** Multilingual Digital Scam Message Detection  
> **Evaluation Date:** November 2026 | **Evaluation Split:** Held-out Test Set (N = 8,202 records)  
> **Status:** Trained, Verified & Calibrated | **Zero Fabrication Policy Active**

---

## 1. Executive Summary

TRUSTLENS AI Model 1 evaluates incoming digital communications (SMS, WhatsApp, Email) across English, Hindi (Devanagari), and romanized Hinglish to classify messages into legitimate or fraudulent communications.

All models were trained strictly on `data/processed/text_train.parquet` (69,501 samples) and evaluated on the held-out `data/processed/text_test.parquet` (8,202 samples). No test records were used during training, hyperparameter tuning, or vocabulary fitting.

### Selected Production Model:
- **Architecture:** Feature Union (Word 1-2 n-grams + Character 3-5 n-grams) + Calibrated Linear Support Vector Machine (`LinearSVC` with Platt Sigmoid Probability Calibration).
- **Test Accuracy:** **97.77%** (8,019 out of 8,202 correct)
- **Macro F1 Score:** **0.9760** | **Weighted F1 Score:** **0.9777**
- **False Positive Rate (FPR):** **1.68%** (87 false alarms out of 5,191 legitimate messages)
- **False Negative Rate (FNR):** **3.19%** (96 missed threats out of 3,011 threat messages)
- **Brier Score (Calibration Error):** **0.0178** (near-perfect probability calibration)
- **Average Inference Latency:** **~52 ms** on Intel Core i5 CPU

---

## 2. Hardware Profiling & Transformer Compatibility Audit

In accordance with strict development rules, available hardware was audited before finalizing model configurations:

| Hardware / Resource | Detected Specification | Operational Impact |
| :--- | :--- | :--- |
| **Processor** | 12th Gen Intel(R) Core(TM) i5-12450H | 8 Cores (4 P-Cores, 4 E-Cores), 12 Logical Threads. Multi-threaded CPU execution enabled (`torch.set_num_threads(8)`). |
| **Available RAM** | 15.70 GB Total / **2.05 GB Free** | Memory pressure requires avoiding massive batch allocations during backpropagation. |
| **CUDA Acceleration** | **Not Detected (Integrated Intel UHD Graphics)** | CPU-only PyTorch execution. |

### Transformer Model Comparison:
1. **`xlm-roberta-base` (278M params, ~1.1 GB disk):** General multilingual model covering 100 languages. Subword byte-level BPE is robust, but the large memory footprint and higher peak memory during backpropagation make it heavy for CPU-only training.
2. **`google/muril-base-cased` (237M params, ~950 MB disk):** **Selected as the optimal transformer.** MuRIL (Multilingual Representations for Indian Languages) was specifically trained by Google Research on 17 Indian languages + English, and crucially on **transliterated / romanized Hinglish**, providing native linguistic alignment with Indian smishing lures.
3. **`distilbert-base-multilingual-cased` (135M params, ~540 MB disk):** Fast inference alternative for edge deployments.

---

## 3. Comparative Baseline Experiment Benchmark

All baseline models were trained on the training split and evaluated on the identical held-out test set (N = 8,202):

| Model Architecture | Tokenization Scheme | Accuracy | Precision (Macro) | Recall (Macro) | Macro F1 | Weighted F1 | FPR | FNR | Brier Score | Train Time |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Model 1** | Word TF-IDF (1, 2) + Logistic Regression | 96.84% | 0.9649 | 0.9674 | 0.9661 | 0.9685 | 2.87% | 3.65% | 0.0264 | 0.83 s |
| **Model 2** | Char TF-IDF (3, 5) + Logistic Regression | 97.18% | 0.9683 | 0.9714 | 0.9698 | 0.9719 | 2.70% | 3.02% | 0.0236 | 1.19 s |
| **Model 3** | Feature Union (Word+Char) + Logistic Regression | 97.63% | 0.9739 | 0.9753 | 0.9746 | 0.9764 | 2.08% | 2.86% | 0.0194 | 2.16 s |
| **Model 4 (Best)** | **Feature Union + Calibrated LinearSVC (Platt)** | **97.77%** | **0.9763** | **0.9757** | **0.9760** | **0.9777** | **1.68%** | **3.19%** | **0.0178** | **2.65 s** |

### Why Feature Union + Calibrated LinearSVC Outperformed Other Baselines:
1. **Linguistic Synergy:** Word n-grams capture complete deceptive phrases (*"account blocked"*, *"kyc update"*, *"cash prize"*), while character n-grams capture phonetic variations in romanized Hinglish (*"turant"*, *"khata"*, *"karein"*, *"bhejo"*).
2. **Margin Maximization:** LinearSVC maximizes the geometric margin between deceptive threats and benign messages, proving resilient to high-dimensional sparse representations (50,000 features).
3. **Platt Probability Calibration:** Uncalibrated SVM outputs raw decision boundary distances. By applying 3-fold Platt scaling (`CalibratedClassifierCV(method='sigmoid')`), the model produces genuine, statistically calibrated probabilities (Brier score = 0.0178), enabling dependable confidence scoring in production.

---

## 4. Per-Class & Per-Language Performance Breakdown

### 4.1 Global Classification Report (Best Model: Calibrated LinearSVC)

```
              precision    recall  f1-score   support

  Legitimate     0.9815    0.9832    0.9824      5,191
 Scam/Threat     0.9710    0.9681    0.9696      3,011

    accuracy                         0.9777      8,202
   macro avg     0.9763    0.9757    0.9760      8,202
weighted avg     0.9777    0.9777    0.9777      8,202
```

### 4.2 Confusion Matrix (Held-out Test Set)

```
                       Predicted Legitimate    Predicted Scam/Threat
Actual Legitimate             5,104 (TN)              87 (FP)
Actual Scam/Threat               96 (FN)           2,915 (TP)
```

- **True Negatives (TN):** 5,104 benign communications correctly verified.
- **False Positives (FP):** 87 benign messages mistakenly flagged (FPR = 1.68%).
- **False Negatives (FN):** 96 scam lures missed (FNR = 3.19%).
- **True Positives (TP):** 2,915 deceptive threats successfully caught.

### 4.3 Per-Language Performance Breakdown

| Language Stream | Test Samples | Accuracy | Macro F1 | Threat Recall | Observations |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **English** | 7,668 | **97.68%** | **0.9754** | **96.90%** | Exceptional precision on global phishing and telemarketing templates. |
| **Hinglish (Romanized)**| 74 | **100.00%** | **1.0000** | **100.00%** | Zero false negatives on urgent banking/KYC lures. Character n-grams successfully captured informal spellings. |
| **Hindi (Devanagari)** | 460 | **98.91%** | **0.8502** | **54.55%** | High overall accuracy due to strong benign recognition; lower recall on sparse Devanagari threat classes due to limited Devanagari training volume in ScamShield. |

### ⚠️ Language Verification Policy
- **Verified Languages:** English, Hindi (Devanagari), and Romanized Hinglish.
- **Tamil Support Rule:** In accordance with user development instructions, **Tamil is NOT claimed as supported** because the audited benchmark dataset contains no validated Tamil ground truth samples.

---

## 5. Model Artifacts & Deployment Manifest

All artifacts have been serialized to [`ml/artifacts/text_detection/`](file:///c:/Users/jaswant%20karun/TRUSTLENS%20AI/ml/artifacts/text_detection):

- `best_model.joblib`: Serialized Calibrated LinearSVC pipeline (1.8 MB).
- `best_vectorizer.joblib`: 50,000-feature Word + Char Feature Union (1.8 MB).
- `confusion_matrix.png`: High-resolution confusion matrix heatmap.
- `model_metadata.json`: Full training hyperparameters, random seeds, and metadata.
- `experiment_report.json`: Machine-readable results across all evaluated architectures.
- `infer.py`: Production inference interface returning predictions in <60ms with evidence tokens.
- `train_baselines.py` & `evaluate_model.py`: Reproducible training and testing pipelines.
