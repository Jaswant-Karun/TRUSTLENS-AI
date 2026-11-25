# TRUSTLENS AI — PHASE 2.3 FINAL REPORT: REAL INVESTIGATION TIMELINE & EVENT TRACKING

> **Branch:** `remediation/phase-0.5`  
> **Date:** November 25, 2026

---

## 1. Event Types & Schema

Extended [`TimelineEventSchema`](file:///c:/Users/jaswant%20karun/TRUSTLENS%20AI/backend/app/schemas/investigation.py) and `_build_timeline_event()` in [`investigation_service.py`](file:///c:/Users/jaswant%20karun/TRUSTLENS%20AI/backend/app/services/investigation_service.py) with UTC timestamps, chronological ascending sort, and safe metadata (never storing raw sensitive message content):
- `investigation_created` (on `POST /api/v1/investigations`)
- `note_added` (on `POST /api/v1/investigations/{id}/notes`)
- `investigation_status_changed` / `investigation_updated` (on `PATCH /api/v1/investigations/{id}`; suppresses duplicate status event when status is unchanged)
- `analysis_attached` (on `POST /api/v1/investigations/{id}/attach-analysis`; rejects duplicates with `409 Conflict` and preserves the original `analyses` document)

## 2. Historical Recovery Investigation (`INV-2026-0011`)

Direct MongoDB inspection confirmed `INV-2026-0011` already holds `10` graph nodes and `6` persisted `timeline` events (`audit_logs` count = `0`). The earlier Phase 5.0 report of `0` events occurred because the test script read `events` instead of the `timeline` response key. Existing `INV-2026-0011` events were preserved untouched with zero fabricated entries.

## 3. Frontend & API Changes

- **Backend:** [`schemas/investigation.py`](file:///c:/Users/jaswant%20karun/TRUSTLENS%20AI/backend/app/schemas/investigation.py), [`services/investigation_service.py`](file:///c:/Users/jaswant%20karun/TRUSTLENS%20AI/backend/app/services/investigation_service.py), [`api/routes/investigations.py`](file:///c:/Users/jaswant%20karun/TRUSTLENS%20AI/backend/app/api/routes/investigations.py).
- **Frontend:** [`InvestigationTimeline.tsx`](file:///c:/Users/jaswant%20karun/TRUSTLENS%20AI/frontend/components/investigation/InvestigationTimeline.tsx) (dynamic date axis from real timestamps, empty & error states, refresh button), [`InvestigationNotesPanel.tsx`](file:///c:/Users/jaswant%20karun/TRUSTLENS%20AI/frontend/components/investigation/InvestigationNotesPanel.tsx) & [`ObjectInspector.tsx`](file:///c:/Users/jaswant%20karun/TRUSTLENS%20AI/frontend/components/investigation/ObjectInspector.tsx) & [`InvestigationWorkspace.tsx`](file:///c:/Users/jaswant%20karun/TRUSTLENS%20AI/frontend/components/investigation/InvestigationWorkspace.tsx) (auto-refresh timeline on note save).

## 4. Test Evidence

- `.\.venv\Scripts\python.exe -m pytest tests/test_phase2_3_timeline.py tests/test_investigation_auth_and_notes.py -q`: **`6 passed, 1 warning`** (`Command exited with code 0`).
  - Verified `investigation_created`, `note_added`, `investigation_status_changed`, `analysis_attached`, chronological timestamp ordering, `409` duplicate attachment guard, `404` invalid analysis reference, `401` unauthorized timeline access, empty timeline `[]` handling, and `INV-2026-0011` historical safety.
