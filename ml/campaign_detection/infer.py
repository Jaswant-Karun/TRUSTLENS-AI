"""
TRUSTLENS AI - Model 4: Campaign Discovery & Similarity Inference Pipeline
Enables instant campaign nearest-neighbor matching, shared indicator correlation,
and multi-message dynamic clustering.
"""

import sys
import os
import re
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import numpy as np
import joblib

from ml.campaign_detection.embeddings import CampaignEmbeddingEngine


class CampaignInferenceEngine:
    """Production campaign intelligence inference engine."""

    MATCH_THRESHOLD_HIGH = 0.70
    MATCH_THRESHOLD_MODERATE = 0.50

    def __init__(self, artifacts_dir: Optional[str] = None):
        self.artifacts_dir = Path(artifacts_dir or "ml/artifacts/campaign_detection")
        self.artifacts_path = self.artifacts_dir / "cluster_artifacts.joblib"
        self.embedder = CampaignEmbeddingEngine()

        self.centroids: Dict[int, np.ndarray] = {}
        self.exemplars: Dict[int, str] = {}
        self.dossiers: List[Dict[str, Any]] = []
        self.dossier_by_id: Dict[int, Dict[str, Any]] = {}
        self.is_loaded = False
        self._load_artifacts()

    def _load_artifacts(self) -> None:
        if self.artifacts_path.exists():
            try:
                data = joblib.load(self.artifacts_path)
                self.centroids = data.get("centroids", {})
                self.exemplars = data.get("exemplars", {})
                self.dossiers = data.get("dossiers", [])
                self.dossier_by_id = {d["cluster_id"]: d for d in self.dossiers}
                self.is_loaded = True
            except Exception as e:
                print(f"[WARN] Failed to load campaign cluster artifacts: {e}")
                self.is_loaded = False
        else:
            self.is_loaded = False

    def extract_message_iocs(self, text: str) -> Dict[str, List[str]]:
        """Extracts technical IOCs from input message."""
        clean_t = str(text)
        urls = re.findall(r"https?://[^\s<>\"']+|www\.[^\s<>\"']+", clean_t)
        domains = []
        for u in urls:
            try:
                parsed = urlparse(u if "://" in u else "http://" + u)
                d = parsed.netloc.lower().split(":")[0]
                if d:
                    domains.append(d)
            except Exception:
                pass
        upis = re.findall(r"[\w.-]+@(?:okaxis|okhdfcbank|okicici|oksbi|paytm|ybl|apl|upi)", clean_t, re.IGNORECASE)
        phones = re.findall(r"(?:\+91[-\s]?)?[6-9]\d{9}", clean_t)
        return {
            "urls": list(set(urls)),
            "domains": list(set(domains)),
            "upis": list(set(upis)),
            "phones": list(set(phones)),
        }

    def match_campaign(self, message: str) -> Dict[str, Any]:
        """
        Matches a single message against discovered threat campaign clusters
        using cosine similarity in 384D semantic embedding space.
        """
        start_time = time.perf_counter()
        clean_msg = str(message).strip()

        if not self.is_loaded or not clean_msg or not self.centroids:
            latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
            return {
                "message": message,
                "associated_campaign": None,
                "campaign_id": -1,
                "similarity_score": 0.0,
                "match_status": "unassociated_or_uninitialized",
                "shared_indicators": {},
                "processing_time_ms": latency_ms,
                "legal_disclaimer": "Similarity clustering denotes shared linguistic and infrastructure patterns; it does not constitute legal proof of identical organizational origin.",
            }

        # 1. Embed query message
        query_emb = self.embedder.encode([clean_msg], normalize=True)[0]
        iocs = self.extract_message_iocs(clean_msg)

        # 2. Compute similarity to all campaign centroids
        best_cid = -1
        best_sim = -1.0

        for c_id, centroid in self.centroids.items():
            sim = float(np.dot(query_emb, centroid))
            if sim > best_sim:
                best_sim = sim
                best_cid = c_id

        # 3. Classify match status based on calibrated thresholds
        if best_sim >= self.MATCH_THRESHOLD_HIGH:
            match_status = "associated_with_known_campaign"
        elif best_sim >= self.MATCH_THRESHOLD_MODERATE:
            match_status = "potential_variant_or_emerging_campaign"
        else:
            match_status = "unassociated_novel_incident"

        matched_dossier = self.dossier_by_id.get(best_cid) if match_status != "unassociated_novel_incident" else None

        # Cross-reference shared indicators
        shared_domain_matches = []
        if matched_dossier:
            known_domains = set(matched_dossier.get("shared_indicators", {}).get("sample_domains", []))
            shared_domain_matches = list(set(iocs["domains"]) & known_domains)

        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

        return {
            "message": message,
            "associated_campaign": matched_dossier["campaign_name"] if matched_dossier else None,
            "campaign_id": best_cid if matched_dossier else -1,
            "similarity_score": round(best_sim, 4),
            "match_status": match_status,
            "targeted_institution": matched_dossier["targeted_institution"] if matched_dossier else None,
            "exemplar_message": matched_dossier["exemplar_message"] if matched_dossier else None,
            "cluster_size": matched_dossier["sample_count"] if matched_dossier else 0,
            "shared_phrases": matched_dossier["shared_phrases"] if matched_dossier else [],
            "shared_domain_matches": shared_domain_matches,
            "extracted_iocs": iocs,
            "processing_time_ms": latency_ms,
            "legal_disclaimer": "Similarity clustering denotes shared linguistic and infrastructure patterns; it does not constitute legal proof of identical organizational origin.",
        }

    def cluster_batch(
        self, messages: List[str], min_cluster_size: int = 2
    ) -> Dict[str, Any]:
        """
        Dynamically clusters a list of arbitrary messages on the fly.
        """
        start_time = time.perf_counter()
        if not messages or len(messages) < 2:
            return {
                "total_messages": len(messages),
                "clusters_identified": 0,
                "clusters": [],
                "processing_time_ms": 0.0,
            }

        # Embed all messages
        embs = self.embedder.encode(messages, normalize=True)

        from sklearn.cluster import HDBSCAN
        min_size = max(2, min(min_cluster_size, len(messages) // 2))
        clusterer = HDBSCAN(min_cluster_size=min_size, min_samples=1, metric="euclidean")
        labels = clusterer.fit_predict(embs)

        clusters_out = []
        unique_labels = sorted(list(set(labels)))

        for c_id in unique_labels:
            if c_id == -1:
                continue
            indices = np.where(labels == c_id)[0]
            c_msgs = [messages[i] for i in indices]
            c_embs = embs[indices]
            centroid = c_embs.mean(axis=0)
            centroid = centroid / np.linalg.norm(centroid)
            sims = np.dot(c_embs, centroid)
            exemplar = c_msgs[int(np.argmax(sims))]

            clusters_out.append({
                "cluster_id": int(c_id),
                "cluster_name": f"Dynamic Incident Group #{c_id + 1:02d}",
                "sample_size": len(indices),
                "exemplar_text": exemplar[:120] + ("..." if len(exemplar) > 120 else ""),
                "cohesion_score": round(float(np.mean(sims)), 4),
            })

        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

        return {
            "total_messages": len(messages),
            "clusters_identified": len(clusters_out),
            "unclustered_outliers": int(np.sum(labels == -1)),
            "clusters": clusters_out,
            "processing_time_ms": latency_ms,
            "legal_disclaimer": "Similarity clustering denotes shared linguistic and infrastructure patterns; it does not constitute legal proof of identical organizational origin.",
        }


campaign_engine = CampaignInferenceEngine()


if __name__ == "__main__":
    test_queries = [
        "Dear Customer, your electricity power will be cut tonight at 9.30 PM due to unpaid electricity bill. Contact electricity officer immediately.",
        "Your SBI Bank account is suspended today due to pending KYC verification. Please click here to verify.",
        "Congratulations you have won Rs 25,00,000 in Kaun Banega Crorepati lucky draw.",
        "Earn 2000-5000 daily by working from home. Simple YouTube video rating job on Telegram.",
        "Hey, did you finish writing the project report for tomorrow?",
    ]
    for q in test_queries:
        print("\n" + "=" * 60)
        print("Query Message:", q)
        res = campaign_engine.match_campaign(q)
        print(f"Match Status: {res['match_status']} (Sim: {res['similarity_score']:.2%})")
        if res["associated_campaign"]:
            print(f"  -> Campaign: {res['associated_campaign']} (Cluster Size: {res['cluster_size']})")
            print(f"  -> Institution: {res['targeted_institution']}")
            print(f"  -> Key Phrases: {res['shared_phrases']}")
