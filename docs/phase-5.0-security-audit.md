# TRUSTLENS AI — PHASE 5.0: APPLICATION SECURITY AUDIT

> **Scope:** Auth, Password Hashing, JWT, CORS, Secrets, Uploads, Injection, XSS, RBAC, Rate Limiting, Dependencies  
> **Constraint:** Submitted messages, files, and URLs treated as untrusted input; zero suspicious URLs visited.  
> **Date:** November 25, 2026

---

## 1. Security Controls Verification Matrix

| Control | Status | Evidence / Observed Result |
| :--- | :--- | :--- |
| **Password Hashing** | **PASSED** | [`password.py`](file:///c:/Users/jaswant%20karun/TRUSTLENS%20AI/backend/app/security/password.py) uses `bcrypt` (`rounds=12`, automatic salt); verified `$2b$` hash & verification. |
| **JWT Signature & Expiry** | **PASSED** | [`jwt.py`](file:///c:/Users/jaswant%20karun/TRUSTLENS%20AI/backend/app/security/jwt.py) enforces `HS256` signature & `exp`/`iat` claims; invalid token -> `401`. |
| **OWASP Security Headers** | **PASSED** | [`security_headers.py`](file:///c:/Users/jaswant%20karun/TRUSTLENS%20AI/backend/app/middleware/security_headers.py) injects `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `X-XSS-Protection`, `Referrer-Policy`, `Strict-Transport-Security`. |
| **CORS Policy** | **PASSED** | [`main.py`](file:///c:/Users/jaswant%20karun/TRUSTLENS%20AI/backend/app/main.py) uses explicit `cors_origins` list; disallowed origin received `ACAO='none'`. |
| **File Upload Validation** | **PASSED** | [`ocr_service.py`](file:///c:/Users/jaswant%20karun/TRUSTLENS%20AI/backend/app/services/ocr_service.py) rejects non-image MIME (`415`), 0-byte (`400`), corrupted bytes (`400`), and >10MB (`413`) via `PIL.Image.verify()`. |
| **NoSQL / Schema Injection** | **PASSED** | `POST /auth/login` with `{"$ne": ""}` rejected by Pydantic (`422`). |
| **XSS Input Handling** | **PASSED** | `<script>alert(1)</script>` in `/threat-library?search=...` safely escaped/matched `0` records (`HTTP 200`). |
| **Authorization (RBAC)** | **PASSED** | `401` unauth `/analyses`; `403` non-analyst `/reports/{id}/review`; `403` non-admin `/training/jobs`. |
| **Zero-Hop URL Inspection** | **PASSED** | [`analyze.py`](file:///c:/Users/jaswant%20karun/TRUSTLENS%20AI/backend/app/api/routes/analyze.py) & `PhishingURLDetector` extract lexical features only; no outbound HTTP requests to submitted URLs. |
| **Environment Secrets (`.env`)** | **FAILED** *(Dev Fallback)* | Root `.env` is absent (`Test-Path ".env"` -> `False`); [`settings.py`](file:///c:/Users/jaswant%20karun/TRUSTLENS%20AI/backend/app/config/settings.py) falls back to default dev `SECRET_KEY`, `ADMIN_DEFAULT_PASSWORD`, and `DEBUG=True`. |
| **Frontend Dependencies (`npm audit`)** | **FAILED** *(2 Vulns)* | `npm audit --json` reported `2` vulnerabilities (`1` critical, `1` high, `0` moderate, `0` low) in `next@14.2.35` (including `GHSA-9g9p-9gw9-jx7f`). |
| **Python Dependencies (`pip-audit`)** | **NOT TESTED** | `.venv` has no `pip` / `pip-audit` module installed (managed externally via `uv`). |

---

## 2. Required Pre-Production Remediations

1. **Provision Production `.env`:** Set strong random `SECRET_KEY`, rotate `ADMIN_DEFAULT_PASSWORD`, set `DEBUG=False`, and set `N8N_WEBHOOK_SECRET` before any non-local deployment.
2. **Upgrade `next`:** Upgrade `next` (`14.2.35`) to a patched release resolving the `1` critical and `1` high advisory reported by `npm audit`.
