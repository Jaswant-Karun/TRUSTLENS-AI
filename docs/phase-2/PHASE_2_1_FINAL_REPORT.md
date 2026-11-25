# TRUSTLENS AI — PHASE 2.1 FINAL REPORT: INVESTIGATION AUTHENTICATION & NOTES

> **Branch:** `remediation/phase-0.5`  
> **Date:** November 25, 2026

---

## 1. Files Modified & Created
- [`backend/app/schemas/investigation.py`](file:///c:/Users/jaswant%20karun/TRUSTLENS%20AI/backend/app/schemas/investigation.py): Added `owner_id`, `visibility` (`Organization | Private`), `InvestigationNoteCreate`, `InvestigationNoteUpdate`, `InvestigationNoteResponse`.
- [`backend/app/database/indexes.py`](file:///c:/Users/jaswant%20karun/TRUSTLENS%20AI/backend/app/database/indexes.py): Added `("owner_id", 1)` index on `investigations`.
- [`backend/app/services/investigation_service.py`](file:///c:/Users/jaswant%20karun/TRUSTLENS%20AI/backend/app/services/investigation_service.py): Enforced `_check_read_access` / `_check_write_access`, JWT-derived `owner_id` on `create_investigation`, visibility filtering on `list_investigations`, `list_notes`, `add_note` (with 10s duplicate-write guard + `note_added` timeline event + `audit_logs`), `update_note`, and `delete_note`.
- [`backend/app/api/routes/investigations.py`](file:///c:/Users/jaswant%20karun/TRUSTLENS%20AI/backend/app/api/routes/investigations.py): Required `get_current_user` on `POST /investigations`, `POST/PATCH/DELETE /investigations/{id}/notes`; enforced `401`/`403` on private investigations across all read/graph/timeline/object endpoints.
- [`frontend/lib/api.ts`](file:///c:/Users/jaswant%20karun/TRUSTLENS%20AI/frontend/lib/api.ts), [`InvestigationNotesPanel.tsx`](file:///c:/Users/jaswant%20karun/TRUSTLENS%20AI/frontend/components/investigation/InvestigationNotesPanel.tsx), [`ObjectInspector.tsx`](file:///c:/Users/jaswant%20karun/TRUSTLENS%20AI/frontend/components/investigation/ObjectInspector.tsx): Added live persistent notes UI with loading, success, error, and delete controls.
- [`tests/test_investigation_auth_and_notes.py`](file:///c:/Users/jaswant%20karun/TRUSTLENS%20AI/tests/test_investigation_auth_and_notes.py): Added Phase 2.1 security & integration test suite.

## 2. API Contracts Added / Updated
- `POST /api/v1/investigations` (`201`, requires JWT; `401` unauthenticated)
- `GET /api/v1/investigations/{id}/notes` (`200`, respects private investigation isolation)
- `POST /api/v1/investigations/{id}/notes` (`201`, requires JWT + write access; `422` on whitespace-only content)
- `PATCH /api/v1/investigations/{id}/notes/{note_id}` (`200`, author or admin only)
- `DELETE /api/v1/investigations/{id}/notes/{note_id}` (`200`, author or admin only)

## 3. Test & Verification Results
- `.\.venv\Scripts\python.exe -m pytest tests/test_investigation_auth_and_notes.py -q`: **`4 passed, 1 warning`** (`Command exited with code 0`).
  - Verified unauthenticated creation `401`, JWT `owner_id` enforcement (ignoring spoofed payload `owner_id`), private investigation `401`/`403` isolation, admin RBAC, note create/list/edit/delete, whitespace-only note `422`, cross-user note edit/delete `PermissionError`, `404` on invalid IDs, and safe DB exception handling.
- Frontend `tsc --noEmit` + `npm run lint` + `npm run build` (`task-5437`): check status below.
- **Known Limitation:** Browser UI click-through of `InvestigationNotesPanel` requires an authenticated session in Chrome (`DevToolsActivePort` not enabled locally).
