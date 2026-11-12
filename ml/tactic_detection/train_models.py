"""
TRUSTLENS AI - Model 3: Multi-Label Social Engineering & Scam Tactic Detection
Trains One-vs-Rest Logistic Regression & Calibrated Linear Support Vector Classifiers
with FeatureUnion Word/Char TF-IDF and validation-tuned decision thresholds.
"""

import sys
import os
import json
import time
from pathlib import Path
from typing import Dict, Any, List, Tuple

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import numpy as np
import pandas as pd
import joblib
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import FeatureUnion
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.multiclass import OneVsRestClassifier
from sklearn.metrics import (
    f1_score,
    precision_score,
    recall_score,
    hamming_loss,
    precision_recall_curve,
    average_precision_score,
)

from ml.tactic_detection.taxonomy import (
    TACTIC_REGISTRY,
    SUPPORTED_TACTIC_KEYS,
    ALL_TACTIC_KEYS,
    map_scamshield_annotations,
)


def load_dataset(jsonl_path: Path) -> Tuple[List[str], np.ndarray]:
    """Loads and maps raw ScamShield JSONL into texts and multi-hot label array."""
    texts = []
    y_list = []

    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            item = json.loads(line)
            texts.append(item.get("text", ""))
            mapped = map_scamshield_annotations(item)
            # Binary vector for the 9 supported trainable tactics
            row_vec = [mapped[k] for k in SUPPORTED_TACTIC_KEYS]
            y_list.append(row_vec)

    return texts, np.array(y_list, dtype=np.int32)


def tune_thresholds(
    y_true: np.ndarray, y_probs: np.ndarray, label_keys: List[str]
) -> Dict[str, float]:
    """
    Finds optimal decision threshold per label on validation data to maximize F1 score.
    """
    best_thresholds = {}
    threshold_candidates = np.arange(0.10, 0.90, 0.02)

    for idx, key in enumerate(label_keys):
        y_true_col = y_true[:, idx]
        y_prob_col = y_probs[:, idx]

        best_f1 = -1.0
        best_thresh = 0.50

        # If zero positives in validation, default to 0.50
        if y_true_col.sum() == 0:
            best_thresholds[key] = 0.50
            continue

        for thresh in threshold_candidates:
            y_pred = (y_prob_col >= thresh).astype(int)
            score = f1_score(y_true_col, y_pred, zero_division=0)
            if score > best_f1:
                best_f1 = score
                best_thresh = float(round(thresh, 2))

        best_thresholds[key] = best_thresh

    return best_thresholds


def apply_thresholds(
    y_probs: np.ndarray, thresholds: Dict[str, float], label_keys: List[str]
) -> np.ndarray:
    """Applies per-label tuned decision thresholds to prediction probability matrix."""
    y_pred = np.zeros_like(y_probs, dtype=np.int32)
    for idx, key in enumerate(label_keys):
        thresh = thresholds.get(key, 0.50)
        y_pred[:, idx] = (y_probs[:, idx] >= thresh).astype(np.int32)
    return y_pred


def evaluate_multilabel_model(
    model_name: str,
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_probs: np.ndarray,
    label_keys: List[str],
    latency_ms: float,
    train_duration: float,
    thresholds: Dict[str, float],
) -> Dict[str, Any]:
    """Computes comprehensive multi-label evaluation metrics."""
    micro_f1 = round(float(f1_score(y_true, y_pred, average="micro", zero_division=0)), 4)
    macro_f1 = round(float(f1_score(y_true, y_pred, average="macro", zero_division=0)), 4)
    weighted_f1 = round(float(f1_score(y_true, y_pred, average="weighted", zero_division=0)), 4)
    h_loss = round(float(hamming_loss(y_true, y_pred)), 4)

    per_label_report = {}
    for idx, key in enumerate(label_keys):
        y_col_true = y_true[:, idx]
        y_col_pred = y_pred[:, idx]
        y_col_prob = y_probs[:, idx]

        prec = round(float(precision_score(y_col_true, y_col_pred, zero_division=0)), 4)
        rec = round(float(recall_score(y_col_true, y_col_pred, zero_division=0)), 4)
        f1 = round(float(f1_score(y_col_true, y_col_pred, zero_division=0)), 4)
        pr_auc = round(float(average_precision_score(y_col_true, y_col_prob)), 4)
        support = int(y_col_true.sum())

        per_label_report[key] = {
            "name": TACTIC_REGISTRY[key]["name"],
            "code": TACTIC_REGISTRY[key]["code"],
            "precision": prec,
            "recall": rec,
            "f1_score": f1,
            "pr_auc": pr_auc,
            "support": support,
            "tuned_threshold": thresholds.get(key, 0.50),
        }

    return {
        "model_name": model_name,
        "micro_f1": micro_f1,
        "macro_f1": macro_f1,
        "weighted_f1": weighted_f1,
        "hamming_loss": h_loss,
        "per_sample_latency_ms": round(latency_ms, 4),
        "train_duration_seconds": round(train_duration, 2),
        "per_label_metrics": per_label_report,
    }


def main():
    print("=" * 68)
    print("TRUSTLENS AI - MODEL 3: MULTI-LABEL SCAM TACTIC CLASSIFIER")
    print("=" * 68)

    artifacts_dir = Path("ml/artifacts/tactic_detection")
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    # 1. Load Data
    print("\n[1/5] Loading Processed Multi-Label Partitions...")
    train_path = Path("data/raw/scamshield/train.jsonl")
    val_path = Path("data/raw/scamshield/val.jsonl")
    test_path = Path("data/raw/scamshield/test.jsonl")

    X_train_raw, Y_train = load_dataset(train_path)
    X_val_raw, Y_val = load_dataset(val_path)
    X_test_raw, Y_test = load_dataset(test_path)

    print(f"  Train: {len(X_train_raw):,} samples | 9 Active Target Tactics")
    print(f"  Val:   {len(X_val_raw):,} samples")
    print(f"  Test:  {len(X_test_raw):,} samples (Holdout benchmark)")

    # 2. Build Subword Feature Representation
    print("\n[2/5] Building Multilingual Word & Character Feature Union...")
    vectorizer = FeatureUnion([
        (
            "word",
            TfidfVectorizer(
                ngram_range=(1, 2),
                max_features=25000,
                sublinear_tf=True,
                min_df=3,
                lowercase=True,
            ),
        ),
        (
            "char",
            TfidfVectorizer(
                ngram_range=(3, 5),
                analyzer="char_wb",
                max_features=35000,
                sublinear_tf=True,
                min_df=5,
            ),
        ),
    ])

    t0_vec = time.time()
    X_train_vec = vectorizer.fit_transform(X_train_raw)
    X_val_vec = vectorizer.transform(X_val_raw)
    X_test_vec = vectorizer.transform(X_test_raw)
    print(f"  Vocabulary fitted in {time.time() - t0_vec:.2f}s | Feature dimensions: {X_train_vec.shape[1]:,}")

    experiments = []

    # 3. Model A: One-vs-Rest Logistic Regression
    print("\n[3/5] Training Multi-Label Candidate Models...")
    print("  -> Training Model A: One-vs-Rest Logistic Regression (Balanced)...")
    t0_lr = time.time()
    lr_base = LogisticRegression(
        C=2.0,
        class_weight="balanced",
        max_iter=500,
        random_state=42,
        solver="lbfgs",
    )
    clf_lr = OneVsRestClassifier(lr_base)
    clf_lr.fit(X_train_vec, Y_train)
    lr_train_time = time.time() - t0_lr

    # Predict Probabilities on Val & Tune Thresholds
    val_probs_lr = clf_lr.predict_proba(X_val_vec)
    lr_thresholds = tune_thresholds(Y_val, val_probs_lr, SUPPORTED_TACTIC_KEYS)

    # Predict on Test
    t0_inf = time.time()
    test_probs_lr = clf_lr.predict_proba(X_test_vec)
    test_pred_lr = apply_thresholds(test_probs_lr, lr_thresholds, SUPPORTED_TACTIC_KEYS)
    lr_latency = (time.time() - t0_inf) / len(X_test_raw) * 1000

    eval_lr = evaluate_multilabel_model(
        "One-vs-Rest Logistic Regression",
        Y_test,
        test_pred_lr,
        test_probs_lr,
        SUPPORTED_TACTIC_KEYS,
        lr_latency,
        lr_train_time,
        lr_thresholds,
    )
    experiments.append(eval_lr)
    print(f"     Micro F1: {eval_lr['micro_f1']:.4f} | Macro F1: {eval_lr['macro_f1']:.4f} | Hamming Loss: {eval_lr['hamming_loss']:.4f}")

    # 4. Model B: One-vs-Rest Calibrated LinearSVC (Platt Scaling)
    print("  -> Training Model B: One-vs-Rest Calibrated LinearSVC (Platt Scaled)...")
    t0_svm = time.time()
    base_svc = LinearSVC(
        C=1.0,
        class_weight="balanced",
        random_state=42,
        dual="auto",
        max_iter=1500,
    )
    calibrated_svc = CalibratedClassifierCV(estimator=base_svc, method="sigmoid", cv=3)
    clf_svm = OneVsRestClassifier(calibrated_svc)
    clf_svm.fit(X_train_vec, Y_train)
    svm_train_time = time.time() - t0_svm

    # Predict Probabilities on Val & Tune Thresholds
    val_probs_svm = clf_svm.predict_proba(X_val_vec)
    svm_thresholds = tune_thresholds(Y_val, val_probs_svm, SUPPORTED_TACTIC_KEYS)

    # Predict on Test
    t0_inf = time.time()
    test_probs_svm = clf_svm.predict_proba(X_test_vec)
    test_pred_svm = apply_thresholds(test_probs_svm, svm_thresholds, SUPPORTED_TACTIC_KEYS)
    svm_latency = (time.time() - t0_inf) / len(X_test_raw) * 1000

    eval_svm = evaluate_multilabel_model(
        "One-vs-Rest Calibrated LinearSVC",
        Y_test,
        test_pred_svm,
        test_probs_svm,
        SUPPORTED_TACTIC_KEYS,
        svm_latency,
        svm_train_time,
        svm_thresholds,
    )
    experiments.append(eval_svm)
    print(f"     Micro F1: {eval_svm['micro_f1']:.4f} | Macro F1: {eval_svm['macro_f1']:.4f} | Hamming Loss: {eval_svm['hamming_loss']:.4f}")

    # 5. Select Best Performing Multi-Label Model
    best_exp = max(experiments, key=lambda x: (x["macro_f1"], x["micro_f1"]))
    best_clf = clf_svm if "LinearSVC" in best_exp["model_name"] else clf_lr
    best_thresholds = svm_thresholds if "LinearSVC" in best_exp["model_name"] else lr_thresholds
    best_test_probs = test_probs_svm if "LinearSVC" in best_exp["model_name"] else test_probs_lr

    print(f"\n[4/5] Selected Best Multi-Label Model: '{best_exp['model_name']}'")
    print(f"      Macro F1: {best_exp['macro_f1']:.4f} | Micro F1: {best_exp['micro_f1']:.4f} | Hamming Loss: {best_exp['hamming_loss']:.4f}")

    # Save Model Artifacts
    print("\n[5/5] Saving Trained Model Artifacts & Visualizations...")
    joblib.dump(best_clf, artifacts_dir / "best_tactic_model.joblib")
    joblib.dump(vectorizer, artifacts_dir / "vectorizer.joblib")

    # Save to main backend registry
    joblib.dump(
        {"model": best_clf, "vectorizer": vectorizer, "thresholds": best_thresholds},
        Path("ml/artifacts/tactic_multilabel_model.joblib"),
    )

    with open(artifacts_dir / "thresholds.json", "w", encoding="utf-8") as f:
        json.dump(best_thresholds, f, indent=2)

    # Plot Precision-Recall Curves
    plt.figure(figsize=(10, 7))
    for idx, key in enumerate(SUPPORTED_TACTIC_KEYS):
        prec, rec, _ = precision_recall_curve(Y_test[:, idx], best_test_probs[:, idx])
        pr_auc = best_exp["per_label_metrics"][key]["pr_auc"]
        label_name = TACTIC_REGISTRY[key]["name"]
        plt.plot(rec, prec, label=f"{label_name} (PR-AUC={pr_auc:.3f})", lw=1.8)

    plt.title(f"Precision-Recall Curves per Tactic: {best_exp['model_name']}", fontsize=12, fontweight="bold")
    plt.xlabel("Recall", fontsize=11)
    plt.ylabel("Precision", fontsize=11)
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.legend(loc="lower left", fontsize=8)
    plt.tight_layout()
    plt.savefig(artifacts_dir / "pr_curves.png", dpi=200)
    plt.close()

    # Plot Label Co-occurrence Correlation Heatmap
    corr_df = pd.DataFrame(Y_train, columns=[TACTIC_REGISTRY[k]["name"] for k in SUPPORTED_TACTIC_KEYS])
    corr_mat = corr_df.corr()
    plt.figure(figsize=(10, 8))
    sns.heatmap(corr_mat, annot=True, fmt=".2f", cmap="Blues", cbar=True, annot_kws={"size": 8})
    plt.title("Multi-Label Scam Tactic Co-Occurrence Correlation (Train Set)", fontsize=12, fontweight="bold")
    plt.tight_layout()
    plt.savefig(artifacts_dir / "label_cooccurrence.png", dpi=200)
    plt.close()

    # Save Metadata and Taxonomy Inventory
    metadata = {
        "model_id": "trustlens-model3-scam-tactic-v1",
        "created_at_utc": pd.Timestamp.now("UTC").isoformat(),
        "task": "Multi-Label Social Engineering and Scam Tactic Detection",
        "train_samples": len(X_train_raw),
        "val_samples": len(X_val_raw),
        "test_samples": len(X_test_raw),
        "best_model": best_exp["model_name"],
        "micro_f1": best_exp["micro_f1"],
        "macro_f1": best_exp["macro_f1"],
        "weighted_f1": best_exp["weighted_f1"],
        "hamming_loss": best_exp["hamming_loss"],
        "supported_tactics_count": len(SUPPORTED_TACTIC_KEYS),
        "supported_tactics": SUPPORTED_TACTIC_KEYS,
        "unavailable_tactics": [
            {
                "id": k,
                "name": TACTIC_REGISTRY[k]["name"],
                "status": "unavailable",
                "reason": TACTIC_REGISTRY[k]["mapping_source"],
            }
            for k in ALL_TACTIC_KEYS
            if not TACTIC_REGISTRY[k]["supported"]
        ],
        "taxonomy": TACTIC_REGISTRY,
    }

    with open(artifacts_dir / "tactic_metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    with open(artifacts_dir / "tactic_experiment_report.json", "w", encoding="utf-8") as f:
        json.dump({"experiments": experiments, "best_model": best_exp}, f, indent=2)

    print(f"\n[OK] All Model 3 artifacts, PR curves, and reports saved to {artifacts_dir}")
    print("=" * 68)
    print("MODEL 3 TRAINING & BENCHMARK COMPLETED SUCCESSFULLY!")
    print("=" * 68)


if __name__ == "__main__":
    main()
