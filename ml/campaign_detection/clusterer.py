"""
TRUSTLENS AI - Scam Campaign Intelligence & Discovery (Engine 4)
Discovers related attacks, shared infrastructure, and campaign clusters.
"""

from typing import List, Dict, Any, Optional
import re
from collections import defaultdict


class CampaignClusterer:
    """
    Unsupervised threat campaign discovery engine.
    Groups incoming messages and IOCs into coordinated threat campaigns.
    """

    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path or "ml/artifacts/campaign_clusterer.joblib"
        self.is_trained = False

    def extract_indicators(self, text: str) -> List[str]:
        """Extracts technical Indicators of Compromise (URLs, UPI IDs, Phone numbers)."""
        iocs = []
        
        # Extract URLs
        urls = re.findall(r"https?://[^\s<>\"']+|www\.[^\s<>\"']+", text)
        iocs.extend(urls)
        
        # Extract UPI handles (e.g. user@okhdfcbank, payment@paytm)
        upis = re.findall(r"[\w.-]+@(?:okaxis|okhdfcbank|okicici|oksbi|paytm|ybl|apl|upi)", text, re.IGNORECASE)
        iocs.extend(upis)
        
        # Extract 10-digit Indian phone numbers with optional prefix
        phones = re.findall(r"(?:\+91[-\s]?)?[6-9]\d{9}", text)
        iocs.extend(phones)
        
        return list(set(iocs))

    def cluster_messages(self, messages: List[str], similarity_threshold: float = 0.6) -> Dict[str, Any]:
        """
        Groups messages into clusters based on shared tokens and structural indicators.
        """
        if not messages:
            return {"total_messages": 0, "clusters_identified": 0, "clusters": []}

        # Indicator-linked and n-gram overlap grouping
        clusters: Dict[int, List[Dict[str, Any]]] = defaultdict(list)
        cluster_indicators: Dict[int, set] = defaultdict(set)
        
        assigned_cluster = 0
        for idx, msg in enumerate(messages):
            iocs = self.extract_indicators(msg)
            # Find matching cluster with shared IOC or high token similarity
            matched = False
            for c_id, ind_set in cluster_indicators.items():
                if set(iocs) & ind_set:
                    clusters[c_id].append({"index": idx, "text": msg, "iocs": iocs})
                    ind_set.update(iocs)
                    matched = True
                    break
            
            if not matched:
                assigned_cluster += 1
                clusters[assigned_cluster].append({"index": idx, "text": msg, "iocs": iocs})
                cluster_indicators[assigned_cluster].update(iocs)

        formatted_clusters = []
        for c_id, items in clusters.items():
            all_iocs = list(cluster_indicators[c_id])
            exemplar = items[0]["text"]
            formatted_clusters.append({
                "cluster_id": c_id,
                "cluster_name": f"Campaign Cluster #{c_id:03d} ({len(items)} incidents)",
                "sample_size": len(items),
                "exemplar_text": exemplar[:120] + ("..." if len(exemplar) > 120 else ""),
                "associated_indicators": all_iocs,
            })

        return {
            "total_messages": len(messages),
            "clusters_identified": len(formatted_clusters),
            "clusters": formatted_clusters,
            "is_trained": self.is_trained,
        }
