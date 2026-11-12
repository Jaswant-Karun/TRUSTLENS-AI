# TRUSTLENS AI — n8n Automation & Orchestration Architecture

This directory houses the automation workflows connecting external threat intelligence feeds, FastAPI backend services, and automated SOC alerting pipelines.

## 🔄 Core Workflows

### 1. Threat Feed Ingestion & IOC Sync (`threat_feed_ingestion.json`)
- **Trigger:** Scheduled Cron (Every 6 hours).
- **Nodes:**
  - `Cron Trigger`: Activates pipeline periodically.
  - `HTTP Request (URLhaus)`: Pulls latest verified malicious URLs from URLhaus API.
  - `Feature Extraction Hook`: Sends URLs to FastAPI `/api/v1/urls/scan`.
  - `MongoDB Node`: Upserts new IOC indicators to `ioc_indicators` collection in MongoDB Atlas.

### 2. High-Severity Incident Triage & Alerting (`incident_triage_alert.json`)
- **Trigger:** Webhook (`/webhook/threat-alert`).
- **Nodes:**
  - `Webhook Receiver`: Listens for critical scans from FastAPI backend.
  - `Filter / IF Node`: Checks if `confidence > 0.85` and involves `TACTIC_CREDENTIAL_HARVESTING` or `TACTIC_FINANCIAL_COERCION`.
  - `Slack / Telegram / Email Node`: Formats security advisory with IOCs and dispatches immediate notification.
  - `Audit Logger`: Logs notification receipt to MongoDB `audit_logs`.

### 3. Scheduled Campaign Re-Clustering (`campaign_clustering_job.json`)
- **Trigger:** Daily Cron (00:00 UTC).
- **Nodes:**
  - `Cron Trigger`: Daily midnight dispatch.
  - `HTTP Request`: Calls FastAPI `/api/v1/campaigns/cluster` with unclustered threat payloads.
  - `MongoDB Batch Update`: Updates cluster assignments and silhouette scores.

## 🚀 Running n8n Locally
1. Start n8n CLI:
   ```bash
   n8n start
   ```
2. Navigate to `http://localhost:5678`.
3. Go to **Workflows -> Import from File** and select any JSON file from `n8n/workflows/`.

