# TRUSTLENS AI — PHASE 5.1: PRODUCTION TEST REPORT

> **Scope:** Live Local Production-Build Services (`http://127.0.0.1:8000` & `http://localhost:3000`) vs External Public Cloud URLs  
> **Date:** November 25, 2026

---

## 1. Local Production-Build Verification (`PASSED`)

All checks below received actual live responses from the local FastAPI + Next.js 14 production servers (`npm run build` + `next start`, `uvicorn backend.app.main:app`):

| Check | Endpoint | Result |
| :--- | :--- | :--- |
| **Health Check** | `GET /api/v1/health` | **PASSED** (`HTTP 200`, `p50=3.05 ms`) |
| **Authentication** | `POST /api/v1/auth/login` + RBAC | **PASSED** (`401` unauth, `403` non-admin, `200` admin JWT) |
| **Text Analysis** | `POST /api/v1/analyze/text` | **PASSED** (Proxy & Backend parity: `threat_level=high, risk=0.75`) |
| **URL Analysis** | `POST /api/v1/analyze/url` | **PASSED** (Proxy & Backend parity: `threat_level=critical, risk=1.0`) |
| **Graph & Timeline Loading** | `GET /api/v1/investigations/INV-2026-0011/graph`, `/timeline` | **PASSED** (`HTTP 200`, `10` nodes, `p50=6.29 ms`) |
| **Model Metrics** | `GET /api/v1/models`, `/models/metrics` | **PASSED** (`HTTP 200`, 4 SHA-256 verified models) |
| **Report Export** | `GET /api/v1/exports/json`, `/exports/stix` | **PASSED** (`HTTP 200`, valid JSON & STIX 2.1 bundle) |
| **Production Docs Gating** | `APP_ENV=production DEBUG=false` | **PASSED** (`docs_url=None`, `openapi_url=None`) |

---

## 2. Public Cloud URL Verification (`BLOCKED`)

No public Vercel (`*.vercel.app`), Render (`*.onrender.com`), MongoDB Atlas Cloud, or hosted n8n URLs were provisioned or accessible from this local workspace (`vercel` and `render` CLIs are not installed and no cloud tokens are configured). Therefore, live public-URL tests are classified as **BLOCKED** pending cloud provisioning by the repository owner.
