"""
TRUSTLENS AI - Model 3 Multi-Label & Confidence Calibration Evaluation
Evaluates v2.3 One-vs-Rest Calibrated LinearSVC on 8,563 annotated test samples:
- Micro-F1, Macro-F1, Hamming Loss, Exact-Match Accuracy
- Multi-label (>= 2 tactics) subset performance
- Per-label Brier Score and Expected Calibration Error (ECE)
"""

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, brier_score_loss, f1_score, hamming_loss

from ml.tactic_detection.labels import SUPPORTED_LABELS, map_processed_row_to_tactics


def compute_ece(y_true: np.ndarray, y_prob: np.ndarray, n_bins: int = 10) -> float:
    bins = np.linspace(0.0, 1.0, n_bins + 1)
    ece = 0.0
    n = len(y_true)
    for i in range(n_bins):
        mask = (y_prob >= bins[i]) & (y_prob < bins[i + 1] if i < n_bins - 1 else y_prob <= bins[i + 1])
        if np.any(mask):
            ece += (np.sum(mask) / n) * abs(float(y_true[mask].mean()) - float(y_prob[mask].mean()))
    return round(float(ece), 4)


def main():
    v2_dir = Path("ml/artifacts/tactic_detection/v2.3_candidate")
    clf = joblib.load(v2_dir / "ovr_linearsvc.joblib")
    vec = joblib.load(v2_dir / "vectorizer.joblib")
    rep = json.loads((v2_dir / "evaluation_report.json").read_text(encoding="utf-8"))
    per_lbl_meta = rep["selected_model_summary"]["per_label"]
    thresholds = np.array([per_lbl_meta[k]["threshold"] for k in SUPPORTED_LABELS])

    df = pd.read_parquet("data/processed/text_test.parquet")
    df = df[df["tactics"] != "{}"].reset_index(drop=True)
    texts = df["cleaned_text"].fillna("").tolist()
    y_true = np.array(
        [
            [map_processed_row_to_tactics(r["tactics"], r["head2_scam_intent"], r["metadata_json"])[k] for k in SUPPORTED_LABELS]
            for _, r in df.iterrows()
        ],
        dtype=np.int32,
    )

    X = vec.transform(texts)
    probs = clf.predict_proba(X)
    y_pred = (probs >= thresholds).astype(int)

    multi_mask = y_true.sum(axis=1) >= 2
    per_label_cal = {}
    for idx, key in enumerate(SUPPORTED_LABELS):
        per_label_cal[key] = {
            "support": int(y_true[:, idx].sum()),
            "brier_score": round(float(brier_score_loss(y_true[:, idx], probs[:, idx])), 4),
            "ece_10bins": compute_ece(y_true[:, idx], probs[:, idx]),
            "threshold": float(thresholds[idx]),
        }

    out = {
        "annotated_test_samples": int(len(df)),
        "multi_label_messages_count": int(multi_mask.sum()),
        "overall": {
            "micro_f1": round(float(f1_score(y_true, y_pred, average="micro", zero_division=0)), 4),
            "macro_f1": round(float(f1_score(y_true, y_pred, average="macro", zero_division=0)), 4),
            "hamming_loss": round(float(hamming_loss(y_true, y_pred)), 4),
            "exact_match_accuracy": round(float(accuracy_score(y_true, y_pred)), 4),
        },
        "multi_label_subset": {
            "samples": int(multi_mask.sum()),
            "micro_f1": round(float(f1_score(y_true[multi_mask], y_pred[multi_mask], average="micro", zero_division=0)), 4),
            "macro_f1": round(float(f1_score(y_true[multi_mask], y_pred[multi_mask], average="macro", zero_division=0)), 4),
            "exact_match_accuracy": round(float(accuracy_score(y_true[multi_mask], y_pred[multi_mask])), 4),
        },
        "per_label_calibration": per_label_cal,
        "mean_brier_score": round(float(np.mean([v["brier_score"] for v in per_label_cal.values()])), 4),
        "mean_ece": round(float(np.mean([v["ece_10bins"] for v in per_label_cal.values()])), 4),
    }

    out_path = v2_dir / "calibration_and_multilabel_report.json"
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
