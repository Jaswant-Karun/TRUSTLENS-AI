# TRUSTLENS AI — OWASP Security Audit Report

**Audit Scope:** Authentication, authorization, session handling, API security, input validation, file uploads, CORS, secrets management, database access, and dependency vulnerabilities.

---

## 1. Automated Security Tool Results
- **Frontend Dependency Scan (`npm audit --json` in `frontend/`):**
  - Total: **6** vulnerabilities (`1 critical`, `4 high`, `1 moderate`, `0 low`, `0 info`).
  - Packages flagged: `next` (critical), `@next/eslint-plugin-next` (high), `eslint-config-next` (high), `glob` (high), `postcss` (high), `minimatch` (moderate) — all have `fixAvailable: true` via Next.js/ESLint major/minor upgrades.
- **Backend Static Sink Scan (`git grep` across `backend/` and `ml/`):**
  - `0` uses of `eval(`, `exec(`, `pickle.load`, `yaml.load(`, `shell=True`, or `verify=False`.
  - `1` `subprocess.run([sys.executable, script], check=True)` in `ml/pipeline/reproducible_pipeline.py` (fixed internal script list, no shell=True, no user input).
- **Python Dependency Scanner (`pip` / `pip-audit` / `bandit`):**
  - `.venv` does not have `pip`, `pip-audit`, or `bandit` installed (`No module named pip`), so automated Python CVE scanning could not run in this environment.

---

## 2. Findings by Severity

### Critical
1. **Frontend `next` Package Vulnerability (`npm audit`) — Open (Tracked)**
   - **OWASP Category:** A06:2021 Vulnerable and Outdated Components
   - **Evidence:** `npm audit` reported `next` (`critical`) and 5 related `high`/`moderate` transitive/dev packages (`@next/eslint-plugin-next`, `eslint-config-next`, `glob`, `postcss`, `minimatch`).
   - **Recommendation:** Schedule a dedicated Next.js upgrade + full frontend build/E2E regression pass rather than applying an unverified breaking major bump.

### High
2. **Optional-Auth Dependency Bypassed Session Revocation & Deactivation — FIXED**
   - **OWASP Category:** A07:2021 Identification and Authentication Failures
   - **File:** `backend/app/security/dependencies.py` (`get_optional_current_user`)
   - **Finding:** Unlike `get_current_user`, `get_optional_current_user` did not check `user.get("is_active", True)` or `session_revoked_before`, allowing logged-out or deactivated JWTs to authenticate on optional-auth endpoints.
   - **Fix Applied:** Enforced `is_active` and `session_revoked_before` checks in `get_optional_current_user()`.

3. **Hardcoded Default `SECRET_KEY` & `ADMIN_DEFAULT_PASSWORD` Permitted in Production — FIXED**
   - **OWASP Category:** A02:2021 Cryptographic Failures / A05:2021 Security Misconfiguration
   - **File:** `backend/app/config/settings.py` & `backend/app/main.py`
   - **Finding:** `AppSettings` fell back to hardcoded defaults even when `APP_ENV=production`.
   - **Fix Applied:** Added `settings.validate_production_security()` called in `lifespan()` to refuse startup in `production` if `SECRET_KEY` is default/`< 32` chars or `ADMIN_DEFAULT_PASSWORD` is left at the default.

### Medium
4. **Image Upload Lacked Decoded Format Verification & Dimension/Pixel Caps — FIXED**
   - **OWASP Category:** A04:2021 Insecure Design / A05:2021 Security Misconfiguration
   - **File:** `backend/app/services/ocr_service.py`
   - **Finding:** Trusted `file.content_type` + `image.verify()` without checking `image.format` against `{JPEG, PNG, WEBP, BMP}` or capping pixel dimensions against decompression bombs.
   - **Fix Applied:** Enforced `Image.MAX_IMAGE_PIXELS = 25_000_000`, `image.format in ALLOWED_PIL_FORMATS`, and `MAX_IMAGE_DIM = 8192`.

### Low
5. **Overly Broad CORS Methods/Headers & Missing API CSP/Permissions Headers — FIXED**
   - **OWASP Category:** A05:2021 Security Misconfiguration
   - **Files:** `backend/app/main.py`, `backend/app/middleware/security_headers.py`
   - **Fix Applied:** Restricted `CORSMiddleware` `allow_methods` and `allow_headers` to explicit allowlists, and added `Permissions-Policy` and `Content-Security-Policy: default-src 'none'; frame-ancestors 'none'` on non-docs API responses.

---

## 3. Verified Secure Controls
- **Database Access:** Parameterized Motor/PyMongo queries with `re.escape()` on regex searches and `owner_id`/`visibility` authorization enforcement.
- **Model Artifact Integrity:** `CentralModelLoader` enforces SHA-256 verification before `joblib.load()`.
- **Rate Limiting:** `RateLimitMiddleware` (`120 req/min` global, `20 req/min` auth) + per-user/IP report submission limits (`10/min`).
