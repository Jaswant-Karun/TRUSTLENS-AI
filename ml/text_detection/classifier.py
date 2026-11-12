"""
TRUSTLENS AI - Multilingual Scam Message Classifier (Engine 1)
Supports English, Hindi (Devanagari), and romanized Hinglish.
"""

from typing import Dict, Any, Optional
import os
import re


class MultilingualScamClassifier:
    """
    Multilingual Scam and Social Engineering Classifier.
    Evaluates SMS, WhatsApp, and email content across English, Hindi, and Hinglish.
    """

    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path or "ml/artifacts/multilingual_text_model.joblib"
        self.vectorizer_path = "ml/artifacts/tfidf_vectorizer.joblib"
        self.model = None
        self.vectorizer = None
        self.is_trained = False
        self._load_artifacts_if_available()

    def _load_artifacts_if_available(self) -> None:
        """Loads serialized models if they exist in artifacts directory."""
        if os.path.exists(self.model_path) and os.path.exists(self.vectorizer_path):
            try:
                import joblib
                self.model = joblib.load(self.model_path)
                self.vectorizer = joblib.load(self.vectorizer_path)
                self.is_trained = True
            except Exception:
                self.is_trained = False
        else:
            self.is_trained = False

    def detect_language(self, text: str) -> str:
        """Identifies primary language / script representation."""
        # Check Devanagari Unicode range
        if re.search(r"[\u0900-\u097F]", text):
            return "Hindi (Devanagari)"
        
        # Check Romanized Hinglish vocabulary markers
        hinglish_markers = [
            "aapka", "karein", "turant", "paisa", "khata", "sampark",
            "kare", "hai", "bheje", "band", "hoga", "shukriya", "dhyan"
        ]
        text_lower = text.lower()
        if any(re.search(rf"\b{w}\b", text_lower) for w in hinglish_markers):
            return "Hinglish (Romanized Hindi)"
            
        return "English"

    def predict(self, text: str) -> Dict[str, Any]:
        """
        Classifies incoming message.
        Uses trained model if available; otherwise returns linguistic evaluation
        and truthfully reports untrained model status.
        """
        lang = self.detect_language(text)

        if self.is_trained and self.model and self.vectorizer:
            X = self.vectorizer.transform([text])
            probs = self.model.predict_proba(X)[0]
            pred_idx = probs.argmax()
            classes = self.model.classes_
            predicted_label = str(classes[pred_idx])
            confidence = round(float(probs[pred_idx]), 4)
            is_threat = predicted_label.lower() in ["phishing", "smishing", "scam", "spam"]
            model_ver = "trained-calibrated-v1"
            explanation = f"Classified by trained {type(self.model).__name__} with confidence {confidence:.2%}"
        else:
            # Baseline deterministic heuristic (untrained state)
            threat_indicators = [
                "urgent", "immediately", "blocked", "suspended", "kyc",
                "otp", "verify", "lottery", "winner", "reward", "turant", "khata"
            ]
            matches = [w for w in threat_indicators if re.search(rf"\b{w}\b", text.lower())]
            is_threat = len(matches) >= 2
            predicted_label = "suspicious_heuristic" if is_threat else "unclassified"
            confidence = round(min(0.90, len(matches) * 0.25), 2)
            model_ver = "linguistic-heuristic-baseline (untrained ML)"
            explanation = f"Detected {len(matches)} suspicious keywords: {', '.join(matches[:4])}" if matches else "No overt baseline keywords detected"

        return {
            "text": text,
            "predicted_label": predicted_label,
            "confidence": confidence,
            "is_threat": is_threat,
            "detected_language": lang,
            "is_trained": self.is_trained,
            "model_version": model_ver,
            "explanation": explanation,
        }

