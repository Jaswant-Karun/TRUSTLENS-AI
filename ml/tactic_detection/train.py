"""
TRUSTLENS AI - Phase 2.3: Multi-Label Tactic Detection Training Pipeline
Trains One-vs-Rest Logistic Regression & One-vs-Rest Calibrated LinearSVC
on leak-free ScamShield annotated splits (excluding unannotated Mendeley rows).
Tunes per-label decision thresholds on the validation split ONLY.
Saves candidate artifacts under ml/artifacts/tactic_detection/v2.3_candidate/.
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
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import FeatureUnion
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.multiclass import OneVsRestClassifier
from sklearn.metrics import f1_score

from ml.tactic_detection.labels import (
    TACTIC_LABELS,
    SUPPORTED_LABELS,
    UNSUPPORTED_LABELS,
    map_processed_row_to_tactics,
)

RANDOM_SEED = 42


def compute_sha256(filepath: Path) -> str:
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def load_annotated_split(parquet_path: str):
    df = pd.read_parquet(parquet_path)
    # Only keep rows with genuine ScamShield multi-head annotations
    df = df[df["tactics"] != "{}"].reset_index(drop=True)
    texts = df["cleaned_text"].fillna("").tolist()

    y_rows = []
    for _, row in df.iterrows():
        mapped = map_processed_row_to_tactics(
            row["tactics"], row["head2_scam_intent"], row["metadata_json"]
        )
        y_rows.append([mapped[k] for k in SUPPORTED_LABELS])

    return texts, np.array(y_rows, dtype=np.int32), df


def tune_thresholds(y_true: np.ndarray, y_probs: np.ndarray) -> dict:
    thresholds = {}
    candidates = np.arange(0.15, 0.86, 0.05)
    for idx, key in enumerate(SUPPORTED_LABELS):
        col_t = y_true[:, idx]
        col_p = y_probs[:, idx]
        if col_t.sum() == 0:
            thresholds[key] = 0.50
            continue
        best_f1, best_th = -1.0, 0.50
        for th in candidates:
            score = f1_score(col_t, (col_p >= th).astype(int), zero_division=0)
            if score > best_f1:
                best_f1 = score
                best_th = float(round(th, 2))
        thresholds[key] = best_th
    return thresholds


def main():
    print("=" * 70)
    print("TRUSTLENS AI - PHASE 2.3: TACTIC MULTI-LABEL TRAINING")
    print("=" * 70)

    out_dir = Path("ml/artifacts/tactic_detection/v2.3_candidate")
    out_dir.mkdir(parents=True, exist_ok=True)

    print("\n[1/3] Loading Annotated Train & Validation Splits...")
    X_train_raw, y_train, _ = load_annotated_split("data/processed/text_train.parquet")
    X_val_raw, y_val, _ = load_annotated_split("data/processed/text_val.parquet")

    print(f"  Annotated Train: {len(X_train_raw):,} | Annotated Val: {len(X_val_raw):,}")
    print(f"  Supported Labels ({len(SUPPORTED_LABELS)}): {SUPPORTED_LABELS}")
    print(f"  Blocked/Unavailable ({len(UNSUPPORTED_LABELS)}): {UNSUPPORTED_LABELS}")

    # Save label schema
    with open(out_dir / "label_schema.json", "w", encoding="utf-8") as f:
        json.dump(
            {
                "supported_labels": SUPPORTED_LABELS,
                "unsupported_labels": UNSUPPORTED_LABELS,
                "taxonomy": TACTIC_LABELS,
            },
            f,
            indent=2,
        )

    # 2. Vectorize
    print("\n[2/3] Fitting Word+Char FeatureUnion TF-IDF...")
    vectorizer = FeatureUnion([
        ("word_tfidf", TfidfVectorizer(ngram_range=(1, 3), max_features=40000, sublinear_tf=True, strip_accents=None)),
        ("char_tfidf", TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5), max_features=40000, sublinear_tf=True)),
    ])
    X_train_vec = vectorizer.fit_transform(X_train_raw)
    X_val_vec = vectorizer.transform(X_val_raw)
    vec_path = out_dir / "vectorizer.joblib"
    joblib.dump(vectorizer, vec_path)

    artifact_hashes = {"vectorizer.joblib": compute_sha256(vec_path)}
    models_summary = {}

    # Model A: One-vs-Rest Logistic Regression
    print("\n[3/3] Training OvR Multi-Label Models...")
    print("  -> Training One-vs-Rest Logistic Regression...")
    t0 = time.perf_counter()
    ovr_lr = OneVsRestClassifier(
        LogisticRegression(C=1.0, class_weight="balanced", max_iter=1000, random_state=RANDOM_SEED),
        n_jobs=-1,
    )
    ovr_lr.fit(X_train_vec, y_train)
    lr_t = round(time.perf_counter() - t0, 2)
    lr_val_probs = ovr_lr.predict_proba(X_val_vec)
    lr_thresh = tune_thresholds(y_val, lr_val_probs)
    lr_val_pred = np.column_stack([(lr_val_probs[:, i] >= lr_thresh[k]).astype(int) for i, k in enumerate(SUPPORTED_LABELS)])
    lr_path = out_dir / "ovr_logreg.joblib"
    joblib.dump(ovr_lr, lr_path)
    artifact_hashes[lr_path.name] = compute_sha256(lr_path)
    models_summary["ovr_logreg"] = {
        "display_name": "One-vs-Rest Logistic Regression (Balanced)",
        "train_duration_seconds": lr_t,
        "val_micro_f1": round(float(f1_score(y_val, lr_val_pred, average="micro", zero_division=0)), 4),
        "val_macro_f1": round(float(f1_score(y_val, lr_val_pred, average="macro", zero_division=0)), 4),
        "thresholds": lr_thresh,
        "size_mb": round(lr_path.stat().st_size / (1024 * 1024), 3),
    }
    print(f"     Done in {lr_t}s | Val Micro F1: {models_summary['ovr_logreg']['val_micro_f1']} | Macro F1: {models_summary['ovr_logreg']['val_macro_f1']}")

    # Model B: One-vs-Rest Calibrated LinearSVC
    print("  -> Training One-vs-Rest Calibrated LinearSVC...")
    t0 = time.perf_counter()
    ovr_svc = OneVsRestClassifier(
        CalibratedClassifierCV(
            estimator=LinearSVC(C=1.0, class_weight="balanced", max_iter=3000, random_state=RANDOM_SEED),
            method="sigmoid",
            cv=3,
        ),
        n_jobs=-1,
    )
    ovr_svc.fit(X_train_vec, y_train)
    svc_t = round(time.perf_counter() - t0, 2)
    svc_val_probs = ovr_svc.predict_proba(X_val_vec)
    svc_thresh = tune_thresholds(y_val, svc_val_probs)
    svc_val_pred = np.column_stack([(svc_val_probs[:, i] >= svc_thresh[k]).astype(int) for i, k in enumerate(SUPPORTED_LABELS)])
    svc_path = out_dir / "ovr_linearsvc.joblib"
    joblib.dump(ovr_svc, svc_path)
    artifact_hashes[svc_path.name] = compute_sha256(svc_path)
    models_summary["ovr_linearsvc"] = {
        "display_name": "One-vs-Rest Calibrated LinearSVC (Balanced)",
        "train_duration_seconds": svc_t,
        "val_micro_f1": round(float(f1_score(y_val, svc_val_pred, average="micro", zero_division=0)), 4),
        "val_macro_f1": round(float(f1_score(y_val, svc_val_pred, average="macro", zero_division=0)), 4),
        "thresholds": svc_thresh,
        "size_mb": round(svc_path.stat().st_size / (1024 * 1024), 3),
    }
    print(f"     Done in {svc_t}s | Val Micro F1: {models_summary['ovr_linearsvc']['val_micro_f1']} | Macro F1: {models_summary['ovr_linearsvc']['val_macro_f1']}")

    metadata = {
        "phase": "2.3",
        "dataset_version": "2.0.5",
        "random_seed": RANDOM_SEED,
        "train_samples": len(X_train_raw),
        "val_samples": len(X_val_raw),
        "supported_labels": SUPPORTED_LABELS,
        "unsupported_labels": UNSUPPORTED_LABELS,
        "trained_at_utc": datetime.now(timezone.utc).isoformat(),
        "models": models_summary,
        "artifact_sha256": artifact_hashes,
    }
    with open(out_dir / "training_metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print(f"\nCandidate tactic training artifacts saved to {out_dir}")


if __name__ == "__main__":
    main()
