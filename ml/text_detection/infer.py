"""
TRUSTLENS AI - Model 1 Standalone Production Inference Engine
Returns:
- Predicted class (legitimate, spam, smishing, scam)
- Calibrated confidence score
- Model version
- Detected language
- Supporting text evidence (most influential n-grams)
- Processing time in milliseconds
"""

import sys
import os
import time
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import joblib
import numpy as np
from ml.preprocessing.text_preprocessor import text_preprocessor


class ScamMessageInferenceEngine:
    def __init__(self, artifacts_dir: Optional[str] = None):
        self.artifacts_dir = Path(artifacts_dir or "ml/artifacts/text_detection")
        self.model_path = self.artifacts_dir / "best_model.joblib"
        self.vectorizer_path = self.artifacts_dir / "best_vectorizer.joblib"

        self.model = None
        self.vectorizer = None
        self.is_loaded = False
        self._load_artifacts()

    def _load_artifacts(self) -> None:
        if self.model_path.exists() and self.vectorizer_path.exists():
            try:
                self.model = joblib.load(self.model_path)
                self.vectorizer = joblib.load(self.vectorizer_path)
                self.is_loaded = True
            except Exception as e:
                print(f"[WARN] Failed to load model artifacts: {e}")
                self.is_loaded = False
        else:
            self.is_loaded = False

    def explain_prediction(self, text: str, top_k: int = 5) -> List[str]:
        """Extracts top contributing n-grams/tokens from message for explainability."""
        if not self.is_loaded:
            return []
        try:
            # Check if linear model with feature weights
            if hasattr(self.model, "calibrated_classifiers_"):
                # Calibrated LinearSVC
                base_clf = self.model.calibrated_classifiers_[0].estimator
                coef = base_clf.coef_[0]
            elif hasattr(self.model, "coef_"):
                coef = self.model.coef_[0]
            else:
                return []

            feature_names = np.array(self.vectorizer.get_feature_names_out())
            X = self.vectorizer.transform([text])
            nonzero_idx = X.nonzero()[1]

            if len(nonzero_idx) == 0:
                return []

            # Contribution = tfidf_value * coefficient
            contributions = X.data * coef[nonzero_idx]
            top_indices = nonzero_idx[np.argsort(contributions)[-top_k:]]
            return [str(feature_names[i]).replace("char__", "").replace("word__", "") for i in reversed(top_indices)]
        except Exception:
            return []

    def predict(self, raw_text: str) -> Dict[str, Any]:
        """Classifies incoming digital communication."""
        start_time = time.perf_counter()

        # Step 1: Preprocessing & language identification
        norm = text_preprocessor.preprocess(raw_text, mask_personal_data=True)
        cleaned_text = norm["cleaned_text"]
        detected_language = norm["language"]

        if not self.is_loaded:
            latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
            return {
                "input_text": raw_text,
                "cleaned_text": cleaned_text,
                "predicted_class": "unclassified",
                "is_threat": False,
                "confidence": 0.0,
                "model_version": "uninitialized",
                "detected_language": detected_language,
                "supporting_evidence": [],
                "processing_time_ms": latency_ms,
                "status": "Awaiting Model 1 baseline training",
            }

        # Step 2: Vectorization & Inference
        X = self.vectorizer.transform([cleaned_text])
        if hasattr(self.model, "predict_proba"):
            probs = self.model.predict_proba(X)[0]
            pred_idx = int(probs.argmax())
            confidence = float(probs[pred_idx])
        else:
            decision = self.model.decision_function(X)[0]
            pred_idx = 1 if decision > 0 else 0
            confidence = float(1.0 / (1.0 + np.exp(-decision)))

        is_threat = bool(pred_idx == 1)

        # Fine-grained class mapping based on heuristics and extracted tokens
        if not is_threat:
            predicted_class = "legitimate"
        elif norm["extracted_urls"] or "http" in raw_text.lower():
            predicted_class = "smishing"
        elif any(w in raw_text.lower() for w in ["upi", "kyc", "bank", "khata", "blocked"]):
            predicted_class = "scam"
        else:
            predicted_class = "spam"

        # Step 3: Evidence Extraction
        evidence = self.explain_prediction(cleaned_text, top_k=4)

        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

        return {
            "input_text": raw_text,
            "cleaned_text": cleaned_text,
            "predicted_class": predicted_class,
            "is_threat": is_threat,
            "confidence": round(confidence, 4),
            "model_version": "trustlens-model1-v1.0",
            "detected_language": detected_language,
            "supporting_evidence": evidence,
            "processing_time_ms": latency_ms,
            "extracted_urls": norm["extracted_urls"],
        }


engine = ScamMessageInferenceEngine()


if __name__ == "__main__":
    sample_texts = [
        "Aapka SBI khata turant band ho jayega, kripya apna KYC update karein: http://192.168.1.50/sbi",
        "Hey, are you free this evening for dinner at the new Italian place?",
        "URGENT: Submit OTP immediately to claim your 50,000 cash prize!"
    ]
    for text in sample_texts:
        res = engine.predict(text)
        print("\nInput:", text)
        print("Result:", res)
