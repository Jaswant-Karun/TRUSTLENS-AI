"""
TRUSTLENS AI - Production ML Monitoring & Human-Reviewed Feedback Service
Computes real-time monitoring metrics from MongoDB analyses, ml_feedback, and models_registry_v2.json:
- Prediction distribution, latency percentiles, error rates
- Input language distribution drift vs v2.0.5 training baseline
- Language-specific metrics strictly from human-verified ground-truth feedback
- Separate pending user feedback from verified ground-truth labels
- Model version history & rollback tracking
"""

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional

from backend.app.database.collections import get_analyses_collection
from backend.app.database.manager import db_manager

COLL_ML_FEEDBACK = "ml_feedback"

# v2.0.5 Training corpus language baseline (text_train.parquet: 62604 EN, 5042 HI, 1070 HG)
TRAINING_LANG_BASELINE = {
    "English": 0.9111,
    "Hindi": 0.0734,
    "Hinglish": 0.0156,
}


class MLMonitoringService:
    """Computes live production ML monitoring and manages human-reviewed feedback."""

    def get_feedback_collection(self):
        return db_manager.get_collection(COLL_ML_FEEDBACK)

    async def get_monitoring_snapshot(self, limit: int = 1000) -> Dict[str, Any]:
        analyses_coll = get_analyses_collection()
        feedback_coll = self.get_feedback_collection()

        cursor = analyses_coll.find({}, {"_id": 0}).sort("created_at", -1).limit(limit)
        records = await cursor.to_list(length=limit)

        pred_dist: Dict[str, int] = {}
        input_type_dist: Dict[str, int] = {}
        lang_counts: Dict[str, int] = {}
        latencies: List[float] = []
        error_count = 0

        for r in records:
            tl = str(r.get("threat_level") or r.get("risk_assessment", {}).get("threat_level") or "unknown").lower()
            pred_dist[tl] = pred_dist.get(tl, 0) + 1

            itype = str(r.get("input_type") or r.get("channel") or "unknown").lower()
            input_type_dist[itype] = input_type_dist.get(itype, 0) + 1

            tm = r.get("text_model") or {}
            lang = tm.get("detected_language") or r.get("detected_language")
            if lang:
                lang_counts[str(lang)] = lang_counts.get(str(lang), 0) + 1

            lat = r.get("processing_time_ms")
            if isinstance(lat, (int, float)) and lat >= 0:
                latencies.append(float(lat))

            if tl in ("error", "unavailable") or tm.get("status") in ("error", "unavailable"):
                error_count += 1

        total = len(records)
        latencies_sorted = sorted(latencies)
        n_lat = len(latencies_sorted)
        latency_stats = {
            "sample_count": n_lat,
            "avg_ms": round(sum(latencies_sorted) / n_lat, 2) if n_lat else None,
            "p50_ms": round(latencies_sorted[n_lat // 2], 2) if n_lat else None,
            "p95_ms": round(latencies_sorted[min(n_lat - 1, int(n_lat * 0.95))], 2) if n_lat else None,
            "max_ms": round(latencies_sorted[-1], 2) if n_lat else None,
        }

        # Input language distribution drift (Total Variation Distance)
        total_lang = sum(lang_counts.values())
        live_lang_dist = {k: round(v / total_lang, 4) for k, v in lang_counts.items()} if total_lang else {}
        tvd = None
        if total_lang > 0:
            all_langs = set(TRAINING_LANG_BASELINE.keys()) | set(live_lang_dist.keys())
            tvd = round(0.5 * sum(abs(live_lang_dist.get(l, 0.0) - TRAINING_LANG_BASELINE.get(l, 0.0)) for l in all_langs), 4)

        # Feedback stats (strictly separating pending user reports from verified ground truth)
        fb_records = await feedback_coll.find({}, {"_id": 0}).sort("submitted_at_utc", -1).limit(limit).to_list(length=limit)
        fp_pending = sum(1 for f in fb_records if f.get("feedback_type") == "false_positive" and f.get("review_status") == "pending_review")
        fn_pending = sum(1 for f in fb_records if f.get("feedback_type") == "false_negative" and f.get("review_status") == "pending_review")
        fp_verified = sum(1 for f in fb_records if f.get("feedback_type") == "false_positive" and f.get("review_status") == "verified_ground_truth")
        fn_verified = sum(1 for f in fb_records if f.get("feedback_type") == "false_negative" and f.get("review_status") == "verified_ground_truth")
        rejected_count = sum(1 for f in fb_records if f.get("review_status") == "rejected")

        # Language-specific metrics computed ONLY from human-verified ground-truth records
        verified_by_lang: Dict[str, Dict[str, Any]] = {}
        for f in fb_records:
            if f.get("review_status") != "verified_ground_truth" or not f.get("is_verified_ground_truth"):
                continue
            lang = f.get("detected_language") or "Unknown"
            bucket = verified_by_lang.setdefault(lang, {"verified_samples": 0, "verified_fp": 0, "verified_fn": 0})
            bucket["verified_samples"] += 1
            if f.get("feedback_type") == "false_positive":
                bucket["verified_fp"] += 1
            elif f.get("feedback_type") == "false_negative":
                bucket["verified_fn"] += 1

        # Model version & promotion history from registry
        reg_path = Path("ml/registry/models_registry_v2.json")
        active_versions: Dict[str, str] = {}
        promotion_history: List[Dict[str, Any]] = []
        if reg_path.exists():
            reg = json.loads(reg_path.read_text(encoding="utf-8"))
            for mid, m in reg.get("models", {}).items():
                if m.get("deployment_status") == "Production":
                    active_versions[m.get("task", mid)] = f"{mid} (v{m.get('version')})"
            promotion_history = reg.get("promotion_history", [])[-10:]

        return {
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "total_analyses_monitored": total,
            "prediction_distribution": pred_dist,
            "input_type_distribution": input_type_dist,
            "latency_ms": latency_stats,
            "error_rate": round(error_count / total, 4) if total else 0.0,
            "error_count": error_count,
            "input_drift": {
                "training_language_baseline": TRAINING_LANG_BASELINE,
                "live_language_distribution": live_lang_dist,
                "language_counts": lang_counts,
                "total_variation_distance": tvd,
                "drift_alert": bool(tvd is not None and tvd >= 0.25),
            },
            "feedback_summary": {
                "total_submitted": len(fb_records),
                "pending_review": {"false_positive": fp_pending, "false_negative": fn_pending},
                "verified_ground_truth": {"false_positive": fp_verified, "false_negative": fn_verified},
                "rejected": rejected_count,
                "auto_training_from_user_reports": False,
            },
            "verified_language_performance": verified_by_lang,
            "active_production_versions": active_versions,
            "model_version_history": promotion_history,
        }

    async def submit_feedback(
        self,
        analysis_id: str,
        feedback_type: str,
        suggested_label: str,
        submitted_by: str,
        comment: Optional[str] = None,
        detected_language: Optional[str] = None,
        model_version: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Stores user feedback strictly as pending_review (never as verified ground truth)."""
        if feedback_type not in ("false_positive", "false_negative"):
            raise ValueError("feedback_type must be 'false_positive' or 'false_negative'")

        doc = {
            "feedback_id": f"fb-{uuid.uuid4().hex[:12]}",
            "analysis_id": analysis_id,
            "feedback_type": feedback_type,
            "suggested_label": suggested_label,
            "comment": comment or "",
            "detected_language": detected_language,
            "model_version": model_version,
            "submitted_by": submitted_by,
            "submitted_at_utc": datetime.now(timezone.utc).isoformat(),
            "review_status": "pending_review",
            "is_verified_ground_truth": False,
            "verified_label": None,
            "reviewed_by": None,
            "reviewed_at_utc": None,
            "reviewer_notes": None,
        }
        coll = self.get_feedback_collection()
        await coll.insert_one(dict(doc))
        return doc

    async def list_feedback(self, review_status: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        coll = self.get_feedback_collection()
        query = {"review_status": review_status} if review_status else {}
        return await coll.find(query, {"_id": 0}).sort("submitted_at_utc", -1).limit(limit).to_list(length=limit)

    async def review_feedback(
        self,
        feedback_id: str,
        decision: str,
        reviewed_by: str,
        verified_label: Optional[str] = None,
        reviewer_notes: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Human-review gate: promotes a pending user report to verified_ground_truth or rejects it."""
        if decision not in ("verified_ground_truth", "rejected"):
            raise ValueError("decision must be 'verified_ground_truth' or 'rejected'")
        if decision == "verified_ground_truth" and not verified_label:
            raise ValueError("verified_label is required when approving feedback as verified_ground_truth")

        coll = self.get_feedback_collection()
        existing = await coll.find_one({"feedback_id": feedback_id}, {"_id": 0})
        if not existing:
            return None

        updates = {
            "review_status": decision,
            "is_verified_ground_truth": decision == "verified_ground_truth",
            "verified_label": verified_label if decision == "verified_ground_truth" else None,
            "reviewed_by": reviewed_by,
            "reviewed_at_utc": datetime.now(timezone.utc).isoformat(),
            "reviewer_notes": reviewer_notes or "",
        }
        await coll.update_one({"feedback_id": feedback_id}, {"$set": updates})
        existing.update(updates)
        return existing


monitoring_service = MLMonitoringService()
