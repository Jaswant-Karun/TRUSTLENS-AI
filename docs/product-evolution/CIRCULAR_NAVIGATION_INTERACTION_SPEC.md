# TRUSTLENS AI — CENTRAL CIRCULAR NAVIGATION INTERACTION SPECIFICATION

> **Phase:** 3.0 Design Specification (Do Not Implement Yet)

---

## 1. Concept & Purpose

Replace passive menu hunting with one signature **Central Circular Navigation** control on the landing/entry experience. Initially, only the central hub button is visible. Clicking or activating the center smoothly expands a radial ring of **5 focused primary user actions**, keeping cognitive load low and preserving visual clarity.

---

## 2. Selected Primary Actions (5 Radial Nodes)

Only core user journeys are placed on the ring (never all 14+ routes):

| # | Angle (Desktop) | Label | Icon (`lucide-react`) | Target Workflow |
| :--- | :--- | :--- | :--- | :--- |
| 1 | `-90°` (Top) | **Analyze Message** | `MessageSquareWarning` | `/analyze/text` (or `/login?next=/analyze/text` if auth-gated) |
| 2 | `-18°` (Top-Right) | **Inspect URL** | `Link2` | `/analyze/url` |
| 3 | `+54°` (Bottom-Right) | **Scan Screenshot** | `ScanSearch` | `/analyze/image` |
| 4 | `+126°` (Bottom-Left) | **Investigations** | `FolderSearch` | `/investigations` |
| 5 | `+198°` (Top-Left) | **Threat Intelligence** | `ShieldAlert` | `/intelligence/campaigns` |

*(Auth-aware behavior: If unauthenticated and clicking an auth-protected workflow, prompt clean Sign In / Sign Up modal or redirect with `next=` parameter.)*

---

## 3. Interaction & State Machine

1. **Collapsed State (Default):**
   - Central circular button (`72px–84px` diameter) with TRUSTLENS shield/lens emblem and subtle aria-label `"Open primary navigation actions"`.
   - Radial action buttons are unmounted or `aria-hidden="true"`, `tabIndex={-1}`, `pointer-events: none`.
2. **Expanded State (On Click / Enter / Space):**
   - Center button icon transitions to `X` (`aria-expanded="true"`, label `"Close navigation actions"`).
   - 5 circular action buttons (`56px` diameter + concise external/below label) animate outward along radius `R` (`140px` desktop, `112px` tablet).
   - Clicking the center button again, pressing `Escape`, or clicking outside collapses the ring.
3. **Selection:**
   - Clicking or pressing `Enter` on any radial node navigates to its workflow and collapses the control.

---

## 4. Accessibility, Keyboard & Motion Rules

- **Keyboard Navigation:**
  - `Tab` focuses the center button; `Enter` or `Space` toggles expansion.
  - When expanded, `ArrowRight`/`ArrowDown` and `ArrowLeft`/`ArrowUp` (or `Tab`) cycle through the 5 radial items in clockwise order; `Escape` closes and returns focus to the center button.
- **Reduced Motion (`prefers-reduced-motion: reduce`):**
  - Disable spring/scale/stagger animations via `framer-motion` `useReducedMotion()`; switch to instant opacity fade (`<= 100ms`) or immediate state change.
- **Responsive Mobile Behavior (`< 640px`):**
  - Below `640px`, radial radius `140px` risks horizontal clipping on `360px–390px` viewports. On mobile viewports, either scale radius to `96px` with compact labels or smoothly morph the expanded state into a clean 2-column / bottom-arc radial fan centered in the viewport so all touch targets remain `>= 44x44px` with zero horizontal overflow.
