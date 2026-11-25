# TRUSTLENS AI — SECURITY AUDIT (PHASE 0)

> **Constraint:** Untrusted messages, files, and URLs are never executed or visited; zero secrets printed.

---

## 1. Verified Security Controls (`PASSED`)
- **Password Hashing:** `bcrypt` (`rounds=12`) with per-password salt (`backend/app/security/password.py`).
- **JWT & RBAC:** `HS256` signed tokens (`exp`/`iat`), `401` on missing/invalid JWT, `403` on non-analyst report review and non-admin training/promotion.
- **OWASP Headers & CORS:** `SecurityHeadersMiddleware` sets `X-Content-Type-Options`, `X-Frame-Options: DENY`, `X-XSS-Protection`, `Referrer-Policy`, `Strict-Transport-Security`. Explicit `cors_origins` rejects disallowed origins (`ACAO='none'`).
- **Upload & Injection Safety:** `ocr_service.py` enforces MIME (`415`), 0-byte (`400`), corrupt payload (`400` via `PIL.Image.verify()`), and 10MB limit (`413`). Pydantic rejects NoSQL dict injection (`422`); XSS search payloads return `HTTP 200` with `0` matches.
- **Zero-Hop URL Safety & Redaction:** URL scanner never opens submitted URLs; n8n analysis notification sets `message_content_redacted: true`.
- **Production Docs Gating:** `/docs`, `/redoc`, `/openapi.json` disabled when `APP_ENV=production` and `DEBUG=false`.

## 2. Security Risks & Gaps (`FAILED` / `NOT TESTED`)
- **Absent Root `.env` (`FAILED` for Prod):** `settings.py` falls back to dev `SECRET_KEY`, `ADMIN_DEFAULT_PASSWORD`, and `DEBUG=True` when `.env` is absent.
- **Frontend Dependency Advisories (`FAILED`):** `npm audit --json` in `frontend/` reported `2` vulnerabilities (`1` critical, `1` high) in `next@14.2.35`.
- **Python `pip-audit` (`NOT TESTED`):** `pip` is not installed in the `uv`-managed `.venv`.
- **Unauthenticated Investigation Endpoints:** `GET/POST /api/v1/investigations*` currently have no JWT requirement (`Public`). Review whether `POST /investigations` should require authentication.
