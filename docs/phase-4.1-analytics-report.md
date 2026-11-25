# TRUSTLENS AI — PHASE 4.1: DATABASE-BACKED ANALYTICS REPORT

> **Backend API:** `GET /api/v1/analytics/overview`  
> **Frontend Route:** `/analytics` (linking to `/models`, `/history`, `/reports`)  
> **Date:** November 25, 2026

---

## 1. Live Database Aggregation

Implemented [`analytics_service.py`](file:///c:/Users/jaswant%20karun/TRUSTLENS%20AI/backend/app/services/analytics_service.py) and [`analytics.py`](file:///c:/Users/jaswant%20karun/TRUSTLENS%20AI/backend/app/api/routes/analytics.py) to compute operational and ML telemetry directly from MongoDB collections and verified evaluation artifacts, with zero static counters or fabricated charts.

Verified live database summary counts (`test_phase4_1_workspaces.py`):
- **Analyses:** `152`
- **Suspicious URLs:** `11`
- **Community Reports:** `4`
- **Campaign Clusters:** `47`
- **Threat Indicators:** `6`
- **Investigations:** `5`

---

## 2. Supported Measurements & Filters

Updated [`analytics/page.tsx`](file:///c:/Users/jaswant%20karun/TRUSTLENS%20AI/frontend/app/analytics/page.tsx) to render only measurements backed by actual records:
- **Analysis Volume Over Time** (`created_at` date buckets)
- **Model Prediction Distribution** (`threat_level`)
- **Language Distribution** (`text_model.detected_language`)
- **Scam Category Distribution** (`text_model.predicted_label` / `analysis_type`)
- **URL Classification Distribution** (`suspicious_urls.is_phishing` / `status`)
- **Tactic Detection Distribution** (`tactic_model.detected_tactics` + `scam_reports.assigned_tactics`)
- **Campaign Similarity Cluster Sizes** (Top 10 clusters from HDBSCAN dossiers)
- **Human-Review Outcomes** (`scam_reports.status`)
- **Model Evaluation Benchmarks** (`ml/artifacts/model_dashboard_data.json`)

**Date & Source Filtering:** Supports `start_date`, `end_date`, and `source` (`all | text | url | image | comprehensive | community_report`). Verified that an empty future date range (`2099-01-01` to `2099-12-31`) returns `total_analyses=0` with explicit `limitations` notices rather than fabricated data.
