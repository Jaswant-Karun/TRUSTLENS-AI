"""
TRUSTLENS AI - Scam Tactic Multi-Label Detector (Engine 3)
Connects the trained multi-label inference pipeline to the FastAPI service.
"""

from typing import Dict, Any, Optional
from pathlib import Path

from ml.tactic_detection.infer import ScamTacticInferenceEngine


class ScamTacticDetector:
    """
    Multi-label tactic detection engine.
    Tags messages with specific social engineering techniques.
    """

    def __init__(self, model_path: Optional[str] = None):
        self.engine = ScamTacticInferenceEngine()
        self.is_trained = self.engine.is_loaded

    def detect(self, text: str) -> Dict[str, Any]:
        """
        Scans message for psychological and social engineering manipulation tactics.
        """
        res = self.engine.predict(text)
        return {
            "tactics": res["tactics"],
            "tactic_count": res["tactic_count"],
            "primary_vector": res["primary_vector"],
            "investment_advisory": res.get("investment_advisory"),
            "is_trained": self.is_trained,
            "model_version": res.get("model_version", "trustlens-model3-calibrated-linear-v1.0"),
            "processing_time_ms": res.get("processing_time_ms", 0.0),
        }
