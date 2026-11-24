/**
 * TRUSTLENS AI - Centralized Frontend API Client
 * Provides strictly typed client-side methods to communicate with FastAPI endpoints.
 * Never fabricates synthetic statistics; handles loading and error states cleanly.
 */

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
  threat_level: "clean" | "low" | "medium" | "high" | "critical" | "inconclusive";
  confidence: number;
  risk_score: number;
  risk_assessment: {
    threat_level: string;
    calibrated_confidence: number;
    risk_score: number;
    verdict: string;
    primary_vector?: string;
    transparency_breakdown: Record<string, number>;
    remedial_actions: string[];
  };
  text_model?: {
    model_id: string;
    is_threat: boolean;
    confidence: number;
    predicted_label: string;
    detected_language: string;
    language_confidence?: number;
  };
  url_model?: {
    model_id: string;
    is_phishing: boolean;
    phishing_probability: number;
    features?: Record<string, any>;
    top_risk_factors?: string[];
  };
  tactic_model?: {
    model_id: string;
    detected_tactics: string[];
    tactic_count: number;
    tactics?: Array<{ tactic_code: string; tactic_name: string; confidence: number }>;
  };
  campaign_association?: {
    cluster_id: number;
    campaign_name?: string;
    similarity_score: number;
  };
  extracted_iocs?: Record<string, string[]>;
  explainability?: {
    text_highlights?: Array<{ token: string; weight: number }>;
    url_shap?: Array<{ feature: string; impact: string }>;
  };
  processing_time_ms: number;
  created_at: string;
  metadata?: Record<string, any>;
}

export interface AnalysisHistoryItem {
  analysis_id: string;
  created_at: string;
  channel: string;
  sender?: string;
  content_preview: string;
  threat_level: string;
  risk_score: number;
  is_threat: boolean;
}

export interface PaginatedAnalyses {
  items: AnalysisHistoryItem[];
  total: number;
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
  created_at: string;
}

/** Token Management */
export function getStoredToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("trustlens_token");
}

export function setStoredToken(token: string): void {
  if (typeof window !== "undefined") {
    localStorage.setItem("trustlens_token", token);
  }
}

export function clearStoredToken(): void {
  if (typeof window !== "undefined") {
    localStorage.removeItem("trustlens_token");
  }
}

/** Helper for resilient fetch */
async function apiFetch<T>(endpoint: string, options?: RequestInit): Promise<T> {
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

/** List real HDBSCAN campaign clusters */
export async function getCampaigns(limit = 20): Promise<CampaignSummary[]> {
  return apiFetch<CampaignSummary[]>(`/campaigns?limit=${limit}`);
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
  content: string;
  channel?: string;
  sender?: string;
}): Promise<ScanResult> {
  return apiFetch<ScanResult>("/analyze/text", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
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
export async function scanImage(file: File): Promise<ScanResult> {
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
}): Promise<PaginatedAnalyses> {
  const query = new URLSearchParams();
  if (params?.page) query.set("page", params.page.toString());
  if (params?.page_size) query.set("page_size", params.page_size.toString());
  if (params?.threat_level) query.set("threat_level", params.threat_level);
  if (params?.channel) query.set("channel", params.channel);

  return apiFetch<PaginatedAnalyses>(`/analyses?${query.toString()}`);
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
    verdict: "verified_scam" | "benign" | "inconclusive";
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
