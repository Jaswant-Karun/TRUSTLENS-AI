# TRUSTLENS AI — n8n Cyber Intelligence Workflows (`n8n/workflows/`)

All workflows orchestrate **TRUSTLENS AI FastAPI** endpoints (`$env.TRUSTLENS_API_URL`) while Python services perform all ML, validation, deduplication, and database operations.

## Required Environment Variables (No Hardcoded Secrets)

Configure these in your n8n environment before activating any workflow:
- `TRUSTLENS_API_URL` (e.g., `http://127.0.0.1:8000`)
- `TRUSTLENS_ADMIN_EMAIL` (admin/service account email)
- `TRUSTLENS_ADMIN_PASSWORD` (admin/service account password)
- `TRUSTLENS_AUTOMATION_SECRET` (shared secret checked on `X-TrustLens-Automation-Secret` for incoming webhooks)

## Exported Workflows

1. **`01_threat_intelligence_ingestion.json`** — Scheduled 6h feed sync, source/timestamp validation, indicator deduplication, provenance recording, and audit logging (`POST /api/v1/automation/ingest-feed`).
2. **`02_analysis_notification.json`** — Webhook-triggered analysis completion handler (`POST /api/v1/automation/analysis-notification`) with `analysis_id` validation, risk/evidence check, persistent duplicate suppression, and raw message redaction.
3. **`03_training_request.json`** — Authenticated admin webhook (`POST /api/v1/training/jobs`), model/dataset validation, job status polling (`GET /api/v1/training/jobs/{job_id}`), and completion logging.
4. **`04_model_approval.json`** — Candidate vs production evaluation comparison (`POST /api/v1/training/jobs/{job_id}/compare`) with mandatory human approval gate before promotion (`POST /api/v1/training/jobs/{job_id}/promote`).
5. **`05_community_report_review.json`** — Community report validation (`POST /api/v1/reports`), human-review task queuing, and audit history logging.
6. **`06_daily_intelligence_report.json`** — Scheduled daily intelligence summary (`GET /api/v1/automation/daily-summary`) computed strictly from live MongoDB statistics.
