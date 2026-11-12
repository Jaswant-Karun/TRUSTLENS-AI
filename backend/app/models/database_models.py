"""
TRUSTLENS AI - MongoDB Document Schemas & Models
Defines complete data models for all 10 MongoDB Atlas collections.
"""

from typing import List, Optional, Dict, Any, Union
from datetime import datetime, timezone
from pydantic import BaseModel, Field


def get_utc_now() -> datetime:
    return datetime.now(timezone.utc)


# 1. Users Collection
class UserDocument(BaseModel):
    model_config = {"extra": "allow"}

    user_id: str
    email: str
    hashed_password: str
    full_name: str
    role: str = "user"  # "user" | "analyst" | "admin"
    is_active: bool = True
    created_at: datetime = Field(default_factory=get_utc_now)
    last_login: Optional[datetime] = None


# 2. Analyses Collection
class AnalysisDocument(BaseModel):
    model_config = {"extra": "allow"}

    analysis_id: str
    user_id: Optional[str] = "anonymous"
    analysis_type: str = "text"  # "text" | "url" | "image" | "comprehensive"
    input_payload: Dict[str, Any]
    threat_level: str = "clean"  # "clean" | "low" | "medium" | "high" | "critical" | "inconclusive"
    confidence: float = 0.0
    risk_score: float = 0.0
    risk_assessment: Dict[str, Any]
    model_results: Dict[str, Any]
    extracted_iocs: Dict[str, List[str]] = Field(default_factory=dict)
    explainability: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=get_utc_now)


# 3. Suspicious URLs Collection
class SuspiciousURLDocument(BaseModel):
    model_config = {"extra": "allow"}

    url: str
    domain: str
    risk_score: float
    is_phishing: bool
    features: Dict[str, Any]
    shap_impacts: List[Dict[str, Any]] = Field(default_factory=list)
    hit_count: int = 1
    first_seen: datetime = Field(default_factory=get_utc_now)
    last_seen: datetime = Field(default_factory=get_utc_now)
    status: str = "active"  # "active" | "mitigated" | "whitelisted"


# 4. Scam Reports Collection
class ScamReportDocument(BaseModel):
    model_config = {"extra": "allow"}

    report_id: str
    reporter_user_id: Optional[str] = "anonymous"
    reporter_contact: Optional[str] = None
    target_type: str  # "sms" | "whatsapp" | "url" | "call" | "upi" | "email"
    target_identifier: Optional[str] = None
    content: str
    description: Optional[str] = None
    evidence_urls: List[str] = Field(default_factory=list)
    status: str = "pending"  # "pending" | "under_review" | "verified_scam" | "benign"
    reviewed_by: Optional[str] = None
    review_notes: Optional[str] = None
    assigned_tactics: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=get_utc_now)
    reviewed_at: Optional[datetime] = None


# 5. Scam Campaigns Collection
class ScamCampaignDocument(BaseModel):
    model_config = {"extra": "allow"}

    campaign_id: str
    campaign_name: str
    targeted_entity: str
    size: int = 1
    cohesion_score: float = 0.0
    status: str = "active"  # "active" | "dormant" | "mitigated"
    primary_tactics: List[str] = Field(default_factory=list)
    exemplar_text: str = ""
    shared_iocs: Dict[str, List[str]] = Field(default_factory=dict)
    discovered_at: datetime = Field(default_factory=get_utc_now)
    last_activity: datetime = Field(default_factory=get_utc_now)


# 6. Threat Indicators Collection
class ThreatIndicatorDocument(BaseModel):
    model_config = {"extra": "allow"}

    indicator_id: str
    type: str  # "url" | "domain" | "phone" | "upi" | "ip"
    value: str
    threat_category: str = "fraud"
    severity: str = "medium"  # "low" | "medium" | "high" | "critical"
    associated_campaigns: List[str] = Field(default_factory=list)
    sighting_count: int = 1
    first_seen: datetime = Field(default_factory=get_utc_now)
    last_seen: datetime = Field(default_factory=get_utc_now)


# 7. Model Registry Collection
class ModelRegistryDocument(BaseModel):
    model_config = {"extra": "allow"}

    model_id: str
    display_name: str
    semantic_version: str = "v1.0.0"
    status: str = "production_verified"
    algorithm: str
    evaluation_summary: Dict[str, Any]
    training_parameters: Dict[str, Any]
    hardware_requirements: Dict[str, Any]
    artifacts: List[Dict[str, Any]]
    updated_at: datetime = Field(default_factory=get_utc_now)


# 8. Model Evaluations Collection
class ModelEvaluationDocument(BaseModel):
    model_config = {"extra": "allow"}

    evaluation_id: str
    evaluation_date: str
    test_datasets: List[str]
    model_results: Dict[str, Any]
    auditor: str
    verdict: str
    created_at: datetime = Field(default_factory=get_utc_now)


# 9. Automation Logs Collection
class AutomationLogDocument(BaseModel):
    model_config = {"extra": "allow"}

    log_id: str
    workflow_name: str
    trigger_event: str
    status: str = "success"  # "success" | "failed"
    payload_summary: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    duration_ms: float = 0.0
    executed_at: datetime = Field(default_factory=get_utc_now)


# 10. Audit Logs Collection
class AuditLogDocument(BaseModel):
    model_config = {"extra": "allow"}

    audit_id: str
    user_id: Optional[str] = "system"
    action: str  # "register" | "login" | "scan_text" | "scan_url" | "scan_image" | "review_report"
    resource_type: str
    resource_id: Optional[str] = None
    client_ip: Optional[str] = None
    user_agent: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=get_utc_now)
