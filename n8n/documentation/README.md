# 🛡️ TRUSTLENS AI — n8n Automation & Orchestration Architecture

This directory houses the complete production orchestration architecture connecting **n8n Automation**, **FastAPI Backend Services**, **MongoDB Atlas**, and the **Python ML Training & Inference Engine**.

---

## 🏛️ Core Architectural Invariant

> **CRITICAL ARCHITECTURAL BOUNDARY:**
> - **n8n** is strictly the **orchestration and scheduling layer** (triggers, webhooks, rate limits, retries, approval routing, and notifications).
> - **Python** is strictly responsible for **all ML operations**: dataset ingestion & validation, model training loops, model evaluation calculations, artifact generation, model registration, and inference scoring.
> - **No machine learning algorithms are executed inside n8n Code nodes.**

---

## 🔄 The 6 Production n8n Workflows

| # | Workflow File | Trigger | Responsibility | Target Backend Endpoint |
|---|---|---|---|---|
| **1** | `01_dataset_monitoring.json` | Schedule (`0 */6 * * *`) | Periodically queries approved threat intelligence feeds (URLhaus, PhishTank), validates timestamps/sources, filters duplicates, and ingests into MongoDB Atlas. | `POST /api/v1/automation/ingest-feed` |
| **2** | `02_automated_ml_training.json` | Webhook (`/webhook/trigger-ml-training`) | Receives authenticated retrain requests, verifies HMAC/secret, checks active model locks to prevent concurrent training collisions, enqueues jobs to the Python training worker, and polls progress. | `POST /api/v1/training/jobs`<br>`GET /api/v1/training/jobs/{id}` |
| **3** | `03_model_evaluation_registration.json` | Webhook (`/webhook/evaluate-and-register`) | Evaluates completed training candidates against baseline production models, checks acceptance gates (no F1 degradation), halts on regression, dispatches human approval requests, and promotes approved models with full audit trails. | `POST /api/v1/training/jobs/{id}/compare`<br>`POST /api/v1/training/jobs/{id}/promote` |
| **4** | `04_suspicious_campaign_alerts.json` | Webhook (`/webhook/campaign-alert-trigger`) | Receives newly clustered campaign indicators from Model 4, validates cohesion thresholds ($\ge 0.60$), checks 24-hour duplicate suppression, identifies impacted entities, and dispatches security bulletins. | `POST /api/v1/automation/campaign-alerts` |
| **5** | `05_community_report_review.json` | Webhook (`/webhook/community-report-ingress`) | Sanitizes community-submitted scam messages and suspicious URLs, masks sensitive PII, checks duplicates, enqueues into human review queue, and alerts on-duty security analysts. | `POST /api/v1/reports`<br>`POST /api/v1/reports/{id}/review` |
| **6** | `06_daily_intelligence_report.json` | Schedule (`0 8 * * *`) | Executes daily at 08:00 UTC, compiles actual verified 24h threat telemetry, community report counts, model latency/accuracy baselines, and active campaign clusters into an executive briefing. | `GET /api/v1/automation/daily-summary`<br>`POST /api/v1/automation/log-execution` |

---

## ⚙️ Environment Variables Configuration

Configure these environment variables in your n8n container or `.env` file:

```bash
# TrustLens Backend Connectivity
TRUSTLENS_API_URL=http://127.0.0.1:8000
TRUSTLENS_ADMIN_USER=admin@trustlens.ai
TRUSTLENS_ADMIN_PASSWORD=AdminPass123!

# Automation Webhook Secrets
TRUSTLENS_AUTOMATION_SECRET=Secr3t-TrustLens-AutoTr4in-2026
TRUSTLENS_LEAD_AUDITOR=sec_lead_analyst
TRUSTLENS_HUMAN_APPROVAL_TOKEN=AUTH-HUMAN-LEAD-2026-CONFIRM

# SOC Notification Dispatch Channels
ADMIN_ALERT_WEBHOOK_URL=http://127.0.0.1:8000/api/v1/automation/log-execution
SOC_ALERT_DISPATCH_WEBHOOK=http://127.0.0.1:8000/api/v1/automation/log-execution
EXECUTIVE_DISPATCH_WEBHOOK=http://127.0.0.1:8000/api/v1/automation/log-execution
```

---

## 🚀 Step-by-Step Setup & Importing into n8n

### Step 1: Start n8n
If using n8n via npm or Docker:
```bash
# Option A: npm
npx n8n start

# Option B: Docker
docker run -it --rm --name n8n -p 5678:5678 -v ~/.n8n:/home/node/.n8n n8nio/n8n
```

### Step 2: Import Workflows
1. Open your browser and navigate to `http://localhost:5678`.
2. In the left navigation bar, select **Workflows**.
3. Click the **...** menu in the top-right corner and select **Import from File**.
4. Select each JSON file in `n8n/workflows/`:
   - `01_dataset_monitoring.json`
   - `02_automated_ml_training.json`
   - `03_model_evaluation_registration.json`
   - `04_suspicious_campaign_alerts.json`
   - `05_community_report_review.json`
   - `06_daily_intelligence_report.json`

### Step 3: Configure Environment Variables
Inside n8n UI, navigate to **Settings -> Variables** (or inject via docker environment variables) to supply `TRUSTLENS_API_URL` and credentials.

---

## 🔒 Security & Concurrency Guarantees

1. **Zero Unauthenticated Triggers:** All webhooks validate HMAC headers or shared secrets before executing backend interactions.
2. **Anti-Collision Locks:** The Python training worker enforces per-model mutex locks (`_active_model_locks`), rejecting duplicate requests with HTTP 409 Conflict if training is already in progress.
3. **No Blind Overwrites:** Completed models are placed in candidate evaluation state. Models cannot be promoted without human review and explicit token verification.
4. **Duplicate Suppression:** Campaign alerts enforce a 24-hour suppression window, preventing subscriber notification flooding.
5. **PII Masking:** Community reports and threat feeds are sanitized prior to human queuing.
