"""
TRUSTLENS AI - Scam Campaign Intelligence & Discovery (Engine 4)
Wraps CampaignInferenceEngine for backend service integration.
"""

from typing import List, Dict, Any, Optional
from ml.campaign_detection.infer import CampaignInferenceEngine


class CampaignClusterer:
    """
    Unsupervised threat campaign discovery engine.
    Groups incoming messages and IOCs into coordinated threat campaigns.
    """

    def __init__(self, model_path: Optional[str] = None):
        self.engine = CampaignInferenceEngine()
        self.is_trained = self.engine.is_loaded

    def extract_indicators(self, text: str) -> List[str]:
        """Extracts technical Indicators of Compromise (URLs, UPI IDs, Phone numbers)."""
        iocs = self.engine.extract_message_iocs(text)
        combined = []
        for v in iocs.values():
            combined.extend(v)
        return list(set(combined))

    def match_campaign(self, message: str) -> Dict[str, Any]:
        """Matches a single message to known campaign clusters."""
        return self.engine.match_campaign(message)

    def cluster_messages(self, messages: List[str], similarity_threshold: float = 0.6) -> Dict[str, Any]:
        """
        Groups messages into clusters based on semantic similarity and shared indicators.
        """
        res = self.engine.cluster_batch(messages)
        formatted_clusters = []
        for c in res.get("clusters", []):
            iocs = self.extract_indicators(c.get("exemplar_text", ""))
            formatted_clusters.append({
                "cluster_id": c["cluster_id"],
                "cluster_name": c["cluster_name"],
                "sample_size": c["sample_size"],
                "exemplar_text": c["exemplar_text"],
                "associated_indicators": iocs,
                "cohesion_score": c.get("cohesion_score", 0.0),
            })

        return {
            "total_messages": res.get("total_messages", len(messages)),
            "clusters_identified": len(formatted_clusters),
            "clusters": formatted_clusters,
            "processing_time_ms": res.get("processing_time_ms", 0.0),
            "legal_disclaimer": "Similarity clustering denotes shared linguistic and infrastructure patterns; it does not constitute legal proof of identical organizational origin.",
        }
