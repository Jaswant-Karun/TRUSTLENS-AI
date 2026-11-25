# TRUSTLENS AI — PRODUCT ARCHITECTURE GAPS (PHASE 0)

> **Product Goal:** Coherent ThreatQ-inspired fraud intelligence workflow — not disconnected dashboard cards.

---

## 1. Workflow Readiness Assessment (Workflows 1–11)

1. **Submit text / URL / screenshot (Workflows 1–5):** **Ready.** Dedicated & comprehensive analysis pages validate inputs safely, run SHA-256 verified ML models, return calibrated risk + tactics + SHAP/feature evidence, and clearly separate ML, Threat Intel, and Human Review.
2. **Save and revisit investigations & explore 1-hop relationships (Workflows 6–7):** **Partially Ready.** `/investigations` and `/investigations/[id]` support creation, graph exploration, and 1-hop MongoDB expansion; however, `POST /investigations` is unauthenticated, `INV-2026-0011` has `0` timeline events, and promoting an individual analysis directly into an investigation node can be streamlined.
3. **Report suspicious content & authorized review (Workflows 8–9):** **Ready.** `/reports` + `POST /api/v1/reports/{id}/review` (`require_analyst_or_admin`).
4. **Share/export verified intelligence & track history (Workflows 10–11):** **Ready.** `/threat-library`, `/history`, `/reports` (5 report types, JSON, STIX 2.1).

## 2. Priority Architectural & Coherence Gaps

1. **Duplicate ML Model Loader (`958.96 MB` RSS):** Consolidate `ml_service.py` and `ProductionMLEngine` so `SentenceTransformer` loads once (`CentralModelLoader`), cutting memory footprint for Render (`2 GB`).
2. **Frontend Layout Theme Split (`AppShell.tsx` vs `TopNavigation.tsx`):** `app/layout.tsx` wraps all routes in light-themed `AppShell.tsx`, conflicting with dark SOC workspaces (`/investigations`, `/threat-library`, `/analytics`).
3. **MongoDB Index Mismatch (`threat_indicators`):** Align `indexes.py` (`type`, `value`) with actual document fields (`indicator_type`, `indicator_value`).
4. **Legacy `v1/routers/telemetry.py` & `tests/test_n8n_automation.py`:** Replace or remove hardcoded-zero `telemetry.py` and update `tests/test_n8n_automation.py` to match Phase 4.2.
5. **Recommended Coherent Navigation:** Keep `/investigations` as the primary ThreatQ workspace, `/analyze/*` as the 4-tab intake workbench, `/threat-library` as the unified intelligence repository, `/analytics` as live DB telemetry, and `/reports` as triage + STIX/JSON export.
