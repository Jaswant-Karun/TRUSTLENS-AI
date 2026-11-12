"""
TRUSTLENS AI - Phishing URL Detector (Engine 2)
Integrates 17-feature extraction with XGBoost / Random Forest classifier.
"""

from pathlib import Path
from typing import Dict, Any, Optional
import os

from ml.url_detection.features import extract_url_features


class PhishingURLDetector:
    """
    Phishing URL Detection engine.
    Uses structural and lexical features to predict phishing risk without visiting target websites.
    """

    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path or "ml/artifacts/phishing_url_model.joblib"
        self.model = None
        self.is_trained = False
        self._load_model_if_available()

    def _load_model_if_available(self) -> None:
        """Loads trained weights if present on disk; keeps status truthful otherwise."""
        if os.path.exists(self.model_path):
            try:
                import joblib
                self.model = joblib.load(self.model_path)
                self.is_trained = True
            except Exception:
                self.is_trained = False
                self.model = None
        else:
            self.is_trained = False
            self.model = None

    def analyze(self, url: str) -> Dict[str, Any]:
        """
        Extracts features and evaluates the URL.
        If a trained ML model is available, uses the model's calibrated probability.
        Otherwise, returns deterministic lexical features with an explicit 'untrained' flag.
        """
        features = extract_url_features(url)
        risk_factors = []

        if features["has_ip_address"]:
            risk_factors.append("Direct IP address used instead of hostname")
        if features["is_suspicious_tld"]:
            risk_factors.append("High-risk top-level domain (TLD) associated with phishing")
        if features["is_shortened"]:
            risk_factors.append("URL shortener obscures destination endpoint")
        if features["has_suspicious_keywords"]:
            risk_factors.append("Contains sensitive authentication keywords (login/kyc/update/bank)")
        if features["domain_entropy"] > 4.2:
            risk_factors.append("High domain entropy indicates algorithmic generation (DGA)")

        if self.is_trained and self.model is not None:
            # Predict using trained model
            # Feature ordering must match training schema
            import pandas as pd
            df_features = pd.DataFrame([features])
            pred_prob = float(self.model.predict_proba(df_features)[0][1])
            is_phishing = pred_prob >= 0.50
            predicted_label = "phishing" if is_phishing else "legitimate"
            risk_score = round(pred_prob, 4)
            model_ver = "trained-xgboost-v1"
        else:
            # Untrained state: report features truthfully without fabricating predictions
            is_phishing = len(risk_factors) >= 2
            predicted_label = "suspicious_heuristic" if is_phishing else "unclassified"
            risk_score = round(min(1.0, len(risk_factors) * 0.25), 2)
            model_ver = "lexical-heuristic-baseline (untrained ML)"

        return {
            "url": url,
            "predicted_label": predicted_label,
            "risk_score": risk_score,
            "is_phishing": is_phishing,
            "features": features,
            "top_risk_factors": risk_factors,
            "is_trained": self.is_trained,
            "model_version": model_ver,
        }
