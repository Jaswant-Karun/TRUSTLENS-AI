"""
TRUSTLENS AI - MongoDB Document Schemas & Indexing
Defines data structures stored in MongoDB Atlas collections.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class ThreatScanDocument(BaseModel):
    """Stored in 'threat_scans' collection."""
    scan_id: str = Field(..., description="Unique UUID for this scan")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    channel: str = Field(..., description="sms | email | url | ocr_screenshot")
    raw_payload: str
    detected_language: Optional[str] = "unknown"
    threat_level: str = "clean"  # clean | low | medium | high | critical
    
    # Model 1 & 2 outputs
    text_prediction: Optional[Dict[str, Any]] = None
    url_prediction: Optional[Dict[str, Any]] = None
    
    # Model 3 output
    tactics: List[str] = Field(default_factory=list)
    
    # Model 4 output
    campaign_id: Optional[str] = None
    extracted_iocs: List[Dict[str, str]] = Field(default_factory=list)
    
    # Explainability metadata
    shap_attribution: Optional[Dict[str, float]] = None
    client_ip: Optional[str] = None


class CampaignClusterDocument(BaseModel):
    """Stored in 'campaign_clusters' collection."""
    campaign_id: str
    campaign_name: str
    first_seen: datetime = Field(default_factory=datetime.utcnow)
    last_seen: datetime = Field(default_factory=datetime.utcnow)
    incident_count: int = 1
    exemplar_text: str
    ioc_list: List[str] = Field(default_factory=list)
    status: str = "active"  # active | dormant | mitigated


class IOCIndicatorDocument(BaseModel):
    """Stored in 'ioc_indicators' collection."""
    ioc_type: str = Field(..., description="url | domain | upi_id | phone | ip")
    value: str
    reputation: str = "suspicious"  # clean | suspicious | malicious
    sighting_count: int = 1
    first_observed: datetime = Field(default_factory=datetime.utcnow)
    last_observed: datetime = Field(default_factory=datetime.utcnow)
    associated_campaigns: List[str] = Field(default_factory=list)


# Indexing definitions for MongoDB Atlas initialisation
MONGODB_COLLECTIONS_INDEXES = {
    "threat_scans": [
        {"keys": [("scan_id", 1)], "unique": True},
        {"keys": [("timestamp", -1)]},
        {"keys": [("threat_level", 1)]},
        {"keys": [("channel", 1)]},
    ],
    "campaign_clusters": [
        {"keys": [("campaign_id", 1)], "unique": True},
        {"keys": [("last_seen", -1)]},
        {"keys": [("status", 1)]},
    ],
    "ioc_indicators": [
        {"keys": [("value", 1), ("ioc_type", 1)], "unique": True},
        {"keys": [("reputation", 1)]},
        {"keys": [("sighting_count", -1)]},
    ],
}
