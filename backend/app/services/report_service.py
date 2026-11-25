"""
TRUSTLENS AI - Community Scam Reporting Service
Handles crowd-sourced threat submissions and analyst review workflows.
"""

import hashlib
import re
import time
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
from ml.preprocessing.text_preprocessor import text_preprocessor

VALID_REPORT_STATUSES = {"pending", "reviewed", "rejected", "confirmed", "verified_scam", "benign", "under_review", "inconclusive"}
CONFIRMED_STATUSES = {"confirmed", "verified_scam"}
PAN_REGEX = re.compile(r"\b[A-Z]{5}\d{4}[A-Z]\b")
AADHAAR_REGEX = re.compile(r"\b\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b")
CARD_REGEX = re.compile(r"\b(?:\d{4}[\s\-]?){3,4}\d{1,4}\b")


class CommunityScamReportService:
    """Manages scam reporting, PII redaction, deduplication, abuse prevention, and verification workflows."""

    SUBMISSION_LIMIT_PER_MIN = 10

    def __init__(self):
        self._rate_windows: Dict[str, List[float]] = {}

    def _check_abuse_rate_limit(self, key: str) -> None:
        now = time.monotonic()
        window = [ts for ts in self._rate_windows.get(key, []) if (now - ts) < 60.0]
        if len(window) >= self.SUBMISSION_LIMIT_PER_MIN:
            self._rate_windows[key] = window
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Report submission rate limit exceeded. Please try again later.",
            )
        window.append(now)
        self._rate_windows[key] = window

    @staticmethod
    def redact_sensitive_text(raw: Optional[str]) -> Optional[str]:
        if raw is None:
            return None
        masked = text_preprocessor.mask_pii(str(raw))
        masked = PAN_REGEX.sub("[PAN]", masked)
        masked = AADHAAR_REGEX.sub("[AADHAAR]", masked)
        masked = CARD_REGEX.sub("[CARD]", masked)
        return masked

    async def create_report(
        self,
        target_type: str,
        content: str,
        target_identifier: Optional[str] = None,
        description: Optional[str] = None,
        evidence_urls: Optional[List[str]] = None,
        reporter_user_id: Optional[str] = "anonymous",
        client_ip: Optional[str] = None,
        redact_sensitive_content: bool = True,
        allow_public_listing: bool = False,
    ) -> Dict[str, Any]:
        """Creates a pending community scam report with PII redaction, abuse rate limiting, and deduplication."""
        rate_key = f"{client_ip or 'unknown'}:{reporter_user_id or 'anonymous'}"
        self._check_abuse_rate_limit(rate_key)

        reports_coll = get_reports_collection()
        audit_coll = get_audit_collection()

        clean_content = self.redact_sensitive_text(content) if redact_sensitive_content else content
        clean_desc = self.redact_sensitive_text(description) if redact_sensitive_content else description
        clean_ident = self.redact_sensitive_text(target_identifier) if (redact_sensitive_content and target_identifier) else target_identifier
        norm_hash = hashlib.sha256(
            f"{target_type.lower()}:{' '.join((clean_content or '').lower().split())}".encode("utf-8")
        ).hexdigest()

        # Duplicate detection
        existing = await reports_coll.find_one({"content_sha256": norm_hash})
        if existing:
            now = datetime.now(timezone.utc)
            new_dup_count = int(existing.get("duplicate_count", 1)) + 1
            await reports_coll.update_one(
                {"report_id": existing["report_id"]},
                {"$set": {"duplicate_count": new_dup_count, "last_reported_at": now}},
            )
            existing["duplicate_count"] = new_dup_count
            existing["is_duplicate"] = True
            existing.pop("_id", None)
            return existing

        report_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)

        report_doc = {
            "report_id": report_id,
            "reporter_user_id": reporter_user_id or "anonymous",
            "target_type": target_type,
            "target_identifier": clean_ident,
            "content": clean_content,
            "description": clean_desc,
            "evidence_urls": evidence_urls or [],
            "content_sha256": norm_hash,
            "duplicate_count": 1,
            "is_duplicate": False,
            "pii_redacted": bool(redact_sensitive_content),
            "allow_public_listing": bool(allow_public_listing),
            "status": "pending",
            "eligible_for_threat_intel": False,
            "eligible_for_ml_training": False,
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
            # Privacy control: never expose reporter identity in listings
            item["reporter_user_id"] = "redacted"

        total_pages = (total_count + page_size - 1) // page_size if total_count > 0 else 1

        return {
            "items": items,
            "total_count": total_count,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
        }

    async def get_verified_training_candidates(self, limit: int = 200) -> List[Dict[str, Any]]:
        """Returns ONLY confirmed/verified_scam reports with PII redacted for ML training review."""
        reports_coll = get_reports_collection()
        items = await reports_coll.find({"eligible_for_ml_training": True}).sort("reviewed_at", -1).limit(limit).to_list(length=limit)
        for item in items:
            item.pop("_id", None)
            item["reporter_user_id"] = "redacted"
        return items

    async def review_report(
        self,
        report_id: str,
        verdict: str,
        notes: Optional[str] = None,
        assigned_tactics: Optional[List[str]] = None,
        reviewer_id: str = "analyst",
        client_ip: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Analyst moderation: supports pending, reviewed, rejected, confirmed (and legacy aliases)."""
        if verdict not in VALID_REPORT_STATUSES:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Invalid status '{verdict}'.")

        reports_coll = get_reports_collection()
        indicators_coll = get_indicators_collection()
        audit_coll = get_audit_collection()

        report = await reports_coll.find_one({"report_id": report_id})
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Scam report '{report_id}' not found.",
            )

        is_confirmed = verdict in CONFIRMED_STATUSES
        now = datetime.now(timezone.utc)
        update_data = {
            "status": verdict,
            "eligible_for_threat_intel": is_confirmed,
            "eligible_for_ml_training": is_confirmed,
            "reviewed_by": reviewer_id,
            "review_notes": notes,
            "assigned_tactics": assigned_tactics or [],
            "reviewed_at": now,
        }

        await reports_coll.update_one({"report_id": report_id}, {"$set": update_data})

        # ONLY confirmed / verified_scam reports may populate threat_indicators
        if is_confirmed:
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
                            "source": "Community Report (Analyst Confirmed)",
                            "verification_status": "verified",
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

