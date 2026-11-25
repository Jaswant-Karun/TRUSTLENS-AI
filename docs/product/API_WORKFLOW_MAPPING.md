# TRUSTLENS AI — API WORKFLOW MAPPING

> **Grounded in:** `backend/app/api/routes/*`, `backend/app/api/v1/routers/telemetry.py`, and `frontend/lib/api.ts`.

---

| Workflow | Frontend Action | Endpoint | Auth / Role | Backend Service | ML / DB Dependencies |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **A. Message Scan** | Submit text on `/analyze/text` | `POST /api/v1/analyze/text` | Optional JWT | `threat_analysis_service` | Models 1, 3, 4 + `risk_service` -> `analyses` |
| **B. URL Scan** | Submit URL on `/analyze/url` | `POST /api/v1/analyze/url` | Optional JWT | `threat_analysis_service` | Model 2 + SHAP + `risk_service` -> `analyses`, `suspicious_urls` |
| **C. Screenshot Scan** | Upload image on `/analyze/image` | `POST /api/v1/analyze/image` | Optional JWT | `ocr_service` + `threat_analysis_service` | Tesseract OCR -> Models 1, 3 -> `analyses` |
| **D. Investigations** | List / Create / Open case | `GET/POST /api/v1/investigations`, `GET /{id}` | Public *(harden POST)* | `investigation_service` | `investigations` |
| **D. Graph & Timeline** | Load canvas & 3-track timeline | `GET /api/v1/investigations/{id}/graph`, `/timeline` | Public | `investigation_service` | `investigations` |
| **D. Inspector & 1-Hop** | Click node / Expand neighbors | `GET /api/v1/investigations/{id}/objects/{obj_id}`, `/relationships` | Public | `investigation_service` | `investigations`, `analyses`, `threat_indicators` |
| **E. Community Reports** | Submit / List / Review report | `POST/GET /api/v1/reports`, `POST /{id}/review` | `POST/GET` public; `review` `analyst`/`admin` | `report_service` | `scam_reports`, `threat_indicators`, `audit_logs` |
| **History** | Browse past scans | `GET /api/v1/analyses`, `/{id}` | `get_current_user` | `threat_analysis_service` | `analyses` (own for `user`, all for `analyst`/`admin`) |
| **Threat Library** | Search, filter, sort, paginate | `GET /api/v1/threat-library`, `/{item_id}` | Public | `threat_library_service` | `analyses`, `suspicious_urls`, `threat_indicators`, `scam_reports`, `campaign_service` |
| **Analytics & Telemetry** | View live DB distributions | `GET /api/v1/analytics/overview`, `GET /api/v1/telemetry/summary` | Public | `analytics_service` | MongoDB collections + `model_service` |
| **Reports & Exports** | Generate report / JSON / STIX 2.1 | `GET /api/v1/intelligence-reports/generate`, `/exports/json`, `/exports/stix` | `401` on private `analysis` | `reporting_service` | MongoDB + `campaign_service` + `model_service` |
| **Automation & Training** | n8n feeds, alerts, jobs, promote | `POST /api/v1/automation/*`, `/training/*` | `analyst`/`admin`; `admin` on promote | `automation_service`, `training_orchestrator` | `automation_logs`, `training`, `model_registry` |
