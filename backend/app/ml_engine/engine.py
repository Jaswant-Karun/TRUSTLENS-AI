"""
TRUSTLENS AI - Production Machine Learning Engine
Wraps and interfaces with the four verified ML models and explainability engines:
- Model 1: Multilingual Scam Text Classifier (Calibrated LinearSVC)
- Model 2: Phishing URL Detector (XGBoost)
- Model 3: Multi-Label Scam Tactic Detector (One-vs-Rest LinearSVC)
- Model 4: Scam Campaign Discovery (HDBSCAN + MiniLM-L6-v2)
- Explainers: SHAP TreeExplainer, Linear Saliency, Tactic Evidence, Campaign Attributions

STRICT ANTI-FABRICATION RULE:
- If a model artifact is missing or an inference error occurs, return an explicit error or unavailable status.
- Never replace failed predictions with synthetic or fabricated output.
"""

import sys
import os
import re
import time
from pathlib import Path
from typing import Dict, Any, List, Optional

from backend.app.core.logging import logger

# Import actual trained ML components
try:
    from ml.text_detection.classifier import MultilingualScamClassifier
    from ml.url_detection.classifier import PhishingURLDetector
    from ml.tactic_detection.detector import ScamTacticDetector
    from ml.campaign_detection.clusterer import CampaignClusterer
    from ml.explainability.explainer import composite_explainer
except ImportError as e:
    logger.error(f"Error importing ML components from ml/: {e}")
    MultilingualScamClassifier = None
    PhishingURLDetector = None
    ScamTacticDetector = None
    CampaignClusterer = None
    composite_explainer = None


class ProductionMLEngine:
    """
    Unified ML Engine providing decoupled, resilient inference across all 4 TRUSTLENS AI tracks.
    """

    def __init__(self):
        logger.info("Initializing Production ML Engine...")
        self.text_classifier = None
        self.url_detector = None
        self.tactic_detector = None
        self.campaign_clusterer = None
        self.explainer = composite_explainer

        self._init_models()

    def _init_models(self):
        try:
            if MultilingualScamClassifier:
                self.text_classifier = MultilingualScamClassifier()
        except Exception as e:
            logger.warning(f"Model 1 (Text Scam) failed to initialize: {e}")

        try:
            if PhishingURLDetector:
                self.url_detector = PhishingURLDetector()
        except Exception as e:
            logger.warning(f"Model 2 (URL Phishing) failed to initialize: {e}")

        try:
            if ScamTacticDetector:
                self.tactic_detector = ScamTacticDetector()
        except Exception as e:
            logger.warning(f"Model 3 (Scam Tactics) failed to initialize: {e}")

        try:
            if CampaignClusterer:
                self.campaign_clusterer = CampaignClusterer()
        except Exception as e:
            logger.warning(f"Model 4 (Campaign Discovery) failed to initialize: {e}")

    def get_status(self) -> Dict[str, bool]:
        """Returns loaded/operational status for all 4 engines."""
        return {
            "model_1_text_scam": bool(self.text_classifier and self.text_classifier.is_trained),
            "model_2_phishing_url": bool(self.url_detector and self.url_detector.is_trained),
            "model_3_tactic_detector": bool(self.tactic_detector and self.tactic_detector.is_trained),
            "model_4_campaign_clusterer": bool(self.campaign_clusterer and self.campaign_clusterer.is_trained),
        }

    def predict_text(self, text: str, sender: Optional[str] = None, channel: str = "sms") -> Dict[str, Any]:
        """Calls Model 1 independently with error handling."""
        if not self.text_classifier or not self.text_classifier.is_trained:
            return {
                "status": "unavailable",
                "error": "Model 1 (Text Scam Detector) artifact is not loaded.",
                "is_threat": None,
                "confidence": 0.0,
            }
        try:
            return self.text_classifier.predict(text)
        except Exception as e:
            logger.error(f"Inference error in Model 1: {e}")
            return {"status": "error", "error": str(e), "is_threat": None, "confidence": 0.0}

    def predict_url(self, url: str) -> Dict[str, Any]:
        """Calls Model 2 independently with zero network requests."""
        if not self.url_detector or not self.url_detector.is_trained:
            return {
                "status": "unavailable",
                "error": "Model 2 (Phishing URL Detector) artifact is not loaded.",
                "is_phishing": None,
                "risk_score": 0.0,
            }
        try:
            return self.url_detector.analyze(url)
        except Exception as e:
            logger.error(f"Inference error in Model 2: {e}")
            return {"status": "error", "error": str(e), "is_phishing": None, "risk_score": 0.0}

    def predict_tactics(self, text: str) -> Dict[str, Any]:
        """Calls Model 3 independently."""
        if not self.tactic_detector or not self.tactic_detector.is_trained:
            return {
                "status": "unavailable",
                "error": "Model 3 (Scam Tactic Detector) artifact is not loaded.",
                "tactics": [],
                "tactic_count": 0,
            }
        try:
            return self.tactic_detector.detect(text)
        except Exception as e:
            logger.error(f"Inference error in Model 3: {e}")
            return {"status": "error", "error": str(e), "tactics": [], "tactic_count": 0}

    def match_campaign(self, text: str) -> Dict[str, Any]:
        """Calls Model 4 independently."""
        if not self.campaign_clusterer or not self.campaign_clusterer.is_trained:
            return {
                "status": "unavailable",
                "error": "Model 4 (Campaign Discovery Engine) artifact is not loaded.",
                "matched": False,
                "campaign_id": None,
            }
        try:
            return self.campaign_clusterer.match_campaign(text)
        except Exception as e:
            logger.error(f"Inference error in Model 4: {e}")
            return {"status": "error", "error": str(e), "matched": False, "campaign_id": None}

    def explain(self, content: str, scan_results: Dict[str, Any]) -> Dict[str, Any]:
        """Runs transparent explainability suite across SHAP, saliency, tactics, and campaigns."""
        if not self.explainer:
            return {"explainability": "Explainer suite currently uninitialized."}
        try:
            return self.explainer.explain_composite(content, scan_results)
        except Exception as e:
            logger.error(f"Explainability execution error: {e}")
            return {"explainability_error": str(e)}


ml_engine = ProductionMLEngine()
