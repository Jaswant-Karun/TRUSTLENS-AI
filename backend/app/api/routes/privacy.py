"""
TRUSTLENS AI - Privacy & Data Protection Endpoints
GET  /api/v1/privacy/policy
GET  /api/v1/privacy/consent
PUT  /api/v1/privacy/consent
GET  /api/v1/privacy/access-logs
POST /api/v1/privacy/retention/preview
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from backend.app.security.dependencies import get_current_user, require_analyst_or_admin
from backend.app.services.privacy_service import privacy_service

router = APIRouter(prefix="/privacy", tags=["Privacy & Data Protection"])


class ConsentUpdateRequest(BaseModel):
    external_ioc_enrichment: Optional[bool] = None
    community_report_public_listing: Optional[bool] = None
    product_telemetry: Optional[bool] = None
    security_notifications: Optional[bool] = None


@router.get("/policy", response_model=Dict[str, Any])
async def get_privacy_policy_and_governance():
    """Returns data collection purposes, retention periods, user-rights endpoints, and DPDP/GDPR assessment."""
    return privacy_service.get_privacy_governance_summary()


@router.get("/transparency", response_model=Dict[str, Any])
async def get_trust_and_transparency_framework():
    """Returns the TRUSTLENS AI Trust & Transparency Framework (languages, limitations, provenance, uncertainty, rights, contact)."""
    return {
        "framework_version": "1.0.0",
        "supported_languages": {
            "evaluated": ["English", "Hindi", "Hinglish"],
            "unsupported_unverified": ["Tamil", "Bengali"],
            "note": "Languages with 0 verified training/evaluation samples are never claimed as supported.",
        },
        "model_limitations": {
            "model_1_text": "Word+Char TF-IDF + Calibrated LinearSVC (v2.1): evaluated on English, Hindi, and Hinglish only; Tamil/Bengali unsupported (0 samples).",
            "model_2_url": "Zero-hop XGBoost (v2.2): lexical, brand, and homograph profiling only; never visits target URLs and does not prove server safety or malice.",
            "model_3_tactics": "OvR Calibrated LinearSVC (v2.3): supports 9 verified tactics; 'fake_investment' is Blocked due to 0 verified ground-truth labels.",
            "model_4_campaign": "Multilingual MiniLM-L12-v2 + HDBSCAN (v2.4): unsupervised similarity clustering only; does not prove identical criminal origin.",
        },
        "dataset_provenance": [
            {"id": "scamshield", "source": "Hugging Face (sidzzz07/scamshield-dataset)", "license": "MIT", "records": 85680},
            {"id": "sms_phishing", "source": "Mendeley Data (10.17632/f45bkkt8pr.1)", "license": "CC BY 4.0", "records": 5971},
            {"id": "legitphish", "source": "Mendeley Data (10.17632/hx4m73v2sf.2)", "license": "CC BY 4.0", "records": 101219},
            {"id": "uci_sms_spam", "source": "UCI ML Repository (id=228)", "license": "CC BY 4.0", "records": 5574},
            {"id": "phishtank_feed", "source": "PhishTank / Cisco Talos", "license": "PhishTank Data Feeds ToU", "records": "dynamic"},
            {"id": "cisa_kev", "source": "U.S. CISA KEV", "license": "CC0 1.0 Public Domain", "records": "dynamic"},
            {"id": "urlhaus_community", "source": "abuse.ch URLhaus", "license": "Community Fair-Use (Commercial Blocked)", "records": "dynamic"},
        ],
        "prediction_uncertainty": {
            "calibrated_models": ["trustlens-model1-v2.1 (Platt)", "trustlens-model3-calibrated-linear-v2.3 (Platt)"],
            "uncalibrated_signals": ["trustlens-model2-xgboost-v2.2 (GBDT + policy guard)", "hdbscan-v2.4 (cosine similarity)"],
            "inconclusive_policy": "Inputs with < 2 tokens and no URL return 'inconclusive' rather than guessing.",
        },
        "data_handling_practices": {
            "pii_redaction": "Phones, emails, OTPs, UPIs, PAN, Aadhaar, and cards masked prior to persistence.",
            "retention": "90 days for analyses and unverified reports; 365 days for audit logs.",
            "no_auto_training_from_reports": True,
        },
        "reporting_and_moderation": {
            "statuses": ["pending", "reviewed", "rejected", "confirmed"],
            "gating": "Only analyst-confirmed reports influence threat_indicators or training candidate pools.",
        },
        "human_review_requirements": [
            "Model promotion to Production requires explicit human approval.",
            "Community reports require analyst confirmation before entering intelligence feeds.",
            "User FP/FN feedback requires human review before becoming verified ground truth.",
            "High-uncertainty or inconclusive assessments are flagged for human review.",
        ],
        "user_rights": {
            "consent": "GET/PUT /api/v1/privacy/consent",
            "export": "GET /api/v1/auth/export-data",
            "delete_analysis": "DELETE /api/v1/analyses/{analysis_id}",
            "delete_account": "DELETE /api/v1/auth/account",
            "access_logs": "GET /api/v1/privacy/access-logs",
        },
        "security_contact": {
            "email": "security@trustlens.ai",
            "disclosure_policy": "Report security vulnerabilities responsibly via security@trustlens.ai.",
        },
        "disclaimers": [
            "TRUSTLENS AI is a decision-support tool and does not guarantee universal fraud detection or 100% accuracy.",
            "Automated risk scores and similarity clusters do not constitute legal proof of malicious intent or shared criminal origin.",
        ],
    }


@router.get("/consent", response_model=Dict[str, Any])
async def get_my_consent(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Retrieves the authenticated user's granular consent preferences."""
    return await privacy_service.get_consent(current_user["user_id"])


@router.put("/consent", response_model=Dict[str, Any])
async def update_my_consent(
    payload: ConsentUpdateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Updates granular consent preferences with audit logging."""
    prefs = {k: v for k, v in payload.model_dump().items() if v is not None}
    return await privacy_service.update_consent(current_user["user_id"], prefs)


@router.get("/access-logs", response_model=Dict[str, Any])
async def get_my_access_logs(
    limit: int = Query(default=50, ge=1, le=200),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Returns access and privacy audit logs for the authenticated user."""
    logs = await privacy_service.get_user_access_logs(current_user["user_id"], limit=limit)
    return {"total": len(logs), "logs": logs}


@router.post("/retention/preview", response_model=Dict[str, Any])
async def preview_retention_policy(
    reviewer: Dict[str, Any] = Depends(require_analyst_or_admin),
):
    """Dry-run evaluation of expired analyses and unverified reports under retention policy."""
    return await privacy_service.enforce_retention_policy(dry_run=True)
