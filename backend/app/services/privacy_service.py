"""
TRUSTLENS AI - Privacy-First Data Protection Service
Defines and enforces:
- Data collection purposes & minimization
- Granular, revocable user consent mechanisms
- Data retention policies & dry-run/enforced purging
- Field-level symmetric encryption (Fernet) & PII redaction
- Access/audit log retrieval & DPDP/GDPR governance metadata
"""

import base64
import hashlib
import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List, Optional

from cryptography.fernet import Fernet

from backend.app.config.settings import settings
from backend.app.database.collections import get_analyses_collection, get_audit_collection, get_reports_collection
from backend.app.database.manager import db_manager
from backend.app.services.report_service import CommunityScamReportService

COLL_USER_CONSENTS = "user_consents"

DATA_COLLECTION_PURPOSES: List[Dict[str, Any]] = [
    {
        "purpose_id": "fraud_detection_inference",
        "title": "Digital Fraud & Phishing Analysis",
        "description": "Analyze user-submitted text, URLs, or screenshots to assess scam/phishing risk.",
        "data_categories": ["submitted_text_sanitized", "submitted_url", "ocr_extracted_text"],
        "minimization": "PII (phones, emails, OTPs, PAN, Aadhaar) is masked prior to ML persistence.",
    },
    {
        "purpose_id": "investigation_case_management",
        "title": "Threat Investigation & Correlation",
        "description": "Allow authenticated analysts/users to organize analyses, notes, and IOCs into private or org cases.",
        "data_categories": ["investigation_metadata", "analyst_notes", "evidence_references"],
        "minimization": "Private investigations are strictly owner-isolated.",
    },
    {
        "purpose_id": "community_threat_reporting",
        "title": "Community Scam Reporting & Moderation",
        "description": "Collect user-submitted fraud reports for human analyst moderation.",
        "data_categories": ["redacted_report_content", "target_type", "moderation_status"],
        "minimization": "Reporter identity is redacted in public listings; unverified reports never enter ML training.",
    },
    {
        "purpose_id": "account_authentication",
        "title": "Account Authentication & Session Security",
        "description": "Authenticate users, enforce RBAC, and support session revocation and account deletion.",
        "data_categories": ["email", "bcrypt_password_hash", "role", "session_revocation_timestamp"],
        "minimization": "Passwords hashed with bcrypt; JWTs support server-side session revocation.",
    },
    {
        "purpose_id": "security_audit_logging",
        "title": "Security & Privacy Access Auditing",
        "description": "Record authentication, data export, consent changes, and deletion events.",
        "data_categories": ["user_id", "action", "resource_type", "timestamp"],
        "minimization": "Sensitive payloads and secrets are never written to audit logs.",
    },
]

DATA_RETENTION_POLICY: Dict[str, Dict[str, Any]] = {
    "analyses": {"retention_days": 90, "policy": "User-submitted analyses retained 90 days unless deleted earlier by user."},
    "ioc_enrichment_cache": {"retention_days": 1, "policy": "Cached enrichment expires after 3600 seconds (<= 1 day)."},
    "scam_reports_unverified": {"retention_days": 90, "policy": "Pending/rejected community reports purged after 90 days."},
    "audit_logs": {"retention_days": 365, "policy": "Security and privacy audit logs retained 365 days."},
    "user_accounts": {"retention_days": None, "policy": "Retained while active; erased upon DELETE /api/v1/auth/account."},
}


class PrivacyProtectionService:
    """Implements consent, retention, field-level encryption, redaction, and privacy governance."""

    @staticmethod
    def _get_fernet() -> Fernet:
        key_material = hashlib.sha256(settings.SECRET_KEY.encode("utf-8")).digest()
        return Fernet(base64.urlsafe_b64encode(key_material))

    def encrypt_sensitive_field(self, plaintext: str) -> str:
        return self._get_fernet().encrypt(plaintext.encode("utf-8")).decode("utf-8")

    def decrypt_sensitive_field(self, ciphertext: str) -> str:
        return self._get_fernet().decrypt(ciphertext.encode("utf-8")).decode("utf-8")

    @staticmethod
    def redact_pii(text: str) -> str:
        return CommunityScamReportService.redact_sensitive_text(text) or ""

    async def get_consent(self, user_id: str) -> Dict[str, Any]:
        coll = db_manager.get_collection(COLL_USER_CONSENTS)
        doc = await coll.find_one({"user_id": user_id})
        if not doc:
            return {
                "user_id": user_id,
                "external_ioc_enrichment": False,
                "community_report_public_listing": False,
                "product_telemetry": False,
                "security_notifications": True,
                "updated_at_utc": None,
            }
        doc.pop("_id", None)
        return doc

    async def update_consent(self, user_id: str, preferences: Dict[str, bool]) -> Dict[str, Any]:
        coll = db_manager.get_collection(COLL_USER_CONSENTS)
        audit_coll = get_audit_collection()
        now_dt = datetime.now(timezone.utc)
        current = await self.get_consent(user_id)

        updated = {
            "user_id": user_id,
            "external_ioc_enrichment": bool(preferences.get("external_ioc_enrichment", current["external_ioc_enrichment"])),
            "community_report_public_listing": bool(preferences.get("community_report_public_listing", current["community_report_public_listing"])),
            "product_telemetry": bool(preferences.get("product_telemetry", current["product_telemetry"])),
            "security_notifications": bool(preferences.get("security_notifications", current["security_notifications"])),
            "updated_at_utc": now_dt.isoformat(),
        }

        existing = await coll.find_one({"user_id": user_id})
        if existing:
            await coll.update_one({"user_id": user_id}, {"$set": updated})
        else:
            await coll.insert_one(dict(updated))

        await audit_coll.insert_one({
            "audit_id": str(uuid.uuid4()),
            "user_id": user_id,
            "action": "update_privacy_consent",
            "resource_type": "user_consent",
            "resource_id": user_id,
            "timestamp": now_dt,
            "details": {k: updated[k] for k in ("external_ioc_enrichment", "community_report_public_listing", "product_telemetry", "security_notifications")},
        })
        return updated

    async def get_user_access_logs(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        audit_coll = get_audit_collection()
        logs = await audit_coll.find({"user_id": user_id}, {"_id": 0}).sort("timestamp", -1).limit(limit).to_list(length=limit)
        return logs

    async def enforce_retention_policy(self, dry_run: bool = True) -> Dict[str, Any]:
        """Identifies (and optionally purges) expired analyses and unverified reports per retention policy."""
        now_dt = datetime.now(timezone.utc)
        cutoff_analyses = now_dt - timedelta(days=DATA_RETENTION_POLICY["analyses"]["retention_days"])
        cutoff_reports = now_dt - timedelta(days=DATA_RETENTION_POLICY["scam_reports_unverified"]["retention_days"])

        an_coll = get_analyses_collection()
        rep_coll = get_reports_collection()

        exp_analyses = await an_coll.count_documents({"created_at": {"$lt": cutoff_analyses}})
        exp_reports = await rep_coll.count_documents({
            "created_at": {"$lt": cutoff_reports},
            "status": {"$in": ["pending", "rejected"]},
        })

        purged_analyses = 0
        purged_reports = 0
        if not dry_run:
            if exp_analyses:
                res_a = await an_coll.delete_many({"created_at": {"$lt": cutoff_analyses}})
                purged_analyses = getattr(res_a, "deleted_count", 0)
            if exp_reports:
                res_r = await rep_coll.delete_many({
                    "created_at": {"$lt": cutoff_reports},
                    "status": {"$in": ["pending", "rejected"]},
                })
                purged_reports = getattr(res_r, "deleted_count", 0)

        return {
            "dry_run": dry_run,
            "evaluated_at_utc": now_dt.isoformat(),
            "expired_analyses_found": exp_analyses,
            "expired_unverified_reports_found": exp_reports,
            "purged_analyses": purged_analyses,
            "purged_reports": purged_reports,
        }

    def get_privacy_governance_summary(self) -> Dict[str, Any]:
        return {
            "policy_version": "1.0.0",
            "data_collection_purposes": DATA_COLLECTION_PURPOSES,
            "data_retention_policy": DATA_RETENTION_POLICY,
            "user_rights_endpoints": {
                "consent_management": "GET/PUT /api/v1/privacy/consent",
                "personal_data_export": "GET /api/v1/auth/export-data",
                "account_deletion": "DELETE /api/v1/auth/account",
                "analysis_deletion": "DELETE /api/v1/analyses/{analysis_id}",
                "access_logs": "GET /api/v1/privacy/access-logs",
            },
            "technical_safeguards": {
                "pii_redaction": "Automated masking of phones, emails, OTPs, UPIs, PAN, Aadhaar, and cards.",
                "encryption_in_transit": "TLS/HTTPS + HSTS headers.",
                "encryption_at_rest": "Fernet AES-128-CBC+HMAC-SHA256 field-level encryption helper + bcrypt password hashing.",
            },
            "jurisdictional_assessment": {
                "india_dpdp_act_2023": {
                    "applicable_when": "Processing digital personal data of Data Principals in India.",
                    "technical_alignment": "Explicit purpose limitation, granular opt-in consent, data erasure (/auth/account, /analyses/{id}), and PII minimization.",
                },
                "eu_gdpr": {
                    "applicable_when": "Offering services to or monitoring individuals in the EEA/UK.",
                    "technical_alignment": "Right of access & portability (/auth/export-data), right to erasure, consent withdrawal, and retention limits.",
                },
                "regulatory_compliance_claim": False,
                "verification_notice": "Technical privacy controls are implemented; formal regulatory compliance requires independent legal and DPO verification.",
            },
        }


privacy_service = PrivacyProtectionService()
