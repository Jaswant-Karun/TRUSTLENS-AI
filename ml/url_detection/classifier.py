"""
TRUSTLENS AI - Phishing URL Detector (Engine 2)
Integrates 17-feature extraction with XGBoost / Random Forest classifier.
"""

from pathlib import Path
from typing import Dict, Any, Optional, List
import os

from ml.url_detection.features import extract_url_features, FEATURE_COLUMNS
from ml.url_detection.infer import PhishingURLInferenceEngine


class PhishingURLDetector:
    """
    Phishing URL Detection engine.
    Uses structural and lexical features to predict phishing risk without visiting target websites.
    """

    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path or "ml/artifacts/phishing_url_model.joblib"
        self.engine = PhishingURLInferenceEngine(
            artifacts_dir=str(Path(self.model_path).parent / "url_detection" if "url_detection" not in str(self.model_path) else Path(self.model_path).parent)
        )
        self.is_trained = self.engine.is_loaded

    def analyze(self, url: str) -> Dict[str, Any]:
        """
        Extracts features and evaluates the URL.
        Guarantees zero outbound network connections to target endpoints.
        """
        res = self.engine.predict(url)
        return {
            "url": url,
            "predicted_label": res["predicted_label"],
            "risk_score": res["risk_score"],
            "is_phishing": res["is_phishing"],
            "features": res["features"],
            "top_risk_factors": res["top_risk_factors"],
            "is_trained": self.is_trained,
            "model_version": res.get("model_version", "trustlens-model2-xgboost-v1.0"),
            "processing_time_ms": res.get("processing_time_ms", 0.0),
        }

