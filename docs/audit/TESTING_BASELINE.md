# TRUSTLENS AI — TESTING BASELINE (PHASE 0)

> **Date:** November 25, 2026  
> **Rule:** Only actually executed checks are marked PASSED; blocked/missing dependencies are recorded honestly.

---

## 1. Executed Test Suites

| Suite / Command | Result | Details |
| :--- | :--- | :--- |
| `.\.venv\Scripts\python.exe -m pytest -q` | **PARTIAL (`71 passed, 3 failed`)** | `71` backend/ML/security/risk tests passed in `57.27s`. `3` legacy tests in `tests/test_n8n_automation.py` failed due to Phase 4.2 schema/allowlist/workflow-count updates (`10` `0*.json` files vs `6`, `Test_URLhaus_Feed_*` rejected by allowlist, `telemetry_24h` replaced by `analyses_performed`). |
| `npx tsc --noEmit` (`frontend/`) | **PASSED** | `0` TypeScript errors. |
| `npm run build` (`frontend/`) | **PASSED** | `19/19` Next.js routes compiled (`exit 0`). |
| `.\.venv\Scripts\python.exe test_phase4_frontend_ml.py` | **PASSED** | `8` frontend routes `HTTP 200` + `3` proxy-to-backend ML parity checks passed. |
| `.\.venv\Scripts\python.exe test_phase4_1_workspaces.py` | **PASSED** | Threat Library (`267` items, 7 facets), Analytics (`171` analyses), 5 report types, JSON & STIX 2.1 exports, RBAC (`401`/`403`) passed. |
| `.\.venv\Scripts\python.exe test_phase4_2_n8n.py` | **PASSED** | All `6` Phase 4.2 n8n workflow JSONs & backend orchestration endpoints passed. |
| `.\.venv\Scripts\python.exe test_phase5_audit.py` | **PASSED** | `17` frontend routes `HTTP 200`, security checks, `300+300` ML held-out spot check, latency & concurrency passed. |

## 2. Blocked / Not Run Tests

| Check | Status | Exact Reason |
| :--- | :--- | :--- |
| `npm run lint` (`next lint`) | **BLOCKED** | `ESLint must be installed: npm install --save-dev eslint` in `frontend/node_modules`. |
| Live Chrome DevTools Browser QA | **BLOCKED** | `DevToolsActivePort` not found (`chrome://inspect/#remote-debugging` not enabled). |
| Live n8n Server Workflow Import/Trigger | **BLOCKED** | No n8n daemon running on port `5678`. |
| Public Cloud Deployment Verification (Vercel/Render/Atlas) | **BLOCKED** | No `vercel`/`render` CLI or cloud credentials configured locally. |
| `pip-audit` | **NOT TESTED** | `pip` module absent in `uv`-managed `.venv`. |
