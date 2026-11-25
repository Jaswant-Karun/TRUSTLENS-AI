"""
TRUSTLENS AI - Phase 2.3: Held-Out Multi-Label Tactic Evaluation
Computes Micro F1, Macro F1, per-label Precision/Recall/F1, Hamming Loss,
PR-AUC, generates Precision-Recall curves, and logs real FP/FN examples.
"""

import sys
import json
import time
import shutil
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import joblib
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.metrics import (
    f1_score,
    precision_score,
    recall_score,
    hamming_loss,
    average_precision_score,
    precision_recall_curve,
)

from ml.tactic_detection.labels import SUPPORTED_LABELS, UNSUPPORTED_LABELS
from ml.tactic_detection.train import load_annotated_split


def main():
    print("=" * 70)
    print("TRUSTLENS AI - PHASE 2.3: HELD-OUT TACTIC EVALUATION")
    print("=" * 70)

    out_dir = Path("ml/artifacts/tactic_detection/v2.3_candidate")
    with open(out_dir / "training_metadata.json", "r", encoding="utf-8") as f:
        meta = json.load(f)

    X_test_raw, y_test, test_df = load_annotated_split("data/processed/text_test.parquet")
    vectorizer = joblib.load(out_dir / "vectorizer.joblib")
    X_test_vec = vectorizer.transform(X_test_raw)

    print(f"Loaded untouched annotated test split: {len(X_test_raw):,} samples")

    results = []
    best_probs = None
    for key, m_info in meta["models"].items():
        clf = joblib.load(out_dir / f"{key}.joblib")
        thresholds = m_info["thresholds"]

        t0 = time.perf_counter()
        y_probs = clf.predict_proba(X_test_vec)
        latency_ms = round(((time.perf_counter() - t0) * 1000) / len(X_test_raw), 4)

        y_pred = np.column_stack([
            (y_probs[:, i] >= thresholds[k]).astype(int)
            for i, k in enumerate(SUPPORTED_LABELS)
        ])

        micro_f1 = round(float(f1_score(y_test, y_pred, average="micro", zero_division=0)), 4)
        macro_f1 = round(float(f1_score(y_test, y_pred, average="macro", zero_division=0)), 4)
        h_loss = round(float(hamming_loss(y_test, y_pred)), 4)

        per_label = {}
        for idx, lbl in enumerate(SUPPORTED_LABELS):
            yt = y_test[:, idx]
            yp = y_pred[:, idx]
            ypr = y_probs[:, idx]
            per_label[lbl] = {
                "precision": round(float(precision_score(yt, yp, zero_division=0)), 4),
                "recall": round(float(recall_score(yt, yp, zero_division=0)), 4),
                "f1": round(float(f1_score(yt, yp, zero_division=0)), 4),
                "pr_auc": round(float(average_precision_score(yt, ypr)), 4) if yt.sum() > 0 else 0.0,
                "support": int(yt.sum()),
                "threshold": thresholds[lbl],
            }

        results.append({
            "model_key": key,
            "display_name": m_info["display_name"],
            "micro_f1": micro_f1,
            "macro_f1": macro_f1,
            "hamming_loss": h_loss,
            "inference_latency_ms_per_sample": latency_ms,
            "size_mb": m_info["size_mb"],
            "per_label": per_label,
        })
        print(f"\n  [{key}] Micro F1: {micro_f1:.4f} | Macro F1: {macro_f1:.4f} | Hamming Loss: {h_loss:.4f} | Latency: {latency_ms} ms")

    best = sorted(results, key=lambda r: (r["macro_f1"], r["micro_f1"]), reverse=True)[0]
    best_clf = joblib.load(out_dir / f"{best['model_key']}.joblib")
    best_probs = best_clf.predict_proba(X_test_vec)
    best_thresh = meta["models"][best["model_key"]]["thresholds"]
    best_preds = np.column_stack([
        (best_probs[:, i] >= best_thresh[k]).astype(int)
        for i, k in enumerate(SUPPORTED_LABELS)
    ])

    # Generate Precision-Recall Curves figure
    fig, ax = plt.subplots(figsize=(9, 6))
    for idx, lbl in enumerate(SUPPORTED_LABELS):
        if y_test[:, idx].sum() > 0:
            p, r, _ = precision_recall_curve(y_test[:, idx], best_probs[:, idx])
            ap = best["per_label"][lbl]["pr_auc"]
            ax.plot(r, p, label=f"{lbl} (AP={ap:.3f})")
    ax.set_title(f"Phase 2.3 Multi-Label Precision-Recall Curves ({best['display_name']})", fontweight="bold")
    ax.set_xlabel("Recall")
    ax.set_ylabel("Precision")
    ax.legend(loc="lower left", fontsize=8)
    ax.grid(True, alpha=0.3)
    pr_path = out_dir / "pr_curves_v2.3.png"
    fig.savefig(pr_path, dpi=150, bbox_inches="tight")
    plt.close(fig)

    docs_fig = Path("docs/screenshots/tactic_pr_curves_v2.3.png")
    docs_fig.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(pr_path, docs_fig)

    # Extract real False Positive and False Negative examples
    fp_examples = []
    fn_examples = []
    for idx, lbl in enumerate(SUPPORTED_LABELS):
        fp_idx = np.where((y_test[:, idx] == 0) & (best_preds[:, idx] == 1))[0]
        fn_idx = np.where((y_test[:, idx] == 1) & (best_preds[:, idx] == 0))[0]
        if len(fp_idx) > 0 and len(fp_examples) < 3:
            i = fp_idx[0]
            fp_examples.append({
                "tactic": lbl,
                "text": test_df.iloc[i]["cleaned_text"][:140],
                "predicted_prob": round(float(best_probs[i, idx]), 4),
            })
        if len(fn_idx) > 0 and len(fn_examples) < 3:
            i = fn_idx[0]
            fn_examples.append({
                "tactic": lbl,
                "text": test_df.iloc[i]["cleaned_text"][:140],
                "predicted_prob": round(float(best_probs[i, idx]), 4),
            })

    report = {
        "phase": "2.3",
        "dataset_version": "2.0.5",
        "test_samples": len(X_test_raw),
        "supported_labels": SUPPORTED_LABELS,
        "unsupported_labels": UNSUPPORTED_LABELS,
        "selected_model_key": best["model_key"],
        "selected_model_summary": best,
        "false_positive_examples": fp_examples,
        "false_negative_examples": fn_examples,
        "experiments": results,
    }

    with open(out_dir / "evaluation_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    with open(out_dir / "selected_model.json", "w", encoding="utf-8") as f:
        json.dump({"selected_model_key": best["model_key"], "model_version": "trustlens-model3-v2.3-candidate"}, f, indent=2)

    print(f"\nSelected Tactic Model: {best['display_name']} (Micro F1: {best['micro_f1']:.4f}, Macro F1: {best['macro_f1']:.4f})")


if __name__ == "__main__":
    main()
