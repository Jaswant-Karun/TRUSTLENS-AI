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
