# TRUSTLENS AI — DATABASE & DATA INTEGRITY AUDIT (PHASE 0)

> **Engine:** MongoDB (`motor` async driver) via `backend/app/database/manager.py`  
> **Database:** `trustlens_ai` (11 collections defined in `backend/app/database/collections.py`)

---

## 1. Collection & Index Audit
- **Connection Lifecycle:** Managed in FastAPI `lifespan` (`db_manager.connect()` -> `init_database_indexes()` -> `seed_initial_admin()` -> `db_manager.disconnect()`).
- **Verified Persisted Counts (Phase 4.1 / 5.0):** `analyses` (`152`–`171`), `suspicious_urls` (`11`), `scam_reports` (`4`–`5`), `threat_indicators` (`6`–`8`), `investigations` (`5`), `scam_campaigns` (`0` in MongoDB; served from `ml/artifacts/campaign_detection/campaign_dossiers.json` `47` clusters).
- **Real vs Seeded Data:** `investigations` (`INV-2026-0011`, `INV-2026-0006`, `INV-2026-0138`, `INV-2026-2219`, `INV-2026-7E76`) are baseline seeded dossiers constructed from real HDBSCAN clusters and stored analyses. `INV-2026-0011` currently returns `0` timeline events from `/timeline` despite `10` graph nodes.

## 2. Database Integrity Findings
1. **Index / Field Mismatch (`backend/app/database/indexes.py`):** `COLL_THREAT_INDICATORS` specifies unique index `[("type", 1), ("value", 1)]` and `("severity", 1)`, whereas `automation_service.py` and `threat_library_service.py` store `indicator_type`, `indicator_value`, and `confidence`. This prevents the intended unique index from enforcing deduplication at the MongoDB level.
2. **Campaign Collection Empty (`scam_campaigns: 0 docs`):** `campaign_service.py` falls back cleanly to `campaign_dossiers.json`, but MongoDB-native queries on `scam_campaigns` see 0 documents until synced.
3. **No Geospatial Indexes Used:** Confirmed none required for current schema.
