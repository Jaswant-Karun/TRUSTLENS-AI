"""
TRUSTLENS AI - Phase 2.2: Phishing URL Classification Training Pipeline
Trains and compares Logistic Regression (scaled, balanced), Random Forest (balanced),
and XGBoost Classifier on the leak-free Phase 2.0.5 domain-grouped URL splits.
Saves candidate artifacts under ml/artifacts/url_detection/v2.2_candidate/.
"""

import sys
import json
import time
import hashlib
from pathlib import Path
from datetime import datetime, timezone

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score
import xgboost as xgb

from ml.url_detection.features import FEATURE_COLUMNS

RANDOM_SEED = 42


def compute_sha256(filepath: Path) -> str:
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def main():
    print("=" * 70)
    print("TRUSTLENS AI - PHASE 2.2: PHISHING URL CLASSIFICATION TRAINING")
    print("=" * 70)

    out_dir = Path("ml/artifacts/url_detection/v2.2_candidate")
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. Load Train and Validation Splits ONLY (Test split kept untouched)
    print("\n[1/3] Loading Domain-Grouped URL Train and Validation Splits...")
    train_df = pd.read_parquet("data/processed/urls_train.parquet")
    val_df = pd.read_parquet("data/processed/urls_val.parquet")

    X_train = train_df[FEATURE_COLUMNS].astype(float).values
    y_train = train_df["is_phishing"].astype(int).values

    X_val = val_df[FEATURE_COLUMNS].astype(float).values
    y_val = val_df["is_phishing"].astype(int).values

    print(f"  Train: {len(X_train):,} URLs (Phish%: {y_train.mean():.2%})")
    print(f"  Val:   {len(X_val):,} URLs (Phish%: {y_val.mean():.2%})")

    # Save feature schema and label mapping
    label_mapping = {0: "legitimate", 1: "phishing"}
    with open(out_dir / "label_mapping.json", "w", encoding="utf-8") as f:
        json.dump(label_mapping, f, indent=2)
    with open(out_dir / "feature_schema.json", "w", encoding="utf-8") as f:
        json.dump({"features": FEATURE_COLUMNS, "count": len(FEATURE_COLUMNS)}, f, indent=2)

    # Fit StandardScaler on Train ONLY
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_val_scaled = scaler.transform(X_val)
    scaler_path = out_dir / "scaler.joblib"
    joblib.dump(scaler, scaler_path)

    # Compute class imbalance ratio for XGBoost
    neg_count = int((y_train == 0).sum())
    pos_count = int((y_train == 1).sum())
    scale_pos_weight = round(neg_count / max(1, pos_count), 4)

    # 2. Train 3 Models
    print("\n[2/3] Training Reproducible Models...")
    models_summary = {}
    artifact_hashes = {"scaler.joblib": compute_sha256(scaler_path)}

    # A. Logistic Regression
    print("\n  -> Training Logistic Regression (StandardScaler + balanced)...")
    t0 = time.perf_counter()
    lr = LogisticRegression(C=1.0, class_weight="balanced", max_iter=1000, random_state=RANDOM_SEED)
    lr.fit(X_train_scaled, y_train)
    lr_t = round(time.perf_counter() - t0, 2)
    lr_val_pred = lr.predict(X_val_scaled)
    lr_path = out_dir / "logistic_regression.joblib"
    joblib.dump(lr, lr_path)
    artifact_hashes[lr_path.name] = compute_sha256(lr_path)
    models_summary["logistic_regression"] = {
        "display_name": "Logistic Regression (Scaled, Balanced)",
        "requires_scaler": True,
        "train_duration_seconds": lr_t,
        "val_accuracy": round(float(accuracy_score(y_val, lr_val_pred)), 4),
        "val_macro_f1": round(float(f1_score(y_val, lr_val_pred, average="macro")), 4),
        "size_mb": round(lr_path.stat().st_size / (1024 * 1024), 4),
    }
    print(f"     Done in {lr_t}s | Val Macro F1: {models_summary['logistic_regression']['val_macro_f1']:.4f}")

    # B. Random Forest
    print("\n  -> Training Random Forest (100 trees, balanced)...")
    t0 = time.perf_counter()
    rf = RandomForestClassifier(
        n_estimators=100, max_depth=16, class_weight="balanced", random_state=RANDOM_SEED, n_jobs=-1
    )
    rf.fit(X_train, y_train)
    rf_t = round(time.perf_counter() - t0, 2)
    rf_val_pred = rf.predict(X_val)
    rf_path = out_dir / "random_forest.joblib"
    joblib.dump(rf, rf_path)
    artifact_hashes[rf_path.name] = compute_sha256(rf_path)
    models_summary["random_forest"] = {
        "display_name": "Random Forest Classifier (100 Trees, Balanced)",
        "requires_scaler": False,
        "train_duration_seconds": rf_t,
        "val_accuracy": round(float(accuracy_score(y_val, rf_val_pred)), 4),
        "val_macro_f1": round(float(f1_score(y_val, rf_val_pred, average="macro")), 4),
        "size_mb": round(rf_path.stat().st_size / (1024 * 1024), 4),
    }
    print(f"     Done in {rf_t}s | Val Macro F1: {models_summary['random_forest']['val_macro_f1']:.4f}")

    # C. XGBoost Classifier
    print("\n  -> Training XGBoost Classifier...")
    t0 = time.perf_counter()
    xgb_clf = xgb.XGBClassifier(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        scale_pos_weight=scale_pos_weight,
        eval_metric="logloss",
        random_state=RANDOM_SEED,
        n_jobs=-1,
    )
    xgb_clf.fit(X_train, y_train)
    xgb_t = round(time.perf_counter() - t0, 2)
    xgb_val_pred = xgb_clf.predict(X_val)
    xgb_path = out_dir / "xgboost_model.joblib"
    joblib.dump(xgb_clf, xgb_path)
    artifact_hashes[xgb_path.name] = compute_sha256(xgb_path)
    models_summary["xgboost_model"] = {
        "display_name": "XGBoost Classifier (GBDT)",
        "requires_scaler": False,
        "train_duration_seconds": xgb_t,
        "val_accuracy": round(float(accuracy_score(y_val, xgb_val_pred)), 4),
        "val_macro_f1": round(float(f1_score(y_val, xgb_val_pred, average="macro")), 4),
        "size_mb": round(xgb_path.stat().st_size / (1024 * 1024), 4),
    }
    print(f"     Done in {xgb_t}s | Val Macro F1: {models_summary['xgboost_model']['val_macro_f1']:.4f}")

    # 3. Save Training Metadata & Config
    metadata = {
        "phase": "2.2",
        "dataset_version": "2.0.5",
        "random_seed": RANDOM_SEED,
        "train_samples": len(X_train),
        "val_samples": len(X_val),
        "scale_pos_weight": scale_pos_weight,
        "feature_count": len(FEATURE_COLUMNS),
        "features": FEATURE_COLUMNS,
        "labels": label_mapping,
        "trained_at_utc": datetime.now(timezone.utc).isoformat(),
        "models": models_summary,
        "artifact_sha256": artifact_hashes,
    }
    with open(out_dir / "training_metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print(f"\nCandidate URL training artifacts saved to {out_dir}")


if __name__ == "__main__":
    main()
