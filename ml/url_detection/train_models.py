"""
TRUSTLENS AI - Model 2: Phishing URL Detection Training & SHAP Pipeline
Trains and compares:
1. Baseline: Logistic Regression (with StandardScaler)
2. Random Forest Classifier
3. XGBoost Classifier (Extreme Gradient Boosting)

Computes:
- Accuracy, Precision, Recall, F1 (Macro & Binary), ROC-AUC, PR-AUC
- Confusion matrix, FPR, FNR, Inference Latency
- SHAP Feature Importance & Attribution using TreeExplainer
"""

import sys
import os
import json
import time
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

from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
import xgboost as xgb
import shap

from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, average_precision_score, confusion_matrix
)
from ml.url_detection.features import FEATURE_COLUMNS


def compute_rates(cm: np.ndarray):
    """Calculates False Positive Rate (FPR) and False Negative Rate (FNR)."""
    tn, fp, fn, tp = cm.ravel()
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
    fnr = fn / (fn + tp) if (fn + tp) > 0 else 0.0
    return float(fpr), float(fnr)


def evaluate_model(name: str, model, X_test, y_test, is_scaled: bool = False, scaler=None) -> dict:
    """Evaluates URL classifier on test split and computes latency."""
    X_input = scaler.transform(X_test) if (is_scaled and scaler is not None) else X_test

    start_t = time.perf_counter()
    y_pred = model.predict(X_input)
    latency_ms = (time.perf_counter() - start_t) * 1000 / len(y_test)

    if hasattr(model, "predict_proba"):
        y_prob = model.predict_proba(X_input)[:, 1]
    else:
        y_prob = model.predict(X_input)

    cm = confusion_matrix(y_test, y_pred)
    fpr, fnr = compute_rates(cm)

    acc = float(accuracy_score(y_test, y_pred))
    prec = float(precision_score(y_test, y_pred, zero_division=0))
    rec = float(recall_score(y_test, y_pred, zero_division=0))
    f1_bin = float(f1_score(y_test, y_pred, zero_division=0))
    f1_mac = float(f1_score(y_test, y_pred, average="macro", zero_division=0))
    roc_auc = float(roc_auc_score(y_test, y_prob))
    pr_auc = float(average_precision_score(y_test, y_prob))

    return {
        "model_name": name,
        "accuracy": round(acc, 4),
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "f1_binary": round(f1_bin, 4),
        "f1_macro": round(f1_mac, 4),
        "roc_auc": round(roc_auc, 4),
        "pr_auc": round(pr_auc, 4),
        "false_positive_rate": round(fpr, 4),
        "false_negative_rate": round(fnr, 4),
        "confusion_matrix": cm.tolist(),
        "per_sample_latency_ms": round(latency_ms, 4),
    }


def main():
    print("=" * 65)
    print("TRUSTLENS AI - MODEL 2: PHISHING URL CLASSIFIER TRAINING")
    print("=" * 65)

    artifacts_dir = Path("ml/artifacts/url_detection")
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    # 1. Load Data
    print("\n[1/4] Loading Processed Parquet Splits...")
    train_df = pd.read_parquet("data/processed/urls_train.parquet")
    val_df = pd.read_parquet("data/processed/urls_val.parquet")
    test_df = pd.read_parquet("data/processed/urls_test.parquet")

    X_train = train_df[FEATURE_COLUMNS].values
    y_train = train_df["is_phishing"].values

    X_val = val_df[FEATURE_COLUMNS].values
    y_val = val_df["is_phishing"].values

    X_test = test_df[FEATURE_COLUMNS].values
    y_test = test_df["is_phishing"].values

    print(f"  Train: {len(X_train):,} samples (Phishing: {y_train.mean():.2%})")
    print(f"  Val:   {len(X_val):,} samples (Phishing: {y_val.mean():.2%})")
    print(f"  Test:  {len(X_test):,} samples (Phishing: {y_test.mean():.2%})")

    # Fit Scaler for linear model
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    joblib.dump(scaler, artifacts_dir / "scaler.joblib")

    experiments = []

    # 2. Model Experiments
    print("\n[2/4] Training and Comparing Models...")

    # Model A: Baseline Logistic Regression
    print("\n  -> Model A: Baseline Logistic Regression")
    lr = LogisticRegression(C=1.0, class_weight="balanced", max_iter=1000, random_state=42)
    t0 = time.time()
    lr.fit(X_train_scaled, y_train)
    lr_train_t = time.time() - t0
    lr_eval = evaluate_model("Logistic Regression Baseline", lr, X_test, y_test, is_scaled=True, scaler=scaler)
    lr_eval["train_duration_seconds"] = round(lr_train_t, 2)
    experiments.append(lr_eval)
    joblib.dump(lr, artifacts_dir / "logistic_regression.joblib")
    print(f"     Accuracy: {lr_eval['accuracy']:.4f} | F1: {lr_eval['f1_binary']:.4f} | ROC-AUC: {lr_eval['roc_auc']:.4f} | FPR: {lr_eval['false_positive_rate']:.4f}")

    # Model B: Random Forest
    print("\n  -> Model B: Random Forest Classifier (100 Trees)")
    rf = RandomForestClassifier(n_estimators=100, max_depth=16, class_weight="balanced", random_state=42, n_jobs=-1)
    t0 = time.time()
    rf.fit(X_train, y_train)
    rf_train_t = time.time() - t0
    rf_eval = evaluate_model("Random Forest", rf, X_test, y_test, is_scaled=False)
    rf_eval["train_duration_seconds"] = round(rf_train_t, 2)
    experiments.append(rf_eval)
    joblib.dump(rf, artifacts_dir / "random_forest.joblib")
    print(f"     Accuracy: {rf_eval['accuracy']:.4f} | F1: {rf_eval['f1_binary']:.4f} | ROC-AUC: {rf_eval['roc_auc']:.4f} | FPR: {rf_eval['false_positive_rate']:.4f}")

    # Model C: XGBoost
    print("\n  -> Model C: Extreme Gradient Boosting (XGBoost)")
    scale_pos = (y_train == 0).sum() / (y_train == 1).sum()
    xgb_model = xgb.XGBClassifier(
        n_estimators=150,
        max_depth=6,
        learning_rate=0.1,
        scale_pos_weight=scale_pos,
        eval_metric="logloss",
        random_state=42,
        n_jobs=-1
    )
    t0 = time.time()
    xgb_model.fit(X_train, y_train, eval_set=[(X_val, y_val)], verbose=False)
    xgb_train_t = time.time() - t0
    xgb_eval = evaluate_model("XGBoost Classifier", xgb_model, X_test, y_test, is_scaled=False)
    xgb_eval["train_duration_seconds"] = round(xgb_train_t, 2)
    experiments.append(xgb_eval)
    joblib.dump(xgb_model, artifacts_dir / "xgboost_model.joblib")
    print(f"     Accuracy: {xgb_eval['accuracy']:.4f} | F1: {xgb_eval['f1_binary']:.4f} | ROC-AUC: {xgb_eval['roc_auc']:.4f} | FPR: {xgb_eval['false_positive_rate']:.4f}")

    # 3. Select Best Model
    best_exp = max(experiments, key=lambda x: x["roc_auc"])
    print(f"\n[3/4] Best Performing URL Model: '{best_exp['model_name']}' (ROC-AUC = {best_exp['roc_auc']:.4f})")

    best_model_obj = xgb_model if "XGBoost" in best_exp["model_name"] else rf
    joblib.dump(best_model_obj, artifacts_dir / "best_url_model.joblib")
    
    # Update main backend registry artifact
    main_art = Path("ml/artifacts")
    joblib.dump(best_model_obj, main_art / "phishing_url_model.joblib")

    # Plot Confusion Matrix
    best_cm = np.array(best_exp["confusion_matrix"])
    plt.figure(figsize=(6, 5))
    sns.heatmap(best_cm, annot=True, fmt="d", cmap="Reds", cbar=False,
                xticklabels=["Legitimate", "Phishing"],
                yticklabels=["Legitimate", "Phishing"])
    plt.title(f"Confusion Matrix: {best_exp['model_name']}", fontsize=11, fontweight="bold")
    plt.ylabel("Ground Truth")
    plt.xlabel("Predicted Class")
    plt.tight_layout()
    plt.savefig(artifacts_dir / "confusion_matrix.png", dpi=200)
    plt.close()

    # 4. SHAP Feature Attribution
    print("\n[4/4] Computing SHAP TreeExplainer Attributions...")
    explainer = shap.TreeExplainer(best_model_obj)
    
    # Subsample 1,000 validation records for rapid, robust SHAP estimation
    val_sub = val_df.sample(n=min(1000, len(val_df)), random_state=42)
    X_val_sub = val_sub[FEATURE_COLUMNS].values
    shap_values = explainer.shap_values(X_val_sub)

    # If binary classification returns list or 2D array
    if isinstance(shap_values, list):
        shap_vals_target = shap_values[1]
    else:
        shap_vals_target = shap_values

    # SHAP Summary Plot
    plt.figure(figsize=(10, 7))
    shap.summary_plot(shap_vals_target, X_val_sub, feature_names=FEATURE_COLUMNS, show=False)
    plt.title(f"SHAP Feature Importance & Impact: {best_exp['model_name']}", fontsize=12, fontweight="bold")
    plt.tight_layout()
    plt.savefig(artifacts_dir / "shap_summary.png", dpi=200)
    plt.close()

    # Mean absolute SHAP values per feature
    mean_abs_shap = np.abs(shap_vals_target).mean(axis=0)
    feature_ranking = [
        {"feature": feat, "mean_abs_shap": round(float(val), 4)}
        for feat, val in sorted(zip(FEATURE_COLUMNS, mean_abs_shap), key=lambda x: x[1], reverse=True)
    ]

    with open(artifacts_dir / "shap_feature_importance.json", "w", encoding="utf-8") as f:
        json.dump(feature_ranking, f, indent=2)

    with open(artifacts_dir / "feature_schema.json", "w", encoding="utf-8") as f:
        json.dump({"feature_columns": FEATURE_COLUMNS}, f, indent=2)

    metadata = {
        "model_id": "trustlens-model2-phishing-url-v1",
        "created_at_utc": pd.Timestamp.now("UTC").isoformat(),
        "task": "Machine Learning Phishing URL Detection",
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "best_model": best_exp["model_name"],
        "roc_auc": best_exp["roc_auc"],
        "pr_auc": best_exp["pr_auc"],
        "f1_binary": best_exp["f1_binary"],
        "accuracy": best_exp["accuracy"],
        "top_features_by_shap": [f["feature"] for f in feature_ranking[:5]],
        "security_policy": "Zero outbound network calls. Lexical indicators do not prove server maliciousness.",
    }

    with open(artifacts_dir / "model_metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    with open(artifacts_dir / "url_experiment_report.json", "w", encoding="utf-8") as f:
        json.dump({"experiments": experiments, "best_model": best_exp, "feature_ranking": feature_ranking}, f, indent=2)

    print(f"\n[OK] All Model 2 artifacts and SHAP visualizations saved to {artifacts_dir}")
    print("=" * 65)
    print("MODEL 2 TRAINING & EVALUATION COMPLETED!")
    print("=" * 65)
    return experiments


if __name__ == "__main__":
    main()
