# TRUSTLENS AI — BACKEND & API CONNECTIVITY AUDIT (PHASE 0)

> **Entry Point:** `backend/app/main.py` (`FastAPI` + `uvicorn`)  
> **API Base:** `/api/v1` (mounted via `backend/app/api/v1/api.py`)

---

## 1. Core Endpoint Inventory & Verification Status

| Method | Route | Auth | DB / ML Deps | Consumers | Runtime Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/health` | Public | `db_manager`, `CentralModelLoader` | `lib/api.ts`, Render health check | **Verified (HTTP 200)** |
| `POST` | `/api/v1/auth/login`, `/register` | Public | MongoDB `users`, `bcrypt`, `HS256` | `reports/page.tsx`, CLI tests | **Verified (HTTP 200 / 401 / 422)** |
| `POST` | `/api/v1/analyze/text`, `/url`, `/image`, `/comprehensive` | Optional JWT | `CentralModelLoader`, `risk_service`, `ocr_service`, `analyses` | `/analyze/*`, `/investigation` | **Verified (HTTP 200 / 400 / 415)** |
| `GET` | `/api/v1/analyses`, `/analyses/{id}` | `get_current_user` | MongoDB `analyses` | `/history`, `test_phase4_1` | **Verified (401 unauth, 200 auth)** |
| `GET/POST` | `/api/v1/investigations`, `/{id}` | Public | MongoDB `investigations` | `/investigations`, `/investigations/[id]` | **Verified (HTTP 200 / 404)** |
| `GET` | `/api/v1/investigations/{id}/graph`, `/timeline` | Public | MongoDB `investigations` | `InvestigationWorkspace.tsx` | **Verified (HTTP 200 / 404)** |
| `GET` | `/api/v1/investigations/{id}/objects/{obj_id}`, `/relationships` | Public | `investigations`, `analyses`, `threat_indicators` | `ObjectInspector.tsx` | **Verified (HTTP 200)** |
| `GET` | `/api/v1/threat-library`, `/{item_id}` | Public | `analyses`, `suspicious_urls`, `threat_indicators`, `scam_reports`, `campaign_service` | `/threat-library` | **Verified (HTTP 200)** |
| `GET` | `/api/v1/analytics/overview` | Public | MongoDB aggregations + `model_service` | `/analytics` | **Verified (HTTP 200)** |
| `GET` | `/api/v1/intelligence-reports/generate`, `/exports/json`, `/exports/stix` | Optional JWT (`401` on private `analysis`) | MongoDB + `campaign_service` + `model_service` | `/reports`, `/threat-library` | **Verified (HTTP 200 / 401)** |
| `GET/POST` | `/api/v1/reports`, `/{id}/review` | Public POST/GET; `require_analyst_or_admin` on review | MongoDB `scam_reports` | `/reports` | **Verified (201 / 401 / 403 / 200)** |
| `GET/POST` | `/api/v1/training/jobs`, `/{id}/compare`, `/{id}/promote` | `require_analyst_or_admin`; `require_admin` on promote | `training_service`, `model_registry` | n8n Workflows 3 & 4 | **Verified (403 user / 200 admin)** |
| `GET/POST` | `/api/v1/automation/*` | `require_analyst_or_admin` | `automation_service`, `automation_logs` | n8n Workflows 1, 2, 6 | **Verified (test_phase4_2_n8n.py)** |
| `GET` | `/api/v1/telemetry/summary` *(legacy)* | Public | None (hardcoded `0`s) | Legacy only | **Duplicate / Obsolete** |

## 2. Backend Defects Identified
1. **Duplicate Legacy Router (`backend/app/api/v1/routers/telemetry.py`):** Returns static `0`s instead of delegating to `analytics_service`.
2. **Legacy Test Drift (`tests/test_n8n_automation.py`):** 3 assertions fail against updated Phase 4.2 allowlists, workflow count (`10` `0*.json` files due to legacy + Phase 4.2 coexistence), and `analyses_performed` summary schema.
3. **Starlette Deprecation Warnings:** `HTTP_422_UNPROCESSABLE_ENTITY` and `HTTP_413_REQUEST_ENTITY_TOO_LARGE` logged during `pytest`.
