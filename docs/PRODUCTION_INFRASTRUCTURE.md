# TRUSTLENS AI — Production Infrastructure & Deployment Architecture

## 1. Resource & ML Memory Sizing (Measured Baseline)
- **On-disk ML artifacts (`ml/artifacts/`):** 86 files totaling **108.83 MB**.
- **In-memory runtime footprint:** Loading `199/199` transformer weights alongside XGBoost, scikit-learn, FastAPI, and Tesseract OCR consumes **~1.2–1.8 GB RAM per worker**.
- **Sizing Decision:** Run **1 Uvicorn worker per container (`--workers 1`)** with **4 GB RAM / 2 vCPU** limits (2 GB reservation) and scale horizontally across replicas instead of multi-worker forking inside a single container.

---

## 2. Infrastructure Evaluation & Configuration

| Layer | Recommended Provider / Config | Rationale & Repo Configuration |
| :--- | :--- | :--- |
| **Frontend Hosting** | **Vercel (Next.js App Router)** or `infra/Dockerfile.frontend` | `frontend/vercel.json` configures security headers (`X-Content-Type-Options`, `X-Frame-Options: DENY`, `Referrer-Policy`). Static Capacitor assets live separately in Android `.aab`. |
| **FastAPI Hosting** | **Cloud Run / AWS ECS Fargate / Render** (`infra/Dockerfile.backend`) | 4 GB RAM, 2 vCPU, `--workers 1`, non-root `trustlens` user, `/api/v1/health` healthcheck, `tesseract-ocr` + `tesseract-ocr-hin` pre-installed. |
| **MongoDB Atlas** | **MongoDB Atlas M10+ Dedicated Cluster** | TLS 1.2+ enforced, VPC peering / private endpoint or strict egress IP allowlist, 14 collection indexes via `init_database_indexes()`. |
| **ML Model Artifact Storage** | **S3 / Cloudflare R2 / GCS** (`MODEL_ARTIFACTS_URI`) | Heavy `.joblib`, `.safetensors`, `.pt`, `.onnx`, `.bin` binaries are excluded in `.gitignore` & `.dockerignore` and synced/SHA-256 verified at boot via `infra/scripts/sync_model_artifacts.py`. |
| **Background Job Processing** | **Scheduled Workers / Cloud Scheduler + Async Queue** | Threat intelligence polling (`cisa_kev`, `phishtank`), notification delivery (`NotificationService`), and retraining locks run out-of-band without blocking inference workers. |
| **Secure Secrets Management** | **Cloud Secret Manager / Vercel Env / GitHub OIDC** | `SECRET_KEY`, `MONGODB_URI`, `ADMIN_DEFAULT_PASSWORD`, `N8N_WEBHOOK_SECRET`, `SENTRY_DSN` injected at runtime. `validate_production_security()` blocks default secrets, `DEBUG=true`, or `localhost` in production. |
| **HTTPS** | **TLS 1.3 Edge Termination + HSTS** | `SecurityHeadersMiddleware` emits `Strict-Transport-Security: max-age=31536000; includeSubDomains`. Android release builds enforce `cleartextTrafficPermitted="false"`. |
| **Domain & DNS** | **Cloudflare DNS (`trustlens.ai`, `api.trustlens.ai`, `staging.trustlens.ai`)** | DNSSEC enabled, strict SSL/TLS mode, CAA records restricting certificate issuance. |
| **Database Backups** | **MongoDB Atlas Continuous Cloud Backup** | Point-in-Time Recovery (PITR) + automated daily snapshots retained per compliance policy + quarterly restore verification drills. |
| **Monitoring** | **Uptime Checks + Structured JSON Logs** | `/api/v1/health` synthetic probes every 60s; `RequestLoggingMiddleware` emits request IDs and latency (`ms`) for P95/P99 alerting and memory/OOM alerts at 80%. |
| **Error Tracking** | **Sentry (`SENTRY_DSN`)** | Configured per environment (`staging` vs `production`) with PII scrubbing enabled so raw user messages/tokens are never captured in stack traces. |

---

## 3. Environment Separation

| Setting | Development (`infra/env/.env.development.example`) | Staging (`infra/env/.env.staging.example`) | Production (`infra/env/.env.production.example`) |
| :--- | :--- | :--- | :--- |
| `APP_ENV` | `development` | `staging` | `production` |
| `DEBUG` | `true` | `false` | `false` (enforced) |
| `MONGODB_URI` | `mongodb://localhost:27017` | `mongodb+srv://...staging...` | `mongodb+srv://...prod...` (`localhost` blocked) |
| `ALLOWED_ORIGINS` | `http://localhost:3000` | `https://staging.trustlens.ai` | `https://trustlens.ai,...` (`localhost` blocked) |
| `MODEL_ARTIFACTS_URI` | Local `ml/artifacts` | `s3://trustlens-ml-artifacts-staging/v2/` | `s3://trustlens-ml-artifacts-prod/v2/` |
| `SENTRY_DSN` | Empty | Staging Sentry DSN | Production Sentry DSN |
