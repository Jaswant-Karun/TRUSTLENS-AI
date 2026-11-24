/**
 * TRUSTLENS AI - Cyber Threat Investigation Workspace Types
 * Models graph nodes, relationships, timeline events, and inspector telemetry.
 */

export type NodeType =
  | "message"          // Suspicious messages (SMS, WhatsApp, Email)
  | "url"              // Suspicious/Phishing URLs
  | "domain"           // FQDN / Registered domains
  | "ip"               // IP addresses
  | "scam_category"    // Financial, Electricity, Job, etc.
  | "tactic"           // Social engineering tactics (Urgency, Authority, etc.)
  | "campaign_cluster" // Unsupervised campaign clusters (Central nodes)
  | "user_report"      // Community crowd submissions
  | "threat_indicator" // Phone numbers, UPI handles, hashes
  | "source_reference";// External intelligence sources (CERT-In, ScamShield)

export interface GraphNode {
  id: string;
  label: string;
  type: NodeType;
  subType?: string;
  severity?: "critical" | "high" | "medium" | "low" | "clean";
  count?: number;        // Badge counter (e.g. 45 indicators, 18 events)
  x: number;
  y: number;
  vx?: number;
  vy?: number;
  radius?: number;
  isCentral?: boolean;
  metadata?: {
    description?: string;
    confidence?: number;
    riskScore?: number;
    modelVersion?: string;
    modelOutput?: any;
    evidence?: string[];
    sources?: string[];
    tags?: string[];
    attributes?: Record<string, any>;
    firstSeen?: string;
    lastSeen?: string;
    status?: "active" | "mitigated" | "under_review" | "verified";
    assignedTactics?: string[];
    [key: string]: any;
  };
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  label?: string;
  relationship?:
    | "contains_url"
    | "resolves_to"
    | "exhibits_tactic"
    | "belongs_to_cluster"
    | "references_indicator"
    | "reported_by"
    | "attributed_to"
    | "targets_entity"
    | "associated_with"
    | string;
  severity?: "critical" | "high" | "medium" | "low" | "neutral";
  isDashed?: boolean;
  weight?: number;
}

export interface TimelineEvent {
  id: string;
  title: string;
  timestamp: string; // ISO or formatted date
  dateLabel: string;
  track: "tasks" | "situation" | "indicators";
  severity?: "critical" | "high" | "medium" | "low" | "info";
  relatedNodeIds?: string[];
  description?: string;
  author?: string;
  rangeEnd?: string; // For situation ranges
}

export interface InvestigationData {
  id: string;
  title: string;
  description: string;
  severity: "critical" | "high" | "medium" | "low";
  visibility: "Organization" | "Analyst Only" | "Public Feed";
  status: "Active" | "Closed" | "Under Review";
  created: {
    date: string;
    author: string;
    relative: string;
  };
  lastModified: {
    date: string;
    author: string;
    relative: string;
  };
  objectsCount: number;
  tasksCount: number;
  commentsCount: number;
  sources: string[];
  tags: string[];
  attributes: Record<string, string>;
  nodes: GraphNode[];
  edges: GraphEdge[];
  timeline: TimelineEvent[];
}

/**
 * Adapter helpers that map strict Backend Graph API Contract schemas
 * to the frontend ThreatGraph, Inspector, and Timeline visual component models.
 */
export function adaptBackendNode(n: {
  id: string;
  type: string;
  label: string;
  properties?: Record<string, any>;
  source: string;
  verification_status?: string;
  created_at?: string;
}): GraphNode {
  const p = n.properties || {};
  return {
    id: n.id,
    label: n.label,
    type: n.type as NodeType,
    subType: p.subType || p.tactic_code || p.indicator_type,
    severity: p.severity,
    count: p.count || p.cluster_size,
    x: typeof p.x === "number" ? p.x : (Math.random() - 0.5) * 500,
    y: typeof p.y === "number" ? p.y : (Math.random() - 0.5) * 400,
    radius: p.isCentral ? 40 : 24,
    isCentral: Boolean(p.isCentral),
    metadata: {
      description: p.description,
      confidence: p.confidence,
      riskScore: p.risk_score,
      modelVersion: p.model_version,
      evidence: p.evidence,
      sources: [n.source],
      tags: p.tags || [],
      attributes: p,
      firstSeen: n.created_at,
      status: n.verification_status as any,
      rawText: p.raw_text,
    },
  };
}

export function adaptBackendEdge(e: {
  id: string;
  source: string;
  target: string;
  relationship_type: string;
  evidence_reference?: string;
  created_at?: string;
}): GraphEdge {
  return {
    id: e.id,
    source: e.source,
    target: e.target,
    label: e.relationship_type.replace(/_/g, " "),
    relationship: e.relationship_type,
    severity: "neutral",
    isDashed: e.relationship_type === "reported_by" || e.relationship_type === "attributed_to",
    weight: 1.0,
  };
}

export function adaptBackendTimeline(t: {
  id: string;
  event_type: string;
  title: string;
  description?: string;
  related_object_ids?: string[];
  timestamp: string;
  source: string;
}): TimelineEvent {
  const d = new Date(t.timestamp);
  const dateLabel = isNaN(d.getTime())
    ? t.timestamp
    : d.toLocaleDateString("en-US", { month: "short", day: "numeric" });
  const track =
    t.event_type === "task"
      ? "tasks"
      : t.event_type === "indicator"
      ? "indicators"
      : "situation";

  return {
    id: t.id,
    title: t.title,
    timestamp: t.timestamp,
    dateLabel,
    track,
    severity: "high",
    relatedNodeIds: t.related_object_ids || [],
    description: t.description,
    author: t.source,
  };
}

