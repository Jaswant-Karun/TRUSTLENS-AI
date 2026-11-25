"""
TRUSTLENS AI - Threat Library Service
Aggregates, filters, sorts, and paginates actual stored threat intelligence across
suspicious messages, URLs, domains, indicators, tactics, similarity clusters, and community reports.
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone
import hashlib

from backend.app.database.collections import (
    get_analyses_collection,
    get_urls_collection,
    get_indicators_collection,
    get_reports_collection,
)
from backend.app.services.campaign_service import campaign_service


SEVERITY_ORDER = {
    "critical": 5,
    "high": 4,
    "medium": 3,
    "moderate": 3,
    "low": 2,
    "inconclusive": 1,
    "clean": 0,
}

TACTIC_CATALOG: Dict[str, str] = {
    "urgency_and_time_pressure": "Artificial urgency or countdown pressure forcing immediate action.",
    "threats_and_intimidation": "Legal, police, tax, or penalty threats used to coerce compliance.",
    "otp_and_credential_requests": "Direct solicitation of OTPs, PINs, passwords, or CVV codes.",
    "financial_manipulation": "Deceptive payment, fee, or wire-transfer solicitation.",
    "bank_impersonation": "Spoofing of banking institutions, RBI, or KYC departments.",
    "government_impersonation": "Impersonation of tax, customs, police, or government agencies.",
    "fake_employment_opportunities": "Fraudulent work-from-home, part-time, or task-based job offers.",
    "fake_investment_schemes": "Unrealistic crypto, stock, or trading return promises.",
    "account_suspension_threats": "Warnings that bank, SIM, or utility accounts will be blocked.",
    "prize_and_reward_scams": "Unsolicited lottery, cashback, or prize claim lures.",
    "refund_and_payment_manipulation": "Fake refund links or collect-request QR/UPI traps.",
}


def _short_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8", errors="ignore")).hexdigest()[:12]


def _normalize_severity(raw: Optional[str], risk_score: Optional[float] = None) -> str:
    if raw:
        val = str(raw).lower().strip()
        if val == "moderate":
            return "medium"
        if val in SEVERITY_ORDER:
            return val
    if isinstance(risk_score, (int, float)):
        if risk_score >= 0.85:
            return "critical"
        if risk_score >= 0.65:
            return "high"
        if risk_score >= 0.40:
            return "medium"
        if risk_score > 0.0:
            return "low"
    return "inconclusive"


class ThreatLibraryService:
    """Unified searchable repository over persisted TRUSTLENS AI threat records."""

    async def _collect_items(self) -> List[Dict[str, Any]]:
        items: List[Dict[str, Any]] = []
        seen_domains: Dict[str, Dict[str, Any]] = {}
        tactic_counts: Dict[str, int] = {}
        tactic_sources: Dict[str, List[str]] = {}

        # 1. Analyses -> Suspicious Messages, URLs, and Tactic telemetry
        analyses_coll = get_analyses_collection()
        analyses_docs = await analyses_coll.find({}, {"_id": 0}).sort("created_at", -1).limit(500).to_list(length=500)

        for doc in analyses_docs:
            analysis_id = doc.get("analysis_id", "")
            analysis_type = doc.get("analysis_type", "text")
            created_at = doc.get("created_at", "")
            if isinstance(created_at, datetime):
                created_at = created_at.isoformat()
            payload = doc.get("input_payload") or {}
            threat_level = _normalize_severity(doc.get("threat_level"), doc.get("risk_score"))
            confidence = doc.get("confidence")

            # Track tactics from analysis
            tactics_list = (doc.get("tactic_model") or {}).get("detected_tactics") or []
            for t in tactics_list:
                t_name = t.get("tactic") if isinstance(t, dict) else str(t)
                if t_name:
                    tactic_counts[t_name] = tactic_counts.get(t_name, 0) + 1
                    tactic_sources.setdefault(t_name, []).append(analysis_id)

            # Suspicious message record
            text_val = payload.get("text") or (doc.get("text_model") or {}).get("text")
            if text_val and analysis_type in ("text", "comprehensive", "image", "sms"):
                tm = doc.get("text_model") or {}
                items.append({
                    "item_id": f"msg:{analysis_id}",
                    "raw_id": analysis_id,
                    "entity_type": "suspicious_message",
                    "label": text_val[:80] + ("..." if len(text_val) > 80 else ""),
                    "summary": f"Label: {tm.get('predicted_label', 'unknown')} | Lang: {tm.get('detected_language', 'unknown')}",
                    "severity": threat_level,
                    "confidence": float(confidence) if isinstance(confidence, (int, float)) else None,
                    "provenance": "ml_model",
                    "source_name": tm.get("model_id") or tm.get("model_version") or "trustlens-model1-v1.0",
                    "verification_status": "automated_inference",
                    "created_at": str(created_at),
                    "metadata": {
                        "analysis_id": analysis_id,
                        "analysis_type": analysis_type,
                        "text": text_val,
                        "predicted_label": tm.get("predicted_label"),
                        "detected_language": tm.get("detected_language"),
                        "risk_score": doc.get("risk_score"),
                        "detected_tactics": tactics_list,
                        "extracted_iocs": doc.get("extracted_iocs") or {},
                    },
                })

            # URL record from analysis if URL analysis
            url_val = payload.get("url") or (doc.get("url_model") or {}).get("url")
            if url_val and analysis_type in ("url", "comprehensive"):
                um = doc.get("url_model") or {}
                items.append({
                    "item_id": f"url:analysis:{analysis_id}",
                    "raw_id": analysis_id,
                    "entity_type": "url",
                    "label": url_val,
                    "summary": f"Classification: {um.get('predicted_label', threat_level)} | Score: {doc.get('risk_score', 'N/A')}",
                    "severity": threat_level,
                    "confidence": float(confidence) if isinstance(confidence, (int, float)) else None,
                    "provenance": "ml_model",
                    "source_name": um.get("model_id") or um.get("model_version") or "trustlens-model2-xgboost-v1.0",
                    "verification_status": "automated_inference",
                    "created_at": str(created_at),
                    "metadata": {
                        "analysis_id": analysis_id,
                        "url": url_val,
                        "risk_score": doc.get("risk_score"),
                        "url_model": um,
                    },
                })

        # 2. Suspicious URLs collection -> URLs & Domains
        urls_coll = get_urls_collection()
        url_docs = await urls_coll.find({}, {"_id": 0}).sort("last_seen", -1).limit(300).to_list(length=300)
        for udoc in url_docs:
            u_val = udoc.get("url", "")
            dom_val = udoc.get("domain", "")
            risk_s = udoc.get("risk_score")
            sev = _normalize_severity(udoc.get("status"), risk_s)
            last_seen = udoc.get("last_seen", "")
            if isinstance(last_seen, datetime):
                last_seen = last_seen.isoformat()

            if u_val:
                items.append({
                    "item_id": f"url:{_short_hash(u_val)}",
                    "raw_id": u_val,
                    "entity_type": "url",
                    "label": u_val,
                    "summary": f"Domain: {dom_val or 'unknown'} | Hits: {udoc.get('hit_count', 1)} | Phishing: {udoc.get('is_phishing')}",
                    "severity": sev,
                    "confidence": float(risk_s) if isinstance(risk_s, (int, float)) else None,
                    "provenance": "ml_model",
                    "source_name": "Suspicious URLs Store (Model 2)",
                    "verification_status": "verified" if udoc.get("status") == "confirmed" else "automated_inference",
                    "created_at": str(last_seen),
                    "metadata": udoc,
                })
            if dom_val and dom_val not in seen_domains:
                seen_domains[dom_val] = {
                    "item_id": f"dom:{_short_hash(dom_val)}",
                    "raw_id": dom_val,
                    "entity_type": "domain",
                    "label": dom_val,
                    "summary": f"Extracted from URLs | Hits: {udoc.get('hit_count', 1)} | Status: {udoc.get('status', 'monitored')}",
                    "severity": sev,
                    "confidence": float(risk_s) if isinstance(risk_s, (int, float)) else None,
                    "provenance": "threat_intel",
                    "source_name": "URL Domain Extractor",
                    "verification_status": "verified" if udoc.get("status") == "confirmed" else "automated_inference",
                    "created_at": str(last_seen),
                    "metadata": {"domain": dom_val, "sample_url": u_val, "hit_count": udoc.get("hit_count", 1)},
                }

        # 3. Threat Indicators collection -> Indicators (and domains)
        ind_coll = get_indicators_collection()
        ind_docs = await ind_coll.find({}, {"_id": 0}).sort("last_seen", -1).limit(300).to_list(length=300)
        for idoc in ind_docs:
            ind_id = idoc.get("indicator_id") or _short_hash(str(idoc.get("indicator_value", "")))
            ind_val = idoc.get("indicator_value", "")
            ind_type = idoc.get("indicator_type", "unknown")
            conf = idoc.get("confidence")
            last_seen = idoc.get("last_seen") or idoc.get("first_seen") or ""
            if isinstance(last_seen, datetime):
                last_seen = last_seen.isoformat()
            status_val = str(idoc.get("status", "active")).lower()
            verif = "verified" if status_val in ("verified", "confirmed", "active") else "unverified"
            prov = "human_review" if "report" in str(idoc.get("source", "")).lower() else "threat_intel"

            items.append({
                "item_id": f"ind:{ind_id}",
                "raw_id": ind_id,
                "entity_type": "indicator",
                "label": f"[{ind_type.upper()}] {ind_val}",
                "summary": f"Source: {idoc.get('source', 'internal')} | Status: {status_val} | Tags: {', '.join(idoc.get('tags') or [])}",
                "severity": _normalize_severity(None, conf),
                "confidence": float(conf) if isinstance(conf, (int, float)) else None,
                "provenance": prov,
                "source_name": idoc.get("source") or "Threat Indicators Store",
                "verification_status": verif,
                "created_at": str(last_seen),
                "metadata": idoc,
            })

            if ind_type == "domain" and ind_val and ind_val not in seen_domains:
                seen_domains[ind_val] = {
                    "item_id": f"dom:{_short_hash(ind_val)}",
                    "raw_id": ind_val,
                    "entity_type": "domain",
                    "label": ind_val,
                    "summary": f"Threat Indicator Domain | Source: {idoc.get('source', 'internal')}",
                    "severity": _normalize_severity(None, conf),
                    "confidence": float(conf) if isinstance(conf, (int, float)) else None,
                    "provenance": prov,
                    "source_name": idoc.get("source") or "Threat Indicators Store",
                    "verification_status": verif,
                    "created_at": str(last_seen),
                    "metadata": idoc,
                }

        items.extend(seen_domains.values())

        # 4. Community Reports collection -> Community Reports & Tactic telemetry
        reports_coll = get_reports_collection()
        rep_docs = await reports_coll.find({}, {"_id": 0}).sort("created_at", -1).limit(300).to_list(length=300)
        for rdoc in rep_docs:
            rep_id = rdoc.get("report_id", "")
            rep_status = str(rdoc.get("status", "pending")).lower()
            created_at = rdoc.get("created_at", "")
            if isinstance(created_at, datetime):
                created_at = created_at.isoformat()

            for t in rdoc.get("assigned_tactics") or []:
                tactic_counts[t] = tactic_counts.get(t, 0) + 1
                tactic_sources.setdefault(t, []).append(rep_id)

            verif = (
                "verified" if rep_status in ("verified_scam", "benign")
                else "under_review" if rep_status == "under_review"
                else "unverified"
            )
            sev = "high" if rep_status == "verified_scam" else ("clean" if rep_status == "benign" else "medium")

            items.append({
                "item_id": f"rep:{rep_id}",
                "raw_id": rep_id,
                "entity_type": "community_report",
                "label": f"[{rdoc.get('target_type', 'sms').upper()}] {rdoc.get('target_identifier') or rdoc.get('content', '')[:60]}",
                "summary": (rdoc.get("content") or "")[:140],
                "severity": sev,
                "confidence": 1.0 if rep_status == "verified_scam" else None,
                "provenance": "human_review",
                "source_name": f"Community Report ({rep_status})",
                "verification_status": verif,
                "created_at": str(created_at),
                "metadata": rdoc,
            })

        # 5. Similarity Clusters (HDBSCAN Campaign Dossiers)
        campaigns = await campaign_service.list_campaigns(limit=100)
        for camp in campaigns:
            cid = camp.get("campaign_id") if camp.get("campaign_id") is not None else camp.get("cluster_id")
            cohesion = camp.get("cohesion_score")
            size = camp.get("cluster_size", 0)
            target = camp.get("targeted_entity") or camp.get("target_brand") or "Unattributed Cluster"
            last_act = camp.get("last_detected") or camp.get("last_activity") or ""
            items.append({
                "item_id": f"clu:{cid}",
                "raw_id": str(cid),
                "entity_type": "similarity_cluster",
                "label": f"Cluster #{cid}: {target}",
                "summary": f"Size: {size} messages | Cohesion: {cohesion} | Primary Tactic: {camp.get('primary_tactic') or ', '.join(camp.get('primary_tactics') or [])}",
                "severity": "critical" if size >= 50 else ("high" if size >= 15 else "medium"),
                "confidence": float(cohesion) if isinstance(cohesion, (int, float)) else None,
                "provenance": "unsupervised_clustering",
                "source_name": "HDBSCAN Multilingual Clusterer (Model 4)",
                "verification_status": "automated_inference",
                "created_at": str(last_act),
                "metadata": camp,
            })

        # 6. Tactics (Observed in DB + Catalog)
        all_tactic_keys = sorted(set(list(TACTIC_CATALOG.keys()) + list(tactic_counts.keys())))
        for t_key in all_tactic_keys:
            obs_count = tactic_counts.get(t_key, 0)
            items.append({
                "item_id": f"tac:{t_key}",
                "raw_id": t_key,
                "entity_type": "tactic",
                "label": t_key.replace("_", " ").title(),
                "summary": f"{TACTIC_CATALOG.get(t_key, 'Observed social engineering tactic.')} (Observed hits: {obs_count})",
                "severity": "high" if obs_count >= 5 else ("medium" if obs_count > 0 else "low"),
                "confidence": None,
                "provenance": "ml_model" if obs_count > 0 else "threat_intel",
                "source_name": "Model 3 Tactic Taxonomy & Detections",
                "verification_status": "verified",
                "created_at": "",
                "metadata": {
                    "tactic_id": t_key,
                    "description": TACTIC_CATALOG.get(t_key, ""),
                    "observed_hits": obs_count,
                    "linked_records": tactic_sources.get(t_key, [])[:20],
                },
            })

        return items

    async def query_library(
        self,
        search: Optional[str] = None,
        entity_type: Optional[str] = None,
        severity: Optional[str] = None,
        verification_status: Optional[str] = None,
        provenance: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        page: int = 1,
        page_size: int = 20,
    ) -> Dict[str, Any]:
        all_items = await self._collect_items()

        # Compute facet counts before filtering
        type_counts: Dict[str, int] = {}
        for it in all_items:
            et = it["entity_type"]
            type_counts[et] = type_counts.get(et, 0) + 1

        filtered = all_items
        if entity_type and entity_type != "all":
            filtered = [i for i in filtered if i["entity_type"] == entity_type]
        if severity and severity != "all":
            filtered = [i for i in filtered if i["severity"] == severity]
        if verification_status and verification_status != "all":
            filtered = [i for i in filtered if i["verification_status"] == verification_status]
        if provenance and provenance != "all":
            filtered = [i for i in filtered if i["provenance"] == provenance]
        if search and search.strip():
            q = search.strip().lower()
            filtered = [
                i for i in filtered
                if q in i["label"].lower()
                or q in i["summary"].lower()
                or q in i["source_name"].lower()
                or q in i["entity_type"].lower()
                or q in str(i["raw_id"]).lower()
            ]

        reverse = sort_order.lower() != "asc"
        if sort_by == "severity":
            filtered.sort(key=lambda x: SEVERITY_ORDER.get(x["severity"], 0), reverse=reverse)
        elif sort_by == "confidence":
            filtered.sort(key=lambda x: x["confidence"] if x["confidence"] is not None else -1.0, reverse=reverse)
        elif sort_by == "label":
            filtered.sort(key=lambda x: x["label"].lower(), reverse=reverse)
        else:
            filtered.sort(key=lambda x: x.get("created_at") or "", reverse=reverse)

        total = len(filtered)
        total_pages = max(1, (total + page_size - 1) // page_size)
        start = (page - 1) * page_size
        end = start + page_size
        page_items = filtered[start:end]

        return {
            "items": page_items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "facets": {
                "entity_types": type_counts,
            },
        }

    async def get_item_detail(self, item_id: str) -> Optional[Dict[str, Any]]:
        all_items = await self._collect_items()
        for item in all_items:
            if item["item_id"] == item_id:
                return item
        return None


threat_library_service = ThreatLibraryService()
