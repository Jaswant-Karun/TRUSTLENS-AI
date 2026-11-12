"""
TRUSTLENS AI - Core Schemas Re-export
Maintains full backward compatibility while delegating to backend.app.schemas.
"""

from typing import Union, List, Optional, Dict, Any
from pydantic import BaseModel, Field
from backend.app.schemas import *
from backend.app.schemas.analysis import (
    TextAnalysisRequest as TextScanRequest,
    URLAnalysisRequest as URLScanRequest,
)

# Maintain legacy schema names if expected by existing tests
class LexicalFeatures(BaseModel):
    model_config = {"extra": "allow"}
    url_length: int = 0
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
    model_config = {"extra": "allow"}
    url: str
    predicted_label: str
    risk_score: float
    is_phishing: bool
    features: LexicalFeatures
    top_risk_factors: List[str] = []
    model_version: str = "trustlens-model2-xgboost-v1.0"


class TextScanResponse(BaseModel):
    model_config = {"extra": "allow"}
    text: str
    predicted_label: str
    confidence: float
    is_threat: bool
    detected_language: str
    model_version: str
    explanation: Optional[str] = None


class CompositeScanRequest(BaseModel):
    content: str = Field(..., min_length=2, max_length=10000)
    channel: str = Field("auto")
    sender: Optional[str] = None


class CompositeScanResponse(BaseModel):
    model_config = {"extra": "allow"}
    scan_id: str
    detected_type: str
    overall_threat_level: str
    confidence: float
    text_analysis: Optional[Dict[str, Any]] = None
    url_analysis: Optional[Dict[str, Any]] = None
    tactics_analysis: Optional[Dict[str, Any]] = None
    campaign_association: Optional[Dict[str, Any]] = None


class DetectedTactic(BaseModel):
    model_config = {"extra": "allow"}
    tactic_code: str
    tactic_name: str
    confidence: float
    evidence_tokens: List[str] = []
    threat_level: Optional[str] = None
    explanation: Optional[str] = None


class TacticScanRequest(BaseModel):
    text: str


class TacticScanResponse(BaseModel):
    model_config = {"extra": "allow"}
    tactics: List[DetectedTactic] = []
    tactic_count: int = 0
    primary_vector: Optional[str] = None
    investment_advisory: Optional[Dict[str, Any]] = None
    model_version: str = "trustlens-model3-multilabel-v1.0"


class CampaignClusterRequest(BaseModel):
    messages: List[str] = Field(..., min_length=2)
    similarity_threshold: float = Field(0.75, ge=0.0, le=1.0)


class CampaignCluster(BaseModel):
    model_config = {"extra": "allow"}
    cluster_id: int
    cluster_name: str
    sample_size: int
    exemplar_text: str
    associated_indicators: List[str] = []
    cohesion_score: Optional[float] = None


class CampaignClusterResponse(BaseModel):
    model_config = {"extra": "allow"}
    total_messages: int
    clusters_identified: int
    clusters: List[CampaignCluster] = []


class TelemetrySummaryResponse(BaseModel):
    model_config = {"extra": "allow"}
    total_scans_analyzed: int
    total_threats_blocked: int
    active_campaigns_tracked: int
    avg_inference_latency_ms: float
    threat_breakdown: Dict[str, int]
    top_tactics: List[Dict[str, Any]]
    system_status: str


class SystemHealthResponse(BaseModel):
    model_config = {"extra": "allow"}
    status: str
    app_name: str
    version: str
    database_connected: bool
    models_loaded: Dict[str, bool]
