# TRUSTLENS AI — DUPLICATE CODE & FUNCTION AUDIT (PHASE 0)

> **Policy:** Behavioral equivalence, inputs, outputs, side effects, and callers were checked before classifying items as duplicates. No files were deleted or merged in Phase 0.

---

## 1. Duplicate ML Model Loading (`SentenceTransformer` Loaded Multiple Times)
- **Files:** `backend/app/ml_engine/engine.py` (`ProductionMLEngine` + `CentralModelLoader`) vs `backend/app/services/ml_service.py` (`MLOrchestrationService`) vs `ml/campaign_detection/clusterer.py`.
- **Evidence:** During FastAPI startup and `test_phase5_audit.py`, `Loading weights: 100% 103/103` (`paraphrase-multilingual-MiniLM-L12-v2`) executes multiple times, driving Python RSS memory to `958.96 MB`.
- **Overlap:** Partially overlapping (`CentralModelLoader` enforces SHA-256 registry checksums; `MLOrchestrationService` instantiates `ml/*` classes directly).
- **Retain:** `CentralModelLoader` / `ProductionMLEngine` as the single SHA-256 verified model registry loader; route `ml_service.py` calls through it.
- **Consolidation Risk:** Medium — requires verifying identical return schemas for `scan_text`, `scan_url`, `scan_tactics`, and `cluster_campaigns` used by `tests/` and `v1/routers/`.

## 2. Duplicate / Competing API Router Trees
- **Files:** `backend/app/api/routes/` (primary v1 routes) vs `backend/app/api/v1/routers/` (`health.py`, `scans.py`, `urls.py`, `tactics.py`, `telemetry.py`, `campaigns.py`).
- **Evidence:** Both are mounted in `backend/app/api/v1/api.py`. `v1/routers/telemetry.py` returns hardcoded `0`s while `routes/analytics.py` queries MongoDB.
- **Retain:** `backend/app/api/routes/*` as canonical source of truth.
- **Consolidation Risk:** Low-Medium — check if `tests/test_ml_inference_api.py` calls legacy `/scans`, `/urls`, `/tactics` paths before deprecating.

## 3. Duplicate / Competing Frontend Navigation & Shell Components
- **Files:** `frontend/components/investigation/TopNavigation.tsx` vs `frontend/components/Navbar.tsx` vs `frontend/components/ui/TopNavbar.tsx` vs `frontend/components/AppShell.tsx`.
- **Evidence:** `app/layout.tsx` wraps pages in `AppShell.tsx` (light theme), while ThreatQ pages (`/investigations`, `/threat-library`, `/analytics`) render `TopNavigation.tsx` (dark SOC `#171C25`).
- **Retain:** `TopNavigation.tsx` as the unified dark SOC top bar; refactor `AppShell.tsx` to avoid double-chrome or light-mode clash.
- **Consolidation Risk:** Low — requires checking `/dashboard`, `/history`, `/models`, `/reports`, `/settings` layout wrapping.

## 4. Duplicate Graph Components
- **Files:** `frontend/components/KillChainGraph.tsx` vs `frontend/components/investigation/ThreatGraph.tsx`.
- **Evidence:** `ThreatGraph.tsx` is the active interactive SVG graph in `/investigations/[id]`.
- **Retain:** `frontend/components/investigation/ThreatGraph.tsx`.

## 5. Static Mock Data File Alongside Live API Client
- **Files:** `frontend/components/investigation/mockData.ts` vs `frontend/lib/api.ts`.
- **Evidence:** `/investigations/[id]` fetches live MongoDB data via `lib/api.ts`; `mockData.ts` is static fixture data.
- **Retain:** `frontend/lib/api.ts`. Review `mockData.ts` for removal after confirming zero imports.
