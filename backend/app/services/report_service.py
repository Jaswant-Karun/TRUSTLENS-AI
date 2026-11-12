"""
TRUSTLENS AI - Community Scam Reporting Service
Handles crowd-sourced threat submissions and analyst review workflows.
"""

import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from fastapi import HTTPException, status

from backend.app.database.collections import (
    get_reports_collection,
    get_indicators_collection,
    get_audit_collection,
)
from backend.app.services.analysis_service import threat_analysis_service


class CommunityScamReportService:
    """Manages scam reporting and review lifecycle."""

    async def create_report(
        self,
        target_type: str,
        content: str,
        target_identifier: Optional[str] = None,
        description: Optional[str] = None,
        evidence_urls: Optional[List[str]] = None,
        reporter_user_id: Optional[str] = "anonymous",
        client_ip: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Creates a pending community scam report."""
        reports_coll = get_reports_collection()
        audit_coll = get_audit_collection()

        report_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)

        report_doc = {
            "report_id": report_id,
            "reporter_user_id": reporter_user_id or "anonymous",
            "target_type": target_type,
            "target_identifier": target_identifier,
            "content": content,
            "description": description,
            "evidence_urls": evidence_urls or [],
            "status": "pending",
            "reviewed_by": None,
            "review_notes": None,
            "assigned_tactics": [],
            "created_at": now,
            "reviewed_at": None,
        }

        await reports_coll.insert_one(report_doc)

        # Audit log
        await audit_coll.insert_one({
            "audit_id": str(uuid.uuid4()),
            "user_id": reporter_user_id or "anonymous",
            "action": "submit_scam_report",
            "resource_type": "report",
            "resource_id": report_id,
            "client_ip": client_ip,
            "timestamp": now,
            "details": {"target_type": target_type},
        })

        report_doc.pop("_id", None)
        return report_doc

    async def list_reports(
        self,
        status_filter: Optional[str] = None,
        target_type: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Dict[str, Any]:
        """Lists reports with optional status and target filtering."""
        reports_coll = get_reports_collection()
        query: Dict[str, Any] = {}
        if status_filter:
            query["status"] = status_filter
        if target_type:
            query["target_type"] = target_type

        skip = (page - 1) * page_size
        total_count = await reports_coll.count_documents(query)
        cursor = reports_coll.find(query).sort("created_at", -1).skip(skip).limit(page_size)
        items = await cursor.to_list(length=page_size)

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

    async def review_report(
        self,
        report_id: str,
        verdict: str,
        notes: Optional[str] = None,
        assigned_tactics: Optional[List[str]] = None,
        reviewer_id: str = "analyst",
        client_ip: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Analyst action: confirms scam or marks benign, extracting IOCs if confirmed."""
        reports_coll = get_reports_collection()
        indicators_coll = get_indicators_collection()
        audit_coll = get_audit_collection()

        report = await reports_coll.find_one({"report_id": report_id})
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Scam report '{report_id}' not found.",
            )

        now = datetime.now(timezone.utc)
        update_data = {
            "status": verdict,
            "reviewed_by": reviewer_id,
            "review_notes": notes,
            "assigned_tactics": assigned_tactics or [],
            "reviewed_at": now,
        }

        await reports_coll.update_one({"report_id": report_id}, {"$set": update_data})

        # If verified scam, automatically extract IOCs into threat_indicators collection
        if verdict == "verified_scam":
            iocs = threat_analysis_service.extract_iocs(report.get("content", ""))
            for u in iocs.get("urls", []):
                await indicators_coll.update_one(
                    {"value": u, "type": "url"},
                    {
                        "$set": {
                            "value": u,
                            "type": "url",
                            "severity": "high",
                            "threat_category": "phishing_url",
                            "last_seen": now,
                        },
                        "$inc": {"sighting_count": 1},
                        "$setOnInsert": {"indicator_id": str(uuid.uuid4()), "first_seen": now},
                    },
                    upsert=True,
                )
            for p in iocs.get("phones", []):
                await indicators_coll.update_one(
                    {"value": p, "type": "phone"},
                    {
                        "$set": {
                            "value": p,
                            "type": "phone",
                            "severity": "high",
                            "threat_category": "fraud_sender",
                            "last_seen": now,
                        },
                        "$inc": {"sighting_count": 1},
                        "$setOnInsert": {"indicator_id": str(uuid.uuid4()), "first_seen": now},
                    },
                    upsert=True,
                )

        # Audit log
        await audit_coll.insert_one({
            "audit_id": str(uuid.uuid4()),
            "user_id": reviewer_id,
            "action": "review_scam_report",
            "resource_type": "report",
            "resource_id": report_id,
            "client_ip": client_ip,
            "timestamp": now,
            "details": {"verdict": verdict, "notes": notes},
        })

        updated = await reports_coll.find_one({"report_id": report_id})
        updated.pop("_id", None)
        return updated


report_service = CommunityScamReportService()

