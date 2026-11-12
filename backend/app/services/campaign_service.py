"""
TRUSTLENS AI - Campaign Intelligence Service
Serves discovered scam campaign dossiers, similarity lookups, and shared indicators.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import json
from pathlib import Path

from backend.app.database.collections import get_campaigns_collection
from backend.app.ml_engine.engine import ml_engine


class CampaignIntelligenceService:
    """Manages scam campaign records and cluster dossiers."""

    def __init__(self):
        self.dossiers_path = Path("ml/artifacts/campaign_detection/campaign_dossiers.json")
        self._cached_dossiers: List[Dict[str, Any]] = []
        self._load_cached_dossiers()

    def _load_cached_dossiers(self):
        if self.dossiers_path.exists():
            try:
                with open(self.dossiers_path, "r", encoding="utf-8") as f:
                    self._cached_dossiers = json.load(f)
            except Exception:
                self._cached_dossiers = []

    async def list_campaigns(
        self,
        status: Optional[str] = None,
        target: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Lists active scam campaigns from MongoDB or cached dossiers."""
        campaigns_coll = get_campaigns_collection()
        query: Dict[str, Any] = {}
        if status:
            query["status"] = status
        if target:
            query["targeted_entity"] = {"$regex": target, "$options": "i"}

        cursor = campaigns_coll.find(query).sort("cluster_size", -1).limit(limit)
        items = await cursor.to_list(length=limit)

        if items:
            for item in items:
                item.pop("_id", None)
            return items

        # Fallback to local high-density dossiers if MongoDB collection is fresh
        dossiers = self._cached_dossiers
        if target:
            target_lower = target.lower()
            dossiers = [
                d for d in dossiers
                if target_lower in (d.get("targeted_institution") or d.get("targeted_entity") or "").lower()
            ]
        
        results = []
        for d in dossiers[:limit]:
            categories = d.get("predominant_categories")
            tactics = list(categories.keys()) if isinstance(categories, dict) else d.get("primary_tactics", [])
            results.append({
                "cluster_id": d.get("cluster_id") or 0,
                "campaign_name": d.get("campaign_name") or d.get("name") or f"Campaign #{d.get('cluster_id')}",
                "targeted_entity": d.get("targeted_institution") or d.get("targeted_entity") or "Generic / Unspecified Institution",
                "cluster_size": d.get("sample_count") or d.get("size") or 1,
                "cohesion_score": float(d.get("cluster_cohesion_score") or d.get("cohesion_score") or 0.8),
                "primary_tactics": tactics,
                "status": "active",
                "last_activity": datetime.now(timezone.utc),
            })
        return results

    async def get_campaign_by_id(self, campaign_id: int) -> Optional[Dict[str, Any]]:
        """Retrieves complete dossier for a campaign by ID."""
        campaigns_coll = get_campaigns_collection()
        doc = await campaigns_coll.find_one({"campaign_id": str(campaign_id)})
        if doc:
            doc.pop("_id", None)
            return doc

        # Look in cached dossiers
        for d in self._cached_dossiers:
            if d.get("cluster_id") == campaign_id:
                categories = d.get("predominant_categories")
                tactics = list(categories.keys()) if isinstance(categories, dict) else d.get("primary_tactics", [])
                indicators = d.get("shared_indicators") or d.get("shared_iocs") or {}
                return {
                    "cluster_id": d.get("cluster_id"),
                    "campaign_name": d.get("campaign_name") or d.get("name") or f"Campaign #{d.get('cluster_id')}",
                    "targeted_entity": d.get("targeted_institution") or d.get("targeted_entity") or "Generic / Unspecified Institution",
                    "cluster_size": d.get("sample_count") or d.get("size") or 1,
                    "cohesion_score": float(d.get("cluster_cohesion_score") or d.get("cohesion_score") or 0.8),
                    "primary_tactics": tactics,
                    "exemplar_message": d.get("exemplar_message", ""),
                    "shared_phrases": d.get("shared_phrases", []),
                    "shared_iocs": indicators,
                    "legal_disclaimer": (
                        d.get("soc_legal_disclaimer") or
                        "Legal Disclaimer: Campaign similarity clusters indicate mathematical and linguistic overlap; "
                        "they do not establish forensically confirmed identity of criminal actors or syndicates."
                    ),
                    "discovered_at": datetime.now(timezone.utc),
                }
        return None


campaign_service = CampaignIntelligenceService()

