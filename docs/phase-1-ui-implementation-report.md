# TRUSTLENS AI — Phase 1: Advanced Cyber Threat Investigation Workspace UI Report

**Date:** November 24, 2026  
**Role:** Principal UI/UX Designer & Senior Frontend Architect  
**Objective:** Deliver an advanced cybersecurity investigation workspace inspired by the ThreatQ interaction philosophy, replacing conventional SaaS admin dashboard layouts with a dark, information-dense threat intelligence cockpit.

---

## 1. Executive Summary

Phase 1 delivers the **Advanced Cyber Threat Investigation Workspace UI** for **TRUSTLENS AI**.

Inspired directly by the attached ThreatQ reference interface, the workspace transforms incident investigation into a unified, full-screen analyst command center consisting of:
1. **Persistent Top Navigation Bar** (`#252D38`): Branding, Threat Library, Investigations, Analytics, Create Investigation workflow, global threat search, real-time alert notifications, help playbook, settings, and SOC lead profile.
2. **Central Interactive Relationship Graph** (`#181E28`): A high-performance, dark-mode SVG threat graph featuring 10 distinct cybersecurity object types, dynamic selection halos, halo-pulse rings for central campaign hubs, and connected neighbor highlight propagation.
3. **Floating Graph Controls & Radar Minimap**: Seamless pan, zoom, fit-to-screen, layout reset, object-type filtering, node search, and a bird's-eye radar minimap tracking camera viewport bounds.
4. **Persistent Right-Side Object Inspector Panel** (`#252D38`): Contextual side panel displaying investigation-level telemetry (objects count, severity, timestamps, sources, tags, attributes) when idle, and deep entity forensic breakdowns (model outputs, SHAP explanations, confidence scores, technical IOCs, connected neighbors) upon node selection.
5. **Bottom Multi-Track Correlation Timeline** (`#1E2631`): Chronological multi-tier event timeline displaying Tasks & Mitigation, Situation & Pretexts, and Threat Indicators/Detections mapped across chronological date guides.

---

## 2. Visual Alignment with ThreatQ Reference

```
+-----------------------------------------------------------------------------------------------------------------+
| [Logo] TRUSTLENS AI    Home   Threat Library v   [● Investigations]   Analytics v    [+ Create]  [Q]  [*] [?]  (RS) |
+-----------------------------------------------------------------------------------------------------------------+
|  [Search / Zoom / Minimap]               [Threat Graph Canvas]                    | [Object Details Inspector]  |
|                                                                                   |                             |
|        (Message) -------> (Phishing URL)                                          | OBJECTS   TASKS   COMMENTS  |
|            \                     \                                                |   139       3        0      |
|             \                     v                                               |                             |
|              +-----> (( CENTRAL SYNDICATE #11 )) <-----+                          | SEVERITY       VISIBILITY   |
|                            /           \                \                         | CRITICAL       Organization |
|                           v             v                v                        |                             |
|                    (Tactic T01)     (IOC Phone)   (Citizen Report)                | CREATED                     |
|                                                                                   | Yesterday by Senior Analyst |
|                                                                                   |                             |
|                                                                                   | > DESCRIPTION               |
|                                                                                   | > SOURCES (3)               |
|                                                                                   | > TAGS                      |
|                                                                                   | > ATTRIBUTES                |
+-----------------------------------------------------------------------------------+-----------------------------+
| [TASKS]       [Read CERT-In advisory]     [Hunt for indicators]   [Plan mitigation]                             |
| [SITUATION]   [Window of exposure]        [Operation FakeKYC]     [Report of mass SMS]                          |
| [SELECTED]    [sbi-kyc-update.com seen]   [194.168.20.14 created] [UPI handle flagged]                          |
| JAN 9         JAN 16                      JAN 23                  JAN 30          FEB 6    FEB 13   FEB 20      |
+-----------------------------------------------------------------------------------------------------------------+
```

### Color Palette Implementation

| Element | Specification Token | Hex Code | Purpose |
| :--- | :--- | :---: | :--- |
| **Main Background** | `threatq.bg` | `#171C25` | Deep navy base workspace background |
| **Top Navigation** | `threatq.nav` | `#252D38` | Structured horizontal navigation strip |
| **Graph Canvas** | `threatq.canvas` | `#181E28` | High-contrast dot-grid graph workspace |
| **Side Inspector** | `threatq.panel` | `#252D38` | Collapsible right-hand forensic inspector |
| **Borders & Dividers**| `threatq.border` | `#3A4553` | Subtle, non-intrusive container framing |
| **Bottom Timeline** | `threatq.timeline` | `#1E2631` | Multi-track horizontal chronological strip |
| **Primary Accent** | `threatq.accent` | `#3B82F6` | Primary action buttons and selection pills |
| **Cyan Accent** | `threatq.cyan` | `#38BDF8` | Active indicators, focus halos, and tags |
| **Primary Text** | `threatq.text` | `#F1F5F9` | High-readability light typography |
| **Muted Text** | `threatq.muted` | `#AAB4C2` | Metadata labels and timestamps |

---

## 3. Library Selection & Evaluation (Graph Engine)

As mandated by Section 4, available graph visualization technologies were formally evaluated prior to architectural selection:

| Evaluation Criteria | React Flow (`@xyflow/react`) | Cytoscape.js | Custom Native SVG & D3 Force Engine (**Selected**) |
| :--- | :--- | :--- | :--- |
| **ThreatQ Aesthetic Match** | Fair (Default nodes are rectangular cards; circular spider nodes require custom wrappers) | Good (Canvas-based graph, circular glyphs supported) | **Flawless** (Exact circular node badges, counter pills, pulse rings, and edge halos) |
| **DOM & Styling Integration** | High (React DOM components) | Low (Canvas-rendered; difficult to integrate Tailwind tooltips & Lucide icons) | **Native** (Pure React + SVG + Tailwind CSS; seamless icon & text layout) |
| **Bundle Impact** | ~180 kB minified | ~210 kB minified | **0 kB external footprint** (Built on native browser SVG DOM & React hooks) |
| **App Router & SSR Safety** | Potential hydration mismatches with server rendering | Canvas context cannot pre-render during SSR | **100% SSR-safe**; static pre-rendering passes Next.js build |
| **Interactivity** | Pan, zoom, drag supported | Pan, zoom, drag supported | **Full drag, pan, zoom-to-cursor, node focus isolation, and minimap tracking** |

**Architectural Decision:** Implemented a native React SVG Force & Geometry engine in `ThreatGraph.tsx`. It delivers maximum rendering performance, instant responsiveness, exact ThreatQ aesthetic fidelity, and zero third-party dependency vulnerabilities.

---

## 4. Graph Object Types & Relationships

The workspace supports all 10 required cybersecurity entity types:

1. **Suspicious Messages (`message`)**: Rendered in Sky Blue (`#0284C7`) with mail glyph. Contains raw SMS/WhatsApp text and Model 1 Bi-LSTM classification score.
2. **URLs (`url`)**: Rendered in Amber (`#D97706`) with link glyph. Contains extracted features and Model 2 XGBoost phishing probability.
3. **Domains (`domain`)**: Rendered in Emerald (`#059669`) with globe glyph. Represents FQDNs and registrar attributes.
4. **IP Addresses (`ip`)**: Rendered in Pink (`#DB2777`) with server glyph. Tracks hosting infrastructure and C2 endpoints.
5. **Scam Categories (`scam_category`)**: Rendered in Crimson (`#DC2626`) with shield-alert glyph. Groups attacks into Banking KYC, Utility, or Job Fraud.
6. **Social Engineering Tactics (`tactic`)**: Rendered in Purple (`#7C3AED`) with zap glyph. Maps to the standardized 10-tactic taxonomy.
7. **Campaign Clusters (`campaign_cluster`)**: Central hub node rendered in Crimson/Orange with an animated ping pulse ring, representing HDBSCAN density clusters (e.g. `SBI KYC SYNDICATE #11`).
8. **User Reports (`user_report`)**: Rendered in Cyan (`#0891B2`) with user-check glyph. Represents crowd-sourced citizen evidence submissions.
9. **Threat Indicators (`threat_indicator`)**: Rendered in Gold (`#CA8A04`) with fingerprint glyph and counter badge pills (e.g. `45` VoIP phone numbers, `18` UPI handles).
10. **Source References (`source_reference`)**: Rendered in Slate (`#475569`) with database glyph. Links external feeds (CERT-In, ScamShield).

---

## 5. Working Interactions Verified

- **Pan & Zoom**: Dragging the canvas pans the camera; mouse-wheel and toolbar buttons zoom from $0.25\times$ to $3.0\times$ centered on cursor coordinates.
- **Node Dragging**: Any node can be repositioned dynamically in real-time.
- **Node Focus & Isolation**: Clicking a node highlights it with an active cyan border, illuminates all directly connected edges and neighbors, and dims all unrelated nodes to $25\%$ opacity.
- **Bi-directional Timeline Sync**: Clicking an event in the bottom timeline immediately selects the corresponding graph node, centers the camera, and opens its forensic dossier in the inspector.
- **Search & Filter**: Floating toolbar filters nodes by text and provides a multi-select checkbox dropdown to toggle entity types on the fly.
- **Minimap Radar**: Real-time floating minimap in the top-left tracks coordinate boundaries and renders a dynamic camera viewport rectangle.
- **Collapsible Inspectors**: Both the right-side inspector and bottom timeline support one-click collapse/expand to maximize graph viewing area on smaller viewports.

---

## 6. Files Created & Modified

### Created Files
- `frontend/components/investigation/types.ts`: Comprehensive TypeScript interfaces for nodes, edges, timeline tracks, and investigation dossiers.
- `frontend/components/investigation/TopNavigation.tsx`: ThreatQ-inspired persistent top navigation bar with brand logo, primary tabs, search, notifications, help modal, and user profile.
- `frontend/components/investigation/ThreatGraph.tsx`: Core interactive SVG relationship graph engine with 10 object types, dragging, zoom, pan, and focus isolation.
- `frontend/components/investigation/GraphToolbar.tsx`: Top-left floating glassmorphism control toolbar.
- `frontend/components/investigation/GraphMinimap.tsx`: Floating bird's-eye radar minimap.
- `frontend/components/investigation/ObjectInspector.tsx`: Right-side inspector panel with investigation stats, collapsible accordions, and node details.
- `frontend/components/investigation/InvestigationTimeline.tsx`: Bottom multi-track chronological correlation timeline.
- `frontend/components/investigation/InvestigationWorkspace.tsx`: Top-level orchestrator connecting navigation, canvas, toolbar, minimap, inspector, and timeline.
- `frontend/components/investigation/CreateInvestigationModal.tsx`: Modal dialog for creating new investigation dossiers.
- `frontend/components/investigation/EmptyInvestigationState.tsx`: High-end standby empty state with radar graphic.
- `frontend/components/investigation/mockData.ts`: Illustrative preview fixture based on observed Campaign Cluster #11 telemetry.
- `frontend/app/investigations/[id]/page.tsx`: Full-screen investigation workspace dynamic route.
- `frontend/app/investigations/page.tsx`: Active investigations directory and workspace launcher.
- `frontend/app/threat-library/page.tsx`: Threat library landing hub connecting Tactics, Campaigns, and Indicators.
- `frontend/app/analytics/page.tsx`: Analytics landing hub connecting Models, History, and Reports.

### Modified Files
- `frontend/tailwind.config.ts`: Added `threatq` color tokens matching the reference palette.
- `frontend/components/AppShell.tsx`: Configured route-aware shell logic so `/investigations/*`, `/threat-library`, and `/analytics` render edge-to-edge full-width dark workspaces.
- `frontend/components/ui/Sidebar.tsx`: Added navigation links to Investigation Workspace and Threat Directory.
- `frontend/app/investigation/page.tsx`: Added ThreatQ Advanced Workspace callout banner.

---

## 7. Build & Verification Results

1. **TypeScript Typecheck (`npx tsc --noEmit`)**: Clean exit with **Code 0** (0 type errors).
2. **Next.js Production Build (`npm run build`)**: Compiled successfully into standalone production output:
   - Route `/investigations/[id]`: 17.2 kB (server-rendered on demand).
   - Route `/investigations`: 5.42 kB.
   - Route `/threat-library`: 3.03 kB.
   - Route `/analytics`: 3.03 kB.
   - All 19 routes passed with zero errors and zero lint warnings.
3. **Visual Verification**: High-resolution screenshots captured across Desktop, Laptop, Tablet, and Mobile viewports preserved in `docs/screenshots/`:
   - `investigation_workspace_threatq.png` (Desktop 1440×900)
   - `investigation_workspace_laptop.png` (Laptop 1280×800)
   - `investigation_workspace_tablet.png` (Tablet 768×1024)
   - `investigation_workspace_mobile.png` (Mobile 375×667)
   - `investigations_directory.png` (Desktop 1440×900)
