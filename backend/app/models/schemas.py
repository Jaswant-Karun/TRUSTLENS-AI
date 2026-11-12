"""
TRUSTLENS AI - Pydantic Request & Response Schemas
Type-safe request validation and response serialisation models.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime, timezone


def get_utc_now() -> datetime:
    return datetime.now(timezone.utc)


# --- HEALTH & STATUS ---

class SystemHealthResponse(BaseModel):
    status: str = Field(..., json_schema_extra={"example": "healthy"})
    app_name: str
    version: str
    database_connected: bool
    models_loaded: Dict[str, bool]
    timestamp: datetime = Field(default_factory=get_utc_now)


# --- TEXT SCAM CLASSIFICATION (ENGINE 1) ---

class TextScanRequest(BaseModel):
    text: str = Field(..., min_length=2, max_length=5000, description="Message text (SMS, WhatsApp, email) to scan")
    sender: Optional[str] = Field(None, description="Sender ID or phone number if available")
    channel: str = Field("sms", description="Communication channel: sms, email, whatsapp, etc.")


class TextScanResponse(BaseModel):
    text: str
    predicted_label: str = Field(..., description="legitimate | spam | phishing | smishing | scam")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Calibrated confidence score")
    is_threat: bool
    detected_language: str
    model_version: str
    explanation: Optional[str] = None
    processed_at: datetime = Field(default_factory=get_utc_now)


# --- PHISHING URL DETECTION (ENGINE 2) ---

class URLScanRequest(BaseModel):
    url: str = Field(..., min_length=4, max_length=2048, description="URL to analyze")


class LexicalFeatures(BaseModel):
    model_config = {"extra": "allow"}

    url_length: int
    domain_length: int = 0
    path_length: int = 0
    count_dots: int = 0
    count_hyphens: int = 0
    count_subdomains: int = 0
    has_ip_address: Union[bool, int] = False
    has_at_symbol: bool = False
    has_double_slash: bool = False
    has_suspicious_keywords: bool = False
    url_entropy: float = 0.0
    domain_entropy: float = 0.0
    digit_ratio: float = 0.0
    special_char_ratio: float = 0.0
    is_suspicious_tld: bool = False
    is_shortened: bool = False
    count_params: int = 0


class URLScanResponse(BaseModel):
    url: str
    predicted_label: str = Field(..., description="legitimate | phishing")
    risk_score: float = Field(..., ge=0.0, le=1.0, description="Phishing risk score (0.0 to 1.0)")
    is_phishing: bool
    features: LexicalFeatures
    top_risk_factors: List[str] = Field(default_factory=list)
    model_version: str
    processed_at: datetime = Field(default_factory=get_utc_now)


# --- SCAM TACTIC DETECTION (ENGINE 3) ---

class TacticScanRequest(BaseModel):
    text: str = Field(..., min_length=2, max_length=5000)


class DetectedTactic(BaseModel):
    tactic_code: str
    tactic_name: str
    confidence: float
    evidence_tokens: List[str] = Field(default_factory=list)


class TacticScanResponse(BaseModel):
    tactics: List[DetectedTactic]
    tactic_count: int
    primary_vector: Optional[str] = None
    model_version: str
    processed_at: datetime = Field(default_factory=get_utc_now)


# --- SCAM CAMPAIGN INTELLIGENCE (ENGINE 4) ---

class CampaignClusterRequest(BaseModel):
    messages: List[str] = Field(..., min_length=2, description="List of messages to cluster")
    similarity_threshold: float = Field(0.75, ge=0.0, le=1.0)


class CampaignCluster(BaseModel):
    cluster_id: int
    cluster_name: str
    sample_size: int
    exemplar_text: str
    associated_indicators: List[str] = Field(default_factory=list)


class CampaignClusterResponse(BaseModel):
    total_messages: int
    clusters_identified: int
    clusters: List[CampaignCluster]
    processed_at: datetime = Field(default_factory=get_utc_now)


# --- COMPOSITE UNIFIED SCAN ---

class CompositeScanRequest(BaseModel):
    content: str = Field(..., description="Text content or URL to analyze")
    channel: str = Field("auto", description="auto | sms | email | url | ocr_text")
    sender: Optional[str] = None


class CompositeScanResponse(BaseModel):
    scan_id: str
    detected_type: str  # text | url
    overall_threat_level: str  # clean | low | medium | high | critical
    confidence: float
    text_analysis: Optional[TextScanResponse] = None
    url_analysis: Optional[URLScanResponse] = None
    tactics_analysis: Optional[TacticScanResponse] = None
    campaign_association: Optional[Dict[str, Any]] = None
    processed_at: datetime = Field(default_factory=get_utc_now)


# --- TELEMETRY & SOC OVERVIEW ---

class TelemetrySummaryResponse(BaseModel):
    total_scans_analyzed: int
    total_threats_blocked: int
    active_campaigns_tracked: int
    avg_inference_latency_ms: float
    threat_breakdown: Dict[str, int]
    top_tactics: List[Dict[str, Any]]
    system_status: str
