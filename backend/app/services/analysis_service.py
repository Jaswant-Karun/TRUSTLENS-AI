"""
TRUSTLENS AI - Core Threat Analysis Orchestration Service
Coordinates multi-model inference, transparent risk calibration, explainability,
and persistent record keeping across MongoDB Atlas collections.
"""

import re
import uuid
import time
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse

from backend.app.core.logging import logger
from backend.app.ml_engine.engine import ml_engine
from backend.app.services.risk_service import risk_service
from backend.app.database.collections import (
    get_analyses_collection,
    get_urls_collection,
    get_indicators_collection,
    get_audit_collection,
)


class ThreatAnalysisService:
    """End-to-end threat analysis pipeline."""

    @staticmethod
    def extract_iocs(text: str) -> Dict[str, List[str]]:
        """Extracts technical IOCs: URLs, domains, phones, UPI IDs, IPv4 addresses."""
        clean = str(text)
        urls = re.findall(r"https?://[^\s<>\"']+|www\.[^\s<>\"']+", clean)
        
        # Domains from URLs
        domains = []
        for u in urls:
            try:
                parsed = urlparse(u if "://" in u else f"http://{u}")
                if parsed.netloc:
                    domains.append(parsed.netloc.lower())
            except Exception:
                pass

        # Indian phone numbers
        phones = re.findall(r"(?:(?:\+91|91|0)[-.\s]?)?[6-9]\d{9}\b", clean)
        # UPI Handles
        upis = re.findall(r"\b[a-zA-Z0-9.\-_]{2,256}@[a-zA-Z]{2,64}\b", clean)
        # IPv4 addresses
        ips = re.findall(r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b", clean)

        return {
            "urls": list(set(urls)),
            "domains": list(set(domains)),
            "phones": list(set(phones)),
            "upis": list(set(upis)),
            "ips": list(set(ips)),
        }

    async def analyze_text(
        self,
        text: str,
        channel: str = "sms",
        sender: Optional[str] = None,
        user_id: Optional[str] = "anonymous",
        client_ip: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Runs complete multi-model threat analysis on incoming text."""
        start_time = time.perf_counter()
        analysis_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)

        # 1. Model 1: Multilingual Scam Classifier
        text_res = ml_engine.predict_text(text, sender=sender, channel=channel)

        # 2. Model 3: Multi-Label Scam Tactics
        tactic_res = ml_engine.predict_tactics(text)

        # 3. Model 4: Scam Campaign Discovery
        campaign_res = ml_engine.match_campaign(text)

        # 4. Extract Technical IOCs
        iocs = self.extract_iocs(text)

        # 5. Model 2: Check embedded URLs if present
        url_res = None
        if iocs.get("urls"):
            primary_url = iocs["urls"][0]
            url_res = ml_engine.predict_url(primary_url)

        # 6. Check Threat Intelligence for known IOC sightings
        indicators_coll = get_indicators_collection()
        threat_intel_match = False
        all_values = iocs.get("urls", []) + iocs.get("domains", []) + iocs.get("phones", []) + iocs.get("upis", [])
        if all_values:
            existing_ioc = await indicators_coll.find_one({"value": {"$in": all_values}, "severity": {"$in": ["high", "critical"]}})
            if existing_ioc:
                threat_intel_match = True

        # 7. Transparent Risk Aggregation Service
        assessment = risk_service.assess_risk(
            text_result=text_res,
            url_result=url_res,
            tactic_result=tactic_res,
            campaign_result=campaign_res,
            threat_intel_match=threat_intel_match,
            raw_content=text,
        )

        # 8. Explainability Engine
        scan_payload = {
            "scan_id": analysis_id,
            "detected_type": "text",
            "overall_threat_level": assessment["threat_level"],
            "text_analysis": text_res,
            "url_analysis": url_res,
            "tactics_analysis": tactic_res,
            "campaign_association": campaign_res,
        }
        explainability = ml_engine.explain(text, scan_payload)

        processing_time = round((time.perf_counter() - start_time) * 1000, 2)

        # 9. Persist to MongoDB Atlas 'analyses' collection
        analyses_coll = get_analyses_collection()
        analysis_doc = {
            "analysis_id": analysis_id,
            "user_id": user_id or "anonymous",
            "analysis_type": "text",
            "input_payload": {"text": text, "sender": sender, "channel": channel},
            "threat_level": assessment["threat_level"],
            "confidence": assessment["calibrated_confidence"],
            "risk_score": assessment["risk_score"],
            "risk_assessment": assessment,
            "text_model": text_res,
            "url_model": url_res,
            "tactic_model": tactic_res,
            "campaign_association": campaign_res,
            "extracted_iocs": iocs,
            "explainability": explainability,
            "processing_time_ms": processing_time,
            "created_at": now,
        }
        await analyses_coll.insert_one(analysis_doc)

        # 10. Update 'suspicious_urls' & 'threat_indicators' if threats found
        if url_res and url_res.get("is_phishing") and iocs.get("urls"):
            urls_coll = get_urls_collection()
            u = iocs["urls"][0]
            await urls_coll.update_one(
                {"url": u},
                {
                    "$set": {
                        "url": u,
                        "domain": urlparse(u).netloc,
                        "risk_score": url_res.get("risk_score", 1.0),
                        "is_phishing": True,
                        "features": url_res.get("features", {}),
                        "shap_impacts": url_res.get("top_risk_factors", []),
                        "last_seen": now,
                        "status": "active",
                    },
                    "$inc": {"hit_count": 1},
                },
                upsert=True,
            )

        # Audit log
        audit_coll = get_audit_collection()
        await audit_coll.insert_one({
            "audit_id": str(uuid.uuid4()),
            "user_id": user_id or "anonymous",
            "action": "scan_text",
            "resource_type": "analysis",
            "resource_id": analysis_id,
            "client_ip": client_ip,
            "timestamp": now,
            "details": {"threat_level": assessment["threat_level"], "risk_score": assessment["risk_score"]},
        })

        return {
            "analysis_id": analysis_id,
            "analysis_type": "text",
            "threat_level": assessment["threat_level"],
            "confidence": assessment["calibrated_confidence"],
            "risk_score": assessment["risk_score"],
            "risk_assessment": assessment,
            "text_model": text_res,
            "url_model": url_res,
            "tactic_model": tactic_res,
            "campaign_association": campaign_res,
            "extracted_iocs": iocs,
            "explainability": explainability,
            "processing_time_ms": processing_time,
            "created_at": now,
        }

    async def analyze_url(
        self,
        url: str,
        user_id: Optional[str] = "anonymous",
        client_ip: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Runs zero-hop deterministic URL phishing inspection."""
        start_time = time.perf_counter()
        analysis_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)

        # 1. Model 2: Phishing URL Detector
        url_res = ml_engine.predict_url(url)

        # 2. Risk Assessment
        assessment = risk_service.assess_risk(
            url_result=url_res,
            raw_content=url,
        )

        # 3. Explainability
        scan_payload = {
            "scan_id": analysis_id,
            "detected_type": "url",
            "overall_threat_level": assessment["threat_level"],
            "url_analysis": url_res,
        }
        explainability = ml_engine.explain(url, scan_payload)
        processing_time = round((time.perf_counter() - start_time) * 1000, 2)

        # 4. Persist to MongoDB Atlas 'analyses' & 'suspicious_urls'
        analyses_coll = get_analyses_collection()
        domain = urlparse(url if "://" in url else f"http://{url}").netloc
        iocs = {"urls": [url], "domains": [domain] if domain else []}

        analysis_doc = {
            "analysis_id": analysis_id,
            "user_id": user_id or "anonymous",
            "analysis_type": "url",
            "input_payload": {"url": url},
            "threat_level": assessment["threat_level"],
            "confidence": assessment["calibrated_confidence"],
            "risk_score": assessment["risk_score"],
            "risk_assessment": assessment,
            "url_model": url_res,
            "extracted_iocs": iocs,
            "explainability": explainability,
            "processing_time_ms": processing_time,
            "created_at": now,
        }
        await analyses_coll.insert_one(analysis_doc)

        if url_res.get("is_phishing"):
            urls_coll = get_urls_collection()
            await urls_coll.update_one(
                {"url": url},
                {
                    "$set": {
                        "url": url,
                        "domain": domain,
                        "risk_score": url_res.get("risk_score", 1.0),
                        "is_phishing": True,
                        "features": url_res.get("features", {}),
                        "last_seen": now,
                        "status": "active",
                    },
                    "$inc": {"hit_count": 1},
                },
                upsert=True,
            )

        return {
            "analysis_id": analysis_id,
            "analysis_type": "url",
            "threat_level": assessment["threat_level"],
            "confidence": assessment["calibrated_confidence"],
            "risk_score": assessment["risk_score"],
            "risk_assessment": assessment,
            "url_model": url_res,
            "extracted_iocs": iocs,
            "explainability": explainability,
            "processing_time_ms": processing_time,
            "created_at": now,
        }

    async def get_analyses_history(
        self,
        user_id: Optional[str] = None,
        role: str = "user",
        threat_level: Optional[str] = None,
        channel: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Dict[str, Any]:
        """Retrieves paginated scan history from MongoDB."""
        analyses_coll = get_analyses_collection()
        query: Dict[str, Any] = {}

        # Standard users can only view their own scan history
        if role not in ["analyst", "admin"] and user_id:
            query["user_id"] = user_id

        if threat_level:
            query["threat_level"] = threat_level
        if channel:
            query["input_payload.channel"] = channel

        skip = (page - 1) * page_size
        total_count = await analyses_coll.count_documents(query)

        cursor = analyses_coll.find(query).sort("created_at", -1).skip(skip).limit(page_size)
        items = await cursor.to_list(length=page_size)

        # Remove internal MongoDB _id from returned items
        for item in items:
            item.pop("_id", None)

        total_pages = (total_count + page_size - 1) // page_size if total_count > 0 else 1

        return {
            "items": items,
            "total_count": total_count,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
        }

    async def get_analysis_by_id(
        self,
        analysis_id: str,
        user_id: Optional[str] = None,
        role: str = "user",
    ) -> Optional[Dict[str, Any]]:
        """Retrieves a single analysis record by ID."""
        analyses_coll = get_analyses_collection()
        query = {"analysis_id": analysis_id}
        if role not in ["analyst", "admin"] and user_id:
            query["user_id"] = user_id

        doc = await analyses_coll.find_one(query)
        if doc:
            doc.pop("_id", None)
        return doc


analysis_service = ThreatAnalysisService()
threat_analysis_service = analysis_service
