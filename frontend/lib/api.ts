/**
 * TRUSTLENS AI - Centralized Frontend API Client
 * Provides strictly typed client-side methods to communicate with FastAPI endpoints.
 * Never fabricates synthetic statistics; handles loading and error states cleanly.
 */

import {
  clearStoredTokenSecure,
  getStoredTokenSync,
  initAuthStorage,
  setStoredTokenSecure,
} from "./secureStorage";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "/api/v1";

export interface SystemHealth {
  status: string;
  app_name: string;
  version: string;
  database_connected: boolean;
  models_loaded: Record<string, boolean>;
  environment?: string;
  timestamp?: string;
}

export interface MetricSummary {
  active_models_count: number;
  production_readiness: string;
  total_benchmark_samples: number;
  average_inference_latency_ms: number;
  active_campaign_dossiers: number;
  active_social_engineering_tactics: number;
}

export interface ModelMetricsResponse {
  platform: string;
  edition: string;
  generated_at: string;
  overall_summary: MetricSummary;
  models: {
    text_scam_detector: any;
    phishing_url_detector: any;
    tactic_detector: any;
    campaign_discovery?: any;
    campaign_clusterer?: any;
  };
  soc_intelligence_cards?: Record<string, string>;
}

export interface CampaignSummary {
  cluster_id?: number;
  campaign_id?: number;
  campaign_name?: string;
  targeted_entity?: string;
  target_brand?: string;
  cluster_size: number;
  cohesion_score: number;
  primary_tactics?: string[];
  primary_tactic?: string;
  status: string;
  last_activity?: string;
  first_detected?: string;
  last_detected?: string;
}

export interface CampaignDetail {
  campaign_id: number;
  cluster_id?: number;
  cluster_size: number;
  targeted_entity?: string;
  target_brand?: string;
  primary_tactic?: string;
  primary_tactics?: string[];
  cohesion_score: number;
  status: string;
  exemplar_message: string;
  shared_urls: string[];
  shared_domains: string[];
  shared_threat_indicators: string[];
  first_detected: string;
  last_detected: string;
  legal_disclaimer: string;
}

export interface ScanResult {
  analysis_id: string;
  analysis_type: string;
  threat_level: "clean" | "low" | "medium" | "high" | "critical" | "inconclusive" | string;
  confidence: number;
  risk_score: number;
  risk_assessment: {
    threat_level: string;
    calibrated_confidence: number;
    risk_score: number;
    verdict: string;
    primary_vector?: string;
    transparency_breakdown: Record<string, any>;
    remedial_actions: string[];
  };
  text_model?: {
    model_id?: string;
    text?: string;
    is_threat: boolean;
    confidence: number;
    predicted_label: string;
    detected_language: string;
    language_confidence?: number;
    model_version?: string;
    explanation?: string;
    processing_time_ms?: number;
    [key: string]: any;
  };
  url_model?: {
    model_id?: string;
    url?: string;
    is_phishing: boolean;
    phishing_probability?: number;
    risk_score?: number;
    predicted_label?: string;
    features?: Record<string, any>;
    top_risk_factors?: string[];
    model_version?: string;
    processing_time_ms?: number;
    [key: string]: any;
  };
  tactic_model?: {
    model_id?: string;
    detected_tactics?: string[];
    tactic_count: number;
    primary_vector?: string;
    tactics?: Array<{
      tactic_id?: string;
      tactic_code?: string;
      tactic_name: string;
      threat_level?: string;
      confidence: number;
      explanation?: string;
      evidence_tokens?: string[];
      [key: string]: any;
    }>;
    model_version?: string;
    processing_time_ms?: number;
    [key: string]: any;
  };
  campaign_association?: {
    cluster_id?: number;
    campaign_id?: number;
    campaign_name?: string;
    associated_campaign?: string;
    similarity_score: number;
    targeted_institution?: string;
    cluster_size?: number;
    shared_phrases?: string[];
    extracted_iocs?: Record<string, string[]>;
    legal_disclaimer?: string;
    [key: string]: any;
  };
  extracted_iocs?: Record<string, string[]>;
  explainability?: {
    text_highlights?: Array<{ token: string; weight: number }>;
    url_shap?: Array<{ feature: string; impact: string }>;
    [key: string]: any;
  };
  processing_time_ms: number;
  created_at: string;
  metadata?: Record<string, any>;
  [key: string]: any;
}

export interface ImageAnalysisResponse {
  analysis_id: string;
  extracted_text: string;
  ocr_confidence: number;
  analysis_status: "completed" | "insufficient-evidence" | "inconclusive" | string;
  analysis_result?: ScanResult | null;
  processing_time_ms: number;
  created_at: string;
}

export interface AnalysisHistoryItem {
  analysis_id: string;
  created_at: string;
  channel: string;
  analysis_type?: string;
  sender?: string;
  content_preview: string;
  threat_level: string;
  risk_score: number;
  is_threat: boolean;
  model_version?: string;
  status?: string;
}

export interface PaginatedAnalyses {
  items: AnalysisHistoryItem[];
  total_count?: number;
  total?: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface CommunityReport {
  report_id: string;
  reporter_user_id?: string;
  target_type: string;
  target_identifier?: string;
  content: string;
  description?: string;
  evidence_urls: string[];
  status: "pending" | "under_review" | "verified_scam" | "benign";
  reviewed_by?: string;
  review_notes?: string;
  assigned_tactics: string[];
  created_at: string;
  reviewed_at?: string;
}

export interface UserProfile {
  user_id: string;
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
  email_verified?: boolean;
  onboarding_preferences?: {
    preferred_language?: string;
    primary_focus?: string;
    threat_alerts_opt_in?: boolean;
    email_notifications?: boolean;
    in_app_notifications?: boolean;
  };
  created_at: string;
  last_login?: string | null;
}

/** Token Management (Android Keystore EncryptedSharedPreferences on native, localStorage on web) */
export { initAuthStorage };

export function getStoredToken(): string | null {
  return getStoredTokenSync();
}

export function setStoredToken(token: string): void {
  setStoredTokenSecure(token);
}

export function clearStoredToken(): void {
  clearStoredTokenSecure();
}

/** Helper for resilient fetch */
export async function apiFetch<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const token = getStoredToken();
  const headers: Record<string, string> = {
    Accept: "application/json",
    ...(options?.headers as Record<string, string>),
  };

  if (token && !headers["Authorization"]) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const url = `${API_BASE}${endpoint}`;
  try {
    const res = await fetch(url, {
      ...options,
      headers,
    });

    if (!res.ok) {
      const errorBody = await res.json().catch(() => ({}));
      const message = errorBody?.detail || errorBody?.message || `HTTP ${res.status}: ${res.statusText}`;
      throw new Error(message);
    }

    return await res.json();
  } catch (err: any) {
    if (url.startsWith("/api/v1") && typeof window !== "undefined") {
      const directUrl = `http://127.0.0.1:8000${endpoint}`;
      try {
        const directRes = await fetch(directUrl, {
          ...options,
          headers,
        });
        if (directRes.ok) return await directRes.json();
      } catch {
        // Fall through
      }
    }
    throw err;
  }
}

/** Check platform and backend health */
export async function getHealth(): Promise<SystemHealth> {
  return apiFetch<SystemHealth>("/health");
}

/** Get genuine held-out evaluation benchmarks & telemetry */
export async function getModelMetrics(): Promise<ModelMetricsResponse> {
  return apiFetch<ModelMetricsResponse>("/models/metrics");
}

/** List model registry entries */
export async function getModelRegistry(): Promise<any> {
  return apiFetch<any>("/models");
}

/** Get experimental lineage and benchmark progression */
export async function getExperiments(): Promise<any> {
  return apiFetch<any>("/models/experiments");
}

/** Get live production ML monitoring snapshot */
export async function getModelMonitoring(): Promise<any> {
  return apiFetch<any>("/models/monitoring");
}

/** Submit FP/FN feedback (stored as pending_review) */
export async function submitModelFeedback(payload: {
  analysis_id: string;
  feedback_type: "false_positive" | "false_negative";
  suggested_label: string;
  comment?: string;
}): Promise<any> {
  return apiFetch<any>("/models/feedback", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

/** List real HDBSCAN campaign clusters */
export async function getCampaigns(limit = 20): Promise<CampaignSummary[]> {
  return apiFetch<CampaignSummary[]>(`/campaigns?limit=${limit}`);
}

/** Get threat intelligence synchronization status and per-source health */
export async function getThreatIntelStatus(limit = 20): Promise<any> {
  return apiFetch<any>(`/threat-intel/status?limit=${limit}`);
}

/** Get single campaign dossier */
export async function getCampaignDetail(id: number): Promise<CampaignDetail> {
  return apiFetch<CampaignDetail>(`/campaigns/${id}`);
}

/** Run multi-modal comprehensive analysis */
export async function scanComprehensive(payload: {
  content: string;
  url?: string;
  channel?: string;
  sender?: string;
}): Promise<ScanResult> {
  return apiFetch<ScanResult>("/analyze/comprehensive", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

/** Run standalone text analysis */
export async function scanText(payload: {
  text?: string;
  content?: string;
  channel?: string;
  sender?: string;
}): Promise<ScanResult> {
  const body = {
    text: payload.text || payload.content || "",
    channel: payload.channel || "sms",
    sender: payload.sender || null,
  };
  return apiFetch<ScanResult>("/analyze/text", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}

/** Run zero-hop offline URL inspection */
export async function scanUrl(url: string): Promise<ScanResult> {
  return apiFetch<ScanResult>("/analyze/url", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url }),
  });
}

/** Run screenshot OCR analysis */
export async function scanImage(file: File): Promise<ImageAnalysisResponse> {
  const formData = new FormData();
  formData.append("file", file);

  const token = getStoredToken();
  const headers: Record<string, string> = {};
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(`${API_BASE}/analyze/image`, {
    method: "POST",
    headers,
    body: formData,
  });

  if (!res.ok) {
    const errorBody = await res.json().catch(() => ({}));
    throw new Error(errorBody?.detail || `OCR Scan Error: HTTP ${res.status}`);
  }
  return await res.json();
}

/** Fetch scan analyses history */
export async function getAnalysesHistory(params?: {
  page?: number;
  page_size?: number;
  threat_level?: string;
  channel?: string;
  search?: string;
  sort_by?: string;
  sort_order?: string;
}): Promise<PaginatedAnalyses> {
  const query = new URLSearchParams();
  if (params?.page) query.set("page", params.page.toString());
  if (params?.page_size) query.set("page_size", params.page_size.toString());
  if (params?.threat_level) query.set("threat_level", params.threat_level);
  if (params?.channel) query.set("channel", params.channel);
  if (params?.search) query.set("search", params.search);
  if (params?.sort_by) query.set("sort_by", params.sort_by);
  if (params?.sort_order) query.set("sort_order", params.sort_order);

  return apiFetch<PaginatedAnalyses>(`/analyses?${query.toString()}`);
}

export async function getAnalysisDetail(analysisId: string): Promise<any> {
  return apiFetch(`/analyses/${encodeURIComponent(analysisId)}`);
}

export async function deleteAnalysis(analysisId: string): Promise<{ deleted: boolean; analysis_id: string }> {
  return apiFetch(`/analyses/${encodeURIComponent(analysisId)}`, {
    method: "DELETE",
  });
}

/** Community Reports */
export async function getCommunityReports(params?: {
  status?: string;
  target_type?: string;
  page?: number;
  page_size?: number;
}): Promise<{ items: CommunityReport[]; total_count: number; page: number; total_pages: number }> {
  const query = new URLSearchParams();
  if (params?.status) query.set("status", params.status);
  if (params?.target_type) query.set("target_type", params.target_type);
  if (params?.page) query.set("page", params.page.toString());
  if (params?.page_size) query.set("page_size", params.page_size.toString());

  return apiFetch<{ items: CommunityReport[]; total_count: number; page: number; total_pages: number }>(
    `/reports?${query.toString()}`
  );
}

export async function submitCommunityReport(payload: {
  target_type: string;
  content: string;
  target_identifier?: string;
  description?: string;
  evidence_urls?: string[];
}): Promise<CommunityReport> {
  return apiFetch<CommunityReport>("/reports", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export async function reviewCommunityReport(
  reportId: string,
  payload: {
    verdict: "verified_scam" | "benign" | "inconclusive" | "under_review";
    notes?: string;
    assigned_tactics?: string[];
  }
): Promise<CommunityReport> {
  return apiFetch<CommunityReport>(`/reports/${reportId}/review`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

/** Auth */
export async function loginUser(email: string, password: string): Promise<{ access_token: string; user: UserProfile }> {
  const res = await apiFetch<any>("/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  if (res?.access_token) {
    setStoredToken(res.access_token);
  }
  return res;
}

export async function getCurrentUser(): Promise<UserProfile> {
  return apiFetch<UserProfile>("/auth/me");
}

export async function registerUser(payload: {
  email: string;
  password: string;
  full_name: string;
  privacy_accepted?: boolean;
  terms_accepted?: boolean;
  onboarding_preferences?: {
    preferred_language: string;
    primary_focus: string;
    threat_alerts_opt_in: boolean;
  };
}): Promise<{
  user_id: string;
  email: string;
  role: string;
  verification_token?: string | null;
  message?: string;
}> {
  return apiFetch("/auth/register", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export async function verifyEmailToken(token: string): Promise<{ verified: boolean; user_id: string }> {
  return apiFetch("/auth/verify-email", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ token }),
  });
}

export async function updateUserProfile(payload: {
  full_name?: string;
  preferred_language?: string;
  primary_focus?: string;
  threat_alerts_opt_in?: boolean;
  email_notifications?: boolean;
  in_app_notifications?: boolean;
}): Promise<UserProfile> {
  return apiFetch<UserProfile>("/auth/me", {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export async function getUserSessions(): Promise<{
  user_id: string;
  sessions: Array<{ audit_id: string; action: string; client_ip?: string; timestamp: string }>;
}> {
  return apiFetch("/auth/sessions");
}

export async function logoutUser(): Promise<void> {
  try {
    if (getStoredToken()) {
      await apiFetch("/auth/logout", { method: "POST" });
    }
  } catch {
    // Always clear client token even if backend token already expired
  } finally {
    clearStoredToken();
  }
}

/* -------------------------------------------------------------------------- */
/* Investigation Graph API Client (Phase 1.2 Contract)                        */
/* -------------------------------------------------------------------------- */

export interface BackendGraphNode {
  id: string;
  type: string;
  label: string;
  properties: Record<string, any>;
  source: string;
  verification_status: string;
  created_at: string;
}

export interface BackendGraphEdge {
  id: string;
  source: string;
  target: string;
  relationship_type: string;
  evidence_reference?: string;
  created_at: string;
}

export interface BackendTimelineEvent {
  id: string;
  event_type: string;
  title: string;
  description?: string;
  related_object_ids: string[];
  timestamp: string;
  source: string;
}

export interface InvestigationSummaryItem {
  id: string;
  title: string;
  description?: string;
  status: string;
  severity?: string;
  visibility?: string;
  created_at: string;
  updated_at: string;
  objects_count: number;
  tasks_count: number;
  comments_count: number;
  tags: string[];
}

export interface InvestigationDetailResponse extends InvestigationSummaryItem {
  sources: string[];
  attributes: Record<string, any>;
  visibility: string;
}

export interface InvestigationGraphResponse {
  investigation_id: string;
  nodes: BackendGraphNode[];
  edges: BackendGraphEdge[];
  total_nodes: number;
  total_edges: number;
}

export interface InvestigationTimelineResponse {
  investigation_id: string;
  timeline: BackendTimelineEvent[];
  total_events: number;
}

export interface ObjectDetailResponse {
  investigation_id: string;
  object: BackendGraphNode;
  relationships_count: number;
}

export interface ObjectRelationshipsResponse {
  investigation_id: string;
  object_id: string;
  connected_nodes: BackendGraphNode[];
  edges: BackendGraphEdge[];
  total_connected: number;
}

/** Lists persisted investigation dossiers */
export async function getInvestigations(params?: {
  status?: string;
  severity?: string;
  limit?: number;
  signal?: AbortSignal;
}): Promise<InvestigationSummaryItem[]> {
  const query = new URLSearchParams();
  if (params?.status) query.set("status", params.status);
  if (params?.severity) query.set("severity", params.severity);
  if (params?.limit) query.set("limit", params.limit.toString());
  return apiFetch<InvestigationSummaryItem[]>(`/investigations?${query.toString()}`, { signal: params?.signal });
}

/** Retrieves single investigation dossier metadata */
export async function getInvestigation(id: string, signal?: AbortSignal): Promise<InvestigationDetailResponse> {
  return apiFetch<InvestigationDetailResponse>(`/investigations/${id}`, { signal });
}

/** Retrieves full graph nodes and edges for an investigation */
export async function getInvestigationGraph(id: string, signal?: AbortSignal): Promise<InvestigationGraphResponse> {
  return apiFetch<InvestigationGraphResponse>(`/investigations/${id}/graph`, { signal });
}

/** Retrieves multi-track chronological timeline events */
export async function getInvestigationTimeline(id: string, signal?: AbortSignal): Promise<InvestigationTimelineResponse> {
  return apiFetch<InvestigationTimelineResponse>(`/investigations/${id}/timeline`, { signal });
}

/** Retrieves specific object details from an investigation */
export async function getInvestigationObject(id: string, objectId: string, signal?: AbortSignal): Promise<ObjectDetailResponse> {
  return apiFetch<ObjectDetailResponse>(`/investigations/${id}/objects/${objectId}`, { signal });
}

/** One-Hop Relationship Expansion query */
export async function getInvestigationObjectRelationships(
  id: string,
  objectId: string,
  signal?: AbortSignal
): Promise<ObjectRelationshipsResponse> {
  return apiFetch<ObjectRelationshipsResponse>(`/investigations/${id}/objects/${objectId}/relationships`, { signal });
}

/** Creates and persists a new investigation dossier */
export async function createInvestigation(payload: {
  title: string;
  description?: string;
  severity?: string;
  visibility?: string;
  tags?: string[];
}): Promise<InvestigationDetailResponse> {
  return apiFetch<InvestigationDetailResponse>("/investigations", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

// =========================================================================
// Phase 4.1: Threat Library, Database Analytics, Reports & STIX 2.1 Exports
// =========================================================================

export interface ThreatLibraryItem {
  item_id: string;
  raw_id: string;
  entity_type:
    | "suspicious_message"
    | "url"
    | "domain"
    | "indicator"
    | "tactic"
    | "similarity_cluster"
    | "community_report";
  label: string;
  summary: string;
  severity: string;
  confidence: number | null;
  provenance: string;
  source_name: string;
  verification_status: string;
  created_at: string;
  metadata: Record<string, any>;
}

export interface ThreatLibraryResponse {
  items: ThreatLibraryItem[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
  facets: {
    entity_types: Record<string, number>;
  };
}

export async function queryThreatLibrary(params?: {
  search?: string;
  entity_type?: string;
  severity?: string;
  verification_status?: string;
  provenance?: string;
  sort_by?: string;
  sort_order?: string;
  page?: number;
  page_size?: number;
}): Promise<ThreatLibraryResponse> {
  const query = new URLSearchParams();
  if (params?.search) query.set("search", params.search);
  if (params?.entity_type && params.entity_type !== "all") query.set("entity_type", params.entity_type);
  if (params?.severity && params.severity !== "all") query.set("severity", params.severity);
  if (params?.verification_status && params.verification_status !== "all")
    query.set("verification_status", params.verification_status);
  if (params?.provenance && params.provenance !== "all") query.set("provenance", params.provenance);
  if (params?.sort_by) query.set("sort_by", params.sort_by);
  if (params?.sort_order) query.set("sort_order", params.sort_order);
  if (params?.page) query.set("page", params.page.toString());
  if (params?.page_size) query.set("page_size", params.page_size.toString());
  return apiFetch<ThreatLibraryResponse>(`/threat-library?${query.toString()}`);
}

export async function getThreatLibraryItem(itemId: string): Promise<ThreatLibraryItem> {
  return apiFetch<ThreatLibraryItem>(`/threat-library/${encodeURIComponent(itemId)}`);
}

export interface AnalyticsOverviewResponse {
  filters_applied: {
    start_date: string | null;
    end_date: string | null;
    source: string;
  };
  summary: {
    total_analyses: number;
    total_suspicious_urls: number;
    total_community_reports: number;
    total_campaigns: number;
    total_threat_indicators: number;
    total_investigations: number;
  };
  analysis_volume_over_time: { date: string; total: number; threats: number }[];
  model_prediction_distribution: { label: string; count: number }[];
  language_distribution: { language: string; count: number }[];
  scam_category_distribution: { category: string; count: number }[];
  url_classification_distribution: { classification: string; count: number }[];
  tactic_detection_distribution: { tactic: string; count: number }[];
  campaign_cluster_sizes: {
    cluster_id: number;
    name: string;
    size: number;
    cohesion_score: number | null;
    status: string;
  }[];
  human_review_outcomes: { outcome: string; count: number }[];
  model_evaluation_metrics: Record<string, any>;
  limitations: string[];
}

export async function getAnalyticsOverview(params?: {
  start_date?: string;
  end_date?: string;
  source?: string;
}): Promise<AnalyticsOverviewResponse> {
  const query = new URLSearchParams();
  if (params?.start_date) query.set("start_date", params.start_date);
  if (params?.end_date) query.set("end_date", params.end_date);
  if (params?.source && params.source !== "all") query.set("source", params.source);
  return apiFetch<AnalyticsOverviewResponse>(`/analytics/overview?${query.toString()}`);
}

export interface IntelligenceReportResponse {
  report_id: string;
  report_type: string;
  investigation_id: string;
  sources: string[];
  evidence: any[];
  model_versions: Record<string, string>;
  predictions: Record<string, any>;
  review_status: string;
  limitations: string[];
  generated_at: string;
  generated_by: string;
}

export async function generateIntelligenceReport(
  reportType: string,
  targetId?: string
): Promise<IntelligenceReportResponse> {
  const query = new URLSearchParams({ report_type: reportType });
  if (targetId) query.set("target_id", targetId);
  return apiFetch<IntelligenceReportResponse>(`/intelligence-reports/generate?${query.toString()}`);
}

export async function exportInvestigationJson(targetType: string, targetId: string): Promise<any> {
  const query = new URLSearchParams({ target_type: targetType, target_id: targetId });
  return apiFetch<any>(`/exports/json?${query.toString()}`);
}

export async function exportInvestigationStix(targetType: string, targetId: string): Promise<any> {
  const query = new URLSearchParams({ target_type: targetType, target_id: targetId });
  return apiFetch<any>(`/exports/stix?${query.toString()}`);
}

export interface InvestigationNoteItem {
  note_id: string;
  investigation_id: string;
  author_id: string;
  author_role: string;
  content: string;
  created_at: string;
  updated_at?: string | null;
}

export async function getInvestigationNotes(investigationId: string): Promise<InvestigationNoteItem[]> {
  return apiFetch<InvestigationNoteItem[]>(`/investigations/${encodeURIComponent(investigationId)}/notes`);
}

export async function addInvestigationNote(investigationId: string, content: string): Promise<InvestigationNoteItem> {
  return apiFetch<InvestigationNoteItem>(`/investigations/${encodeURIComponent(investigationId)}/notes`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ content }),
  });
}

export async function deleteInvestigationNote(investigationId: string, noteId: string): Promise<void> {
  await apiFetch(`/investigations/${encodeURIComponent(investigationId)}/notes/${encodeURIComponent(noteId)}`, {
    method: "DELETE",
  });
}

export async function attachAnalysisToInvestigation(
  investigationId: string,
  analysisId: string
): Promise<InvestigationDetailResponse> {
  return apiFetch<InvestigationDetailResponse>(
    `/investigations/${encodeURIComponent(investigationId)}/attach-analysis`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ analysis_id: analysisId }),
    }
  );
}


