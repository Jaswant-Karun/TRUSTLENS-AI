# TRUSTLENS AI — AUTHENTICATED APPLICATION ARCHITECTURE

> **Phase:** 3.0 Specification (Do Not Implement Yet)  
> **Route Group:** `frontend/app/(app)/`

---

## 1. Purpose

Evolve the existing 14+ sidebar pages into a clean, role-aware authenticated workspace that preserves all working Phase 1 & Phase 2 capabilities while eliminating navigation clutter for everyday users.

---

## 2. Navigation Simplification (Replacing Dense Left Sidebar)

Instead of exposing 14+ technical routes to every user on a static left sidebar:
- **Primary Top Navigation + Compact Radial/Command Switcher:**
  1. **Analyze** (`/analyze` — unified entry point with tabs for Text, URL, Screenshot, and Multi-Modal Studio, reusing `AnalyzeModeTabs`, `ScanWorkbench`, `AnalysisResultPanel`).
  2. **History** (`/history` — personal scan history with search, filters, and one-click "Attach to Investigation").
  3. **Investigations** (`/investigations` & `/investigations/[id]` — case directory + full ThreatQ-style workspace with Graph, ObjectInspector, NotesPanel, Timeline).
  4. **Intelligence** (`/intelligence/campaigns`, `/intelligence/tactics`, `/intelligence/threats`, `/threat-library` — grouped under one Intelligence hub).
  5. **Reports** (`/reports` — community scam submissions and reviewer moderation).
- **Account Menu (Top-Right):**
  - Profile, Privacy & Data Export, Settings, Sign Out.
- **Role-Gated Analyst/Admin Section (only rendered when `role in ['analyst', 'reviewer', 'admin']`):**
  - ML Center (`/models`), Analytics (`/analytics`), Campaign Sync trigger.

---

## 3. Authenticated User Journeys

1. **Unified Analysis -> Save -> Investigate:**
   - User opens `/analyze` (or selects mode from Circular Nav), submits text/URL/screenshot.
   - Result displays calibrated risk score, threat level (`clean | low | medium | high | critical | inconclusive`), detected tactics, and SHAP/token evidence.
   - User clicks **Attach to Investigation** to link the `analysis_id` to an existing or newly created case (`POST /api/v1/investigations/{id}/attach-analysis`).
2. **Case Investigation Workspace (`/investigations/[id]`):**
   - Preserves `InvestigationWorkspace.tsx`, `ThreatGraph.tsx`, `ObjectInspector.tsx`, `InvestigationNotesPanel.tsx`, and `InvestigationTimeline.tsx`.
   - Enforces `Private` vs `Organization` visibility and JWT-derived `owner_id`.
3. **Account & Privacy Self-Service (`/settings` & `/profile`):**
   - View profile (`GET /api/v1/auth/me`), change password, manage consent preferences, export personal analyses/investigations JSON, and delete account (planned in Phase 3 roadmap).

---

## 4. Route & Component Reuse Matrix

| Existing Asset | Disposition in Authenticated App |
| :--- | :--- |
| `frontend/lib/api.ts` | Reuse & extend with auth refresh, profile export, and account deletion clients |
| `ScanWorkbench.tsx` / `AnalysisResultPanel.tsx` | Reuse inside unified `/analyze` flow |
| `InvestigationWorkspace.tsx` + all `components/investigation/*` | Preserve intact on `/investigations/[id]` |
| `AppShell.tsx` / `Sidebar.tsx` | Refactor into clean top-bar + role-gated navigation drawer for mobile/analyst tools |
| `/dashboard` | Retain as `/overview` or redirect authenticated home to `/analyze` + recent activity summary |
