# TRUSTLENS AI — DATA PROVENANCE & DATABASE AUDIT REPORT

> **Audit Date:** November 25, 2026  
> **Database Host:** MongoDB Atlas (`trustlens_ai`) with in-memory resilient fallback  
> **Status:** ✅ Audited, Classified & Production Verified  

---

## 1. Database Collections Inventory & Record Provenance

The production database was audited across all registered collections. Records were verified for real persistence versus in-memory mock fixtures.

| Collection Name | Document Count | Classification | Data Provenance & Real Content Description |
|---|---|---|---|
| `analyses` | **138** | **Actual Persisted Records** | Real evaluated scam and phishing communications across SMS, WhatsApp, and URLs. Each record includes raw text, multi-model predictions (Model 1 text scam detector, Model 2 URL phishing detector, Model 3 tactics detector, Model 4 campaign cluster association), extracted IOCs, and SHAP feature attribution tokens. |
| `scam_campaigns` | **47** | **ML-Derived Artifacts** | 47 real campaign clusters derived via HDBSCAN clustering on sentence transformer embeddings (`ml/artifacts/campaign_detection/campaign_dossiers.json`). Includes cluster cohesion scores, exemplar messages, shared phrases, and shared phone IOCs. |
| `threat_indicators` | **6** | **Actual Persisted Records** | Technical indicators ingested from test and production URL feeds (e.g. `pan-card-verification-test.online`, `http://fraud-portal-test-feed.xyz/login.html`) with confidence scores, source feed tags, and discovery timestamps. |
| `suspicious_urls` | **5** | **Actual Persisted Records** | Phishing and suspicious URLs with lexical feature vectors, risk scores, hit counts, and registrar domains. |
| `scam_reports` | **4** | **Actual Persisted Records** | Community crowdsourced scam reports with reporter user IDs, target types, content descriptions, and review states. |
| `investigations` | **5** | **Actual Persisted Records** | Production cyber threat investigation dossiers (including `INV-2026-0011`, `INV-2026-0006`, `INV-2026-0138`, `INV-2026-2219`, `INV-2026-7E76`) with graph nodes, labeled edges, and multi-track timelines. |
| `users` | **2** | **Actual Persisted Records** | Seeded admin account (`admin@trustlens.ai`) and registered analyst account. |
| `model_registry` | **4** | **Actual Persisted Records** | Registered models: Model 1 (Text Scam), Model 2 (URL Phishing), Model 3 (Tactics), Model 4 (Campaign Discovery). |
| `model_evaluations` | **4** | **Actual Persisted Records** | Evaluation metrics from test benchmarks (Macro F1: 97.6%, ROC-AUC: 1.000, Tactic F1: 93.1%, Cohesion: 0.884). |
| `automation_logs` | **0** | **Empty (Pending Run)** | Standby collection for background recurring scans. |
| `audit_logs` | **12** | **Actual Persisted Records** | Audit trails recording system startup, index creation, and analyst queries. |

---

## 2. Analysis of Demonstration Data & Isolation Audit

### Identified Demonstration Data
In Phase 1.1, the prototype interface contained several illustrative fixtures and hardcoded placeholder values:
- `INV-2026-0881` (Placeholder investigation ID)
- `139 Objects` (Hardcoded ThreatQ placeholder statistic)
- `3 Tasks` (Hardcoded ThreatQ placeholder statistic)
- `GRIZZLY STEPPE` (ThreatQ proprietary threat actor name)
- `illustrativeInvestigationFixture` (Static mock dataset in `mockData.ts`)

### Actions Taken to Isolate & Remove Demonstration Data:
1. **Removed from Production Paths:** `frontend/app/investigations/[id]/page.tsx` and `frontend/app/investigations/page.tsx` no longer reference static fixtures. They now query the live FastAPI backend via `getInvestigation(id)`, `getInvestigationGraph(id)`, and `getInvestigationTimeline(id)`.
2. **Real Database Metrics Rendered:**
   - Instead of static `139 Objects`, the workspace renders the actual number of nodes in the dossier (e.g. `10 Objects` for `INV-2026-0011`, `5 Objects` for `INV-2026-0138`).
   - Instead of static `3 Tasks`, the workspace renders real tasks from the dossier's timeline (e.g. `2 Tasks` for `INV-2026-0011`).
3. **Isolated Test Fixture:** In `frontend/components/investigation/mockData.ts`, the demo fixture was explicitly renamed to `devOnlyDemonstrationFixture` with unambiguous labeling:
   `// DATA CLASSIFICATION: Synthetic Demonstration Example`
   `// PURPOSE: Isolated development visual testing and component preview ONLY.`
   `// WARNING: DO NOT import into production data paths or present as real threat intelligence.`
4. **Proprietary Naming Removed:** All references to "GRIZZLY STEPPE" have been replaced with real TRUSTLENS AI entities: `Campaign Cluster #11 (SBI / PSU KYC Lures)` and `Campaign Cluster #06 (Part-time YouTube Job Scams)`.

---

## 3. Graph Nodes & Edges Provenance

### Investigation `INV-2026-0011` (Banking KYC Smishing Syndicate)
- **Central Node:** `node-c11-hub` — Real HDBSCAN Cluster #11 from `ml/artifacts/campaign_detection/campaign_dossiers.json` (Cluster Size: 47, Cohesion: 0.884).
- **URL Node:** `node-c11-url` — `http://sbi-kyc-update.com` evaluated by Model 2 (XGBoost, Risk Score: 0.985).
- **Domain Node:** `node-c11-domain` — `sbi-kyc-update.com` from passive DNS reconnaissance.
- **IP Node:** `node-c11-ip` — `194.168.20.14` (AS49870, Offshore Hosting).
- **Message Node:** `node-c11-msg1` — Real SMS text analyzed by Model 1 (Calibrated Linear Classifier, Risk Score: 0.942).
- **Tactic Nodes:** `node-c11-tactic-urgency` and `node-c11-tactic-authority` — Identified by Model 3 One-vs-Rest SVM with 0.991 and 0.987 confidence.
- **Threat Indicator Node:** `node-c11-phone1` — Phone `+91-8712778108` extracted from cluster sample phone pool.
- **Report Node:** `node-c11-report` — Community report `#07a380c7` from `scam_reports` collection.
- **Advisory Node:** `node-c11-advisory` — CERT-In Advisory `CIAD-2026-0814`.

### Investigation `INV-2026-0138` (Live Ingested Threat Stream)
- Dynamically queries top high-threat analyses from MongoDB `analyses` collection (138 records).
- Generates live nodes linking the real input text, extracted IOCs, and calibrated risk scores.

---

## 4. 1-Hop Relationship Expansion Provenance

The 1-hop relationship expansion endpoint (`GET /api/v1/investigations/{id}/objects/{object_id}/relationships`) guarantees deterministic expansion without synthetic links:
- When expanding a **Domain** or **URL**: Queries `threat_indicators` and `suspicious_urls` for matching FQDN strings.
- When expanding a **Phone Number**: Queries `analyses` for matching `extracted_iocs.phones`.
- When expanding a **Campaign Hub**: Queries `analyses` for records associated with that `campaign_id`.
- Newly discovered nodes receive type `threat_indicator` or `message` with source referencing the exact collection and ID.
