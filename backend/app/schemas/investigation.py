"""
TRUSTLENS AI - Cyber Threat Investigation & Live Graph Data Contract Schemas
Provides strict Pydantic models for Investigations, Nodes, Edges, and Timelines.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


# ---------------------------------------------------------
# Graph Node & Edge Contracts
# ---------------------------------------------------------

class GraphNodeSchema(BaseModel):
    id: str = Field(..., description="Unique graph node identifier")
    type: str = Field(
        ...,
        description="Node type: campaign_cluster | message | url | domain | ip | tactic | threat_indicator | user_report | source_reference | scam_category"
    )
    label: str = Field(..., description="Human-readable node label / identifier")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Verified technical properties and model telemetry")
    source: str = Field(..., description="Data provenance source (e.g. HDBSCAN Cluster #11, URLhaus, Analysis UUID)")
    verification_status: str = Field(default="verified", description="verified | under_review | flagged")
    created_at: datetime = Field(..., description="Creation / first seen timestamp")


class GraphEdgeSchema(BaseModel):
    id: str = Field(..., description="Unique edge identifier")
    source: str = Field(..., description="Source node ID")
    target: str = Field(..., description="Target node ID")
    relationship_type: str = Field(
        ...,
        description="Relationship type: belongs_to_cluster | contains_url | resolves_to | exhibits_tactic | references_indicator | reported_by | targets_entity | attributed_to"
    )
    evidence_reference: Optional[str] = Field(None, description="Direct reference to supporting token, SHAP attribution, or analysis record")
    created_at: datetime = Field(..., description="Edge discovery timestamp")


# ---------------------------------------------------------
# Timeline Event Contract
# ---------------------------------------------------------

class TimelineEventSchema(BaseModel):
    id: str = Field(..., description="Unique timeline event identifier")
    event_type: str = Field(..., description="Event track/category: task | situation | indicator")
    action_type: Optional[str] = Field(
        None,
        description="Real domain action: investigation_created | analysis_attached | note_added | investigation_status_changed | investigation_updated",
    )
    actor_id: Optional[str] = Field(None, description="Authenticated actor user_id or system source")
    title: str = Field(..., description="Event title")
    description: Optional[str] = Field(None, description="Detailed context or observation rationale")
    related_object_ids: List[str] = Field(default_factory=list, description="IDs of graph nodes linked to this event")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Safe event metadata")
    timestamp: datetime = Field(..., description="Event occurrence or detection timestamp")
    source: str = Field(..., description="Event provenance source")


# ---------------------------------------------------------
# Investigation Core Contracts
# ---------------------------------------------------------

class InvestigationBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=200, description="Investigation title")
    description: Optional[str] = Field(None, description="Detailed investigative scope and briefing")
    status: str = Field(default="active", description="active | in_progress | mitigated | archived")
    severity: Optional[str] = Field(default="high", description="critical | high | medium | low")


class InvestigationCreate(InvestigationBase):
    visibility: str = Field(default="Organization", description="Organization | Private")
    tags: Optional[List[str]] = Field(default_factory=list, description="Categorical threat tags")
    seed_campaign_id: Optional[int] = Field(None, description="Seed from an existing HDBSCAN Campaign Cluster ID")
    seed_analysis_id: Optional[str] = Field(None, description="Seed from an existing Analysis UUID")


class InvestigationSummary(InvestigationBase):
    id: str = Field(..., description="Unique investigation identifier (e.g. INV-2026-0011)")
    owner_id: Optional[str] = Field(None, description="Authenticated owner user_id")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last modified timestamp")
    objects_count: int = Field(default=0, description="Total graph nodes in dossier")
    tasks_count: int = Field(default=0, description="Associated analyst tasks")
    comments_count: int = Field(default=0, description="Analyst comments / notes")
    tags: List[str] = Field(default_factory=list, description="Threat tags")
    visibility: str = Field(default="Organization", description="Organization | Private")


class InvestigationDetail(InvestigationSummary):
    sources: List[str] = Field(default_factory=list, description="Validated intelligence sources")
    attributes: Dict[str, Any] = Field(default_factory=dict, description="Dossier attributes (e.g. Targeted Sector, Campaign Hub)")
    visibility: str = Field(default="Organization", description="Access visibility scope")


# ---------------------------------------------------------
# Investigation Notes Contracts
# ---------------------------------------------------------

class InvestigationNoteCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=2000, description="Analyst investigation note")


class InvestigationNoteUpdate(BaseModel):
    content: str = Field(..., min_length=1, max_length=2000, description="Updated note content")


class InvestigationNoteResponse(BaseModel):
    note_id: str
    investigation_id: str
    author_id: str
    author_role: str
    content: str
    created_at: datetime
    updated_at: Optional[datetime] = None


class InvestigationUpdate(BaseModel):
    status: Optional[str] = Field(None, description="active | in_progress | mitigated | archived")
    visibility: Optional[str] = Field(None, description="Organization | Private")
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = None


class AttachAnalysisRequest(BaseModel):
    analysis_id: str = Field(..., min_length=3, max_length=128, description="Existing analysis UUID to attach")


# ---------------------------------------------------------
# Graph & Relationship Query Responses
# ---------------------------------------------------------

class InvestigationGraphResponse(BaseModel):
    investigation_id: str
    nodes: List[GraphNodeSchema]
    edges: List[GraphEdgeSchema]
    total_nodes: int
    total_edges: int


class InvestigationTimelineResponse(BaseModel):
    investigation_id: str
    timeline: List[TimelineEventSchema]
    total_events: int


class ObjectDetailResponse(BaseModel):
    investigation_id: str
    object: GraphNodeSchema
    relationships_count: int


class ObjectRelationshipsResponse(BaseModel):
    investigation_id: str
    object_id: str
    connected_nodes: List[GraphNodeSchema]
    edges: List[GraphEdgeSchema]
    total_connected: int
