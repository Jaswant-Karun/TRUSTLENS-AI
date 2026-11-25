# TRUSTLENS AI — PRODUCT TRANSFORMATION STRATEGY

> **Phase:** 3.0 (Architecture & Master Planning)  
> **Branch:** `remediation/phase-0.5`  
> **Scope:** Transition from a sidebar-heavy internal SOC dashboard into a cohesive, multi-surface consumer & analyst fraud-intelligence product.

---

## 1. Strategic Shift: From Dashboard App to Product Platform

### Current State
- `frontend/app/page.tsx` immediately executes `redirect("/dashboard")`, offering no public product introduction, trust explanation, or onboarding path.
- `frontend/components/AppShell.tsx` wraps every view in a persistent left `Sidebar` with 14+ routes (`/dashboard`, `/analyze/text`, `/analyze/url`, `/analyze/image`, `/investigation`, `/investigations`, `/history`, `/reports`, `/analytics`, `/intelligence/campaigns`, `/intelligence/tactics`, `/intelligence/threats`, `/threat-library`, `/models`, `/settings`).
- While backend workflows (auth, ML inference, investigations, notes, timelines, campaign sync) are functional and verified (`84` passing pytest cases across Phase 0.5–2.5), the UX presents an internal admin/SOC console rather than an approachable global product.

### Target Three-Surface Product Architecture

All three surfaces share **one FastAPI backend (`backend/app/`)**, **one MongoDB database (`trustlens_ai`)**, **one JWT/RBAC identity system**, and **one validated ML inference pipeline (`ProductionMLEngine` + `MLOrchestrationService`)**:

| Surface | Audience | Primary Purpose | Delivery Technology |
| :--- | :--- | :--- | :--- |
| **1. Public Product Website** | General public, prospective users, security reviewers | Explain what TRUSTLENS AI does, how it works, supported languages, privacy guarantees, honest limitations, and provide central circular quick-entry & Sign Up / Sign In | Next.js 14 App Router (`/` and public routes, zero sidebar) |
| **2. Authenticated Web Application** | Consumers, fraud analysts, reviewers, admins | Unified analysis workspace, persistent scan history, case investigations (graph, notes, timeline), campaign & threat intelligence, community reports, and account/privacy controls | Next.js 14 App Router (route-group isolation, role-aware navigation) |
| **3. Future Android Application** | Mobile users (Google Play Store) | Fast on-the-go SMS/WhatsApp/URL/screenshot verification, share-sheet ingestion, personal scan history, and consented threat alerts | React Native (Expo managed workflow, TypeScript) sharing the same FastAPI REST contracts |

---

## 2. Core Preservation Principles

1. **Preserve Working Backend & ML Services:** Keep FastAPI, MongoDB, `CentralModelLoader`, `get_shared_sentence_transformer()`, `TransparentRiskAggregationService`, `InvestigationService`, `CampaignIntelligenceService`, and n8n automation webhooks intact.
2. **Preserve Next.js 14 / React 18 / Tailwind CSS:** Do not perform disruptive framework upgrades during UI/product evolution; evolve routes via Next.js App Router route groups (`(public)` vs `(app)`).
3. **Single Authentication & RBAC Source:** Extend existing `/api/v1/auth/*` (`bcrypt` rounds=12, `HS256` JWT, `users` collection) rather than building a second auth system.
4. **Honesty & Evidence First:** Never fabricate user counts, accuracy claims, testimonials, or unverified language support. Only state capabilities backed by verified artifacts and tests.

---

## 3. Product Evolution Pillars

1. **Clarity of Entry (Public -> Auth):** Replace immediate `/dashboard` redirect with a clear public landing experience and the **Central Circular Navigation** control for focused primary journeys.
2. **Unified Analysis Flow:** Consolidate text, URL, and screenshot OCR into a single streamlined entry point with progressive disclosure of ML evidence (SHAP/token saliency, tactics, risk score, and "Attach to Investigation").
3. **Role-Appropriate Workspace:** Keep consumer users focused on *Analyze -> History -> Investigations -> Reports -> Profile*, while analyst/admin tools (*Models Governance*, *Campaign Sync*, *Threat Library*, *n8n Telemetry*) remain cleanly gated.
4. **Real-World ML & Data Maturity:** Remediate Hindi recall (`0.5455`) and URL false-positive rate (`15.33%`) through licensed multilingual and benign-URL dataset expansion before public Play Store launch.
5. **Privacy & Play Store Readiness:** Add email verification, password reset, self-service account deletion, personal data export, and explicit consent flows required by Google Play Data Safety.
