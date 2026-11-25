# TRUSTLENS AI — PRODUCT SECURITY & PRIVACY ROADMAP

> **Phase:** 3.0 Security & Privacy Architecture

---

## 1. Current Verified Security Baseline

- `bcrypt` password hashing (`rounds=12`), `HS256` JWT (`exp`/`iat`), RBAC (`user`, `reviewer`, `analyst`, `admin`).
- `SecurityHeadersMiddleware` (`X-Content-Type-Options`, `X-Frame-Options: DENY`, `Referrer-Policy`, `HSTS`) + explicit CORS allowlist.
- Safe image validation (`ocr_service.py`: MIME check, `PIL.Image.verify()`, 10 MB cap) and zero-hop URL inspection (never opens/fetches submitted URLs).
- Phase 2.1–2.4 BOLA & ownership enforcement on `Private` investigations, notes, timelines, and admin-only campaign sync.

---

## 2. Security & Privacy Enhancements Required Before Public Launch

| Domain | Gap / Risk | Target Remediation |
| :--- | :--- | :--- |
| **Secrets & Env** | `settings.py` falls back to dev `SECRET_KEY` when `.env` is missing | Fail fast on startup when `APP_ENV=production` and `SECRET_KEY` is default/weak |
| **Auth Lifecycle** | No email verification, password reset, or refresh token revocation | Add signed email verification tokens, rate-limited password reset, and refresh-token revocation list in MongoDB |
| **Rate Limiting & Abuse** | Basic middleware; public landing + `/auth/*` + `/analyze/*` need per-IP & per-user quotas | Enforce tiered Redis/in-memory rate limits on `/auth/login`, `/auth/register`, `/analyze/*`, and `/reports` |
| **Account Deletion & Export** | Missing self-service GDPR/Play Store data export & deletion | Implement `GET /api/v1/auth/export-data` and `DELETE /api/v1/auth/account` |
| **PII & Content Handling** | Uploaded screenshots/messages may contain OTPs, bank details, or phone numbers | Add optional auto-redaction of sensitive tokens in logs/n8n webhooks (`message_content_redacted: true` already active) and configurable retention TTL for raw uploads |
| **Frontend Dependencies** | `npm audit` flagged advisories in `next@14.2.35` | Plan controlled upgrade to patched Next.js LTS (`15.x` / `16.x` in dedicated dependency phase) |
| **MongoDB Indexes** | `investigations.owner_id_1` defined in `indexes.py` but not yet applied to live DB | Run `ensure_indexes()` on startup / deployment migration |
| **Threat Intel & Model Artifacts** | External feeds (URLhaus) & `.joblib` deserialization risks | Strict URL/domain schema sanitization on feed ingestion; mandatory SHA-256 verification before `joblib.load()` (already enforced in `CentralModelLoader`) |
