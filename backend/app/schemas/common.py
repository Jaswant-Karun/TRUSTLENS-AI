"""
TRUSTLENS AI - Campaign, Model, Report & Common Schemas
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


# --- CAMPAIGN SCHEMAS ---

class CampaignSummary(BaseModel):
    model_config = {"extra": "allow"}

    cluster_id: int = 0
    campaign_name: str = "Unspecified Campaign"
    targeted_entity: str = "Generic / Unspecified Institution"
    cluster_size: int = 1
    cohesion_score: float = 0.0
    primary_tactics: List[str] = Field(default_factory=list)
    status: str = "active"
    last_activity: Optional[datetime] = None


class CampaignDetailResponse(BaseModel):
    model_config = {"extra": "allow"}

    cluster_id: int = 0
    campaign_name: str = "Unspecified Campaign"
    targeted_entity: str = "Generic / Unspecified Institution"
    cluster_size: int = 1
    cohesion_score: float = 0.0
    primary_tactics: List[str] = Field(default_factory=list)
    exemplar_message: str = ""
    shared_phrases: List[str] = Field(default_factory=list)
    shared_iocs: Dict[str, Any] = Field(default_factory=dict)
    legal_disclaimer: str = ""
    discovered_at: Optional[datetime] = None


# --- MODEL MANAGEMENT SCHEMAS ---

class ModelMetadataItem(BaseModel):
    model_config = {"extra": "allow"}

    model_id: str
    display_name: str
    semantic_version: str
    status: str
    algorithm: str
    evaluation_summary: Dict[str, Any]
    training_parameters: Dict[str, Any]
    hardware_requirements: Dict[str, Any]
    artifacts: List[Dict[str, Any]]


class ModelRegistryResponse(BaseModel):
    registry_version: str
    last_updated: str
    models: Dict[str, ModelMetadataItem]


# --- COMMUNITY REPORT SCHEMAS ---

class CreateReportRequest(BaseModel):
    target_type: str = Field(..., description="sms | whatsapp | url | call | upi | email")
    content: str = Field(..., min_length=2, description="Suspicious communication text or target URL")
    target_identifier: Optional[str] = Field(None, description="Sender phone number, sender email, or shortcode")
    description: Optional[str] = Field(None, description="Victim context or incident description")
    evidence_urls: List[str] = Field(default_factory=list)


class ReviewReportRequest(BaseModel):
    verdict: str = Field(..., description="verified_scam | benign | inconclusive")
    notes: Optional[str] = Field(None, description="Analyst verification rationale")
    assigned_tactics: List[str] = Field(default_factory=list)


class ReportResponse(BaseModel):
    model_config = {"extra": "allow"}

    report_id: str
    reporter_user_id: Optional[str]
    target_type: str
    target_identifier: Optional[str]
    content: str
    description: Optional[str]
    evidence_urls: List[str]
    status: str
    reviewed_by: Optional[str]
    review_notes: Optional[str]
    assigned_tactics: List[str]
    created_at: datetime
    reviewed_at: Optional[datetime]


# --- COMMON SCHEMAS ---

class PaginatedResponse(BaseModel):
    items: List[Any]
    total_count: int
    page: int
    page_size: int
    total_pages: int


class MessageResponse(BaseModel):
    message: str
    status: str = "success"
    detail: Optional[str] = None

