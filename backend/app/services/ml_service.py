"""
TRUSTLENS AI - Machine Learning Orchestration Service
Unifies all four ML engines and provides composite scan capabilities for the API.
"""

import uuid
import re
from typing import Dict, Any, Optional

from ml.text_detection.classifier import MultilingualScamClassifier
from ml.url_detection.classifier import PhishingURLDetector
from ml.tactic_detection.detector import ScamTacticDetector
from ml.campaign_detection.clusterer import CampaignClusterer
from backend.app.core.logging import logger


class MLOrchestrationService:
    def __init__(self):
        logger.info("Initializing ML Orchestration Service engines...")
        self.text_classifier = MultilingualScamClassifier()
        self.url_detector = PhishingURLDetector()
        self.tactic_detector = ScamTacticDetector()
        self.campaign_clusterer = CampaignClusterer()

    def get_models_status(self) -> Dict[str, bool]:
        """Returns loaded/trained status for each engine."""
        return {
            "multilingual_text_model": self.text_classifier.is_trained,
            "phishing_url_model": self.url_detector.is_trained,
            "tactic_detector_model": self.tactic_detector.is_trained,
            "campaign_clusterer_model": self.campaign_clusterer.is_trained,
        }

    def scan_text(self, text: str, sender: Optional[str] = None, channel: str = "sms") -> Dict[str, Any]:
        """Runs Engine 1 (Text Scam Classification)."""
        return self.text_classifier.predict(text)

    def scan_url(self, url: str) -> Dict[str, Any]:
        """Runs Engine 2 (Phishing URL Detection)."""
        return self.url_detector.analyze(url)

    def scan_tactics(self, text: str) -> Dict[str, Any]:
        """Runs Engine 3 (Scam Tactic Detection)."""
        return self.tactic_detector.detect(text)

    def cluster_campaigns(self, messages: list, similarity_threshold: float = 0.6) -> Dict[str, Any]:
        """Runs Engine 4 (Campaign Intelligence Discovery)."""
        return self.campaign_clusterer.cluster_messages(messages, similarity_threshold)

    def composite_scan(self, content: str, channel: str = "auto", sender: Optional[str] = None) -> Dict[str, Any]:
        """
        Unified multi-modal scan: Automatically dispatches text, URLs, tactics, and IOCs.
        """
        scan_id = str(uuid.uuid4())
        is_url_target = bool(re.match(r"^(https?://|www\.)", content.strip(), re.IGNORECASE))

        url_res = None
        text_res = None
        tactics_res = None

        if is_url_target:
            detected_type = "url"
            url_res = self.scan_url(content.strip())
            risk_score = url_res["risk_score"]
            campaign_res = None
        else:
            detected_type = "text"
            text_res = self.scan_text(content, sender=sender, channel=channel)
            tactics_res = self.scan_tactics(content)
            campaign_res = self.campaign_clusterer.match_campaign(content)
            
            # Check for embedded URLs in message text
            embedded_urls = re.findall(r"https?://[^\s<>\"']+|www\.[^\s<>\"']+", content)
            if embedded_urls:
                url_res = self.scan_url(embedded_urls[0])
            
            text_risk = text_res["confidence"] if text_res["is_threat"] else 0.1
            if url_res and url_res.get("is_phishing"):
                risk_score = max(text_risk, url_res["risk_score"])
            else:
                risk_score = text_risk

        # Determine calibrated threat category
        if risk_score >= 0.85:
            threat_level = "critical"
        elif risk_score >= 0.65:
            threat_level = "high"
        elif risk_score >= 0.40:
            threat_level = "medium"
        elif risk_score >= 0.20:
            threat_level = "low"
        else:
            threat_level = "clean"

        return {
            "scan_id": scan_id,
            "detected_type": detected_type,
            "overall_threat_level": threat_level,
            "confidence": round(risk_score, 4),
            "text_analysis": text_res,
            "url_analysis": url_res,
            "tactics_analysis": tactics_res,
            "campaign_association": campaign_res,
        }


ml_service = MLOrchestrationService()

