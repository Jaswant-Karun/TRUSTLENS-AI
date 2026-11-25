"""
TRUSTLENS AI - Phase 2.2: Phishing URL Held-Out Evaluation, SHAP & Domain Generalization
Evaluates Logistic Regression, Random Forest, and XGBoost on untouched urls_test.parquet.
Computes global metrics, SHAP TreeExplainer feature importance, and TLD generalization.
"""

import sys
import json
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import joblib
import numpy as np
import pandas as pd
import shap
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
    confusion_matrix,
)

from ml.url_detection.features import FEATURE_COLUMNS


def main():
    print("=" * 70)
    print("TRUSTLENS AI - PHASE 2.2: HELD-OUT URL TEST SET EVALUATION")
    print("=" * 70)

    out_dir = Path("ml/artifacts/url_detection/v2.2_candidate")
    test_df = pd.read_parquet("data/processed/urls_test.parquet")
    X_test = test_df[FEATURE_COLUMNS].astype(float).values
    y_test = test_df["is_phishing"].astype(int).values

    scaler = joblib.load(out_dir / "scaler.joblib")
    X_test_scaled = scaler.transform(X_test)

    with open(out_dir / "training_metadata.json", "r", encoding="utf-8") as f:
        meta = json.load(f)

    results = []
    for key, m_info in meta["models"].items():
        mod_path = out_dir / f"{key}.joblib"
        model = joblib.load(mod_path)
        X_in = X_test_scaled if m_info["requires_scaler"] else X_test

        t0 = time.perf_counter()
        y_pred = model.predict(X_in)
        y_prob = model.predict_proba(X_in)[:, 1]
        latency_ms = round(((time.perf_counter() - t0) * 1000) / len(X_test), 5)

        cm = confusion_matrix(y_test, y_pred)
        tn, fp, fn, tp = cm.ravel()
        fpr = round(float(fp / (fp + tn)) if (fp + tn) > 0 else 0.0, 4)
        fnr = round(float(fn / (fn + tp)) if (fn + tp) > 0 else 0.0, 4)

        res = {
            "model_key": key,
            "display_name": m_info["display_name"],
            "accuracy": round(float(accuracy_score(y_test, y_pred)), 4),
            "precision": round(float(precision_score(y_test, y_pred, zero_division=0)), 4),
            "recall": round(float(recall_score(y_test, y_pred, zero_division=0)), 4),
            "f1_binary": round(float(f1_score(y_test, y_pred, zero_division=0)), 4),
            "macro_f1": round(float(f1_score(y_test, y_pred, average="macro", zero_division=0)), 4),
            "roc_auc": round(float(roc_auc_score(y_test, y_prob)), 4),
            "pr_auc": round(float(average_precision_score(y_test, y_prob)), 4),
            "false_positive_rate": fpr,
            "false_negative_rate": fnr,
            "inference_latency_ms_per_sample": latency_ms,
            "size_mb": m_info["size_mb"],
            "confusion_matrix": cm.tolist(),
        }
        results.append(res)
        print(
            f"\n  [{key}] Macro F1: {res['macro_f1']:.4f} | ROC-AUC: {res['roc_auc']:.4f} | "
            f"PR-AUC: {res['pr_auc']:.4f} | FPR: {fpr:.4f} | FNR: {fnr:.4f} | Latency: {latency_ms} ms"
        )

    best = sorted(results, key=lambda r: (r["macro_f1"], -r["false_negative_rate"]), reverse=True)[0]
    best_model = joblib.load(out_dir / f"{best['model_key']}.joblib")

    # Domain / TLD Group Generalization Breakdown for Selected Model
    X_best_in = X_test_scaled if meta["models"][best["model_key"]]["requires_scaler"] else X_test
    y_best_pred = best_model.predict(X_best_in)

    generalization = {}
    for label_name, mask in [
        ("Popular TLDs (.com/.org/.net/.in etc.)", (test_df["tld_popularity"] == 1).values),
        ("Non-Popular / Long-Tail TLDs", (test_df["tld_popularity"] == 0).values),
        ("HTTPS Scheme URLs", (test_df["https_flag"] == 1).values),
        ("HTTP / Non-HTTPS URLs", (test_df["https_flag"] == 0).values),
    ]:
        if mask.sum() > 0:
            generalization[label_name] = {
                "samples": int(mask.sum()),
                "macro_f1": round(float(f1_score(y_test[mask], y_best_pred[mask], average="macro", zero_division=0)), 4),
                "recall_phishing": round(float(recall_score(y_test[mask], y_best_pred[mask], zero_division=0)), 4),
            }

    # Compute SHAP TreeExplainer global importance on a deterministic 1,000-sample subset
    print("\nComputing SHAP TreeExplainer feature importance...")
    shap_ranking = []
    if best["model_key"] in ("xgboost_model", "random_forest"):
        explainer = shap.TreeExplainer(best_model)
        sample_X = X_test[:1000]
        shap_vals = explainer.shap_values(sample_X)
        if isinstance(shap_vals, list):
            shap_vals = shap_vals[1]
        elif len(shap_vals.shape) == 3:
            shap_vals = shap_vals[:, :, 1]
        mean_abs = np.abs(shap_vals).mean(axis=0)
        for col, val in sorted(zip(FEATURE_COLUMNS, mean_abs), key=lambda x: x[1], reverse=True):
            shap_ranking.append({"feature": col, "mean_abs_shap": round(float(val), 4)})

    report = {
        "phase": "2.2",
        "dataset_version": "2.0.5",
        "test_samples": len(test_df),
        "unique_test_domains": int(test_df["domain_group_id"].nunique()),
        "selected_model_key": best["model_key"],
        "selected_model_summary": best,
        "domain_generalization": generalization,
        "shap_feature_importance": shap_ranking,
        "experiments": results,
    }

    with open(out_dir / "evaluation_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    with open(out_dir / "selected_model.json", "w", encoding="utf-8") as f:
        json.dump({"selected_model_key": best["model_key"], "model_version": "trustlens-model2-v2.2-candidate"}, f, indent=2)

    print(f"\nSelected Optimal URL Model: {best['display_name']} (Macro F1: {best['macro_f1']:.4f})")
    print(f"Evaluation report saved to {out_dir / 'evaluation_report.json'}")


if __name__ == "__main__":
    main()
