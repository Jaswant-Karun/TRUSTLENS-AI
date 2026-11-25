# TRUSTLENS AI — PHASE 2.4 FINAL REPORT: CAMPAIGN DOSSIER JSON TO MONGODB SYNCHRONIZATION

## 1. Objective & Scope

Synchronize the production campaign dossier dataset (`ml/artifacts/campaign_detection/campaign_dossiers.json`) into the MongoDB `scam_campaigns` collection in a repeatable, traceable, safe, and idempotent manner, without deleting existing database records, inventing missing attributes, or overwriting human-verified campaign records.

## 2. Source Data Inventory

- **Production source file:** `ml/artifacts/campaign_detection/campaign_dossiers.json` (57,563 bytes, 47 campaign cluster objects).
- **Non-production candidate file (excluded from sync):** `ml/artifacts/campaign_detection/v2.4_candidate/campaign_dossiers.json` (74,124 bytes). The synchronization service targets only `ml/artifacts/campaign_detection/campaign_dossiers.json`.
- **Target MongoDB collection:** `scam_campaigns` (database `trustlens_ai`).

### Existing `scam_campaigns` Indexes Verified

- `_id_` (`_id: 1`)
- `campaign_id_1` (`campaign_id: 1`, `unique: True`, `background: True`)
- `status_1` (`status: 1`, `background: True`)
- `last_activity_-1` (`last_activity: -1`, `background: True`)
- `targeted_entity_1` (`targeted_entity: 1`, `background: True`)

## 3. Source-to-Destination Field Mapping

Implemented in `CampaignIntelligenceService.sync_campaigns_from_dossiers` (`backend/app/services/campaign_service.py`):

| Source Field (`campaign_dossiers.json`) | Destination Field (`scam_campaigns`) | Type | Validation / Transformation | Optional |
| :--- | :--- | :--- | :--- | :--- |
| `cluster_id` | `campaign_id` | `str` | Cast via `str(int(d["cluster_id"]))` to match `get_campaign_by_id` query `{"campaign_id": str(campaign_id)}` | No |
| `cluster_id` | `cluster_id` | `int` | Cast via `int(d["cluster_id"])`; missing raises `ValueError` | No |
| `campaign_name` | `campaign_name` | `str` | Stripped non-empty string; empty raises `ValueError` | No |
| `targeted_institution` | `targeted_entity` | `str` | Defaults to `"Generic / Unspecified Institution"` if falsy | Yes |
| `sample_count` | `cluster_size` | `int` | Cast via `int(d.get("sample_count") or 1)` | Yes |
| `percentage_of_threats` | `percentage_of_threats` | `float \| None` | Cast to `float` when not `None`, else `None` | Yes |
| `cluster_cohesion_score` | `cohesion_score` | `float` | Validated `0.0 <= cohesion <= 1.0`; out-of-range raises `ValueError` | No |
| `predominant_categories` | `primary_tactics` | `list[str]` | `list(categories.keys())` if `dict`, else `[]` | Yes |
| `predominant_categories` | `predominant_categories` | `dict` | Preserved as `dict` if `dict`, else `{}` | Yes |
| `exemplar_message` | `exemplar_message` | `str` | `str(d.get("exemplar_message") or "")` | Yes |
| `shared_phrases` | `shared_phrases` | `list` | `list(d.get("shared_phrases") or [])` | Yes |
| `shared_indicators` | `shared_iocs` | `dict` | Preserved as `dict` if `dict`, else `{}` | Yes |
| `soc_legal_disclaimer` | `legal_disclaimer` | `str` | Defaults to standard non-attribution clustering disclaimer if absent | Yes |
| *(file path)* | `source_provenance` | `str` | Normalized path `"ml/artifacts/campaign_detection/campaign_dossiers.json"` | System |
| *(file bytes)* | `source_sha256` | `str` | SHA-256 hex digest of raw `campaign_dossiers.json` bytes | System |
| *(mapped payload)* | `content_hash` | `str` | SHA-256 hex digest of `json.dumps(mapped, sort_keys=True)` | System |
| *(insert only)* | `status` | `str` | Set to `"active"` on initial insert | System |
| *(insert only)* | `verification_status` | `str` | Set to `"automated_clustering"` on initial insert | System |
| *(timestamps)* | `discovered_at`, `last_activity`, `created_at`, `updated_at` | `datetime` | UTC timestamps (`datetime.now(timezone.utc)`) | System |

## 4. Implementation Summary

1. **Synchronization Service (`backend/app/services/campaign_service.py`)**
   - Added `sync_campaigns_from_dossiers(self, dry_run: bool = False, actor_id: str = "system")`.
   - Computes `source_sha256` over the raw JSON file and `content_hash` per normalized record.
   - **Conflict & Idempotency Rules:**
     - If an existing record has `verification_status == "verified"`, it is skipped (`skipped += 1`) and never overwritten.
     - If an existing record has an identical `content_hash`, it is skipped (`skipped += 1`).
     - If `dry_run=True`, counts are computed and returned without writing to `scam_campaigns` or `audit_logs`.
     - When `dry_run=False`, records an audit event (`action: "campaigns_synchronized"`, `resource_type: "scam_campaigns"`, `resource_id: "bulk_sync"`) in `audit_logs`.
2. **Admin-Gated Sync Endpoint (`backend/app/api/routes/campaigns.py`)**
   - Added `POST /api/v1/campaigns/sync` protected by `require_admin`, accepting `dry_run: bool = Query(False)`.
3. **Automated Tests (`tests/test_phase2_4_campaign_sync.py`)**
   - Verifies RBAC (`401`/`403` for unauthenticated and non-admin callers), admin dry-run, initial and repeat sync idempotency, database count (`47`), and campaign read endpoints (`GET /api/v1/campaigns` and `GET /api/v1/campaigns/11`).

## 5. Verification Results

### 5.1 Live Dry-Run, Initial Sync, Repeat Sync, and Sample Check (`task-5524`)

- **Dry-run:** `inserted=47, updated=0, skipped=0`, `db_count=0`
- **Initial Sync:** `inserted=47, updated=0, skipped=0, failed=0`, `db_count=47`
- **Repeat Sync:** `inserted=0, updated=0, skipped=47, failed=0`, `db_count=47` (0 duplicates)
- **Sample Record (`campaign_id="11"`):**
  - `campaign_name`: `Campaign Cluster #11 — Generic / Unspecified Institution`
  - `cluster_size`: `254`
  - `cohesion_score`: `0.8193`
  - `source_provenance`: `ml/artifacts/campaign_detection/campaign_dossiers.json`

### 5.2 MongoDB Query Plan Verification (`explain`)

- Query: `{"find": "scam_campaigns", "filter": {"campaign_id": "11"}}`
- Observed `winningPlan`: `{'isCached': False, 'stage': 'EXPRESS_IXSCAN', 'keyPattern': '{ campaign_id: 1 }', 'indexName': 'campaign_id_1'}`

### 5.3 Pytest Verification

- Command: `.\.venv\Scripts\python.exe -m pytest tests/test_phase2_4_campaign_sync.py -q`
- Result: `1 passed in 19.46s`
