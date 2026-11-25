# TRUSTLENS AI — PHASE 0.5 IMPLEMENTATION PLAN

> **Branch:** `remediation/phase-0.5` (recovery tag: `pre-phase-0.5-recovery`)  
> **Date:** November 25, 2026

---

## Planned Files & Changes

1. **Consolidate Model Loading (Zero Prediction Changes):**
   - `ml/campaign_detection/embeddings.py`: Add a thread-safe (`threading.Lock`) process-wide singleton cache (`_MODEL_CACHE`) for `SentenceTransformer(model_name)` so `ProductionMLEngine`, `MLOrchestrationService`, and `CampaignInferenceEngine` share one loaded model instance instead of allocating 3 separate copies (`~959 MB` RSS).
   - `tests/test_model_loading_singleton.py`: Add unit test verifying repeated instantiations of `CampaignEmbeddingEngine` and `ProductionMLEngine` reuse the exact same `SentenceTransformer` object (`is` identity check).

2. **Fix MongoDB `threat_indicators` Index Definitions:**
   - `backend/app/database/indexes.py`: Update `COLL_THREAT_INDICATORS` index spec from `("type", "value")` / `("severity",)` to `("indicator_type", 1), ("indicator_value", 1)` (`unique=True`), `("status", 1)`, `("last_seen", -1)` matching actual documents; safely drop legacy `type_1_value_1` if present without touching document data; verify with `explain()`.

3. **Resolve Telemetry Router Duplication:**
   - `backend/app/api/v1/routers/telemetry.py`: Replace hardcoded `0`s and static `top_tactics` with live calls to `analytics_service.get_overview()`, preserving `TelemetrySummaryResponse` compatibility without fabricating metrics.

4. **Resolve 3 Failing `tests/test_n8n_automation.py` Tests & Safe Cleanup:**
   - Remove confirmed safe Category A / superseded items (after reference check):
     - Root `capture_*.py` scripts (`8` files) and stale JSON dumps (`route_and_viewport_qa_results.json`, `backend_ml_integration_results.json`).
     - Superseded n8n draft JSONs (`01_dataset_monitoring.json`, `02_automated_ml_training.json`, `03_model_evaluation_registration.json`, `04_suspicious_campaign_alerts.json`, `threat_intel_pipeline.json`) so `n8n/workflows/0*.json` contains exactly the `6` Phase 4.2 workflows.
   - Add descriptive `notes` to all nodes in `n8n/workflows/01..06*.json`.
   - Update `tests/test_n8n_automation.py` to use permitted feed source `"URLhaus_Threat_Feed"` and assert the real Phase 4.2 `analyses_performed` daily summary schema.

5. **Next.js Security Audit & ESLint Setup:**
   - `frontend/package.json`: Install `eslint` + `eslint-config-next` compatible with `next@14.2.35` (preserving `.eslintrc.json`), run `npm run lint`, and fix genuine lint errors.
   - Document `next@14.2.35` npm advisories (`fixAvailable: 16.4.6`, `isSemVerMajor: true`) without breaking Next 14 / React 18 via blind `--force`.
