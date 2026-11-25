"""
TRUSTLENS AI - Phase 2.2: Evidence-Oriented Phishing URL Predictor with SHAP
Zero-hop deterministic URL feature extraction + SHAP TreeExplainer attribution.
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, List
import joblib
import numpy as np
import shap

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ml.url_detection.features import extract_url_features, FEATURE_COLUMNS


class CandidateURLPhishingPredictor:
    """Zero-hop URL phishing classifier with real SHAP TreeExplainer attributions."""

    def __init__(self, artifact_dir: str = "ml/artifacts/url_detection/v2.2_candidate"):
        self.artifact_dir = Path(artifact_dir)
        self.model_version = "trustlens-model2-v2.2-candidate"
        self.is_loaded = False
        self.model = None
        self.explainer = None
        self._load()

    def _load(self):
        sel_path = self.artifact_dir / "selected_model.json"
        if not sel_path.exists():
            return
        with open(sel_path, "r", encoding="utf-8") as f:
            sel = json.load(f)
        self.model_key = sel["selected_model_key"]
        self.model = joblib.load(self.artifact_dir / f"{self.model_key}.joblib")
        if self.model_key in ("xgboost_model", "random_forest"):
            self.explainer = shap.TreeExplainer(self.model)
        self.is_loaded = True

    def predict(self, raw_url: str) -> Dict[str, Any]:
        if not self.is_loaded:
            return {"status": "unavailable", "error": "Candidate v2.2 URL model artifacts not loaded."}

        feats = extract_url_features(raw_url)
        X_vec = np.array([[float(feats[col]) for col in FEATURE_COLUMNS]])

        prob_phishing = float(self.model.predict_proba(X_vec)[0][1])
        is_phishing = prob_phishing >= 0.5

        contributing_features: List[Dict[str, Any]] = []
        if self.explainer is not None:
            shap_vals = self.explainer.shap_values(X_vec)
            if isinstance(shap_vals, list):
                shap_vals = shap_vals[1]
            elif len(shap_vals.shape) == 3:
                shap_vals = shap_vals[:, :, 1]
            row_shap = shap_vals[0]
            top_idx = np.argsort(np.abs(row_shap))[::-1][:5]
            for idx in top_idx:
                contributing_features.append({
                    "feature": FEATURE_COLUMNS[idx],
                    "value": feats[FEATURE_COLUMNS[idx]],
                    "shap_impact": round(float(row_shap[idx]), 4),
                    "direction": "increases_phishing_risk" if row_shap[idx] > 0 else "decreases_phishing_risk",
                })

        return {
            "url": raw_url,
            "predicted_class": "phishing" if is_phishing else "legitimate",
            "is_phishing": bool(is_phishing),
            "phishing_probability": round(prob_phishing, 4),
            "important_contributing_features": contributing_features,
            "model_version": self.model_version,
            "network_policy": "zero_hop_offline_only",
            "limitations": (
                "Lexical and structural features alone do not constitute definitive proof that a URL is malicious. "
                "A missing threat-intelligence match or low lexical risk score does not automatically classify a URL as safe."
            ),
        }


if __name__ == "__main__":
    predictor = CandidateURLPhishingPredictor()
    print(json.dumps(predictor.predict("http://192.168.1.50:8080/sbi-kyc/update.php"), indent=2))
