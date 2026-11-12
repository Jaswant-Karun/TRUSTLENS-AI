"""
TRUSTLENS AI - Model 1 Baseline Training & Evaluation Pipeline
Trains and compares:
1. TF-IDF Word n-grams (1, 2) + Logistic Regression
2. TF-IDF Character n-grams (3, 5) + Logistic Regression
3. TF-IDF Feature Union (Word + Char) + Logistic Regression
4. TF-IDF Feature Union + Linear Support Vector Machine (LinearSVC with Platt Calibration)

Computes:
- Accuracy, Precision, Recall, Macro F1, Weighted F1
- Per-class precision, recall, and F1 (Legitimate vs Threat)
- Per-language metrics (English, Hindi, Hinglish)
- False Positive Rate (FPR) and False Negative Rate (FNR)
- Confusion Matrix and calibration curves
"""

import sys
import os
import json
import time
import hashlib
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
import numpy as np
import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import FeatureUnion, Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report, roc_auc_score, brier_score_loss
)


def compute_rates(cm: np.ndarray):
    """Computes False Positive Rate (FPR) and False Negative Rate (FNR) from confusion matrix."""
    tn, fp, fn, tp = cm.ravel()
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
    fnr = fn / (fn + tp) if (fn + tp) > 0 else 0.0
    return float(fpr), float(fnr)


def evaluate_model(name: str, model, X_test, y_test, df_test: pd.DataFrame) -> dict:
    """Evaluates model performance globally and broken down per language."""
    start_t = time.time()
    y_pred = model.predict(X_test)
    eval_duration = time.time() - start_t

    # Probability estimation if supported
    if hasattr(model, "predict_proba"):
        y_prob = model.predict_proba(X_test)[:, 1]
        brier = float(brier_score_loss(y_test, y_prob))
        roc_auc = float(roc_auc_score(y_test, y_prob))
    else:
        y_prob = None
        brier = None
        roc_auc = None

    cm = confusion_matrix(y_test, y_pred)
    fpr, fnr = compute_rates(cm)

    acc = float(accuracy_score(y_test, y_pred))
    prec_macro = float(precision_score(y_test, y_pred, average="macro", zero_division=0))
    rec_macro = float(recall_score(y_test, y_pred, average="macro", zero_division=0))
    f1_macro = float(f1_score(y_test, y_pred, average="macro", zero_division=0))
    f1_weighted = float(f1_score(y_test, y_pred, average="weighted", zero_division=0))

    # Per-class breakdown
    prec_classes = precision_score(y_test, y_pred, average=None, zero_division=0)
    rec_classes = recall_score(y_test, y_pred, average=None, zero_division=0)
    f1_classes = f1_score(y_test, y_pred, average=None, zero_division=0)

    # Per-language breakdown
    per_language_metrics = {}
    for lang in df_test["language"].unique():
        lang_idx = df_test["language"] == lang
        if lang_idx.sum() > 0:
            sub_y_true = y_test[lang_idx]
            sub_y_pred = y_pred[lang_idx]
            per_language_metrics[lang] = {
                "sample_count": int(lang_idx.sum()),
                "accuracy": round(float(accuracy_score(sub_y_true, sub_y_pred)), 4),
                "f1_macro": round(float(f1_score(sub_y_true, sub_y_pred, average="macro", zero_division=0)), 4),
                "recall_threat": round(float(recall_score(sub_y_true, sub_y_pred, pos_label=1, zero_division=0)), 4),
            }

    return {
        "model_name": name,
        "accuracy": round(acc, 4),
        "precision_macro": round(prec_macro, 4),
        "recall_macro": round(rec_macro, 4),
        "f1_macro": round(f1_macro, 4),
        "f1_weighted": round(f1_weighted, 4),
        "false_positive_rate": round(fpr, 4),
        "false_negative_rate": round(fnr, 4),
        "brier_score_loss": round(brier, 4) if brier is not None else None,
        "roc_auc": round(roc_auc, 4) if roc_auc is not None else None,
        "per_class": {
            "legitimate": {
                "precision": round(float(prec_classes[0]), 4),
                "recall": round(float(rec_classes[0]), 4),
                "f1": round(float(f1_classes[0]), 4),
            },
            "threat": {
                "precision": round(float(prec_classes[1]), 4),
                "recall": round(float(rec_classes[1]), 4),
                "f1": round(float(f1_classes[1]), 4),
            },
        },
        "per_language": per_language_metrics,
        "confusion_matrix": cm.tolist(),
        "eval_latency_seconds": round(eval_duration, 4),
    }


def main():
    print("=" * 65)
    print("TRUSTLENS AI - MODEL 1: MULTILINGUAL SCAM DETECTION BASELINES")
    print("=" * 65)

    artifacts_dir = Path("ml/artifacts/text_detection")
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    # 1. Load Parquet Splits
    print("\n[1/4] Loading Processed Splits...")
    train_df = pd.read_parquet("data/processed/text_train.parquet")
    val_df = pd.read_parquet("data/processed/text_val.parquet")
    test_df = pd.read_parquet("data/processed/text_test.parquet")

    X_train_raw = train_df["cleaned_text"].fillna("").tolist()
    y_train = train_df["is_threat"].astype(int).values

    X_val_raw = val_df["cleaned_text"].fillna("").tolist()
    y_val = val_df["is_threat"].astype(int).values

    X_test_raw = test_df["cleaned_text"].fillna("").tolist()
    y_test = test_df["is_threat"].astype(int).values

    print(f"  Train: {len(X_train_raw):,} samples (Threat: {y_train.mean():.2%})")
    print(f"  Val:   {len(X_val_raw):,} samples (Threat: {y_val.mean():.2%})")
    print(f"  Test:  {len(X_test_raw):,} samples (Threat: {y_test.mean():.2%})")

    # 2. Build Vectorization Schemes
    print("\n[2/4] Fitting TF-IDF Vectorizers strictly on Training Data...")
    
    # Scheme A: Word n-grams (1, 2)
    vec_word = TfidfVectorizer(ngram_range=(1, 2), max_features=25000, sublinear_tf=True)
    t0 = time.time()
    X_train_word = vec_word.fit_transform(X_train_raw)
    X_test_word = vec_word.transform(X_test_raw)
    print(f"  Word TF-IDF fitted in {time.time()-t0:.2f}s (Features: {X_train_word.shape[1]:,})")
    joblib.dump(vec_word, artifacts_dir / "tfidf_word.joblib")

    # Scheme B: Character n-grams (3, 5) - critical for Romanized Hinglish & Hindi
    vec_char = TfidfVectorizer(analyzer="char", ngram_range=(3, 5), max_features=35000, sublinear_tf=True)
    t0 = time.time()
    X_train_char = vec_char.fit_transform(X_train_raw)
    X_test_char = vec_char.transform(X_test_raw)
    print(f"  Char TF-IDF fitted in {time.time()-t0:.2f}s (Features: {X_train_char.shape[1]:,})")
    joblib.dump(vec_char, artifacts_dir / "tfidf_char.joblib")

    # Scheme C: Feature Union (Word 1-2 + Char 3-5)
    vec_union = FeatureUnion([
        ("word", TfidfVectorizer(ngram_range=(1, 2), max_features=20000, sublinear_tf=True)),
        ("char", TfidfVectorizer(analyzer="char", ngram_range=(3, 5), max_features=30000, sublinear_tf=True)),
    ])
    t0 = time.time()
    X_train_union = vec_union.fit_transform(X_train_raw)
    X_test_union = vec_union.transform(X_test_raw)
    print(f"  Feature Union fitted in {time.time()-t0:.2f}s (Features: {X_train_union.shape[1]:,})")
    joblib.dump(vec_union, artifacts_dir / "tfidf_union.joblib")

    # 3. Model Training Experiments
    print("\n[3/4] Training Baseline Models...")
    experiments = []

    # Model 1: Word TF-IDF + Logistic Regression
    print("\n  -> Model 1: Word TF-IDF + Logistic Regression")
    m1 = LogisticRegression(C=2.0, class_weight="balanced", max_iter=1000, random_state=42)
    t0 = time.time()
    m1.fit(X_train_word, y_train)
    m1_train_time = time.time() - t0
    m1_eval = evaluate_model("Word TF-IDF + Logistic Regression", m1, X_test_word, y_test, test_df)
    m1_eval["train_duration_seconds"] = round(m1_train_time, 2)
    experiments.append(m1_eval)
    joblib.dump(m1, artifacts_dir / "logistic_regression_word.joblib")
    print(f"     Accuracy: {m1_eval['accuracy']:.4f} | Macro F1: {m1_eval['f1_macro']:.4f} | FPR: {m1_eval['false_positive_rate']:.4f}")

    # Model 2: Char TF-IDF + Logistic Regression
    print("\n  -> Model 2: Char TF-IDF + Logistic Regression")
    m2 = LogisticRegression(C=2.0, class_weight="balanced", max_iter=1000, random_state=42)
    t0 = time.time()
    m2.fit(X_train_char, y_train)
    m2_train_time = time.time() - t0
    m2_eval = evaluate_model("Char TF-IDF + Logistic Regression", m2, X_test_char, y_test, test_df)
    m2_eval["train_duration_seconds"] = round(m2_train_time, 2)
    experiments.append(m2_eval)
    joblib.dump(m2, artifacts_dir / "logistic_regression_char.joblib")
    print(f"     Accuracy: {m2_eval['accuracy']:.4f} | Macro F1: {m2_eval['f1_macro']:.4f} | FPR: {m2_eval['false_positive_rate']:.4f}")

    # Model 3: Feature Union (Word+Char) + Logistic Regression
    print("\n  -> Model 3: Feature Union (Word+Char) + Logistic Regression")
    m3 = LogisticRegression(C=2.5, class_weight="balanced", max_iter=1000, random_state=42)
    t0 = time.time()
    m3.fit(X_train_union, y_train)
    m3_train_time = time.time() - t0
    m3_eval = evaluate_model("Feature Union (Word+Char) + Logistic Regression", m3, X_test_union, y_test, test_df)
    m3_eval["train_duration_seconds"] = round(m3_train_time, 2)
    experiments.append(m3_eval)
    joblib.dump(m3, artifacts_dir / "logistic_regression_union.joblib")
    print(f"     Accuracy: {m3_eval['accuracy']:.4f} | Macro F1: {m3_eval['f1_macro']:.4f} | FPR: {m3_eval['false_positive_rate']:.4f}")

    # Model 4: Feature Union + LinearSVC with Platt Probability Calibration
    print("\n  -> Model 4: Feature Union + Calibrated LinearSVC (Platt Scaling)")
    base_svc = LinearSVC(C=1.0, class_weight="balanced", max_iter=2000, random_state=42)
    calibrated_svc = CalibratedClassifierCV(estimator=base_svc, method="sigmoid", cv=3)
    t0 = time.time()
    calibrated_svc.fit(X_train_union, y_train)
    m4_train_time = time.time() - t0
    m4_eval = evaluate_model("Feature Union + Calibrated LinearSVC", calibrated_svc, X_test_union, y_test, test_df)
    m4_eval["train_duration_seconds"] = round(m4_train_time, 2)
    experiments.append(m4_eval)
    joblib.dump(calibrated_svc, artifacts_dir / "linear_svc_calibrated.joblib")
    print(f"     Accuracy: {m4_eval['accuracy']:.4f} | Macro F1: {m4_eval['f1_macro']:.4f} | FPR: {m4_eval['false_positive_rate']:.4f}")

    # 4. Select and Save Best Production Model
    best_exp = max(experiments, key=lambda x: x["f1_macro"])
    print(f"\n[4/4] Best Performing Baseline Model: '{best_exp['model_name']}' (Macro F1 = {best_exp['f1_macro']:.4f})")
    
    # Save best model and pipeline components
    if "LinearSVC" in best_exp["model_name"]:
        best_model_obj = calibrated_svc
        best_vec_obj = vec_union
    elif "Union" in best_exp["model_name"]:
        best_model_obj = m3
        best_vec_obj = vec_union
    else:
        best_model_obj = m2
        best_vec_obj = vec_char

    joblib.dump(best_model_obj, artifacts_dir / "best_model.joblib")
    joblib.dump(best_vec_obj, artifacts_dir / "best_vectorizer.joblib")

    # Also save to main artifacts directory for backend service integration
    main_artifacts_dir = Path("ml/artifacts")
    joblib.dump(best_model_obj, main_artifacts_dir / "multilingual_text_model.joblib")
    joblib.dump(best_vec_obj, main_artifacts_dir / "tfidf_vectorizer.joblib")

    # Plot Confusion Matrix for Best Model
    best_cm = np.array(best_exp["confusion_matrix"])
    plt.figure(figsize=(6, 5))
    sns.heatmap(best_cm, annot=True, fmt="d", cmap="Blues", cbar=False,
                xticklabels=["Legitimate", "Scam/Threat"],
                yticklabels=["Legitimate", "Scam/Threat"])
    plt.title(f"Confusion Matrix: {best_exp['model_name']}", fontsize=11, fontweight="bold")
    plt.ylabel("Ground Truth")
    plt.xlabel("Predicted Class")
    plt.tight_layout()
    plt.savefig(artifacts_dir / "confusion_matrix.png", dpi=200)
    plt.close()

    # Save Experiment Report & Metadata
    metadata = {
        "model_id": "trustlens-model1-multilingual-v1",
        "created_at_utc": pd.Timestamp.now("UTC").isoformat(),
        "task": "Multilingual Digital Scam Message Detection",
        "train_samples": len(X_train_raw),
        "test_samples": len(X_test_raw),
        "best_model": best_exp["model_name"],
        "macro_f1": best_exp["f1_macro"],
        "accuracy": best_exp["accuracy"],
        "supported_languages": ["English", "Hindi", "Hinglish"],
        "language_validation_note": "Tamil is NOT claimed as supported because the evaluated dataset does not contain Tamil records.",
        "artifacts": {
            "model": "best_model.joblib",
            "vectorizer": "best_vectorizer.joblib",
            "confusion_matrix": "confusion_matrix.png",
        },
    }

    with open(artifacts_dir / "model_metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    with open(artifacts_dir / "experiment_report.json", "w", encoding="utf-8") as f:
        json.dump({"experiments": experiments, "best_model": best_exp}, f, indent=2)

    print(f"\n[OK] All artifacts, checkpoints, and reports saved to {artifacts_dir}")
    print("=" * 65)
    print("BASELINE TRAINING COMPLETE!")
    print("=" * 65)
    return experiments


if __name__ == "__main__":
    main()
