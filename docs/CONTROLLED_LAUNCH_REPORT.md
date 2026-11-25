# TRUSTLENS AI — Controlled Global Product Launch Report & Long-Term Maintenance Plan

- **Version:** `1.0.0`
- **Launch Mode:** Controlled Phased Rollout (Staging -> Google Play Internal Testing -> Closed Testing -> Staged Production)
- **Scope Policy:** **Do not automatically expand supported regions, languages, or fraud detection claims without validation.**

---

## 1. Controlled Launch Scope & Non-Expansion Guardrails
- **Evaluated Languages:** `English`, `Hindi`, `Hinglish` only.
- **Unsupported / Unverified Languages:** `Tamil`, `Bengali` (0 training/evaluation samples; must remain marked unsupported until curated, evaluated, and approved).
- **Blocked / Non-Production Models:** `fake_investment` tactic classifier remains `Blocked` and excluded from production inference.
- **Claim Boundaries:** TRUSTLENS AI is a probabilistic decision-support tool; no 100% accuracy or universal fraud detection claims are permitted in web UI, Play Store copy, or marketing.

---

## 2. Ten Operational Launch Pillars

| Pillar | Implementation & Controls | Verification / Endpoint |
| :--- | :--- | :--- |
| **1. Production Monitoring** | Structured JSON logs (`RequestLoggingMiddleware`), request IDs, process latency (`ms`), Sentry error tracking (`SENTRY_DSN`, `send_default_pii=False`) | `backend/app/middleware/logging_middleware.py`, `backend/app/main.py` |
| **2. Service Availability Tracking** | Synthetic 60s probes on `/api/v1/health` and `/api/v1/health/slo` tracking DB ping latency, model readiness, and 99.9% SLO | `GET /api/v1/health`, `GET /api/v1/health/slo` |
| **3. User Support & Feedback** | In-app model feedback (`POST /api/v1/models/feedback`), community report moderation (`/reports`), and security/support contact `security@trustlens.ai` | `/reports`, `/methodology`, `POST /api/v1/models/feedback` |
| **4. Incident Response Procedures** | Severity matrix (SEV-1 Outage/Security Breach: 15m ack, immediate Cloud Run traffic rollback; SEV-2 Degraded ML/Feed: 1h ack; SEV-3 UI/Minor: next sprint) | `.github/workflows/deploy-production.yml` auto-rollback |
| **5. Model Performance Monitoring** | Drift, calibration (ECE), prediction confidence tracking, and SHA-256 registry enforcement (`CentralModelLoader`) | `GET /api/v1/models/monitoring`, `GET /api/v1/models/metrics` |
| **6. Threat Feed Health Monitoring** | Scheduled polling (`infra/scripts/run_background_worker.py`) with per-source hourly rate limits, idempotency, and `last_successful_sync_utc` tracking | `GET /api/v1/threat-intel/status` |
| **7. Privacy Request Handling** | Consent management, DPDP/GDPR data export, analysis/account deletion, access logs, and retention preview | `/privacy-policy`, `GET /api/v1/privacy/*` |
| **8. Release Management** | Semantic versioning (`TRUSTLENS_VERSION_CODE` / `TRUSTLENS_VERSION_NAME`), gated CI/CD (`workflow_dispatch` + `DEPLOY_PRODUCTION` confirmation), automated rollback | `.github/workflows/deploy-production.yml` |
| **9. Backup & Recovery Drills** | MongoDB Atlas Continuous Cloud Backup + PITR; automated integrity checks via `infra/scripts/verify_backup_restore.py` and quarterly restore drills | `infra/scripts/verify_backup_restore.py` |
| **10. Usage & Cost Monitoring** | Worker memory cap (`4 GB`, `--workers 1`), `RateLimitMiddleware` abuse protection, and `/api/v1/health/slo` volume counters | `GET /api/v1/health/slo`, `infra/docker-compose.staging.yml` |

---

## 3. Google Play Testing & Submission Tracks
1. **Track 1 — Internal Testing:** Upload signed `app-release.aab` (`ai.trustlens.mobile`, `targetSdkVersion = 36`) via Play App Signing; verify Keystore auth, Camera/Gallery rationale modals, Share-Sheet, offline banner, and back-button handling on physical devices.
2. **Track 2 — Closed Testing:** Expand to vetted beta testers (14-day soak if required for new Play Console developer accounts); monitor Play Console Pre-launch report, crash-free rate (`>= 99.5%`), and ANR rate (`< 0.3%`).
3. **Track 3 — Staged Production Rollout:** Promote only after passing all Launch Acceptance Criteria (`5% -> 20% -> 50% -> 100%`), keeping automatic halt triggers on crash spikes.

---

## 4. Measurable Launch Acceptance Criteria (Go / No-Go Gates)
- **Availability:** `>= 99.9%` uptime on `/api/v1/health` over 7-day staging/internal soak.
- **Latency:** `P95` text & URL inference `<= 1500 ms` (verified baseline: text `820.55 ms`, URL `28.35 ms`, comprehensive `505.55 ms`).
- **Error Rate:** `5xx` API error rate `< 0.5%`; Android crash-free sessions `>= 99.5%`.
- **Security & Privacy:** `0` unencrypted secrets in client/APK, `cleartextTrafficPermitted="false"` in release, `0` critical WCAG violations, and verified `run_migrations.py` + `verify_backup_restore.py`.
- **External Deployment Gate:** Live public HTTPS smoke suite (`infra/scripts/production_smoke_test.py`) must pass against deployed `https://` endpoints before public announcement.

---

## 5. Long-Term Maintenance Plan
- **Daily (Automated):** Health/SLO probes, Sentry error triage, threat-intel worker sync health check, rate-limit/abuse alert review.
- **Weekly:** Review user-submitted feedback (`/api/v1/models/feedback`) and community scam reports moderation queue; verify disk/memory headroom on ML replicas.
- **Monthly:** Dependency CVE audit (`npm audit`, `pip-audit`), Play Store SDK/policy compliance check, and calibration/drift review on `GET /api/v1/models/monitoring`.
- **Quarterly:** Database backup restore drill into isolated staging cluster, JWT/webhook secret rotation, and controlled evaluation of any new language or scam-category candidates before registry promotion.
