# TRUSTLENS AI — FRONTEND AUDIT (PHASE 0)

> **Framework:** Next.js 14.2.35 (App Router, `output: "standalone"`)  
> **Routes Compiled (`npm run build`):** 19 routes (`18` static + `1` dynamic `/investigations/[id]`)

---

## 1. Route & State Audit
- **Investigation Workspace (`/investigations`, `/investigations/[id]`):** Connects to `GET /api/v1/investigations`, `/graph`, `/timeline`, `/objects/{id}`, `/objects/{id}/relationships`. Includes loading radar, 404 retry card, empty state (`EmptyInvestigationState`), pan/zoom/drag, node selection, 1-hop expansion, `GraphLegend`, `GraphMinimap`, `ObjectInspector`, and `InvestigationTimeline`.
- **Analysis Pages (`/analyze/text`, `/analyze/url`, `/analyze/image`, `/investigation`):** Connected to `POST /api/v1/analyze/*`; unified via `AnalyzeModeTabs`; `AnalysisResultPanel` enforces `N/A` when confidence is absent and displays ML/TI/Human provenance badges.
- **Threat Library (`/threat-library`) & Analytics (`/analytics`) & Reports (`/reports`):** Connected to `/api/v1/threat-library`, `/api/v1/analytics/overview`, `/api/v1/intelligence-reports/generate`, `/api/v1/exports/json`, `/api/v1/exports/stix`.

## 2. Interaction Inventory
| Component | Visible Control | Intended Action | Actual Implementation | API / Callback | Status | Test Required |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `TopNavigation` | `Create` button | Open create modal or directory | Calls `onCreateClick` or `router.push('/investigations')` | `POST /investigations` | **Verified (code)** | Browser click test |
| `TopNavigation` | `Search` icon | Focus graph search or open Threat Library | Calls `onSearchClick` or `router.push('/threat-library')` | `/threat-library` | **Verified (code)** | Browser click test |
| `TopNavigation` | `Bell` icon | Show recent investigations | Fetches `getInvestigations({ limit: 3 })` | `GET /investigations` | **Verified (code)** | Browser click test |
| `GraphToolbar` | `Filter nodes...` (`/`), Zoom `+/-`, Fit, Reset, Refresh, Minimap, Type Filter | Control graph viewport & filter nodes | Connected to `InvestigationWorkspace` state handlers | Local state + prop sync | **Verified (code)** | Browser interaction test |
| `ThreatGraph` | Click/drag/right-click node | Select, reposition, or expand 1-hop neighbors | Calls `onSelectNode`, drag state, `onExpandNeighbors` | `GET .../relationships` | **Verified (API)** | Browser canvas test (`BLOCKED`) |
| `ThreatLibraryPage` | Tabs, search, dropdowns, sort, pagination, row click, JSON/STIX export | Filter/sort/paginate & inspect/export | Connected to `queryThreatLibrary`, `exportInvestigationJson/Stix` | `GET /threat-library`, `/exports/*` | **Verified (API + HTTP 200)** | Browser UI test (`BLOCKED`) |
| `AnalyticsPage` | Date & source filters | Filter live DB aggregations | Calls `getAnalyticsOverview` | `GET /analytics/overview` | **Verified (API + HTTP 200)** | Browser UI test (`BLOCKED`) |

## 3. Known Frontend Gaps
- `frontend/app/layout.tsx` wraps all routes in `AppShell.tsx` (`bg-slate-50`), creating a theme split between light-mode pages (`/dashboard`, `/models`, `/history`, `/reports`) and dark-SOC pages (`/investigations`, `/threat-library`, `/analytics`).
- `eslint` is not installed in `frontend/node_modules`, blocking `npm run lint`.
- Live Chrome DevTools verification is **BLOCKED** (`DevToolsActivePort` not found).
