# TRUSTLENS AI — NON-FUNCTIONAL REQUIREMENTS

---

1. **Security & Privacy:** `bcrypt` (`rounds=12`), `HS256` JWTs, OWASP headers (`nosniff`, `DENY`, `HSTS`), explicit CORS, `PIL.Image.verify()` upload checks (`<=10MB`), zero-hop URL inspection (never fetch user URLs), raw message redaction in automated alerts, and `/docs` disabled when `APP_ENV=production` & `DEBUG=false`.
2. **Authentication & RBAC:** Strict enforcement of `user` (own analyses only), `analyst` (all analyses, review queue, automation, training submit/compare), and `admin` (model promotion).
3. **Performance & Resource Budget:** Backend RSS `~750 MB` via shared `SentenceTransformer` singleton; text inference `p50 ~105 ms`, URL inference `p50 ~2.6 ms`; Render Standard (`2 GB` RAM, 1 worker) fits without expensive GPU hosting.
4. **Reliability & Error Handling:** Structured `400`/`401`/`403`/`404`/`413`/`415`/`422` JSON responses; explicit `unavailable` / `inconclusive` / `insufficient-evidence` states when models or inputs are missing—never mock fallback data.
5. **Logging, Monitoring & Auditability:** Request timing middleware (`RequestLoggingMiddleware`), immutable `audit_logs`, and `automation_logs` with `log_id`.
6. **Accessibility & Responsiveness:** Keyboard-navigable controls (`/` graph search), high-contrast dark SOC surfaces, and responsive layouts across desktop/tablet/mobile.
7. **Data Retention & Scalability:** MongoDB unique indexes (`analysis_id`, `url`, `(indicator_type, indicator_value)`), paginated queries (`page`, `page_size <= 100`), and isolated test data policy.
