# TRUSTLENS AI — COMPLETE FASTAPI BACKEND ARCHITECTURE AUDIT

> **Audit Date:** November 25, 2026  
> **Branch:** `remediation/phase-0.5`  
> **Scope:** Non-destructive forensic inspection of `backend/app/` routers, schemas, services, MongoDB collections/indexes, auth/RBAC dependencies, and error handling. Zero functioning endpoints were rewritten.

---

## 1. Application Entrypoint & Middleware Stack (`backend/app/main.py`)

- **Lifespan (`lifespan`):** Connects `db_manager` (`mongodb://localhost:27017` / Atlas), runs `init_database_indexes()`, and executes `auth_service.seed_initial_admin()`.
- **Middleware Order:**
  1. `CORSMiddleware` (`settings.cors_origins`, `allow_credentials=True`)
  2. `SecurityHeadersMiddleware` (`X-Content-Type-Options`, `X-Frame-Options: DENY`, `X-XSS-Protection`, `Referrer-Policy`, `HSTS`)
  3. `RequestLoggingMiddleware` (UUID request correlation + latency logging)
  4. `RateLimitMiddleware`
- **Production Docs Gating:** `/docs`, `/redoc`, `/openapi.json` are disabled when `APP_ENV == "production"` and `DEBUG == False`.
- **Structured Error Handling:**
  - `RequestValidationError` -> `422` JSON `{error: "ValidationError", message, details: [{location, message}]}`.
  - Global `Exception` fallback -> `500` JSON `{error: "InternalServerError", message, detail: str(exc) if settings.DEBUG else None}` (prevents secret/stacktrace leaks in production).

---

## 2. Router Topology (`backend/app/api/`)

All v1 routes mount under `settings.API_V1_STR` (`/api/v1`) via `backend/app/api/v1/api.py`:
- **Official Domain Routers (`backend/app/api/routes/__init__.py`):** `health`, `auth`, `analyze`, `analyses`, `campaigns`, `models`, `reports`, `training`, `automation`, `investigations`, `threat_library`, `analytics`, `exports`.
- **Legacy Compatibility Routers (`backend/app/api/v1/routers/`):** `scans`, `urls`, `tactics`, `telemetry` are mounted; `health.py` and `campaigns.py` in `v1/routers/` are **unmounted** legacy files.

---

## 3. Authentication, RBAC & Session Security (`backend/app/security/`)

- **Password Hashing (`password.py`):** `bcrypt` (`rounds=12`).
- **JWT (`jwt.py`):** `HS256` signed tokens with `sub`, `role`, `exp`, `iat`.
- **Dependencies (`dependencies.py`):**
  - `get_current_user`: Validates Bearer JWT, verifies `user_id` exists in `users`, checks `is_active`, and enforces `session_revoked_before` (`iat <= revoked_dt.timestamp()` -> `401`).
  - `get_optional_current_user`: Returns `None` when unauthenticated (used by public-capable `/analyze/*` and `Organization` investigation reads).
  - Role guards: `require_admin`, `require_reviewer`, `require_analyst`.

---

## 4. Database Collections & Indexes (`backend/app/database/`)

Verified against live `trustlens_ai` MongoDB:
- `investigations`: `5` docs; live indexes `['_id_', 'investigation_id_1', 'status_1', 'severity_1', 'created_at_-1']`. *(Note: `owner_id_1` is defined in `indexes.py` and awaits `init_database_indexes()` startup run.)*
- `analyses`: `263` docs; indexes `['_id_', 'analysis_id_1', 'user_id_1', 'created_at_-1', 'threat_level_1', 'analysis_type_1']`.
- `scam_campaigns`: `47` docs; indexes `['_id_', 'campaign_id_1', 'status_1', 'last_activity_-1', 'targeted_entity_1']`.
- `users`: `2` docs; indexes `['_id_', 'email_1', 'role_1', 'created_at_-1']`.
- `audit_logs`: `433` docs; indexes `['_id_', 'audit_id_1', 'timestamp_-1', 'user_id_1', 'action_1']`.
- `threat_indicators`, `scam_reports`, `automation_logs`, `model_evaluations`, `model_registry`, `suspicious_urls`: Present and indexed.

---

## 5. Duplicate / Overlapping Services & Modules Identified

| Module A | Module B | Assessment & Disposition |
| :--- | :--- | :--- |
| `backend/app/config/settings.py` | `backend/app/core/config.py` | **Legacy Duplicate:** `main.py` uses `config/settings.py`. Consolidate carefully in cleanup phase. |
| `backend/app/database/manager.py` | `backend/app/core/database.py` | **Legacy Duplicate:** `main.py` uses `database/manager.py`. Keep until all scripts migrate. |
| `backend/app/schemas/*.py` | `backend/app/models/schemas.py` | **Legacy Schema File:** Official routes use `schemas/`; `models/schemas.py` serves legacy `v1/routers/`. |
| `backend/app/ml_engine/engine.py` | `backend/app/services/ml_service.py` | **Partial Overlap:** Both wrap inference; `SentenceTransformer` singleton (`get_shared_sentence_transformer`) resolved duplicate RAM load (`750.12 MB`). |
| `backend/app/services/report_service.py` | `backend/app/services/reporting_service.py` | **Not Duplicate:** `report_service.py` handles community `scam_reports` CRUD/review; `reporting_service.py` handles JSON/STIX 2.1 report generation. |
| `backend/app/api/v1/routers/{health,campaigns}.py` | `backend/app/api/routes/{health,campaigns}.py` | **Unmounted Legacy Routers:** Safe to archive after verifying zero external imports. |

---

## 6. Missing Endpoints Identified (Planned for Phase 3.x)

1. `POST /api/v1/auth/refresh` — Refresh token rotation for web & Android clients (Phase 3.11).
2. `POST /api/v1/auth/resend-verification` — Resend email verification token (Phase 3.12).
3. `POST /api/v1/auth/forgot-password` & `POST /api/v1/auth/reset-password` & `POST /api/v1/auth/change-password` — Token-based password recovery (Phase 3.13).
4. `GET /api/v1/auth/export-data` & `DELETE /api/v1/auth/account` — Self-service GDPR/Google Play data export & account deletion (Phases 3.15–3.16).
5. `GET /api/v1/investigations/{id}/export` — Case-scoped JSON & STIX 2.1 export enforcing `Private` BOLA rules (Phase 3.33).
