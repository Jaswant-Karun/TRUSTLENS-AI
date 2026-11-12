"""
TRUSTLENS AI - Analysis Schemas
Defines request and response structures for Text, URL, Image, and Comprehensive scans.
"""

from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field


class TextAnalysisRequest(BaseModel):
    text: str = Field(..., min_length=2, max_length=10000, description="Suspicious text content to analyze")
    sender: Optional[str] = Field(None, description="Sender header, phone number, or handle")
    channel: Optional[str] = Field("sms", description="sms | email | whatsapp | telegram | web")


class URLAnalysisRequest(BaseModel):
    url: str = Field(..., min_length=4, max_length=2048, description="Target URL to inspect (fully offline)")


class ComprehensiveAnalysisRequest(BaseModel):
    content: str = Field(..., min_length=2, description="Target content: message text or URL")
    url: Optional[str] = Field(None, description="Optional distinct URL to correlate")
    sender: Optional[str] = Field(None, description="Sender identifier")
    channel: Optional[str] = Field("auto", description="auto | sms | email | whatsapp | web")


class RiskAssessmentSummary(BaseModel):
    model_config = {"extra": "allow"}

    threat_level: str = Field(..., description="clean | low | medium | high | critical | inconclusive")
    calibrated_confidence: float = Field(..., ge=0.0, le=1.0)
    risk_score: float = Field(..., ge=0.0, le=1.0)
    verdict: str
    primary_vector: Optional[str] = None
    transparency_breakdown: Dict[str, Any]
    remedial_actions: List[str] = Field(default_factory=list)


class AnalysisResultResponse(BaseModel):
    model_config = {"extra": "allow"}

    analysis_id: str
    analysis_type: str
    threat_level: str
    confidence: float
    risk_score: float
    risk_assessment: RiskAssessmentSummary
    text_model: Optional[Dict[str, Any]] = None
    url_model: Optional[Dict[str, Any]] = None
    tactic_model: Optional[Dict[str, Any]] = None
    campaign_association: Optional[Dict[str, Any]] = None
    extracted_iocs: Dict[str, List[str]] = Field(default_factory=dict)
    explainability: Optional[Dict[str, Any]] = None
    processing_time_ms: float = 0.0
    created_at: datetime


class ImageAnalysisResponse(BaseModel):
    model_config = {"extra": "allow"}

    analysis_id: str
    extracted_text: str
    ocr_confidence: float
    analysis_status: str  # "completed" | "insufficient-evidence" | "inconclusive"
    analysis_result: Optional[AnalysisResultResponse] = None
    processing_time_ms: float
    created_at: datetime
