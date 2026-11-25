"""
TRUSTLENS AI - Investigation Reporting & STIX 2.1 / JSON Export Service
Generates auditable intelligence reports and strictly validated JSON / STIX 2.1 exports.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import uuid
import re

from backend.app.database.collections import (
    get_analyses_collection,
    get_urls_collection,
    get_investigations_collection,
    get_models_collection,
    get_evaluations_collection,
)
from backend.app.services.campaign_service import campaign_service
from backend.app.services.model_service import model_service


def _utc_iso(dt: Optional[Any] = None) -> str:
    if isinstance(dt, datetime):
        return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
    if isinstance(dt, str) and dt.strip():
        s = dt.strip()
        if s.endswith("Z"):
            return s
        try:
            parsed = datetime.fromisoformat(s.replace("Z", "+00:00"))
            return parsed.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        except Exception:
            pass
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def _stix_id(stix_type: str, seed: str) -> str:
    uid = uuid.uuid5(uuid.NAMESPACE_URL, f"trustlens:{stix_type}:{seed}")
    return f"{stix_type}--{uid}"


def _escape_stix_pattern(val: str) -> str:
    return val.replace("\\", "\\\\").replace("'", "\\'")


def _is_ipv4(val: str) -> bool:
    return bool(re.match(r"^(?:\d{1,3}\.){3}\d{1,3}$", val.strip()))


class ReportingService:
    """Generates structured investigation reports and validated JSON / STIX 2.1 exports."""

    async def _fetch_analysis(self, target_id: str, current_user: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        coll = get_analyses_collection()
        doc = await coll.find_one({"analysis_id": target_id}, {"_id": 0})
        if not doc:
            return None
        role = current_user.get("role", "user")
        if role not in ("analyst", "admin") and doc.get("user_id") != current_user.get("user_id"):
            raise PermissionError("Access denied: You may only access your own analysis records.")
        return doc

    async def generate_report(
        self,
        report_type: str,
        target_id: Optional[str],
        current_user: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        generated_at = _utc_iso()
        generated_by = current_user.get("user_id", "anonymous") if current_user else "anonymous"
        report_id = f"RPT-{uuid.uuid4().hex[:10].upper()}"

        if report_type in ("message_analysis", "url_analysis"):
            if not target_id:
                raise ValueError("target_id (analysis_id) is required for message_analysis and url_analysis reports.")
            if not current_user:
                raise PermissionError("Authentication required to generate reports for private analysis records.")
            doc = await self._fetch_analysis(target_id, current_user)
            if not doc:
                raise LookupError(f"Analysis '{target_id}' was not found.")

            tm = doc.get("text_model") or {}
            um = doc.get("url_model") or {}
            tac = doc.get("tactic_model") or {}
            ra = doc.get("risk_assessment") or {}

            sources = ["TRUSTLENS FastAPI Inference Pipeline"]
            model_versions: Dict[str, str] = {}
            if tm:
                mv = tm.get("model_id") or tm.get("model_version") or "trustlens-model1-v1.0"
                model_versions["text_scam_detector"] = str(mv)
                sources.append(f"ML Model ({mv})")
            if um:
                mv = um.get("model_id") or um.get("model_version") or "trustlens-model2-xgboost-v1.0"
                model_versions["phishing_url_detector"] = str(mv)
                sources.append(f"ML Model ({mv})")
            if tac:
                mv = tac.get("model_id") or tac.get("model_version") or "trustlens-model3-calibrated-linear-v1.0"
                model_versions["tactic_detector"] = str(mv)
                sources.append(f"ML Model ({mv})")

            evidence: List[Dict[str, Any]] = []
            for item in (doc.get("explainability") or {}).get("top_features", []) or []:
                evidence.append({"provenance": "ml_explainability", "detail": item})
            for k, v in (doc.get("extracted_iocs") or {}).items():
                if v:
                    evidence.append({"provenance": "ioc_extractor", "ioc_type": k, "values": v})
            if ra.get("transparency_breakdown"):
                evidence.append({"provenance": "risk_aggregation", "breakdown": ra["transparency_breakdown"]})

            return {
                "report_id": report_id,
                "report_type": report_type,
                "investigation_id": target_id,
                "sources": list(dict.fromkeys(sources)),
                "evidence": evidence,
                "model_versions": model_versions,
                "predictions": {
                    "threat_level": doc.get("threat_level"),
                    "confidence": doc.get("confidence"),
                    "risk_score": doc.get("risk_score"),
                    "verdict": ra.get("verdict"),
                    "text_label": tm.get("predicted_label"),
                    "detected_language": tm.get("detected_language"),
                    "detected_tactics": tac.get("detected_tactics") or [],
                },
                "review_status": "automated_inference",
                "limitations": [
                    "Predictions reflect static lexical/NLP/URL ML inference at analysis time; no live sandbox detonation or external WHOIS lookup was performed.",
                    "Automated inference has not been human-verified unless explicitly escalated to a SOC investigation.",
                ],
                "generated_at": generated_at,
                "generated_by": generated_by,
            }

        if report_type == "comprehensive_investigation":
            if not target_id:
                raise ValueError("target_id (investigation_id or analysis_id) is required.")
            inv_coll = get_investigations_collection()
            inv = await inv_coll.find_one({"investigation_id": target_id}, {"_id": 0})
            if inv:
                nodes = inv.get("nodes") or []
                edges = inv.get("edges") or []
                sources = list(dict.fromkeys([n.get("source") for n in nodes if n.get("source")] + (inv.get("sources") or [])))
                model_versions = {}
                for n in nodes:
                    mv = (n.get("properties") or {}).get("model_version")
                    if mv:
                        model_versions[n.get("type", "model")] = mv
                evidence = [
                    {
                        "node_id": n.get("id"),
                        "type": n.get("type"),
                        "label": n.get("label"),
                        "source": n.get("source"),
                        "verification_status": n.get("verification_status"),
                    }
                    for n in nodes
                ]
                verified_count = sum(1 for n in nodes if n.get("verification_status") == "verified")
                review_status = "verified" if verified_count > 0 else "automated_inference"
                return {
                    "report_id": report_id,
                    "report_type": report_type,
                    "investigation_id": target_id,
                    "sources": sources or ["TRUSTLENS Investigation Graph"],
                    "evidence": evidence,
                    "model_versions": model_versions,
                    "predictions": {
                        "title": inv.get("title"),
                        "severity": inv.get("severity"),
                        "status": inv.get("status"),
                        "node_count": len(nodes),
                        "edge_count": len(edges),
                    },
                    "review_status": review_status,
                    "limitations": [
                        "Graph relationships represent evidence-backed correlations from stored analyses, IOCs, and HDBSCAN clusters.",
                        "Attribution to specific external threat actors is probabilistic unless confirmed by law-enforcement or verified human intelligence.",
                    ],
                    "generated_at": generated_at,
                    "generated_by": generated_by,
                }

            # Fallback: check if target_id is a comprehensive analysis_id
            if current_user:
                doc = await self._fetch_analysis(target_id, current_user)
                if doc:
                    return await self.generate_report("message_analysis", target_id, current_user)
            raise LookupError(f"Investigation '{target_id}' was not found.")

        if report_type == "campaign_similarity":
            if not target_id:
                raise ValueError("target_id (campaign_id) is required.")
            try:
                cid = int(target_id)
            except ValueError:
                raise ValueError("campaign_id must be an integer cluster ID.")
            dossier = await campaign_service.get_campaign_by_id(cid)
            if not dossier:
                raise LookupError(f"Campaign Cluster #{cid} was not found.")

            return {
                "report_id": report_id,
                "report_type": report_type,
                "investigation_id": f"CAMP-{cid}",
                "sources": ["HDBSCAN Multilingual Campaign Clusterer (Model 4)"],
                "evidence": [
                    {"provenance": "exemplar_message", "text": dossier.get("exemplar_message")},
                    {"provenance": "shared_urls", "values": dossier.get("shared_urls") or []},
                    {"provenance": "shared_domains", "values": dossier.get("shared_domains") or []},
                    {"provenance": "shared_iocs", "values": dossier.get("shared_threat_indicators") or dossier.get("shared_iocs") or []},
                ],
                "model_versions": {"campaign_clusterer": "trustlens-model4-hdbscan-v1.0"},
                "predictions": {
                    "cluster_id": cid,
                    "cluster_size": dossier.get("cluster_size"),
                    "cohesion_score": dossier.get("cohesion_score"),
                    "targeted_entity": dossier.get("targeted_entity") or dossier.get("target_brand"),
                    "primary_tactics": dossier.get("primary_tactics") or [dossier.get("primary_tactic")],
                    "status": dossier.get("status"),
                },
                "review_status": "automated_inference",
                "limitations": [
                    dossier.get("legal_disclaimer") or "Cluster membership is based on multilingual embedding density (HDBSCAN) and does not establish legal attribution.",
                ],
                "generated_at": generated_at,
                "generated_by": generated_by,
            }

        if report_type == "model_evaluation":
            metrics_data = model_service.get_models_metrics()
            registry_data = model_service.get_models_registry()
            models_dict = metrics_data.get("models", {})
            model_versions = {
                k: v.get("version") or v.get("model_id") or "v1.0.0"
                for k, v in models_dict.items()
                if isinstance(v, dict)
            }
            return {
                "report_id": report_id,
                "report_type": report_type,
                "investigation_id": "MODEL-EVAL-SUMMARY",
                "sources": ["ml/artifacts/model_dashboard_data.json", "ml/artifacts/model_registry.json"],
                "evidence": [
                    {"model_key": k, "metrics": v}
                    for k, v in models_dict.items()
                ],
                "model_versions": model_versions,
                "predictions": metrics_data.get("overall_summary", {}),
                "review_status": "verified",
                "limitations": [
                    "Metrics reflect held-out benchmark evaluations and do not guarantee identical precision/recall under novel zero-day campaign drift.",
                    f"Registry entries loaded: {len(registry_data.get('models', {})) if isinstance(registry_data.get('models'), dict) else 0}.",
                ],
                "generated_at": generated_at,
                "generated_by": generated_by,
            }

        raise ValueError(f"Unsupported report_type '{report_type}'.")

    async def export_json(
        self,
        target_type: str,
        target_id: str,
        current_user: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        exported_at = _utc_iso()
        exported_by = current_user.get("user_id", "anonymous") if current_user else "anonymous"

        if target_type == "investigation":
            inv_coll = get_investigations_collection()
            doc = await inv_coll.find_one({"investigation_id": target_id}, {"_id": 0})
            if not doc:
                raise LookupError(f"Investigation '{target_id}' was not found.")
            data = doc
        elif target_type == "analysis":
            if not current_user:
                raise PermissionError("Authentication required to export private analysis records.")
            doc = await self._fetch_analysis(target_id, current_user)
            if not doc:
                raise LookupError(f"Analysis '{target_id}' was not found.")
            data = doc
        elif target_type == "campaign":
            cid = int(target_id)
            doc = await campaign_service.get_campaign_by_id(cid)
            if not doc:
                raise LookupError(f"Campaign Cluster #{cid} was not found.")
            data = doc
        elif target_type == "report":
            data = await self.generate_report("comprehensive_investigation", target_id, current_user)
        else:
            raise ValueError(f"Unsupported target_type '{target_type}'.")

        return {
            "export_format": "trustlens-json-v1",
            "target_type": target_type,
            "target_id": target_id,
            "exported_at": exported_at,
            "exported_by": exported_by,
            "data": data,
        }

    async def export_stix_21(
        self,
        target_type: str,
        target_id: str,
        current_user: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Exports strictly mapped STIX 2.1 Bundle without inventing unsupported attributes
        or claiming unvalidated MISP interoperability.
        """
        now_str = _utc_iso()
        identity_id = _stix_id("identity", "trustlens-ai-platform")
        objects: List[Dict[str, Any]] = [
            {
                "type": "identity",
                "spec_version": "2.1",
                "id": identity_id,
                "created": now_str,
                "modified": now_str,
                "name": "TRUSTLENS AI Threat Intelligence Engine",
                "identity_class": "system",
            }
        ]
        object_refs: List[str] = [identity_id]
        unmapped_fields: List[str] = []

        def add_indicator_and_sco(kind: str, value: str, label: str, valid_from: str):
            val = value.strip()
            if not val:
                return
            if kind == "url":
                sco_id = _stix_id("url", val)
                objects.append({"type": "url", "id": sco_id, "value": val})
                pattern = f"[url:value = '{_escape_stix_pattern(val)}']"
            elif kind == "domain":
                sco_id = _stix_id("domain-name", val)
                objects.append({"type": "domain-name", "id": sco_id, "value": val})
                pattern = f"[domain-name:value = '{_escape_stix_pattern(val)}']"
            elif kind == "ip" and _is_ipv4(val):
                sco_id = _stix_id("ipv4-addr", val)
                objects.append({"type": "ipv4-addr", "id": sco_id, "value": val})
                pattern = f"[ipv4-addr:value = '{_escape_stix_pattern(val)}']"
            else:
                unmapped_fields.append(f"{kind}:{val}")
                return

            ind_id = _stix_id("indicator", f"{kind}:{val}")
            objects.append({
                "type": "indicator",
                "spec_version": "2.1",
                "id": ind_id,
                "created": now_str,
                "modified": now_str,
                "created_by_ref": identity_id,
                "name": label[:120],
                "pattern": pattern,
                "pattern_type": "stix",
                "valid_from": valid_from,
            })
            rel_id = _stix_id("relationship", f"{ind_id}-indicates-{sco_id}")
            objects.append({
                "type": "relationship",
                "spec_version": "2.1",
                "id": rel_id,
                "created": now_str,
                "modified": now_str,
                "relationship_type": "based-on",
                "source_ref": ind_id,
                "target_ref": sco_id,
            })
            object_refs.extend([sco_id, ind_id, rel_id])

        def add_tactic(tactic_name: str):
            clean = tactic_name.strip()
            if not clean:
                return
            ap_id = _stix_id("attack-pattern", clean)
            objects.append({
                "type": "attack-pattern",
                "spec_version": "2.1",
                "id": ap_id,
                "created": now_str,
                "modified": now_str,
                "created_by_ref": identity_id,
                "name": clean.replace("_", " ").title(),
                "description": f"TRUSTLENS social-engineering tactic: {clean}",
            })
            object_refs.append(ap_id)

        report_name = f"TRUSTLENS STIX 2.1 Export: {target_id}"
        published_ts = now_str

        if target_type == "investigation":
            inv_coll = get_investigations_collection()
            inv = await inv_coll.find_one({"investigation_id": target_id}, {"_id": 0})
            if not inv:
                raise LookupError(f"Investigation '{target_id}' was not found.")
            report_name = inv.get("title") or report_name
            published_ts = _utc_iso(inv.get("created_at"))
            for n in inv.get("nodes") or []:
                ntype = n.get("type")
                props = n.get("properties") or {}
                if ntype == "url":
                    add_indicator_and_sco("url", props.get("url") or n.get("label", ""), n.get("label", "URL"), published_ts)
                elif ntype == "domain":
                    add_indicator_and_sco("domain", props.get("domain") or n.get("label", ""), n.get("label", "Domain"), published_ts)
                elif ntype == "ip":
                    add_indicator_and_sco("ip", props.get("ip") or n.get("label", ""), n.get("label", "IPv4"), published_ts)
                elif ntype == "tactic":
                    add_tactic(n.get("label", ""))
                else:
                    unmapped_fields.append(f"node_type:{ntype}")

        elif target_type == "analysis":
            if not current_user:
                raise PermissionError("Authentication required to export private analysis records.")
            doc = await self._fetch_analysis(target_id, current_user)
            if not doc:
                raise LookupError(f"Analysis '{target_id}' was not found.")
            published_ts = _utc_iso(doc.get("created_at"))
            payload = doc.get("input_payload") or {}
            if payload.get("url"):
                add_indicator_and_sco("url", payload["url"], f"Analyzed URL ({doc.get('threat_level')})", published_ts)
            iocs = doc.get("extracted_iocs") or {}
            for u in iocs.get("urls") or []:
                add_indicator_and_sco("url", u, "Extracted URL IOC", published_ts)
            for d in iocs.get("domains") or []:
                add_indicator_and_sco("domain", d, "Extracted Domain IOC", published_ts)
            for ip in iocs.get("ips") or []:
                add_indicator_and_sco("ip", ip, "Extracted IPv4 IOC", published_ts)
            for t in (doc.get("tactic_model") or {}).get("detected_tactics") or []:
                t_name = t.get("tactic") if isinstance(t, dict) else str(t)
                add_tactic(t_name)

        elif target_type == "campaign":
            cid = int(target_id)
            dossier = await campaign_service.get_campaign_by_id(cid)
            if not dossier:
                raise LookupError(f"Campaign Cluster #{cid} was not found.")
            camp_id = _stix_id("campaign", str(cid))
            objects.append({
                "type": "campaign",
                "spec_version": "2.1",
                "id": camp_id,
                "created": now_str,
                "modified": now_str,
                "created_by_ref": identity_id,
                "name": f"TRUSTLENS Campaign Cluster #{cid}: {dossier.get('targeted_entity') or dossier.get('target_brand') or 'Unattributed'}",
                "description": f"HDBSCAN cluster size={dossier.get('cluster_size')}, cohesion={dossier.get('cohesion_score')}",
            })
            object_refs.append(camp_id)
            for u in dossier.get("shared_urls") or []:
                add_indicator_and_sco("url", u, f"Campaign #{cid} URL", now_str)
            for d in dossier.get("shared_domains") or []:
                add_indicator_and_sco("domain", d, f"Campaign #{cid} Domain", now_str)
            for t in dossier.get("primary_tactics") or ([dossier.get("primary_tactic")] if dossier.get("primary_tactic") else []):
                add_tactic(str(t))
        else:
            raise ValueError(f"Unsupported target_type '{target_type}' for STIX 2.1 export.")

        # Deduplicate objects by id
        dedup_map: Dict[str, Dict[str, Any]] = {}
        for obj in objects:
            dedup_map[obj["id"]] = obj
        unique_objects = list(dedup_map.values())
        unique_refs = list(dict.fromkeys(object_refs))

        report_obj_id = _stix_id("report", f"{target_type}:{target_id}")
        unique_objects.append({
            "type": "report",
            "spec_version": "2.1",
            "id": report_obj_id,
            "created": now_str,
            "modified": now_str,
            "created_by_ref": identity_id,
            "name": report_name,
            "published": published_ts,
            "report_types": ["threat-report"],
            "object_refs": unique_refs,
        })

        bundle_id = f"bundle--{uuid.uuid4()}"
        return {
            "type": "bundle",
            "id": bundle_id,
            "objects": unique_objects,
            "x_trustlens_stix_validation": {
                "spec_version": "2.1",
                "misp_interoperability_claimed": False,
                "mapped_objects_count": len(unique_objects),
                "unmapped_non_stix_attributes": list(dict.fromkeys(unmapped_fields)),
            },
        }


reporting_service = ReportingService()
