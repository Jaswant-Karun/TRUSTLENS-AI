"""
TRUSTLENS AI - Campaign Intelligence Service
Serves discovered scam campaign dossiers, similarity lookups, and shared indicators.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import hashlib
import json
import uuid
from pathlib import Path

from backend.app.core.logging import logger
from backend.app.database.collections import get_campaigns_collection, get_audit_collection
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

    async def sync_campaigns_from_dossiers(
        self,
        dry_run: bool = False,
        actor_id: str = "system",
    ) -> Dict[str, Any]:
        """
        Idempotently synchronizes ml/artifacts/campaign_detection/campaign_dossiers.json
        into MongoDB scam_campaigns without overwriting human-verified DB records.
        """
        if not self.dossiers_path.exists():
            raise FileNotFoundError(f"Campaign dossiers file not found: {self.dossiers_path}")

        raw_bytes = self.dossiers_path.read_bytes()
        source_sha256 = hashlib.sha256(raw_bytes).hexdigest()
        raw_items = json.loads(raw_bytes.decode("utf-8"))
        if not isinstance(raw_items, list):
            raise ValueError("campaign_dossiers.json must contain a JSON array.")

        campaigns_coll = get_campaigns_collection()
        audit_coll = get_audit_collection()
        now = datetime.now(timezone.utc)

        inserted = 0
        updated = 0
        skipped = 0
        failed = 0
        errors: List[Dict[str, Any]] = []

        for idx, d in enumerate(raw_items):
            try:
                if not isinstance(d, dict) or d.get("cluster_id") is None:
                    raise ValueError("Missing required integer 'cluster_id'.")
                cid_int = int(d["cluster_id"])
                cid_str = str(cid_int)
                campaign_name = str(d.get("campaign_name") or "").strip()
                if not campaign_name:
                    raise ValueError(f"Cluster {cid_int} missing 'campaign_name'.")

                cohesion = float(d["cluster_cohesion_score"])
                if not (0.0 <= cohesion <= 1.0):
                    raise ValueError(f"Cluster {cid_int} cohesion out of range: {cohesion}")

                categories = d.get("predominant_categories")
                primary_tactics = list(categories.keys()) if isinstance(categories, dict) else []
                shared_iocs = d.get("shared_indicators") if isinstance(d.get("shared_indicators"), dict) else {}

                mapped = {
                    "campaign_id": cid_str,
                    "cluster_id": cid_int,
                    "campaign_name": campaign_name,
                    "targeted_entity": str(d.get("targeted_institution") or "Generic / Unspecified Institution"),
                    "cluster_size": int(d.get("sample_count") or 1),
                    "percentage_of_threats": float(d["percentage_of_threats"]) if d.get("percentage_of_threats") is not None else None,
                    "cohesion_score": cohesion,
                    "primary_tactics": primary_tactics,
                    "predominant_categories": categories if isinstance(categories, dict) else {},
                    "exemplar_message": str(d.get("exemplar_message") or ""),
                    "shared_phrases": list(d.get("shared_phrases") or []),
                    "shared_iocs": shared_iocs,
                    "legal_disclaimer": str(
                        d.get("soc_legal_disclaimer")
                        or "Similarity clustering denotes shared linguistic and infrastructure patterns; it does not constitute legal proof of identical organizational origin."
                    ),
                    "source_provenance": str(self.dossiers_path).replace("\\", "/"),
                    "source_sha256": source_sha256,
                }
                content_hash = hashlib.sha256(
                    json.dumps(mapped, sort_keys=True).encode("utf-8")
                ).hexdigest()
                mapped["content_hash"] = content_hash

                existing = await campaigns_coll.find_one({"campaign_id": cid_str})
                if existing:
                    if existing.get("verification_status") == "verified":
                        skipped += 1
                        continue
                    if existing.get("content_hash") == content_hash:
                        skipped += 1
                        continue
                    updated += 1
                    if not dry_run:
                        await campaigns_coll.update_one(
                            {"campaign_id": cid_str},
                            {"$set": {**mapped, "updated_at": now, "last_activity": now}},
                        )
                else:
                    inserted += 1
                    if not dry_run:
                        await campaigns_coll.insert_one({
                            **mapped,
                            "status": "active",
                            "verification_status": "automated_clustering",
                            "discovered_at": now,
                            "last_activity": now,
                            "created_at": now,
                            "updated_at": now,
                        })
            except Exception as exc:
                failed += 1
                errors.append({"index": idx, "error": str(exc)})

        summary = {
            "dry_run": dry_run,
            "source_file": str(self.dossiers_path).replace("\\", "/"),
            "source_sha256": source_sha256,
            "total_source_records": len(raw_items),
            "inserted": inserted,
            "updated": updated,
            "skipped": skipped,
            "failed": failed,
            "errors": errors,
            "executed_at": now.isoformat(),
        }

        if not dry_run:
            await audit_coll.insert_one({
                "audit_id": f"aud-{uuid.uuid4().hex[:10]}",
                "user_id": actor_id,
                "action": "campaigns_synchronized",
                "resource_type": "scam_campaigns",
                "resource_id": "bulk_sync",
                "details": {
                    "inserted": inserted,
                    "updated": updated,
                    "skipped": skipped,
                    "failed": failed,
                    "source_sha256": source_sha256,
                },
                "timestamp": now,
            })
            logger.info(f"Campaign sync completed: inserted={inserted}, updated={updated}, skipped={skipped}, failed={failed}")

        return summary


campaign_service = CampaignIntelligenceService()

