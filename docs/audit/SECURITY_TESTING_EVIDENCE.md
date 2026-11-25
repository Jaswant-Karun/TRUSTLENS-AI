# TRUSTLENS AI — Security Testing Program Evidence Report

**Environment:** Isolated FastAPI `TestClient` with `InMemoryDatabaseFallback` and mocked network socket guards (`socket.getaddrinfo` blocked).  
**Test Suite:** `tests/test_security_testing_program.py`

| Category | Test Case & Reproducible Evidence | Outcome |
| :--- | :--- | :--- |
| **1. Broken Access Control** | `test_01_broken_access_control`: Unauthenticated calls to `/api/v1/security/abuse-monitoring`, `/api/v1/reports/verified-training-candidates`, `/api/v1/exports/misp`, `/api/v1/privacy/consent` return `401`; regular `user` role returns `403` on analyst/admin endpoints. | **PASS** |
| **2. Auth Weaknesses** | `test_02_authentication_weaknesses_and_session_revocation`: Revoked JWT (`session_revoked_before`) and tampered JWT return `401`; brute-force login lockout (`test_abuse_protection.py`) returns `429` after 5 failures. | **PASS** |
| **3. IDOR** | `test_03_idor_private_investigation_and_analysis_isolation`: `owner-b` receives `401`/`403` when accessing `owner-a`'s Private investigation (`INV-IDOR-PRIV-1`) or exporting `owner-a`'s analysis (`an-idor-priv-1`). | **PASS** |
| **4. Injection** | `test_04_05_06_injection_xss_and_cors_csrf`: Query probes `$where` / `$ne` blocked with `400` and logged as operational alerts. | **PASS** |
| **5. XSS** | `test_04_05_06_injection_xss_and_cors_csrf`: `<script>` query probe blocked (`400`); API responses enforce `X-Content-Type-Options: nosniff` and `Content-Security-Policy: default-src 'none'; frame-ancestors 'none'`. | **PASS** |
| **6. CSRF / CORS** | `test_04_05_06_injection_xss_and_cors_csrf`: Stateless Bearer JWT auth (no cookie session) + `Origin: https://evil-csrf-site.com` is NOT reflected in `Access-Control-Allow-Origin`. | **PASS** |
| **7. SSRF** | `test_07_ssrf_zero_network_url_analysis`: Analyzing `http://169.254.169.254/latest/meta-data/` and `http://127.0.0.1:8000/admin` with `socket.getaddrinfo` patched to raise `AssertionError` succeeds offline (`live_redirect_followed: false`). | **PASS** |
| **8. Unsafe File Handling** | `test_08_unsafe_file_handling_and_zip_slip`: GIF spoofed as `image/png` rejected (`415`); Zip Slip (`../../pwn.txt`) blocked (`ValueError`). | **PASS** |
| **9. Secret Exposure** | `test_09_10_secret_exposure_and_dependency_report`: Public endpoints do not leak `SECRET_KEY` or default admin password; `APP_ENV=production` refuses default secrets. | **PASS** |
| **10. Dependency Vulnerabilities** | `npm audit` documented in `docs/audit/OWASP_SECURITY_AUDIT_REPORT.md` (`6` frontend advisories: `1` critical `next`, `4` high, `1` moderate); `.venv` lacks `pip`/`pip-audit`/`bandit`. | **DOCUMENTED** |
