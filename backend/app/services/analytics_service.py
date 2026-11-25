"""
TRUSTLENS AI - Database-Backed Analytics Service
Computes live SOC analytics strictly from persisted MongoDB records and verified
model evaluation artifacts. Never fabricates static counters or synthetic charts.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from collections import Counter

from backend.app.database.collections import (
    get_analyses_collection,
    get_urls_collection,
    get_reports_collection,
    get_indicators_collection,
    get_investigations_collection,
)
from backend.app.services.campaign_service import campaign_service
from backend.app.services.model_service import model_service


def _parse_iso_date(val: Any) -> Optional[str]:
    if not val:
        return None
    if isinstance(val, datetime):
        return val.strftime("%Y-%m-%d")
    s = str(val).strip()
    if len(s) >= 10 and s[4] == "-" and s[7] == "-":
        return s[:10]
    return None


class AnalyticsService:
    """Aggregates real operational and ML metrics from MongoDB."""

    async def get_overview(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        source: Optional[str] = None,
    ) -> Dict[str, Any]:
        analyses_coll = get_analyses_collection()
        urls_coll = get_urls_collection()
        reports_coll = get_reports_collection()
        indicators_coll = get_indicators_collection()
        investigations_coll = get_investigations_collection()

        # Build MongoDB query for analyses
        analysis_query: Dict[str, Any] = {}
        if source and source != "all" and source != "community_report":
            analysis_query["analysis_type"] = source

        raw_analyses = await analyses_coll.find(analysis_query, {"_id": 0}).to_list(length=5000)

        # Apply date range filtering in Python safely across string/datetime formats
        analyses = []
        for doc in raw_analyses:
            d_str = _parse_iso_date(doc.get("created_at"))
            if start_date and d_str and d_str < start_date:
                continue
            if end_date and d_str and d_str > end_date:
                continue
            analyses.append(doc)

        # If source == 'community_report', analyses list is empty by design
        if source == "community_report":
            analyses = []

        # 1. Analysis volume over time
        vol_counter: Counter = Counter()
        threat_vol_counter: Counter = Counter()
        for doc in analyses:
            d_str = _parse_iso_date(doc.get("created_at")) or "unknown"
            vol_counter[d_str] += 1
            tl = str(doc.get("threat_level", "")).lower()
            if tl in ("critical", "high", "medium", "moderate"):
                threat_vol_counter[d_str] += 1

        volume_over_time = [
            {
                "date": d,
                "total": vol_counter[d],
                "threats": threat_vol_counter.get(d, 0),
            }
            for d in sorted(vol_counter.keys())
            if d != "unknown"
        ]

        # 2. Model prediction distribution (threat_level)
        pred_counter: Counter = Counter()
        lang_counter: Counter = Counter()
        cat_counter: Counter = Counter()
        tactic_counter: Counter = Counter()

        for doc in analyses:
            tl = str(doc.get("threat_level") or "inconclusive").lower()
            pred_counter[tl] += 1

            tm = doc.get("text_model") or {}
            lang = tm.get("detected_language")
            if lang:
                lang_counter[str(lang)] += 1

            cat = tm.get("predicted_label") or doc.get("analysis_type")
            if cat:
                cat_counter[str(cat)] += 1

            tactics = (doc.get("tactic_model") or {}).get("detected_tactics") or []
            for t in tactics:
                t_name = t.get("tactic") if isinstance(t, dict) else str(t)
                if t_name:
                    tactic_counter[t_name] += 1

        # 3. URL classification distribution
        url_docs = await urls_coll.find({}, {"_id": 0}).to_list(length=2000)
        url_class_counter: Counter = Counter()
        for u in url_docs:
            d_str = _parse_iso_date(u.get("last_seen"))
            if start_date and d_str and d_str < start_date:
                continue
            if end_date and d_str and d_str > end_date:
                continue
            if u.get("is_phishing") is True:
                url_class_counter["phishing"] += 1
            elif u.get("is_phishing") is False:
                url_class_counter["benign"] += 1
            else:
                url_class_counter[str(u.get("status") or "unknown")] += 1

        # 4. Human-review outcomes & report tactics
        report_docs = await reports_coll.find({}, {"_id": 0}).to_list(length=2000)
        filtered_reports = []
        for r in report_docs:
            d_str = _parse_iso_date(r.get("created_at"))
            if start_date and d_str and d_str < start_date:
                continue
            if end_date and d_str and d_str > end_date:
                continue
            filtered_reports.append(r)

        review_counter: Counter = Counter()
        for r in filtered_reports:
            review_counter[str(r.get("status") or "pending")] += 1
            for t in r.get("assigned_tactics") or []:
                tactic_counter[str(t)] += 1

        # 5. Campaign similarity cluster sizes
        campaigns = await campaign_service.list_campaigns(limit=50)
        cluster_sizes = [
            {
                "cluster_id": c.get("campaign_id") if c.get("campaign_id") is not None else c.get("cluster_id"),
                "name": c.get("targeted_entity") or c.get("target_brand") or f"Cluster #{c.get('cluster_id')}",
                "size": c.get("cluster_size", 0),
                "cohesion_score": c.get("cohesion_score"),
                "status": c.get("status", "active"),
            }
            for c in campaigns[:15]
        ]

        # 6. Counts & Model Evaluation Metrics
        indicators_count = await indicators_coll.count_documents({})
        investigations_count = await investigations_coll.count_documents({})
        eval_metrics = model_service.get_models_metrics()

        limitations: List[str] = []
        if not analyses:
            limitations.append("No analysis records matched the selected date range and source filter.")
        if not lang_counter:
            limitations.append("No language detection records present in the filtered analysis subset.")
        if not tactic_counter:
            limitations.append("No social-engineering tactic detections recorded in the filtered subset.")

        return {
            "filters_applied": {
                "start_date": start_date,
                "end_date": end_date,
                "source": source or "all",
            },
            "summary": {
                "total_analyses": len(analyses),
                "total_suspicious_urls": sum(url_class_counter.values()),
                "total_community_reports": len(filtered_reports),
                "total_campaigns": len(campaigns),
                "total_threat_indicators": indicators_count,
                "total_investigations": investigations_count,
            },
            "analysis_volume_over_time": volume_over_time,
            "model_prediction_distribution": [
                {"label": k, "count": v} for k, v in pred_counter.most_common()
            ],
            "language_distribution": [
                {"language": k, "count": v} for k, v in lang_counter.most_common()
            ],
            "scam_category_distribution": [
                {"category": k, "count": v} for k, v in cat_counter.most_common()
            ],
            "url_classification_distribution": [
                {"classification": k, "count": v} for k, v in url_class_counter.most_common()
            ],
            "tactic_detection_distribution": [
                {"tactic": k, "count": v} for k, v in tactic_counter.most_common()
            ],
            "campaign_cluster_sizes": cluster_sizes,
            "human_review_outcomes": [
                {"outcome": k, "count": v} for k, v in review_counter.most_common()
            ],
            "model_evaluation_metrics": eval_metrics.get("models", {}),
            "limitations": limitations,
        }


analytics_service = AnalyticsService()
