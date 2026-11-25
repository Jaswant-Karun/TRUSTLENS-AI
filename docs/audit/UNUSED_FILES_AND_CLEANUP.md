# TRUSTLENS AI — UNUSED FILES & SAFE CLEANUP MANIFEST (PHASE 0)

> **Deletion Policy:** No files were deleted in Phase 0. All items are classified A/B/C/D with dependency checks and risk levels. Preserve Git history, `.env*`, datasets, model artifacts, and deployment configs.

---

## Category A — Definitely Safe to Remove (After Git Branch Backup)
| File Path | Reason | Reference Check | Risk | Expected Impact |
| :--- | :--- | :--- | :--- | :--- |
| `capture_all_pages.py`, `capture_dashboard_bottom.py`, `capture_dashboard_verified.py`, `capture_design_screenshots.py`, `capture_models_verified.py`, `capture_phase1_2_screenshots.py`, `capture_phase1_validation.py`, `capture_records_intel.py` | Ad-hoc Phase 1 screenshot scripts in repo root | Not imported by `backend/`, `frontend/`, or `tests/` | Low | Cleaner repository root |
| `route_and_viewport_qa_results.json`, `backend_ml_integration_results.json` | One-off QA output JSON dumps | Not read by runtime code | Low | Removes stale static artifacts |

## Category B — Potentially Removable After Dependency Verification
| File Path | Reason | Reference Check | Risk | Expected Impact |
| :--- | :--- | :--- | :--- | :--- |
| `frontend/components/investigation/mockData.ts` | Legacy static investigation fixture | Needs full recursive grep across `frontend/` | Low | Eliminates risk of accidental mock fallback |
| `frontend/components/KillChainGraph.tsx`, `IncidentFeed.tsx`, `ScanWorkbench.tsx`, `TelemetryCards.tsx`, `ModelGovernancePanel.tsx`, `Navbar.tsx` | Older light-theme components superseded by `components/investigation/*` & `components/ui/*` | Must verify `/dashboard`, `/models`, `/history` imports first | Medium | Reduces frontend bundle/maintenance |
| `audit_backend_data.py`, `audit_backend_investigation.py`, `audit_datasets_forensic.py`, `audit_ml_runtime.py`, `inspect_details.py`, `check_status.py` | Root diagnostic scripts | Not imported by runtime; may be referenced in prior docs | Low | Archive into `scripts/` or remove |
| `n8n/workflows/01_dataset_monitoring.json`, `02_automated_ml_training.json`, `03_model_evaluation_registration.json`, `04_suspicious_campaign_alerts.json`, `threat_intel_pipeline.json` | Earlier n8n workflow drafts superseded by Phase 4.2 `01..06` set | Referenced by legacy `tests/test_n8n_automation.py` | Medium | Update `tests/test_n8n_automation.py` before removing |

## Category C — Required for the Application (Preserve)
- `backend/**`, `frontend/app/**`, `frontend/lib/api.ts`, `frontend/components/investigation/*`, `frontend/components/ui/*`, `frontend/components/AppShell.tsx` (used in `layout.tsx`), `ml/**`, `data/**`, `n8n/workflows/01_threat_intelligence_ingestion.json`..`06_daily_intelligence_report.json`, `render.yaml`, `frontend/vercel.json`, `requirements.txt`, `.env.example`, `.gitignore`.

## Category D — Unknown / Requires Manual Review
- Root `test_*.py` scripts (`test_all_routes_and_viewports.py`, `test_analysis_endpoints.py`, `test_and_capture_analysis_pages.py`, `test_backend_and_ml_live.py`, `test_campaign_endpoint.py`, `test_cdp.py`, `test_investigations_api.py`, `test_phase1_2_integration.py`, `test_routes_navigation.py`) — consolidate into `tests/` after reviewing overlap.
