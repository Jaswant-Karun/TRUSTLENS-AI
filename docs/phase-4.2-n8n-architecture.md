# TRUSTLENS AI — PHASE 4.2: N8N CYBER INTELLIGENCE AUTOMATION ARCHITECTURE

> **Orchestrator:** n8n (`n8n/workflows/*.json`)  
> **Execution Plane:** FastAPI Backend (`http://127.0.0.1:8000/api/v1`) + Python ML & Database Services  
> **Date:** November 25, 2026

---

## 1. Separation of Responsibilities

- **n8n (Orchestration Only):** Handles schedules, incoming webhook triggers, secret header validation, HTTP retries (`retryOnFail: true`, `maxTries: 3`, `waitBetweenTries: 2000`), and routing.
- **FastAPI + Python Services (Execution & ML):** Performs all ML inference, feed allowlist & timestamp validation, deduplication, redacted alerting, controlled training job orchestration, human-gated model promotion, and MongoDB audit logging.

---

## 2. The 6 Exported Workflows (`n8n/workflows/`)

1. **[`01_threat_intelligence_ingestion.json`](file:///c:/Users/jaswant%20karun/TRUSTLENS%20AI/n8n/workflows/01_threat_intelligence_ingestion.json):** 6-hour schedule trigger -> admin JWT auth -> `POST /api/v1/automation/ingest-feed` (validates permitted feeds and ISO timestamps, deduplicates `threat_indicators`, logs failures) -> `POST /api/v1/automation/log-execution`.
2. **[`02_analysis_notification.json`](file:///c:/Users/jaswant%20karun/TRUSTLENS%20AI/n8n/workflows/02_analysis_notification.json):** Webhook `analysis-completed` -> secret verification -> admin JWT auth -> `POST /api/v1/automation/analysis-notification` (validates `analysis_id`, checks risk/evidence, suppresses duplicate alerts in `automation_logs`, sets `message_content_redacted: true`).
3. **[`03_training_request.json`](file:///c:/Users/jaswant%20karun/TRUSTLENS%20AI/n8n/workflows/03_training_request.json):** Webhook `trigger-ml-training` -> secret verification -> admin JWT auth -> `POST /api/v1/training/jobs` -> `GET /api/v1/training/jobs/{job_id}` -> `POST /api/v1/automation/log-execution`.
4. **[`04_model_approval.json`](file:///c:/Users/jaswant%20karun/TRUSTLENS%20AI/n8n/workflows/04_model_approval.json):** Webhook `model-evaluation-completed` -> secret verification -> `POST /api/v1/training/jobs/{job_id}/compare` -> mandatory human approval gate (`approved_by` + `approval_token`) -> `POST /api/v1/training/jobs/{job_id}/promote` (Admin role only).
5. **[`05_community_report_review.json`](file:///c:/Users/jaswant%20karun/TRUSTLENS%20AI/n8n/workflows/05_community_report_review.json):** Webhook `community-report-submitted` -> secret verification -> `POST /api/v1/reports` -> `POST /api/v1/automation/log-execution` (analyst triage via `POST /api/v1/reports/{id}/review`).
6. **[`06_daily_intelligence_report.json`](file:///c:/Users/jaswant%20karun/TRUSTLENS AI/n8n/workflows/06_daily_intelligence_report.json):** Daily schedule trigger -> admin JWT auth -> `GET /api/v1/automation/daily-summary` (real MongoDB counts only) -> `POST /api/v1/automation/log-execution`.

---

## 3. Security Controls

- **Environment-Only Secrets:** All workflow JSONs reference `$env.TRUSTLENS_API_URL`, `$env.TRUSTLENS_ADMIN_EMAIL`, `$env.TRUSTLENS_ADMIN_PASSWORD`, and `$env.TRUSTLENS_AUTOMATION_SECRET` with zero hardcoded fallback secrets.
- **Role-Based Enforcement:** `require_analyst_or_admin` on automation/training/review endpoints; `require_admin` on model promotion (`N8N_WEBHOOK_SECRET` configurable in [`settings.py`](file:///c:/Users/jaswant%20karun/TRUSTLENS%20AI/backend/app/config/settings.py)).
- **Sensitive Data Protection:** `process_analysis_notification` omits raw message payloads (`message_content_redacted: true`).
