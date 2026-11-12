"""
TRUSTLENS AI - Multilingual Scam Message Classifier (Engine 1)
Supports English, Hindi (Devanagari), and romanized Hinglish.
Integrates trained Feature Union + Calibrated LinearSVC pipeline.
"""

from typing import Dict, Any, Optional
import os
from pathlib import Path

from ml.text_detection.infer import engine


class MultilingualScamClassifier:
    """
    Multilingual Scam and Social Engineering Classifier.
    Evaluates SMS, WhatsApp, and email content across English, Hindi, and Hinglish.
    """

    def __init__(self, model_path: Optional[str] = None):
        self.engine = engine
        self.is_trained = engine.is_loaded

    def detect_language(self, text: str) -> str:
        """Identifies primary language / script representation."""
        from ml.preprocessing.text_preprocessor import text_preprocessor
        return text_preprocessor.identify_language(text)

    def predict(self, text: str) -> Dict[str, Any]:
        """Classifies incoming message using trained calibrated model."""
        res = self.engine.predict(text)
        return {
            "text": text,
            "predicted_label": res["predicted_class"],
            "confidence": res["confidence"],
            "is_threat": res["is_threat"],
            "detected_language": res["detected_language"],
            "is_trained": self.is_trained,
            "model_version": res["model_version"],
            "explanation": f"Contributing signals: {', '.join(res['supporting_evidence'][:4])}" if res['supporting_evidence'] else "Linguistic indicators analyzed",
            "processing_time_ms": res["processing_time_ms"],
        }
