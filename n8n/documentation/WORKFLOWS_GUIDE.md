# 📘 TRUSTLENS AI — n8n Workflows Technical Guide & Safe Testing

This guide provides node-by-node documentation for each of the six production n8n workflows, detailing their inputs, parameters, security validations, and curl commands for testing with safe sample events.

---

## 🛠️ Workflow 1: Dataset Monitoring (`01_dataset_monitoring.json`)

### Architectural Purpose
Automates continuous ingestion of fresh, verified threat intelligence indicators (suspicious phishing URLs, fraudulent domains, smishing phone numbers) from vetted external feeds into the MongoDB Atlas `threat_indicators` collection.

### Node-by-Node Explanation
1. **Schedule Trigger (Every 6h):** Runs on a recurring 6-hour interval (`0 */6 * * *`).
2. **Authenticate System Admin:** Executes `POST /api/v1/auth/login` to obtain an ephemeral JWT Bearer token.
3. **Fetch Approved Threat Feed:** Retrieves metadata and indicator batches from approved feeds (e.g. URLhaus, PhishTank).
4. **Validate Feed Metadata & Timestamps:** Verifies that feed timestamp is within 24 hours and source is whitelisted.
5. **Ingest to TrustLens Ingestion API:** Dispatches payload to `POST /api/v1/automation/ingest-feed`. The Python backend automatically detects and skips duplicate indicator values.
6. **Log Ingestion Success to Audit Store:** Posts execution telemetry to `/api/v1/automation/log-execution`.
7. **Notify Administrator on Ingestion Failure:** Dispatches alert if feed is offline, rejected, or unverified.

### Safe Sample Test Command
```bash
curl -X POST http://127.0.0.1:8000/api/v1/automation/ingest-feed \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "source_name": "URLhaus_Threat_Feed",
    "feed_timestamp": "2026-11-13T00:00:00Z",
    "indicators": [
      {
        "indicator_type": "url",
        "indicator_value": "http://safe-test-phish-domain.xyz/login",
        "confidence": 0.95,
        "tags": ["test", "phishing"]
      }
    ]
  }'
```

---

## 🛠️ Workflow 2: Automated ML Training (`02_automated_ml_training.json`)

### Architectural Purpose
Enqueues training jobs to the dedicated Python training orchestrator worker. Prevents expensive concurrent training collisions, verifies authorization, and tracks progress asynchronously.

### Safety Invariants
- **Non-blocking:** The webhook returns immediately with job registration; the Python worker executes training in the background.
- **Duplicate Prevention:** If `model1_text` is already training, incoming requests are rejected with `HTTP 409 Conflict`.
- **Zero In-Node ML:** No models are fitted or inferred inside JavaScript.

### Node-by-Node Explanation
1. **Authorized Admin Webhook Trigger:** Listens on `POST /webhook/trigger-ml-training`.
2. **Authenticate Request & Verify Secret:** Validates `x-trustlens-automation-secret`.
3. **Validate Model & Dataset Versions:** Verifies model name is one of `model1_text`, `model2_url`, `model3_tactics`, `model4_campaigns`.
4. **Acquire Admin JWT Session:** Authenticates to TrustLens backend.
5. **Dispatch Job to Python Training Worker:** Dispatches `POST /api/v1/training/jobs`.
6. **Wait Controlled Polling Interval:** Pauses for 2 seconds.
7. **Poll Training Job Status:** Queries `GET /api/v1/training/jobs/{job_id}`.
8. **Check If Training Completed:** IF status is `completed`, forwards metrics to admin; else polls.
9. **Notify Administrator of Training Success:** Dispatches candidate metrics summary.
10. **Notify Administrator on Rejection / Failure:** Notifies admin if duplicate lock or invalid parameters occurred.

### Safe Sample Test Command
```bash
curl -X POST http://127.0.0.1:8000/api/v1/training/jobs \
  -H "Authorization: Bearer <ADMIN_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "model_name": "model2_url",
    "dataset_version": "v1.2-cleaned",
    "hyperparameters": { "max_depth": 6, "n_estimators": 100 }
  }'
```

---

## 🛠️ Workflow 3: Model Evaluation & Gated Registration (`03_model_evaluation_registration.json`)

### Architectural Purpose
Ensures that no newly trained candidate model is blindly deployed to production. Evaluates metrics against production baselines and enforces strict human approval before promoting to the `model_registry`.

### Node-by-Node Explanation
1. **Receive Completed Job Webhook:** Receives `job_id` from Workflow 2.
2. **Acquire Admin Session:** Obtains administrative Bearer token.
3. **Compare Candidate with Production Baseline:** Calls `POST /api/v1/training/jobs/{job_id}/compare`. Calculates Macro F1 delta.
4. **Check Acceptance Gate (No Regression):** Evaluates if candidate meets minimum thresholds and does not regress production F1 by more than 1%.
5. **Dispatch Human Approval Request:** If passed, sends an approval request with review link to the security lead.
6. **Promote Approved Model to Production:** Upon human confirmation with valid approval token, executes `POST /api/v1/training/jobs/{job_id}/promote`.
7. **Record Promotion Audit Trail:** Logs permanent promotion record to `audit_logs` and `automation_logs`.
8. **Flag Model Degradation & Reject Promotion:** Halts deployment and alerts team if model degraded.

### Safe Sample Test Command
```bash
# 1. Compare candidate model against production
curl -X POST http://127.0.0.1:8000/api/v1/training/jobs/<JOB_ID>/compare \
  -H "Authorization: Bearer <ADMIN_TOKEN>"

# 2. Promote model with human approval token
curl -X POST http://127.0.0.1:8000/api/v1/training/jobs/<JOB_ID>/promote \
  -H "Authorization: Bearer <ADMIN_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "approved_by": "lead_ml_auditor",
    "approval_token": "AUTH-HUMAN-LEAD-2026-CONFIRM"
  }'
```

---

## 🛠️ Workflow 4: Suspicious Scam Campaign Alerts (`04_suspicious_campaign_alerts.json`)

### Architectural Purpose
Processes newly discovered scam clusters from Model 4, validates evidence, enforces a 24-hour suppression window against alert storms, and notifies affected brands/institutions.

### Node-by-Node Explanation
1. **Campaign Indicators Webhook Trigger:** Receives cluster data (`cluster_id`, `campaign_name`, `cohesion_score`, `indicators`).
2. **Validate Evidence & Cohesion Threshold:** Requires `cohesion_score >= 0.60` to ensure statistical relevance.
3. **Acquire Alert Service Token:** Authenticates to backend.
4. **Check Duplicate Alert & Resolve Targets:** Calls `POST /api/v1/automation/campaign-alerts`. Backend applies 24-hour suppression cache.
5. **Filter Duplicate Alerts:** If `is_duplicate == true`, suppresses dispatch.
6. **Send Campaign Security Bulletin:** Dispatches security advisory containing sample indicators and mandatory legal disclaimer.
7. **Log Suppression to Audit Trail:** Records suppression actions to `audit_logs`.

### Safe Sample Test Command
```bash
curl -X POST http://127.0.0.1:8000/api/v1/automation/campaign-alerts \
  -H "Authorization: Bearer <ADMIN_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "cluster_id": 11,
    "campaign_name": "Campaign Cluster #11 — State Bank KYC Suspension",
    "targeted_entity": "State Bank of India",
    "cohesion_score": 0.82,
    "indicators": ["http://sbi-kyc-update.top", "8712778108"],
    "exemplar_message": "URGENT! Your SBI account will be suspended today. Update KYC at link."
  }'
```

---

## 🛠️ Workflow 5: Community Report Review (`05_community_report_review.json`)

### Architectural Purpose
Sanitizes public scam submissions, strips/masks sensitive PII, deduplicates against existing records, and routes reports to the security analyst review desk.

### Node-by-Node Explanation
1. **Community Report Ingress Webhook:** Receives incoming report (`channel`, `message_content`, `suspicious_url`).
2. **Validate Input & Mask PII:** Validates content length and masks phone/account numbers.
3. **Acquire Triage Session Token:** Authenticates to backend.
4. **Submit Report to Backend & De-duplicate:** Dispatches `POST /api/v1/reports`.
5. **Notify Security Reviewer on Duty:** Dispatches notification to security analyst desk.
6. **Log Triage Enqueue Event:** Persists enqueue event in `automation_logs`.
7. **Log Rejected Submission:** Records invalid submissions without cluttering the review queue.

### Safe Sample Test Command
```bash
curl -X POST http://127.0.0.1:8000/api/v1/reports \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "channel": "sms",
    "sender": "+919876543210",
    "message_content": "Dear Customer your bank electricity bill is overdue. Call 0891234567.",
    "category": "electricity_scam",
    "description": "Reported smishing message"
  }'
```

---

## 🛠️ Workflow 6: Executive Daily Intelligence Report (`06_daily_intelligence_report.json`)

### Architectural Purpose
Runs daily at 08:00 UTC to aggregate verified telemetry, model latencies, community triage progress, and emerging campaign clusters into an executive security briefing.

### Node-by-Node Explanation
1. **Daily Morning Schedule (08:00 UTC):** Cron trigger `0 8 * * *`.
2. **Acquire Executive Reporting Session:** Authenticates to backend.
3. **Retrieve Actual Telemetry & Scan Stats:** Queries `GET /api/v1/automation/daily-summary`.
4. **Retrieve Model Latency & Accuracy Baselines:** Queries `GET /api/v1/models/metrics`.
5. **Retrieve Emerging Campaign Clusters:** Queries `GET /api/v1/campaigns?limit=5`.
6. **Synthesize Verified Daily Intelligence Dossier:** Generates formatted markdown report.
7. **Store Report Record to Automation Logs:** Persists summary record to `automation_logs`.
8. **Dispatch Executive Briefing to Admin & SOC Leads:** Dispatches executive briefing via webhook/email.

### Safe Sample Test Command
```bash
curl -X GET http://127.0.0.1:8000/api/v1/automation/daily-summary \
  -H "Authorization: Bearer <ADMIN_TOKEN>"
```

