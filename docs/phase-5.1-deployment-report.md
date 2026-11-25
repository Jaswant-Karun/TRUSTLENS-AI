# TRUSTLENS AI — PHASE 5.1: DEPLOYMENT REPORT

> **Git Remote:** `https://github.com/Jaswant-Karun/TRUSTLENS-AI.git`  
> **Local Production Build Verified:** Frontend `http://localhost:3000`, Backend `http://127.0.0.1:8000`  
> **External Cloud Status:** **BLOCKED / NOT DEPLOYED** (No `vercel` / `render` CLI or cloud credentials in environment)  
> **Date:** November 25, 2026

---

## 1. Pre-Deployment Audit & Configuration Hardening

1. **Frontend API Rewrites ([`next.config.mjs`](file:///c:/Users/jaswant%20karun/TRUSTLENS%20AI/frontend/next.config.mjs)):** Updated hardcoded `http://127.0.0.1:8000/api/v1/:path*` rewrite destination to `process.env.BACKEND_API_URL || "http://127.0.0.1:8000"` so Vercel deployments proxy cleanly to Render.
2. **Production API Docs Policy ([`main.py`](file:///c:/Users/jaswant%20karun/TRUSTLENS%20AI/backend/app/main.py)):** Disabled `/docs`, `/redoc`, and `/openapi.json` (`None`) when `APP_ENV=production` and `DEBUG=false` (verified via Python runtime check: `docs_url= None openapi_url= None`).
3. **Deployment Manifests Created:**
   - [`render.yaml`](file:///c:/Users/jaswant%20karun/TRUSTLENS%20AI/render.yaml): Python `3.12.0`, `pip install -r requirements.txt`, `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT --workers 1`, health check `/api/v1/health`, `plan: standard` (`2 GB` RAM).
   - [`frontend/vercel.json`](file:///c:/Users/jaswant%20karun/TRUSTLENS%20AI/frontend/vercel.json): Next.js build (`npm run build`) + OWASP security headers.

---

## 2. Model Deployment & Memory Constraints

- **Measured Process RSS Memory:** `958.96 MB` (driven by `SentenceTransformer` + PyTorch weights). Render's `512 MB` starter/free tier will OOM-kill the service; `plan: standard` (`2 GB` RAM) is required.
- **Artifact Checksums:** `CentralModelLoader` verified SHA-256 hashes for all 4 production models (`trustlens-text-v1.0-prod`, `trustlens-url-v1.0-prod`, `trustlens-tactics-v1.0-prod`, `trustlens-campaign-v1.0-prod`).
- **Git Exclusion of Binaries (`.gitignore`):** `.joblib`, `.onnx`, `.bin`, `.safetensors`, and `.pt` files are excluded from Git. Production Render deployments must mount a Persistent Disk or fetch approved production artifacts from object storage at startup.

---

## 3. Cloud Deployment Readiness Status

| Target | Manifest / Config | Live Cloud Status | Blocker / Requirement |
| :--- | :--- | :--- | :--- |
| **Vercel (Frontend)** | `frontend/vercel.json`, `next.config.mjs` | **NOT DEPLOYED** | Requires `vercel` CLI / GitHub-Vercel integration + `BACKEND_API_URL` env var |
| **Render (Backend)** | `render.yaml`, `requirements.txt` | **NOT DEPLOYED** | Requires Render account/API key + `2 GB` plan + artifact storage |
| **MongoDB Atlas** | `MONGODB_URI` (`sync: false`) | **NOT TESTED** (Local MongoDB `27017` verified) | Requires cloud Atlas cluster URI & IP allowlist |
| **n8n (Hosted)** | `n8n/workflows/*.json` | **NOT DEPLOYED** | Requires separate n8n instance + `$env.TRUSTLENS_*` secrets |
