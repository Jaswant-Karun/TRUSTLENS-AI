"""
TRUSTLENS AI - Model 1 Standalone Evaluation Script
Evaluates saved model checkpoints against the held-out test split.
"""

import sys
import os
import json
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
import numpy as np
import joblib
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, f1_score


def evaluate_checkpoint(
    model_path="ml/artifacts/text_detection/best_model.joblib",
    vec_path="ml/artifacts/text_detection/best_vectorizer.joblib",
    test_parquet="data/processed/text_test.parquet"
):
    print("=" * 65)
    print("TRUSTLENS AI - MODEL 1 CHECKPOINT EVALUATION")
    print(f"Model: {model_path}")
    print(f"Test Split: {test_parquet}")
    print("=" * 65)

    model = joblib.load(model_path)
    vec = joblib.load(vec_path)
    test_df = pd.read_parquet(test_parquet)

    X_test_raw = test_df["cleaned_text"].fillna("").tolist()
    y_true = test_df["is_threat"].astype(int).values

    X_test = vec.transform(X_test_raw)
    y_pred = model.predict(X_test)

    print("\n--- GLOBAL CLASSIFICATION REPORT (N=8,202) ---")
    print(classification_report(y_true, y_pred, target_names=["Legitimate", "Scam/Threat"], digits=4))

    cm = confusion_matrix(y_true, y_pred)
    tn, fp, fn, tp = cm.ravel()
    fpr = fp / (fp + tn)
    fnr = fn / (fn + tp)
    print(f"Confusion Matrix: TN={tn}, FP={fp}, FN={fn}, TP={tp}")
    print(f"False Positive Rate (FPR): {fpr:.4f} ({fpr*100:.2f}%)")
    print(f"False Negative Rate (FNR): {fnr:.4f} ({fnr*100:.2f}%)")

    print("\n--- PER-LANGUAGE PERFORMANCE BREAKDOWN ---")
    for lang in test_df["language"].unique():
        idx = test_df["language"] == lang
        sub_true = y_true[idx]
        sub_pred = y_pred[idx]
        acc = accuracy_score(sub_true, sub_pred)
        f1 = f1_score(sub_true, sub_pred, average="macro", zero_division=0)
        print(f"  Language: {lang:<10} | Samples: {idx.sum():<5} | Accuracy: {acc:.4f} | Macro F1: {f1:.4f}")

    print("\n" + "=" * 65)


if __name__ == "__main__":
    evaluate_checkpoint()
