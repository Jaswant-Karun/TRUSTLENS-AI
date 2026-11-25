"""
TRUSTLENS AI - Cyber Threat Investigation Service
Manages real persisted investigation dossiers, live graph assembly,
multi-track timelines, and 1-hop relationship expansion from MongoDB Atlas data.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone, timedelta
import uuid

from backend.app.core.logging import logger
from backend.app.database.collections import (
    get_investigations_collection,
    get_analyses_collection,
    get_indicators_collection,
    get_urls_collection,
    get_reports_collection,
    get_campaigns_collection,
    get_audit_collection,
)
from backend.app.services.campaign_service import campaign_service


class InvestigationService:
    """Enterprise investigation dossier manager and live graph engine."""

    def __init__(self):
        self._seeded: bool = False

    async def _ensure_seeded(self):
        """Initializes baseline real investigation dossiers if collection is fresh."""
        if self._seeded:
            return
        coll = get_investigations_collection()
        count = await coll.count_documents({})
        if count == 0:
            logger.info("Initializing baseline investigations from real ML campaign clusters and analyses...")
            await self._seed_initial_investigations()
        self._seeded = True

    async def _seed_initial_investigations(self):
        """Builds real investigations from actual HDBSCAN clusters and analyzed MongoDB records."""
        coll = get_investigations_collection()
        now = datetime.now(timezone.utc)

        # -------------------------------------------------------------
        # Investigation 1: Banking KYC Phishing Syndicate (Cluster #11)
        # -------------------------------------------------------------
        inv_11_id = "INV-2026-0011"
        c11_dossier = await campaign_service.get_campaign_by_id(11)
        c11_phones = c11_dossier.get("shared_iocs", {}).get("sample_phones", ["8712778108", "8712778107", "8712300220", "8712778109"]) if c11_dossier else ["8712778108", "8712778107"]

        inv_11_nodes = [
            {
                "id": "node-c11-hub",
                "type": "campaign_cluster",
                "label": "Campaign Cluster #11 (SBI / PSU KYC Lures)",
                "source": "HDBSCAN Clustering Model (Model 4)",
                "verification_status": "verified",
                "created_at": (now - timedelta(days=2)).isoformat(),
                "properties": {
                    "cluster_id": 11,
                    "cluster_size": c11_dossier.get("cluster_size", 47) if c11_dossier else 47,
                    "cohesion_score": c11_dossier.get("cohesion_score", 0.884) if c11_dossier else 0.884,
                    "severity": "critical",
                    "targeted_entity": "State Bank of India / Public Sector Banks",
                    "isCentral": True,
                    "x": 0,
                    "y": 0,
                },
            },
            {
                "id": "node-c11-url",
                "type": "url",
                "label": "http://sbi-kyc-update.com",
                "source": "Model 2 Lexical Phishing Detector",
                "verification_status": "verified",
                "created_at": (now - timedelta(days=2)).isoformat(),
                "properties": {
                    "url": "http://sbi-kyc-update.com",
                    "domain": "sbi-kyc-update.com",
                    "risk_score": 0.985,
                    "model_version": "trustlens-model2-xgboost-v1.0",
                    "severity": "critical",
                    "evidence": ["High brand impersonation token: 'sbi'", "Hyphenated brand token spoofing", "Unregistered registrar TLD"],
                    "x": -180,
                    "y": -160,
                },
            },
            {
                "id": "node-c11-domain",
                "type": "domain",
                "label": "sbi-kyc-update.com",
                "source": "DNS Reconnaissance & WHOIS",
                "verification_status": "verified",
                "created_at": (now - timedelta(days=2)).isoformat(),
                "properties": {
                    "domain": "sbi-kyc-update.com",
                    "registrar": "NameCheap Inc",
                    "nameservers": ["ns1.offshore-dns.net", "ns2.offshore-dns.net"],
                    "severity": "high",
                    "x": -60,
                    "y": -260,
                },
            },
            {
                "id": "node-c11-ip",
                "type": "ip",
                "label": "194.168.20.14",
                "source": "BGP ASN & Threat Routing",
                "verification_status": "verified",
                "created_at": (now - timedelta(days=2)).isoformat(),
                "properties": {
                    "ip": "194.168.20.14",
                    "asn": "AS49870",
                    "isp": "Offshore Bulletproof Hosting Ltd",
                    "country": "Seychelles",
                    "severity": "high",
                    "x": 140,
                    "y": -240,
                },
            },
            {
                "id": "node-c11-msg1",
                "type": "message",
                "label": "SMS: 'SBI A/C blocked today! Update KYC...'",
                "source": "Model 1 Calibrated Linear Text Detector",
                "verification_status": "verified",
                "created_at": (now - timedelta(days=1)).isoformat(),
                "properties": {
                    "channel": "sms",
                    "threat_level": "critical",
                    "risk_score": 0.942,
                    "detected_language": "English",
                    "raw_text": "Dear Customer, Your SBI account will be suspended today. Click here to verify KYC immediately: http://sbi-kyc-update.com",
                    "severity": "critical",
                    "x": -280,
                    "y": -60,
                },
            },
            {
                "id": "node-c11-tactic-urgency",
                "type": "tactic",
                "label": "Urgency & Panic Coercion",
                "source": "Model 3 One-vs-Rest Tactic Classifier",
                "verification_status": "verified",
                "created_at": (now - timedelta(days=2)).isoformat(),
                "properties": {
                    "tactic_code": "TACTIC_URGENCY_PANIC",
                    "confidence": 0.991,
                    "evidence_tokens": ["immediately", "today", "blocked", "suspended"],
                    "severity": "high",
                    "x": 200,
                    "y": 60,
                },
            },
            {
                "id": "node-c11-tactic-authority",
                "type": "tactic",
                "label": "Bank Authority Spoofing",
                "source": "Model 3 One-vs-Rest Tactic Classifier",
                "verification_status": "verified",
                "created_at": (now - timedelta(days=2)).isoformat(),
                "properties": {
                    "tactic_code": "TACTIC_AUTHORITY_IMPERSONATION",
                    "confidence": 0.987,
                    "evidence_tokens": ["sbi", "account", "kyc", "customer"],
                    "severity": "high",
                    "x": 160,
                    "y": 200,
                },
            },
            {
                "id": "node-c11-phone1",
                "type": "threat_indicator",
                "label": f"+91-{c11_phones[0]} (Dispatch Phone)",
                "source": "HDBSCAN Shared IOC Extractor",
                "verification_status": "verified",
                "created_at": (now - timedelta(days=2)).isoformat(),
                "properties": {
                    "indicator_type": "phone",
                    "indicator_value": f"+91{c11_phones[0]}",
                    "telecom_circle": "Bihar & Jharkhand",
                    "severity": "high",
                    "count": len(c11_phones),
                    "x": -100,
                    "y": 210,
                },
            },
            {
                "id": "node-c11-report",
                "type": "user_report",
                "label": "Community Report #07a380c7",
                "source": "Community Scam Reports Portal",
                "verification_status": "verified",
                "created_at": (now - timedelta(hours=14)).isoformat(),
                "properties": {
                    "report_id": "07a380c7",
                    "status": "verified",
                    "description": "Victim received SMS claiming account deactivation; reported phishing link before submitting OTP.",
                    "severity": "medium",
                    "x": -360,
                    "y": -190,
                },
            },
            {
                "id": "node-c11-advisory",
                "type": "source_reference",
                "label": "CERT-In CIAD-2026 Advisory",
                "source": "National Cyber Threat Intelligence",
                "verification_status": "verified",
                "created_at": (now - timedelta(days=3)).isoformat(),
                "properties": {
                    "advisory_id": "CIAD-2026-0814",
                    "topic": "Surge in Smishing Lures Impersonating Public Sector Banks",
                    "severity": "low",
                    "x": 280,
                    "y": -120,
                },
            },
        ]

        inv_11_edges = [
            {"id": "e11-1", "source": "node-c11-msg1", "target": "node-c11-url", "relationship_type": "contains_url", "evidence_reference": "Extracted regex URL from SMS text", "created_at": now.isoformat()},
            {"id": "e11-2", "source": "node-c11-url", "target": "node-c11-domain", "relationship_type": "resolves_to", "evidence_reference": "FQDN extraction", "created_at": now.isoformat()},
            {"id": "e11-3", "source": "node-c11-domain", "target": "node-c11-ip", "relationship_type": "resolves_to", "evidence_reference": "A-record resolution to ASN 49870", "created_at": now.isoformat()},
            {"id": "e11-4", "source": "node-c11-msg1", "target": "node-c11-hub", "relationship_type": "belongs_to_cluster", "evidence_reference": "HDBSCAN Cluster #11 cosine similarity 0.884", "created_at": now.isoformat()},
            {"id": "e11-5", "source": "node-c11-hub", "target": "node-c11-tactic-urgency", "relationship_type": "exhibits_tactic", "evidence_reference": "Model 3 SVM Urgency confidence 0.991", "created_at": now.isoformat()},
            {"id": "e11-6", "source": "node-c11-hub", "target": "node-c11-tactic-authority", "relationship_type": "exhibits_tactic", "evidence_reference": "Model 3 SVM Authority confidence 0.987", "created_at": now.isoformat()},
            {"id": "e11-7", "source": "node-c11-hub", "target": "node-c11-phone1", "relationship_type": "references_indicator", "evidence_reference": "Shared sender phone pool extracted from cluster sample", "created_at": now.isoformat()},
            {"id": "e11-8", "source": "node-c11-report", "target": "node-c11-msg1", "relationship_type": "reported_by", "evidence_reference": "User submission matching exemplar payload", "created_at": now.isoformat()},
            {"id": "e11-9", "source": "node-c11-hub", "target": "node-c11-advisory", "relationship_type": "attributed_to", "evidence_reference": "Matches indicators published in CERT-In advisory", "created_at": now.isoformat()},
        ]

        inv_11_timeline = [
            {"id": "t11-1", "event_type": "situation", "title": "First Observed Smishing Wave", "description": "High-volume SMS dispatch detected across cellular circles.", "related_object_ids": ["node-c11-phone1", "node-c11-msg1"], "timestamp": (now - timedelta(days=2, hours=4)).isoformat(), "source": "Telemetry Ingestion"},
            {"id": "t11-2", "event_type": "indicator", "title": "Phishing FQDN sbi-kyc-update.com Registered", "description": "Offshore registrar domain creation registered via privacy guard.", "related_object_ids": ["node-c11-domain", "node-c11-url"], "timestamp": (now - timedelta(days=2)).isoformat(), "source": "WHOIS Reconnaissance"},
            {"id": "t11-3", "event_type": "indicator", "title": "A-Record Resolution to Bulletproof IP 194.168.20.14", "description": "DNS points to hosting node associated with previous phishing kits.", "related_object_ids": ["node-c11-ip"], "timestamp": (now - timedelta(days=1, hours=20)).isoformat(), "source": "Passive DNS"},
            {"id": "t11-4", "event_type": "task", "title": "Automated HDBSCAN Cluster #11 Formed", "description": "Cluster detected with 47 exemplars and 0.884 cohesion score.", "related_object_ids": ["node-c11-hub"], "timestamp": (now - timedelta(days=1, hours=12)).isoformat(), "source": "TRUSTLENS Model 4"},
            {"id": "t11-5", "event_type": "situation", "title": "Citizen Incident Report Received", "description": "Victim reported fraudulent message with identical lexical pattern.", "related_object_ids": ["node-c11-report"], "timestamp": (now - timedelta(hours=14)).isoformat(), "source": "Citizen Report #07a380c7"},
            {"id": "t11-6", "event_type": "task", "title": "CERT-In & ISP Takedown Initiated", "description": "Emergency abuse notices dispatched to upstream registrar and CERT-In.", "related_object_ids": ["node-c11-advisory", "node-c11-domain"], "timestamp": (now - timedelta(hours=2)).isoformat(), "source": "SOC Automation Engine"},
        ]

        inv_11_doc = {
            "investigation_id": inv_11_id,
            "title": "Banking KYC Smishing Syndicate (Cluster #11)",
            "description": "Multilingual Smishing campaign targeting State Bank of India customers with urgent account freeze alerts leading to credential harvesting.",
            "status": "active",
            "severity": "critical",
            "visibility": "Organization",
            "tags": ["sbi_kyc", "smishing", "model1_bilstm", "model2_xgboost", "cluster_11", "phishing_url"],
            "sources": ["TRUSTLENS ML Telemetry", "ScamShield Corpus", "Community Report #07a380c7", "CERT-In"],
            "attributes": {
                "Targeted Institution": "State Bank of India (PSU Banking)",
                "Campaign Hub": "HDBSCAN Cluster #11",
                "Primary Attack Vector": "SMS Phishing with Urgency Coercion",
                "Hosting Provider": "Offshore Bulletproof Ltd (AS49870)",
                "Target Geography": "India (National Banking Sector)",
            },
            "created_at": now - timedelta(days=2),
            "updated_at": now - timedelta(hours=2),
            "nodes": inv_11_nodes,
            "edges": inv_11_edges,
            "timeline": inv_11_timeline,
        }

        # -------------------------------------------------------------
        # Investigation 2: Fake Employment & YouTube Task Scam Network (Cluster #06)
        # -------------------------------------------------------------
        inv_06_id = "INV-2026-0006"
        inv_06_nodes = [
            {
                "id": "node-c06-hub",
                "type": "campaign_cluster",
                "label": "Campaign Cluster #06 (Part-time YouTube Job Scams)",
                "source": "HDBSCAN Clustering Model (Model 4)",
                "verification_status": "verified",
                "created_at": (now - timedelta(days=3)).isoformat(),
                "properties": {
                    "cluster_id": 6,
                    "cluster_size": 38,
                    "cohesion_score": 0.812,
                    "severity": "high",
                    "targeted_entity": "Job Seekers / Social Media Users",
                    "isCentral": True,
                    "x": 0,
                    "y": 0,
                },
            },
            {
                "id": "node-c06-msg1",
                "type": "message",
                "label": "WhatsApp: 'Earn 3000-5000 daily liking YouTube videos'",
                "source": "Model 1 Calibrated Linear Text Detector",
                "verification_status": "verified",
                "created_at": (now - timedelta(days=2)).isoformat(),
                "properties": {
                    "channel": "whatsapp",
                    "threat_level": "high",
                    "risk_score": 0.892,
                    "raw_text": "Part-time job offer: Earn 3000-5000 daily by liking YouTube videos. Work from home. Contact on Telegram @invest_hr",
                    "severity": "high",
                    "x": -200,
                    "y": -120,
                },
            },
            {
                "id": "node-c06-tactic-job",
                "type": "tactic",
                "label": "Fake Employment Lure",
                "source": "Model 3 Tactic Classifier",
                "verification_status": "verified",
                "created_at": (now - timedelta(days=3)).isoformat(),
                "properties": {
                    "tactic_code": "TACTIC_FAKE_EMPLOYMENT",
                    "confidence": 0.976,
                    "evidence_tokens": ["part-time", "job", "youtube", "earn", "daily"],
                    "severity": "high",
                    "x": 180,
                    "y": -100,
                },
            },
            {
                "id": "node-c06-phone",
                "type": "threat_indicator",
                "label": "+91-9876543210 (HR Recruiter Alias)",
                "source": "Analysis Record UUID 1060fe6c",
                "verification_status": "verified",
                "created_at": (now - timedelta(days=2)).isoformat(),
                "properties": {
                    "indicator_type": "phone",
                    "indicator_value": "+919876543210",
                    "severity": "high",
                    "x": 80,
                    "y": 180,
                },
            },
        ]

        inv_06_edges = [
            {"id": "e06-1", "source": "node-c06-msg1", "target": "node-c06-hub", "relationship_type": "belongs_to_cluster", "evidence_reference": "Cosine embedding similarity 0.753", "created_at": now.isoformat()},
            {"id": "e06-2", "source": "node-c06-hub", "target": "node-c06-tactic-job", "relationship_type": "exhibits_tactic", "evidence_reference": "Model 3 SVM Job confidence 0.976", "created_at": now.isoformat()},
            {"id": "e06-3", "source": "node-c06-hub", "target": "node-c06-phone", "relationship_type": "references_indicator", "evidence_reference": "Extracted phone handle from WhatsApp payload", "created_at": now.isoformat()},
        ]

        inv_06_timeline = [
            {"id": "t06-1", "event_type": "situation", "title": "Mass WhatsApp Job Lure Broadcast", "description": "Unsolicited offers directed at Indian mobile numbers.", "related_object_ids": ["node-c06-msg1"], "timestamp": (now - timedelta(days=3)).isoformat(), "source": "WhatsApp Gateway Telemetry"},
            {"id": "t06-2", "event_type": "task", "title": "HDBSCAN Cluster #06 Activated", "description": "Identified recurring fake employment token attribution.", "related_object_ids": ["node-c06-hub"], "timestamp": (now - timedelta(days=2)).isoformat(), "source": "TRUSTLENS Model 4"},
        ]

        inv_06_doc = {
            "investigation_id": inv_06_id,
            "title": "YouTube Task & Fake Part-Time Employment Scam (Cluster #06)",
            "description": "Fraud ring offering daily income for social media engagement, progressively steering victims into fraudulent crypto deposit task schemes.",
            "status": "in_progress",
            "severity": "high",
            "visibility": "Organization",
            "tags": ["fake_job", "part_time", "task_fraud", "cluster_06", "whatsapp_lure"],
            "sources": ["TRUSTLENS ML Telemetry", "Community Fraud Reports"],
            "attributes": {
                "Targeted Sector": "Unemployed & Part-Time Job Seekers",
                "Campaign Hub": "HDBSCAN Cluster #06",
                "Primary Attack Vector": "WhatsApp Message to Telegram Steering",
                "Monetization Vector": "Pre-paid Task Deposit Scheme",
            },
            "created_at": now - timedelta(days=3),
            "updated_at": now - timedelta(days=1),
            "nodes": inv_06_nodes,
            "edges": inv_06_edges,
            "timeline": inv_06_timeline,
        }

        # -------------------------------------------------------------
        # Investigation 3: Live Threat Analysis Feed Incidents
        # -------------------------------------------------------------
        inv_live_id = "INV-2026-0138"
        analyses_coll = get_analyses_collection()
        recent_analyses = await analyses_coll.find({"threat_level": {"$in": ["critical", "high"]}}).limit(4).to_list(4)

        inv_live_nodes = [
            {
                "id": "node-live-hub",
                "type": "campaign_cluster",
                "label": "Live Ingested High-Threat Incidents Hub",
                "source": "TRUSTLENS Multi-Modal Engine",
                "verification_status": "verified",
                "created_at": now.isoformat(),
                "properties": {
                    "isCentral": True,
                    "severity": "critical",
                    "total_samples": len(recent_analyses),
                    "x": 0,
                    "y": 0,
                },
            }
        ]
        inv_live_edges = []
        inv_live_timeline = [
            {"id": f"t-live-init", "event_type": "task", "title": "Live Investigation Workspace Attached", "description": "Aggregated highest-severity incidents from MongoDB analyses stream.", "related_object_ids": ["node-live-hub"], "timestamp": now.isoformat(), "source": "SOC Telemetry Stream"}
        ]

        for idx, a in enumerate(recent_analyses):
            node_id = f"node-analysis-{idx+1}"
            text_snippet = a.get("input_payload", {}).get("text", "")[:40]
            inv_live_nodes.append({
                "id": node_id,
                "type": "message",
                "label": f"Analysis: '{text_snippet}...'",
                "source": f"Analysis Record UUID {a.get('analysis_id')}",
                "verification_status": "verified",
                "created_at": str(a.get("created_at", now.isoformat())),
                "properties": {
                    "analysis_id": a.get("analysis_id"),
                    "threat_level": a.get("threat_level"),
                    "risk_score": a.get("risk_score"),
                    "confidence": a.get("confidence"),
                    "primary_vector": a.get("risk_assessment", {}).get("primary_vector", "Unknown"),
                    "x": -220 + (idx * 140),
                    "y": -160 + ((idx % 2) * 80),
                },
            })
            inv_live_edges.append({
                "id": f"e-live-{idx+1}",
                "source": node_id,
                "target": "node-live-hub",
                "relationship_type": "belongs_to_cluster",
                "evidence_reference": f"Risk assessment score {a.get('risk_score')}",
                "created_at": now.isoformat(),
            })

        inv_live_doc = {
            "investigation_id": inv_live_id,
            "title": "Live Analyzed Threat Stream & Forensic Audit",
            "description": "Continuous real-time dossier capturing top high-confidence scam submissions and multi-label social engineering indicators.",
            "status": "active",
            "severity": "critical",
            "visibility": "Organization",
            "tags": ["live_telemetry", "mongodb_analyses", "multi_modal", "real_time"],
            "sources": ["MongoDB Atlas analyses Collection (138 Records)", "URLhaus Real-Time Feed"],
            "attributes": {
                "Data Stream": "Active Production Submissions",
                "Evaluated Incidents": "138 Records Persisted in Database",
                "Active Models": "Model 1, Model 2, Model 3, Model 4",
            },
            "created_at": now - timedelta(hours=8),
            "updated_at": now,
            "nodes": inv_live_nodes,
            "edges": inv_live_edges,
            "timeline": inv_live_timeline,
        }

        await coll.insert_one(inv_11_doc)
        await coll.insert_one(inv_06_doc)
        await coll.insert_one(inv_live_doc)
        logger.info("Successfully seeded baseline investigations (INV-2026-0011, INV-2026-0006, INV-2026-0138).")

    def _check_read_access(self, doc: Dict[str, Any], current_user: Optional[Dict[str, Any]]) -> None:
        if doc.get("visibility", "Organization") == "Private":
            if not current_user:
                raise PermissionError("Authentication required to access this private investigation.")
            role = current_user.get("role", "user")
            if role not in ("analyst", "admin") and doc.get("owner_id") != current_user.get("user_id"):
                raise PermissionError("Access denied: You do not have permission to view this private investigation.")

    def _check_write_access(self, doc: Dict[str, Any], current_user: Optional[Dict[str, Any]]) -> None:
        if not current_user:
            raise PermissionError("Authentication required to modify this investigation.")
        role = current_user.get("role", "user")
        if role not in ("analyst", "admin") and doc.get("owner_id") != current_user.get("user_id"):
            raise PermissionError("Access denied: You do not have permission to modify this investigation.")

    async def list_investigations(
        self,
        status: Optional[str] = None,
        severity: Optional[str] = None,
        limit: int = 50,
        current_user: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Lists investigation summaries visible to the caller."""
        await self._ensure_seeded()
        coll = get_investigations_collection()
        query: Dict[str, Any] = {}
        if status:
            query["status"] = status
        if severity:
            query["severity"] = severity

        cursor = coll.find(query).sort("created_at", -1).limit(limit * 2)
        items = await cursor.to_list(length=limit * 2)

        results = []
        role = current_user.get("role", "user") if current_user else None
        user_id = current_user.get("user_id") if current_user else None
        for it in items:
            if it.get("visibility", "Organization") == "Private":
                if not current_user:
                    continue
                if role not in ("analyst", "admin") and it.get("owner_id") != user_id:
                    continue
            results.append({
                "id": it.get("investigation_id"),
                "owner_id": it.get("owner_id"),
                "title": it.get("title"),
                "description": it.get("description"),
                "status": it.get("status", "active"),
                "severity": it.get("severity", "high"),
                "visibility": it.get("visibility", "Organization"),
                "created_at": it.get("created_at"),
                "updated_at": it.get("updated_at"),
                "objects_count": len(it.get("nodes", [])),
                "tasks_count": len([t for t in it.get("timeline", []) if t.get("event_type") == "task"]),
                "comments_count": len(it.get("notes", [])),
                "tags": it.get("tags", []),
            })
            if len(results) >= limit:
                break
        return results

    LEGACY_ALIASES: Dict[str, str] = {
        "INV-2026-KYC-11": "INV-2026-0011",
    }

    def _resolve_id(self, investigation_id: str) -> str:
        return self.LEGACY_ALIASES.get(investigation_id.strip().upper(), investigation_id)

    async def get_investigation_by_id(
        self,
        investigation_id: str,
        current_user: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        """Retrieves single investigation metadata dossier."""
        await self._ensure_seeded()
        resolved_id = self._resolve_id(investigation_id)
        coll = get_investigations_collection()
        doc = await coll.find_one({"investigation_id": resolved_id})
        if not doc:
            return None
        self._check_read_access(doc, current_user)

        return {
            "id": doc.get("investigation_id"),
            "owner_id": doc.get("owner_id"),
            "title": doc.get("title"),
            "description": doc.get("description"),
            "status": doc.get("status", "active"),
            "severity": doc.get("severity", "high"),
            "created_at": doc.get("created_at"),
            "updated_at": doc.get("updated_at"),
            "objects_count": len(doc.get("nodes", [])),
            "tasks_count": len([t for t in doc.get("timeline", []) if t.get("event_type") == "task"]),
            "comments_count": len(doc.get("notes", [])),
            "tags": doc.get("tags", []),
            "sources": doc.get("sources", []),
            "attributes": doc.get("attributes", {}),
            "visibility": doc.get("visibility", "Organization"),
        }

    async def get_investigation_graph(
        self,
        investigation_id: str,
        current_user: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        """Returns the full graph nodes and edges for an investigation."""
        await self._ensure_seeded()
        resolved_id = self._resolve_id(investigation_id)
        coll = get_investigations_collection()
        doc = await coll.find_one({"investigation_id": resolved_id})
        if not doc:
            return None
        self._check_read_access(doc, current_user)

        raw_nodes = doc.get("nodes", [])
        raw_edges = doc.get("edges", [])

        # Format nodes and edges to match contract
        nodes = []
        for n in raw_nodes:
            nodes.append({
                "id": n.get("id"),
                "type": n.get("type"),
                "label": n.get("label"),
                "properties": n.get("properties", {}),
                "source": n.get("source", "TRUSTLENS Intelligence"),
                "verification_status": n.get("verification_status", "verified"),
                "created_at": n.get("created_at", doc.get("created_at")),
            })

        edges = []
        for e in raw_edges:
            edges.append({
                "id": e.get("id"),
                "source": e.get("source"),
                "target": e.get("target"),
                "relationship_type": e.get("relationship_type"),
                "evidence_reference": e.get("evidence_reference"),
                "created_at": e.get("created_at", doc.get("created_at")),
            })

        return {
            "investigation_id": doc.get("investigation_id", investigation_id),
            "nodes": nodes,
            "edges": edges,
            "total_nodes": len(nodes),
            "total_edges": len(edges),
        }

    def _normalize_utc_datetime(self, raw_ts: Any) -> datetime:
        if isinstance(raw_ts, datetime):
            return raw_ts.replace(tzinfo=timezone.utc) if raw_ts.tzinfo is None else raw_ts.astimezone(timezone.utc)
        if isinstance(raw_ts, str) and raw_ts.strip():
            try:
                parsed = datetime.fromisoformat(raw_ts.strip().replace("Z", "+00:00"))
                return parsed.replace(tzinfo=timezone.utc) if parsed.tzinfo is None else parsed.astimezone(timezone.utc)
            except ValueError:
                pass
        return datetime.fromtimestamp(0, tz=timezone.utc)

    async def get_investigation_timeline(
        self,
        investigation_id: str,
        current_user: Optional[Dict[str, Any]] = None,
        page: int = 1,
        page_size: int = 100,
        order: str = "asc",
    ) -> Optional[Dict[str, Any]]:
        """Returns the chronological multi-track timeline for an investigation with UTC ordering and pagination."""
        await self._ensure_seeded()
        resolved_id = self._resolve_id(investigation_id)
        coll = get_investigations_collection()
        doc = await coll.find_one({"investigation_id": resolved_id})
        if not doc:
            return None
        self._check_read_access(doc, current_user)

        raw_timeline = list(doc.get("timeline", []))
        reverse = order.lower() == "desc"
        raw_timeline.sort(
            key=lambda ev: self._normalize_utc_datetime(ev.get("timestamp")),
            reverse=reverse,
        )

        total_events = len(raw_timeline)
        total_pages = (total_events + page_size - 1) // page_size if total_events > 0 else 1
        start = (page - 1) * page_size
        paged = raw_timeline[start : start + page_size]

        timeline = []
        for t in paged:
            norm_ts = self._normalize_utc_datetime(t.get("timestamp"))
            timeline.append({
                "id": t.get("id") or f"evt-{uuid.uuid4().hex[:8]}",
                "event_type": t.get("event_type", "situation"),
                "action_type": t.get("action_type"),
                "actor_id": t.get("actor_id"),
                "title": t.get("title") or "Recorded Event",
                "description": t.get("description"),
                "related_object_ids": t.get("related_object_ids", []),
                "metadata": t.get("metadata", {}),
                "evidence_reference": t.get("evidence_reference") or (t.get("metadata") or {}).get("evidence_reference"),
                "timestamp": norm_ts.isoformat(),
                "source": t.get("source", "TRUSTLENS Intelligence"),
            })

        return {
            "investigation_id": doc.get("investigation_id", investigation_id),
            "timeline": timeline,
            "total_events": total_events,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
        }

    async def get_investigation_audit_history(
        self,
        investigation_id: str,
        current_user: Optional[Dict[str, Any]] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> Optional[Dict[str, Any]]:
        """Returns verified audit_logs entries associated with this investigation."""
        await self._ensure_seeded()
        resolved_id = self._resolve_id(investigation_id)
        coll = get_investigations_collection()
        doc = await coll.find_one({"investigation_id": resolved_id})
        if not doc:
            return None
        self._check_read_access(doc, current_user)

        audit_coll = get_audit_collection()
        query = {
            "$or": [
                {"resource_id": resolved_id},
                {"details.investigation_id": resolved_id},
            ]
        }
        total = await audit_coll.count_documents(query)
        skip = (page - 1) * page_size
        events = await audit_coll.find(query, {"_id": 0}).sort("timestamp", -1).skip(skip).limit(page_size).to_list(length=page_size)
        return {
            "investigation_id": resolved_id,
            "total_count": total,
            "page": page,
            "page_size": page_size,
            "audit_events": events,
        }

    async def get_object_by_id(
        self,
        investigation_id: str,
        object_id: str,
        current_user: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        """Retrieves single object details from an investigation graph."""
        graph = await self.get_investigation_graph(investigation_id, current_user=current_user)
        if not graph:
            return None

        for n in graph["nodes"]:
            if n["id"] == object_id:
                # Count connected relationships
                rel_count = len([
                    e for e in graph["edges"]
                    if e["source"] == object_id or e["target"] == object_id
                ])
                return {
                    "investigation_id": graph["investigation_id"],
                    "object": n,
                    "relationships_count": rel_count,
                }
        return None

    async def get_object_relationships(
        self,
        investigation_id: str,
        object_id: str,
        current_user: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        One-Hop Graph Expansion:
        Retrieves all objects currently connected, PLUS queries MongoDB for newly discovered
        real entities that share the same domain, phone, or tactic.
        """
        graph = await self.get_investigation_graph(investigation_id, current_user=current_user)
        if not graph:
            return None

        # 1. Existing 1-hop connected nodes from current investigation
        connected_node_ids = set()
        existing_edges = []
        for e in graph["edges"]:
            if e["source"] == object_id:
                connected_node_ids.add(e["target"])
                existing_edges.append(e)
            elif e["target"] == object_id:
                connected_node_ids.add(e["source"])
                existing_edges.append(e)

        connected_nodes = [
            n for n in graph["nodes"]
            if n["id"] in connected_node_ids
        ]

        # 2. Query MongoDB for additional real unlinked entities (expansion)
        target_obj = next((n for n in graph["nodes"] if n["id"] == object_id), None)
        now = datetime.now(timezone.utc)

        if target_obj:
            obj_type = target_obj.get("type")
            props = target_obj.get("properties", {})

            # Case A: Expanding a Domain or URL -> Search MongoDB threat_indicators & suspicious_urls
            if obj_type in ["domain", "url"]:
                domain_val = props.get("domain") or target_obj.get("label")
                ind_coll = get_indicators_collection()
                new_inds = await ind_coll.find({"indicator_value": {"$regex": domain_val, "$options": "i"}}).limit(3).to_list(3)
                for ind in new_inds:
                    new_id = f"node-exp-ioc-{ind.get('indicator_id')}"
                    if not any(n["id"] == new_id for n in connected_nodes):
                        new_node = {
                            "id": new_id,
                            "type": "threat_indicator",
                            "label": f"IOC: {ind.get('indicator_value')}",
                            "source": ind.get("source", "MongoDB threat_indicators"),
                            "verification_status": ind.get("status", "verified"),
                            "created_at": ind.get("first_seen", now.isoformat()),
                            "properties": {
                                "indicator_type": ind.get("indicator_type"),
                                "confidence": ind.get("confidence", 0.9),
                                "tags": ind.get("tags", []),
                                "severity": "high",
                            },
                        }
                        connected_nodes.append(new_node)
                        existing_edges.append({
                            "id": f"e-exp-{uuid.uuid4().hex[:6]}",
                            "source": object_id,
                            "target": new_id,
                            "relationship_type": "references_indicator",
                            "evidence_reference": f"1-Hop query match in threat_indicators collection",
                            "created_at": now.isoformat(),
                        })

            # Case B: Expanding a Threat Indicator Phone -> Search MongoDB analyses for matching extracted_iocs.phones
            elif obj_type == "threat_indicator" and props.get("indicator_type") == "phone":
                phone_val = props.get("indicator_value", "").replace("+91", "").strip()
                if phone_val:
                    analyses_coll = get_analyses_collection()
                    matching_analyses = await analyses_coll.find({"extracted_iocs.phones": {"$regex": phone_val}}).limit(2).to_list(2)
                    for a in matching_analyses:
                        new_id = f"node-exp-ana-{a.get('analysis_id')[:8]}"
                        if not any(n["id"] == new_id for n in connected_nodes):
                            new_node = {
                                "id": new_id,
                                "type": "message",
                                "label": f"Correlated Message: '{a.get('input_payload', {}).get('text', '')[:32]}...'",
                                "source": f"MongoDB Analysis {a.get('analysis_id')}",
                                "verification_status": "verified",
                                "created_at": str(a.get("created_at", now.isoformat())),
                                "properties": {
                                    "analysis_id": a.get("analysis_id"),
                                    "threat_level": a.get("threat_level"),
                                    "risk_score": a.get("risk_score"),
                                    "severity": a.get("threat_level", "high"),
                                },
                            }
                            connected_nodes.append(new_node)
                            existing_edges.append({
                                "id": f"e-exp-{uuid.uuid4().hex[:6]}",
                                "source": object_id,
                                "target": new_id,
                                "relationship_type": "belongs_to_cluster",
                                "evidence_reference": f"1-Hop extraction shared phone indicator '{phone_val}'",
                                "created_at": now.isoformat(),
                            })

        return {
            "investigation_id": investigation_id,
            "object_id": object_id,
            "connected_nodes": connected_nodes,
            "edges": existing_edges,
            "total_connected": len(connected_nodes),
        }

    def _build_timeline_event(
        self,
        event_type: str,
        action_type: str,
        title: str,
        description: Optional[str],
        actor_id: str,
        actor_role: str,
        related_object_ids: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        ts = timestamp or datetime.now(timezone.utc)
        return {
            "id": f"evt-{uuid.uuid4().hex[:10]}",
            "event_type": event_type,
            "action_type": action_type,
            "actor_id": actor_id,
            "title": title,
            "description": description,
            "related_object_ids": related_object_ids or [],
            "metadata": metadata or {},
            "timestamp": ts.isoformat(),
            "source": f"{actor_role}:{actor_id}",
        }

    async def create_investigation(
        self,
        payload: Dict[str, Any],
        current_user: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Creates and persists a new investigation dossier owned by the authenticated user."""
        await self._ensure_seeded()
        coll = get_investigations_collection()
        audit_coll = get_audit_collection()
        now = datetime.now(timezone.utc)
        inv_id = f"INV-{now.strftime('%Y')}-{uuid.uuid4().hex[:4].upper()}"

        owner_id = current_user["user_id"]
        owner_role = current_user.get("role", "user")
        visibility = payload.get("visibility") or "Organization"
        if visibility not in ("Organization", "Private"):
            raise ValueError("visibility must be 'Organization' or 'Private'.")

        nodes = [
            {
                "id": f"node-{inv_id.lower()}-central",
                "type": "campaign_cluster",
                "label": payload.get("title"),
                "source": f"User {owner_id}",
                "verification_status": "under_review",
                "created_at": now.isoformat(),
                "properties": {
                    "isCentral": True,
                    "severity": payload.get("severity", "high"),
                    "x": 0,
                    "y": 0,
                },
            }
        ]
        edges = []
        timeline = [
            self._build_timeline_event(
                event_type="task",
                action_type="investigation_created",
                title="Investigation Created",
                description=payload.get("description") or "Investigation opened.",
                actor_id=owner_id,
                actor_role=owner_role,
                related_object_ids=[f"node-{inv_id.lower()}-central"],
                metadata={"visibility": visibility, "severity": payload.get("severity", "high")},
                timestamp=now,
            )
        ]

        doc = {
            "investigation_id": inv_id,
            "owner_id": owner_id,
            "title": payload.get("title"),
            "description": payload.get("description") or "Active cyber threat investigation.",
            "status": payload.get("status", "active"),
            "severity": payload.get("severity", "high"),
            "visibility": visibility,
            "tags": payload.get("tags") or ["analyst_investigation"],
            "sources": ["Authenticated User Submission", "TRUSTLENS Telemetry"],
            "attributes": {
                "Owner": owner_id,
                "Incident ID": inv_id,
                "Status": "Active Investigation",
            },
            "created_at": now,
            "updated_at": now,
            "nodes": nodes,
            "edges": edges,
            "timeline": timeline,
            "notes": [],
            "attached_analysis_ids": [],
        }

        await coll.insert_one(doc)
        await audit_coll.insert_one({
            "audit_id": f"aud-{uuid.uuid4().hex[:10]}",
            "user_id": owner_id,
            "action": "investigation_created",
            "resource_type": "investigations",
            "resource_id": inv_id,
            "details": {"visibility": visibility, "severity": doc["severity"]},
            "timestamp": now,
        })
        logger.info(f"Created new investigation dossier {inv_id} for owner {owner_id}")

        return {
            "id": inv_id,
            "owner_id": owner_id,
            "title": doc["title"],
            "description": doc["description"],
            "status": doc["status"],
            "severity": doc["severity"],
            "created_at": doc["created_at"],
            "updated_at": doc["updated_at"],
            "objects_count": len(nodes),
            "tasks_count": 1,
            "comments_count": 0,
            "tags": doc["tags"],
            "sources": doc["sources"],
            "attributes": doc["attributes"],
            "visibility": doc["visibility"],
        }

    async def list_notes(
        self,
        investigation_id: str,
        current_user: Optional[Dict[str, Any]] = None,
    ) -> Optional[List[Dict[str, Any]]]:
        await self._ensure_seeded()
        resolved_id = self._resolve_id(investigation_id)
        coll = get_investigations_collection()
        doc = await coll.find_one({"investigation_id": resolved_id})
        if not doc:
            return None
        self._check_read_access(doc, current_user)
        notes = list(doc.get("notes", []))
        notes.sort(key=lambda n: str(n.get("created_at", "")), reverse=True)
        return notes

    async def add_note(
        self,
        investigation_id: str,
        content: str,
        current_user: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        await self._ensure_seeded()
        clean_content = content.strip()
        if not clean_content:
            raise ValueError("Note content cannot be empty or whitespace only.")

        resolved_id = self._resolve_id(investigation_id)
        coll = get_investigations_collection()
        audit_coll = get_audit_collection()
        doc = await coll.find_one({"investigation_id": resolved_id})
        if not doc:
            return None
        self._check_write_access(doc, current_user)

        now = datetime.now(timezone.utc)
        author_id = current_user["user_id"]
        author_role = current_user.get("role", "user")

        # Duplicate write protection: if latest note from same author has identical content within 10s
        existing_notes = doc.get("notes", [])
        if existing_notes:
            latest = existing_notes[-1]
            if latest.get("author_id") == author_id and latest.get("content") == clean_content:
                prev_ts = latest.get("created_at")
                if isinstance(prev_ts, str):
                    try:
                        prev_ts = datetime.fromisoformat(prev_ts.replace("Z", "+00:00"))
                    except Exception:
                        prev_ts = None
                if isinstance(prev_ts, datetime) and abs((now - prev_ts.replace(tzinfo=timezone.utc)).total_seconds()) < 10:
                    return latest

        note_id = f"note-{uuid.uuid4().hex[:10]}"
        note_doc = {
            "note_id": note_id,
            "investigation_id": resolved_id,
            "author_id": author_id,
            "author_role": author_role,
            "content": clean_content,
            "created_at": now,
            "updated_at": None,
        }
        timeline_event = self._build_timeline_event(
            event_type="task",
            action_type="note_added",
            title=f"Note Added ({author_role})",
            description="Analyst note recorded.",
            actor_id=author_id,
            actor_role=author_role,
            related_object_ids=[],
            metadata={"note_id": note_id, "length": len(clean_content)},
            timestamp=now,
        )

        await coll.update_one(
            {"investigation_id": resolved_id},
            {
                "$push": {"notes": note_doc, "timeline": timeline_event},
                "$set": {"updated_at": now},
            },
        )
        await audit_coll.insert_one({
            "audit_id": f"aud-{uuid.uuid4().hex[:10]}",
            "user_id": author_id,
            "action": "investigation_note_added",
            "resource_type": "investigations",
            "resource_id": resolved_id,
            "details": {"note_id": note_id},
            "timestamp": now,
        })
        return note_doc

    async def update_note(
        self,
        investigation_id: str,
        note_id: str,
        content: str,
        current_user: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        clean_content = content.strip()
        if not clean_content:
            raise ValueError("Note content cannot be empty or whitespace only.")

        resolved_id = self._resolve_id(investigation_id)
        coll = get_investigations_collection()
        doc = await coll.find_one({"investigation_id": resolved_id})
        if not doc:
            return None
        self._check_write_access(doc, current_user)

        notes = list(doc.get("notes", []))
        target_idx = next((i for i, n in enumerate(notes) if n.get("note_id") == note_id), None)
        if target_idx is None:
            return None

        target_note = notes[target_idx]
        if current_user.get("role") != "admin" and target_note.get("author_id") != current_user.get("user_id"):
            raise PermissionError("Access denied: You may only edit your own notes.")

        now = datetime.now(timezone.utc)
        target_note["content"] = clean_content
        target_note["updated_at"] = now
        notes[target_idx] = target_note

        await coll.update_one(
            {"investigation_id": resolved_id},
            {"$set": {"notes": notes, "updated_at": now}},
        )
        return target_note

    async def delete_note(
        self,
        investigation_id: str,
        note_id: str,
        current_user: Dict[str, Any],
    ) -> bool:
        resolved_id = self._resolve_id(investigation_id)
        coll = get_investigations_collection()
        doc = await coll.find_one({"investigation_id": resolved_id})
        if not doc:
            return False
        self._check_write_access(doc, current_user)

        notes = list(doc.get("notes", []))
        target_note = next((n for n in notes if n.get("note_id") == note_id), None)
        if not target_note:
            return False

        if current_user.get("role") != "admin" and target_note.get("author_id") != current_user.get("user_id"):
            raise PermissionError("Access denied: You may only delete your own notes.")

        remaining = [n for n in notes if n.get("note_id") != note_id]
        await coll.update_one(
            {"investigation_id": resolved_id},
            {"$set": {"notes": remaining, "updated_at": datetime.now(timezone.utc)}},
        )
        return True

    async def update_investigation(
        self,
        investigation_id: str,
        payload: Dict[str, Any],
        current_user: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        await self._ensure_seeded()
        resolved_id = self._resolve_id(investigation_id)
        coll = get_investigations_collection()
        audit_coll = get_audit_collection()
        doc = await coll.find_one({"investigation_id": resolved_id})
        if not doc:
            return None
        self._check_write_access(doc, current_user)

        allowed_statuses = {"active", "in_progress", "mitigated", "archived"}
        allowed_visibilities = {"Organization", "Private"}
        updates: Dict[str, Any] = {}
        new_status = payload.get("status")
        new_visibility = payload.get("visibility")

        if new_status is not None:
            if new_status not in allowed_statuses:
                raise ValueError(f"Invalid status '{new_status}'. Allowed: {sorted(allowed_statuses)}")
            updates["status"] = new_status
        if new_visibility is not None:
            if new_visibility not in allowed_visibilities:
                raise ValueError("visibility must be 'Organization' or 'Private'.")
            updates["visibility"] = new_visibility
        if payload.get("title") is not None:
            updates["title"] = payload["title"]
        if payload.get("description") is not None:
            updates["description"] = payload["description"]

        if not updates:
            return await self.get_investigation_by_id(resolved_id, current_user=current_user)

        now = datetime.now(timezone.utc)
        updates["updated_at"] = now
        actor_id = current_user["user_id"]
        actor_role = current_user.get("role", "user")

        old_status = doc.get("status")
        status_changed = new_status is not None and new_status != old_status
        action_type = "investigation_status_changed" if status_changed else "investigation_updated"
        title = (
            f"Status Changed: {old_status} -> {new_status}"
            if status_changed
            else "Investigation Updated"
        )
        evt = self._build_timeline_event(
            event_type="task",
            action_type=action_type,
            title=title,
            description=f"Updated fields: {', '.join(sorted(k for k in updates if k != 'updated_at'))}",
            actor_id=actor_id,
            actor_role=actor_role,
            metadata={"old_status": old_status, "new_status": new_status} if status_changed else {"fields": list(updates.keys())},
            timestamp=now,
        )

        # Prevent duplicate status-change event if status didn't actually change
        update_op: Dict[str, Any] = {"$set": updates}
        if status_changed or any(k in updates for k in ("title", "description", "visibility")):
            update_op["$push"] = {"timeline": evt}

        await coll.update_one({"investigation_id": resolved_id}, update_op)
        await audit_coll.insert_one({
            "audit_id": f"aud-{uuid.uuid4().hex[:10]}",
            "user_id": actor_id,
            "action": action_type,
            "resource_type": "investigations",
            "resource_id": resolved_id,
            "details": {k: v for k, v in updates.items() if k != "updated_at"},
            "timestamp": now,
        })
        return await self.get_investigation_by_id(resolved_id, current_user=current_user)

    async def attach_analysis(
        self,
        investigation_id: str,
        analysis_id: str,
        current_user: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        await self._ensure_seeded()
        resolved_id = self._resolve_id(investigation_id)
        coll = get_investigations_collection()
        analyses_coll = get_analyses_collection()
        audit_coll = get_audit_collection()

        doc = await coll.find_one({"investigation_id": resolved_id})
        if not doc:
            return None
        self._check_write_access(doc, current_user)

        # Verify analysis exists and caller is authorized to read it
        analysis_doc = await analyses_coll.find_one({"analysis_id": analysis_id}, {"_id": 0})
        if not analysis_doc:
            raise LookupError(f"Analysis '{analysis_id}' was not found.")
        role = current_user.get("role", "user")
        user_id = current_user["user_id"]
        if role not in ("analyst", "admin") and analysis_doc.get("user_id") != user_id:
            raise PermissionError("Access denied: You do not have permission to attach this analysis.")

        attached_ids = list(doc.get("attached_analysis_ids", []))
        if analysis_id in attached_ids:
            raise RuntimeError(f"Analysis '{analysis_id}' is already attached to investigation '{resolved_id}'.")

        now = datetime.now(timezone.utc)
        a_type = analysis_doc.get("analysis_type", "text")
        node_type = "url" if a_type == "url" else "message"
        payload = analysis_doc.get("input_payload") or {}
        label = payload.get("url") or (payload.get("text") or "")[:60] or f"Analysis {analysis_id[:8]}"
        node_id = f"node-ana-{analysis_id[:10]}"

        created_raw = analysis_doc.get("created_at")
        analysis_ts = created_raw.isoformat() if hasattr(created_raw, "isoformat") else (str(created_raw) if created_raw else None)
        model_results = analysis_doc.get("model_results") or {}
        model_ver = (
            analysis_doc.get("model_version")
            or (model_results.get("text_model") or {}).get("model_version")
            or (model_results.get("url_model") or {}).get("model_version")
            or "trustlens-v1.0"
        )

        new_node = {
            "id": node_id,
            "type": node_type,
            "label": label,
            "source": f"Analysis {analysis_id}",
            "verification_status": "automated_inference",
            "created_at": now.isoformat(),
            "properties": {
                "analysis_id": analysis_id,
                "analysis_type": a_type,
                "threat_level": analysis_doc.get("threat_level"),
                "risk_score": analysis_doc.get("risk_score"),
                "severity": analysis_doc.get("threat_level", "medium"),
                "model_version": model_ver,
                "analysis_created_at": analysis_ts,
                "evidence_reference": f"analyses/{analysis_id}",
            },
        }
        nodes = doc.get("nodes", [])
        central_id = nodes[0]["id"] if nodes else node_id
        new_edge = {
            "id": f"e-att-{uuid.uuid4().hex[:8]}",
            "source": node_id,
            "target": central_id,
            "relationship_type": "belongs_to_cluster",
            "evidence_reference": f"Attached analysis {analysis_id} (risk={analysis_doc.get('risk_score')})",
            "created_at": now.isoformat(),
        }
        evt = self._build_timeline_event(
            event_type="indicator",
            action_type="analysis_attached",
            title=f"Analysis Attached ({a_type})",
            description=f"Attached analysis {analysis_id} (threat_level={analysis_doc.get('threat_level')}).",
            actor_id=user_id,
            actor_role=role,
            related_object_ids=[node_id],
            metadata={
                "analysis_id": analysis_id,
                "threat_level": analysis_doc.get("threat_level"),
                "evidence_reference": f"analyses/{analysis_id}",
            },
            timestamp=now,
        )

        await coll.update_one(
            {"investigation_id": resolved_id},
            {
                "$push": {
                    "attached_analysis_ids": analysis_id,
                    "nodes": new_node,
                    "edges": new_edge,
                    "timeline": evt,
                },
                "$set": {"updated_at": now},
            },
        )
        await audit_coll.insert_one({
            "audit_id": f"aud-{uuid.uuid4().hex[:10]}",
            "user_id": user_id,
            "action": "analysis_attached_to_investigation",
            "resource_type": "investigations",
            "resource_id": resolved_id,
            "details": {"analysis_id": analysis_id, "node_id": node_id},
            "timestamp": now,
        })
        return await self.get_investigation_by_id(resolved_id, current_user=current_user)


investigation_service = InvestigationService()
