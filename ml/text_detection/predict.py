"""
TRUSTLENS AI - Phase 2.1: Evidence-Oriented Text Scam Prediction Module
Loads the v2.1 candidate artifacts and provides calibrated multi-class predictions
with linear hyperplane token attribution (never attention weights) and explicit limitations.
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


class CandidateTextScamPredictor:
    """Evidence-oriented predictor for the Phase 2.1 multi-class text scam classifier."""

    def __init__(self, artifact_dir: str = "ml/artifacts/text_detection/v2.1_candidate"):
        self.artifact_dir = Path(artifact_dir)
        self.model_version = "trustlens-model1-v2.1-candidate"
        self.is_loaded = False
        self.vectorizer = None
        self.model = None
        self.label_map = {}
        self._load()

    def _load(self):
        sel_path = self.artifact_dir / "selected_model.json"
        lbl_path = self.artifact_dir / "label_mapping.json"
        if not sel_path.exists() or not lbl_path.exists():
            return

        with open(sel_path, "r", encoding="utf-8") as f:
            sel = json.load(f)
        with open(lbl_path, "r", encoding="utf-8") as f:
            self.label_map = {int(k): v for k, v in json.load(f).items()}

        key = sel["selected_model_key"]
        self.vectorizer = joblib.load(self.artifact_dir / f"{key}_vectorizer.joblib")
        self.model = joblib.load(self.artifact_dir / f"{key}_model.joblib")
        self.model_key = key
        self.is_loaded = True

    def _extract_supporting_tokens(self, X_vec, class_idx: int, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Extracts top supporting n-gram tokens using exact linear hyperplane weights * TF-IDF values.
        Never uses transformer attention weights.
        """
        try:
            feature_names = self.vectorizer.get_feature_names_out()
            if hasattr(self.model, "coef_"):
                coefs = self.model.coef_[class_idx]
            elif hasattr(self.model, "calibrated_classifiers_"):
                # Average base LinearSVC weights across CV calibration folds
                coef_list = [cc.estimator.coef_[class_idx] for cc in self.model.calibrated_classifiers_]
                coefs = np.mean(coef_list, axis=0)
            else:
                return []

            x_arr = X_vec.toarray().ravel()
            nonzero_idx = np.where(x_arr > 0)[0]
            if len(nonzero_idx) == 0:
                return []

            contributions = x_arr[nonzero_idx] * coefs[nonzero_idx]
            top_local = np.argsort(contributions)[::-1][:top_k]

            tokens = []
            for idx in top_local:
                score = float(contributions[idx])
                if score > 0:
                    tokens.append({
                        "token": str(feature_names[nonzero_idx[idx]]),
                        "attribution_score": round(score, 4),
                    })
            return tokens
        except Exception:
            return []

    def predict(self, raw_text: str) -> Dict[str, Any]:
        if not self.is_loaded:
            return {"status": "unavailable", "error": "Candidate v2.1 model artifacts not loaded."}

        norm = text_preprocessor.preprocess(raw_text, mask_personal_data=True)
        cleaned = norm["cleaned_text"]
        if not cleaned:
            return {"status": "error", "error": "Empty or unprocessable text input."}

        X_vec = self.vectorizer.transform([cleaned])
        probs = self.model.predict_proba(X_vec)[0]
        pred_idx = int(np.argmax(probs))
        pred_label = self.label_map[pred_idx]
        confidence = round(float(probs[pred_idx]), 4)

        prob_dict = {
            self.label_map[i]: round(float(probs[i]), 4)
            for i in range(len(probs))
        }

        supporting_tokens = self._extract_supporting_tokens(X_vec, pred_idx, top_k=5)

        return {
            "predicted_class": pred_label,
            "is_threat": pred_label != "legitimate",
            "confidence": confidence,
            "class_probabilities": prob_dict,
            "detected_language": norm["language"],
            "supporting_tokens": supporting_tokens,
            "model_version": self.model_version,
            "limitations": (
                "Baseline TF-IDF linear classifier. Strong on English and Hinglish; "
                "lower threat recall on Devanagari Hindi. Tamil/Bengali are unsupported."
            ),
        }


if __name__ == "__main__":
    predictor = CandidateTextScamPredictor()
    sample = "URGENT: Your SBI account will be blocked today. Update KYC at http://sbi-kyc-update.com"
    print(json.dumps(predictor.predict(sample), indent=2))
