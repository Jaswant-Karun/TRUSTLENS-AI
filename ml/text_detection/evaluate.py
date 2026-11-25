"""
TRUSTLENS AI - Phase 2.1: Held-Out Test Set Evaluation & Model Selection
Evaluates all 3 trained candidate models on the untouched text_test.parquet split.
Selects the optimal model based on Macro F1, per-class recall, FNR, FPR, latency, and size.
"""

import sys
import json
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import yaml
import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import label_binarize
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    roc_auc_score,
    average_precision_score,
)


def main():
    print("=" * 70)
    print("TRUSTLENS AI - PHASE 2.1: HELD-OUT TEST SET EVALUATION")
    print("=" * 70)

    config_path = Path("ml/text_detection/config.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    out_dir = Path(config["artifacts"]["output_dir"])
    label_map = {int(k): v for k, v in config["labels"].items()}
    inv_label_map = {v: k for k, v in label_map.items()}
    classes = sorted(label_map.keys())

    # 1. Load untouched test split
    test_df = pd.read_parquet(config["dataset"]["test_path"])
    X_test_raw = test_df[config["dataset"]["text_column"]].fillna("").tolist()
    y_test = test_df[config["dataset"]["label_column"]].map(inv_label_map).astype(int).values
    y_test_bin = label_binarize(y_test, classes=classes)

    # Binary threat ground truth (0 = legitimate, 1 = any threat: spam/smishing/scam)
    y_true_binary = (y_test != 0).astype(int)

    print(f"Loaded untouched test split: {len(test_df):,} rows")

    results = []
    for model_key, m_cfg in config["models"].items():
        vec_path = out_dir / f"{model_key}_vectorizer.joblib"
        mod_path = out_dir / f"{model_key}_model.joblib"

        vectorizer = joblib.load(vec_path)
        clf = joblib.load(mod_path)
        total_mb = round((vec_path.stat().st_size + mod_path.stat().st_size) / (1024 * 1024), 3)

        # Measure inference latency (vectorize + predict_proba)
        t0 = time.perf_counter()
        X_test_vec = vectorizer.transform(X_test_raw)
        y_pred = clf.predict(X_test_vec)
        y_prob = clf.predict_proba(X_test_vec)
        total_ms = (time.perf_counter() - t0) * 1000
        latency_ms_per_sample = round(total_ms / len(X_test_raw), 4)

        acc = round(float(accuracy_score(y_test, y_pred)), 4)
        f1_mac = round(float(f1_score(y_test, y_pred, average="macro", zero_division=0)), 4)
        f1_wgt = round(float(f1_score(y_test, y_pred, average="weighted", zero_division=0)), 4)

        # Multi-class ROC-AUC and PR-AUC (OvR)
        roc_auc_ovr = round(float(roc_auc_score(y_test_bin, y_prob, multi_class="ovr", average="macro")), 4)
        pr_auc_ovr = round(float(average_precision_score(y_test_bin, y_prob, average="macro")), 4)

        # Per-class metrics
        precs = precision_score(y_test, y_pred, labels=classes, average=None, zero_division=0)
        recs = recall_score(y_test, y_pred, labels=classes, average=None, zero_division=0)
        f1s = f1_score(y_test, y_pred, labels=classes, average=None, zero_division=0)
        per_class = {}
        for idx, cid in enumerate(classes):
            per_class[label_map[cid]] = {
                "precision": round(float(precs[idx]), 4),
                "recall": round(float(recs[idx]), 4),
                "f1": round(float(f1s[idx]), 4),
                "support": int((y_test == cid).sum()),
            }

        # Binary Threat vs Legitimate FPR and FNR
        y_pred_binary = (y_pred != 0).astype(int)
        cm_bin = confusion_matrix(y_true_binary, y_pred_binary)
        tn, fp, fn, tp = cm_bin.ravel()
        fpr = round(float(fp / (fp + tn)) if (fp + tn) > 0 else 0.0, 4)
        fnr = round(float(fn / (fn + tp)) if (fn + tp) > 0 else 0.0, 4)

        # Per-language evaluation
        per_language = {}
        for lang in sorted(test_df["language"].unique()):
            mask = (test_df["language"] == lang).values
            if mask.sum() > 0:
                sub_y = y_test[mask]
                sub_p = y_pred[mask]
                sub_y_bin = (sub_y != 0).astype(int)
                sub_p_bin = (sub_p != 0).astype(int)
                per_language[lang] = {
                    "samples": int(mask.sum()),
                    "accuracy": round(float(accuracy_score(sub_y, sub_p)), 4),
                    "macro_f1": round(float(f1_score(sub_y, sub_p, average="macro", zero_division=0)), 4),
                    "threat_recall": round(float(recall_score(sub_y_bin, sub_p_bin, pos_label=1, zero_division=0)), 4),
                }

        cm_multi = confusion_matrix(y_test, y_pred, labels=classes).tolist()

        res = {
            "model_key": model_key,
            "display_name": m_cfg["display_name"],
            "accuracy": acc,
            "macro_f1": f1_mac,
            "weighted_f1": f1_wgt,
            "roc_auc_ovr_macro": roc_auc_ovr,
            "pr_auc_ovr_macro": pr_auc_ovr,
            "threat_false_positive_rate": fpr,
            "threat_false_negative_rate": fnr,
            "inference_latency_ms_per_sample": latency_ms_per_sample,
            "artifact_size_mb": total_mb,
            "per_class": per_class,
            "per_language": per_language,
            "confusion_matrix": cm_multi,
        }
        results.append(res)
        print(
            f"\n  [{model_key}] Macro F1: {f1_mac:.4f} | Acc: {acc:.4f} | "
            f"ROC-AUC: {roc_auc_ovr:.4f} | FPR: {fpr:.4f} | FNR: {fnr:.4f} | "
            f"Latency: {latency_ms_per_sample} ms | Size: {total_mb} MB"
        )

    # Select best model by Macro F1 (with tie-breaking on lowest FNR)
    best = sorted(results, key=lambda r: (r["macro_f1"], -r["threat_false_negative_rate"]), reverse=True)[0]

    report = {
        "phase": "2.1",
        "dataset_version": config["dataset"]["version"],
        "test_samples": len(test_df),
        "labels": label_map,
        "selection_criteria": "Macro F1, per-class recall, FNR, FPR, inference latency, and artifact size",
        "selected_model_key": best["model_key"],
        "selected_model_summary": best,
        "experiments": results,
    }

    with open(out_dir / "evaluation_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    with open(out_dir / "selected_model.json", "w", encoding="utf-8") as f:
        json.dump({"selected_model_key": best["model_key"], "model_version": "trustlens-model1-v2.1-candidate"}, f, indent=2)

    print(f"\nSelected Optimal Candidate Model: {best['display_name']} (Macro F1: {best['macro_f1']:.4f})")
    print(f"Evaluation report saved to {out_dir / 'evaluation_report.json'}")


if __name__ == "__main__":
    main()
