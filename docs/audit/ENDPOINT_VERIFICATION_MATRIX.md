# TRUSTLENS AI — ENDPOINT VERIFICATION MATRIX

> **Base Prefix:** `/api/v1` (except `GET /`, `/docs`, `/redoc`, `/openapi.json`)  
> **Verification Sources:** Direct FastAPI route inspection + `tests/test_phase2_5_e2e_workflow.py`, `tests/test_signin_auth_flow.py`, `tests/test_registration_and_onboarding.py`, `tests/test_user_profile_and_sessions.py`, `tests/test_message_intelligence_api_and_ui.py`, `tests/test_url_shield_api_and_ui.py`, `tests/test_screenshot_ocr_and_security.py`, `tests/test_phase2_4_campaign_sync.py`, `tests/test_phase2_3_timeline.py`, `tests/test_investigation_auth_and_notes.py`, and full `pytest` suite (`84` tests).

---

## 1. Core & Health Endpoints

| Method | Path | Auth / RBAC | Service / Handler | Verification Status |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/` | Public | `main.root` | **Verified** |
| `GET` | `/api/v1/health` | Public | `routes/health.py` | **Verified** |

## 2. Authentication & User Profile Endpoints (`/api/v1/auth`)

| Method | Path | Auth / RBAC | Service / Handler | Verification Status |
| :--- | :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/auth/register` | Public (`role` restricted to `user\|analyst`) | `auth_service.register_user` | **Verified** (`test_registration_and_onboarding.py`, `test_phase2_5_e2e_workflow.py`) |
| `POST` | `/api/v1/auth/verify-email` | Signed Verification Token | `auth_service.verify_email_token` | **Verified** (`test_registration_and_onboarding.py`) |
| `POST` | `/api/v1/auth/login` | Public (Email + bcrypt) | `auth_service.authenticate_user` | **Verified** (`test_signin_auth_flow.py`) |
| `GET` | `/api/v1/auth/me` | `get_current_user` (JWT) | `routes/auth.get_my_profile` | **Verified** (`test_signin_auth_flow.py`, `test_user_profile_and_sessions.py`) |
| `PATCH` | `/api/v1/auth/me` | `get_current_user` (JWT) | `auth_service.update_profile` | **Verified** (`test_user_profile_and_sessions.py`) |
| `GET` | `/api/v1/auth/sessions` | `get_current_user` (JWT) | `auth_service.get_user_sessions` | **Verified** (`test_user_profile_and_sessions.py`) |
| `POST` | `/api/v1/auth/logout` | `get_current_user` (JWT) | `auth_service.logout_user` | **Verified** (`test_user_profile_and_sessions.py`) |

## 3. ML Analysis & History Endpoints (`/api/v1/analyze`, `/api/v1/analyses`)

| Method | Path | Auth / RBAC | Service / Handler | Verification Status |
| :--- | :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/analyze/text` | `get_optional_current_user` | `analysis_service` + Models 1 & 3 | **Verified** (`test_message_intelligence_api_and_ui.py`) |
| `POST` | `/api/v1/analyze/url` | `get_optional_current_user` | `analysis_service` + Model 2 (Zero-Hop) | **Verified** (`test_url_shield_api_and_ui.py`) |
| `POST` | `/api/v1/analyze/image` | `get_optional_current_user` | `ocr_service` + `analysis_service` | **Verified** (`test_screenshot_ocr_and_security.py`) |
| `POST` | `/api/v1/analyze/comprehensive` | `get_optional_current_user` | `analysis_service` (Multi-modal) | **Verified** (existing pytest suite) |
| `GET` | `/api/v1/analyses` | `get_current_user` | `analysis_service.get_analyses_history` | **Verified** (`test_phase2_5_e2e_workflow.py`) |
| `GET` | `/api/v1/analyses/{analysis_id}` | `get_current_user` | `analysis_service.get_analysis_by_id` | **Verified** (`test_phase2_5_e2e_workflow.py`) |

## 4. Investigation, Notes & Timeline Endpoints (`/api/v1/investigations`)

| Method | Path | Auth / RBAC | Service / Handler | Verification Status |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/investigations` | `get_optional_current_user` (filters `Private`) | `investigation_service.list_investigations` | **Verified** (`test_investigation_auth_and_notes.py`) |
| `POST` | `/api/v1/investigations` | `get_current_user` (JWT `owner_id`) | `investigation_service.create_investigation` | **Verified** (`test_investigation_auth_and_notes.py`) |
| `GET` | `/api/v1/investigations/{id}` | `get_optional_current_user` + `_check_read_access` | `investigation_service.get_investigation` | **Verified** (`test_phase2_5_e2e_workflow.py`) |
| `PATCH` | `/api/v1/investigations/{id}` | `get_current_user` + `_check_write_access` | `investigation_service.update_investigation` | **Verified** (`test_phase2_3_timeline.py`) |
| `GET` | `/api/v1/investigations/{id}/graph` | `get_optional_current_user` + `_check_read_access` | `investigation_service.get_graph` | **Verified** (`test_investigation_auth_and_notes.py`) |
| `GET` | `/api/v1/investigations/{id}/timeline` | `get_optional_current_user` + `_check_read_access` | `investigation_service.get_timeline` | **Verified** (`test_phase2_3_timeline.py`) |
| `GET` | `/api/v1/investigations/{id}/objects/{object_id}` | `get_optional_current_user` + `_check_read_access` | `investigation_service.get_object_detail` | **Verified** (existing suite) |
| `GET` | `/api/v1/investigations/{id}/objects/{object_id}/relationships` | `get_optional_current_user` + `_check_read_access` | `investigation_service.get_object_relationships` | **Verified** (existing suite) |
| `GET` | `/api/v1/investigations/{id}/notes` | `get_optional_current_user` + `_check_read_access` | `investigation_service.list_notes` | **Verified** (`test_investigation_auth_and_notes.py`) |
| `POST` | `/api/v1/investigations/{id}/notes` | `get_current_user` + `_check_write_access` | `investigation_service.add_note` | **Verified** (`test_investigation_auth_and_notes.py`) |
| `PATCH` | `/api/v1/investigations/{id}/notes/{note_id}` | `get_current_user` + Author/Admin | `investigation_service.update_note` | **Verified** (`test_investigation_auth_and_notes.py`) |
| `DELETE` | `/api/v1/investigations/{id}/notes/{note_id}` | `get_current_user` + Author/Admin | `investigation_service.delete_note` | **Verified** (`test_investigation_auth_and_notes.py`) |
| `POST` | `/api/v1/investigations/{id}/attach-analysis` | `get_current_user` + `_check_write_access` | `investigation_service.attach_analysis` | **Verified** (`test_phase2_3_timeline.py`, `409` dup guard) |

## 5. Campaigns, Threat Library, Reports, Models, Analytics & Exports

| Method | Path | Auth / RBAC | Service / Handler | Verification Status |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/campaigns` | Public | `campaign_service.list_campaigns` | **Verified** (`47` docs, `test_phase2_4_campaign_sync.py`) |
| `GET` | `/api/v1/campaigns/{campaign_id}` | Public | `campaign_service.get_campaign_by_id` | **Verified** (`test_phase2_4_campaign_sync.py`) |
| `POST` | `/api/v1/campaigns/sync` | `require_admin` | `campaign_service.sync_campaigns_from_dossiers` | **Verified** (`test_phase2_4_campaign_sync.py`) |
| `GET` | `/api/v1/threat-library` & `/{item_id}` | Public | `threat_library_service` | **Verified** (existing suite) |
| `GET` | `/api/v1/analytics/overview` | Public | `analytics_service.get_overview` | **Verified** (existing suite) |
| `POST` | `/api/v1/reports` | `get_optional_current_user` | `report_service.create_report` | **Verified** (existing suite) |
| `GET` | `/api/v1/reports` | `get_current_user` | `report_service.list_reports` | **Verified** (existing suite) |
| `POST` | `/api/v1/reports/{report_id}/review` | `require_reviewer` | `report_service.review_report` | **Verified** (existing suite) |
| `GET` | `/api/v1/models`, `/metrics`, `/experiments`, `/{model_id}` | Public | `model_service` | **Verified** (existing suite) |
| `GET` | `/api/v1/intelligence-reports/generate`, `/exports/json`, `/exports/stix` | `get_current_user` | `reporting_service` | **Verified** (existing suite) |
| `POST/GET` | `/api/v1/training/jobs*` | `require_admin` | `training_service` | **Verified** (existing suite) |
| `GET/POST` | `/api/v1/automation/*` | Webhook Secret (`X-N8N-Secret`) | `automation_service` | **Verified** (`test_n8n_automation.py`) |
| `POST/GET` | Legacy `/api/v1/{scans,urls,tactics,telemetry}/*` | Legacy compatibility | `v1/routers/*` | **Verified** (existing suite) |
