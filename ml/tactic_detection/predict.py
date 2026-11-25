"""
TRUSTLENS AI - Phase 2.3: Evidence-Oriented Tactic Predictor
Returns detected tactics, per-tactic scores, model version, linear evidence spans,
unsupported/unavailable labels (fake_investment), and explicit limitations.
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, List
import joblib
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ml.preprocessing.text_preprocessor import text_preprocessor
from ml.tactic_detection.labels import TACTIC_LABELS, SUPPORTED_LABELS, UNSUPPORTED_LABELS


class CandidateTacticPredictor:
    def __init__(self, artifact_dir: str = "ml/artifacts/tactic_detection/v2.3_candidate"):
        self.artifact_dir = Path(artifact_dir)
        self.model_version = "trustlens-model3-v2.3-candidate"
        self.is_loaded = False
        self.vectorizer = None
        self.model = None
        self.thresholds = {}
        self._load()

    def _load(self):
        sel_path = self.artifact_dir / "selected_model.json"
        meta_path = self.artifact_dir / "training_metadata.json"
        if not sel_path.exists() or not meta_path.exists():
            return
        with open(sel_path, "r", encoding="utf-8") as f:
            self.model_key = json.load(f)["selected_model_key"]
        with open(meta_path, "r", encoding="utf-8") as f:
            self.thresholds = json.load(f)["models"][self.model_key]["thresholds"]
        self.vectorizer = joblib.load(self.artifact_dir / "vectorizer.joblib")
        self.model = joblib.load(self.artifact_dir / f"{self.model_key}.joblib")
        self.is_loaded = True

    def _extract_evidence_spans(self, X_vec, label_idx: int, top_k: int = 3) -> List[str]:
        try:
            est = self.model.estimators_[label_idx]
            if hasattr(est, "coef_"):
                coefs = est.coef_[0]
            elif hasattr(est, "calibrated_classifiers_"):
                coefs = np.mean([cc.estimator.coef_[0] for cc in est.calibrated_classifiers_], axis=0)
            else:
                return []
            feature_names = self.vectorizer.get_feature_names_out()
            x_arr = X_vec.toarray().ravel()
            nz = np.where(x_arr > 0)[0]
            if len(nz) == 0:
                return []
            contrib = x_arr[nz] * coefs[nz]
            top_local = np.argsort(contrib)[::-1][:top_k]
            return [str(feature_names[nz[i]]).split("__")[-1] for i in top_local if contrib[i] > 0]
        except Exception:
            return []

    def predict(self, raw_text: str) -> Dict[str, Any]:
        if not self.is_loaded:
            return {"status": "unavailable", "error": "Candidate v2.3 tactic model not loaded."}

        norm = text_preprocessor.preprocess(raw_text, mask_personal_data=True)
        cleaned = norm["cleaned_text"]
        X_vec = self.vectorizer.transform([cleaned])
        probs = self.model.predict_proba(X_vec)[0]

        detected = []
        per_tactic_scores = {}
        for idx, lbl in enumerate(SUPPORTED_LABELS):
            score = round(float(probs[idx]), 4)
            thresh = self.thresholds.get(lbl, 0.5)
            per_tactic_scores[lbl] = score
            if score >= thresh:
                detected.append({
                    "tactic_id": lbl,
                    "tactic_name": TACTIC_LABELS[lbl]["name"],
                    "tactic_code": TACTIC_LABELS[lbl]["code"],
                    "score": score,
                    "threshold": thresh,
                    "supporting_evidence_spans": self._extract_evidence_spans(X_vec, idx, top_k=3),
                })

        return {
            "detected_tactics": detected,
            "per_tactic_scores": per_tactic_scores,
            "unsupported_or_unavailable_labels": {
                lbl: TACTIC_LABELS[lbl]["source"] for lbl in UNSUPPORTED_LABELS
            },
            "model_version": self.model_version,
            "limitations": (
                "9 of 10 tactics are supported by genuine ScamShield annotations. "
                "'fake_investment' is unavailable due to absent training labels."
            ),
        }


if __name__ == "__main__":
    p = CandidateTacticPredictor()
    sample = "URGENT: Your SBI account will be suspended today! Verify KYC immediately at http://sbi-kyc.com"
    print(json.dumps(p.predict(sample), indent=2))
