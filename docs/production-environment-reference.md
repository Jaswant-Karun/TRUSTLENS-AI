# TRUSTLENS AI — PRODUCTION ENVIRONMENT REFERENCE

> **Security Rule:** Never commit actual secret values to Git. Configure these variables in Render, Vercel, and n8n secret stores.

---

## 1. Backend Environment Variables (Render)

| Variable | Required | Example / Notes |
| :--- | :--- | :--- |
| `APP_ENV` | Yes | `production` |
| `DEBUG` | Yes | `false` (disables `/docs`, `/redoc`, `/openapi.json`, and stack detail) |
| `SECRET_KEY` | Yes | Random 32+ byte hex secret for HS256 JWT signing |
| `MONGODB_URI` | Yes | `mongodb+srv://<user>:<pass>@<cluster>.mongodb.net/?retryWrites=true&w=majority` |
| `MONGODB_DB_NAME` | Yes | `trustlens_ai` |
| `ALLOWED_ORIGINS` | Yes | `https://<your-vercel-domain>.vercel.app` |
| `ADMIN_DEFAULT_EMAIL` | Yes | Admin bootstrap email |
| `ADMIN_DEFAULT_PASSWORD` | Yes | Strong initial admin password (rotate after first login) |
| `N8N_WEBHOOK_SECRET` | Yes | Shared secret matching `TRUSTLENS_AUTOMATION_SECRET` in n8n |
| `ML_ARTIFACTS_DIR` | Optional | `ml/artifacts` (ensure persistent disk or startup artifact sync) |

---

## 2. Frontend Environment Variables (Vercel)

| Variable | Required | Example / Notes |
| :--- | :--- | :--- |
| `BACKEND_API_URL` | Yes | `https://<your-render-service>.onrender.com` (used by `next.config.mjs` rewrites) |
| `NEXT_PUBLIC_API_URL` | Optional | `/api/v1` (default; routes through Vercel rewrite proxy) |

---

## 3. Automation Environment Variables (n8n)

| Variable | Required | Example / Notes |
| :--- | :--- | :--- |
| `TRUSTLENS_API_URL` | Yes | `https://<your-render-service>.onrender.com` |
| `TRUSTLENS_ADMIN_EMAIL` | Yes | Service/admin account email |
| `TRUSTLENS_ADMIN_PASSWORD` | Yes | Service/admin account password |
| `TRUSTLENS_AUTOMATION_SECRET` | Yes | Shared secret checked on `X-TrustLens-Automation-Secret` |
