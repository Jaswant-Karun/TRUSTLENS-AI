# TRUSTLENS AI — PUBLIC WEBSITE ARCHITECTURE

> **Phase:** 3.0 Specification (Do Not Implement Yet)  
> **Route Group:** `frontend/app/(public)/` (Zero `AppShell` left sidebar)

---

## 1. Purpose

Provide a credible, fast, privacy-transparent public entry point for TRUSTLENS AI that explains what the platform genuinely does, how its evidence-based ML pipeline works, and guides users into Sign Up, Sign In, or focused product journeys via the **Central Circular Navigation** control.

---

## 2. Public Route Map

| Route | Purpose | Auth Required |
| :--- | :--- | :--- |
| `/` | Public product landing page with hero, Central Circular Navigation, workflow explanation, capabilities, languages, and trust/limitations | No |
| `/how-it-works` | Detailed walkthrough of zero-hop URL inspection, TF-IDF/LinearSVC text analysis, OCR extraction, and transparent risk scoring | No |
| `/privacy` | Data handling, screenshot/message sensitivity policy, retention, and non-execution guarantees | No |
| `/docs` | User help, supported input formats, API/limitations FAQ | No |
| `/login` | Sign In page (`POST /api/v1/auth/login`) with redirect to `/app` | No |
| `/register` | Sign Up page (`POST /api/v1/auth/register`) with password policy & consent | No |
| `/forgot-password` | Future password recovery request flow (Phase 3.x) | No |

---

## 3. Landing Page (`/`) Section Blueprint

1. **Minimal Public Top Bar:**
   - Brand mark + `TRUSTLENS AI`
   - Links: `How It Works`, `Languages`, `Privacy & Safety`, `Docs`
   - Actions: `Sign In` (secondary) and `Get Started` (primary CTA -> `/register`)
2. **Hero Section + Central Circular Navigation:**
   - Headline: *"Detect digital deception before people lose their money."*
   - Concise subheadline explaining multilingual scam text, zero-hop URL inspection, and screenshot OCR with evidence-backed explanations.
   - Primary CTA (`Create Free Account`) + Secondary CTA (`Sign In`).
   - Interactive **Central Circular Navigation** widget (see `CIRCULAR_NAVIGATION_INTERACTION_SPEC.md`) offering 5 focused primary journeys.
3. **Real Product Workflow ("How It Works"):**
   - 4-step factual flow: `1. Submit Text, URL, or Screenshot` -> `2. Offline Zero-Hop & ML Analysis` -> `3. Inspect Evidence & Tactics` -> `4. Save to History or Case Investigation`.
4. **Genuine Supported Capabilities (Evidence-Backed Only):**
   - **Text Scam Detection:** Word+Char TF-IDF + Calibrated LinearSVC with phrase/n-gram saliency.
   - **Zero-Hop URL Inspection:** 16 lexical/structural features via XGBoost + SHAP without ever visiting or executing the submitted URL.
   - **Screenshot OCR:** Validated PNG/JPEG/WebP upload (max 10 MB) with OCR text extraction feeding the scam/tactic pipeline.
   - **Social Engineering Tactic Detection:** 9 verified tactics (explicitly noting `fake_investment` is unavailable without ground truth).
   - **Investigation Workspaces:** Persistent notes, evidence attachment, relationship graph, and chronological timelines.
5. **Supported Languages & Honest Scope:**
   - Explicitly list **English**, **Hindi (Devanagari)**, and **Hinglish (Romanized)** as currently trained/evaluated, while transparently noting Hindi recall improvement is an active engineering priority and **Tamil/Bengali** are planned via Phase 3 real-world dataset expansion (not falsely claimed today).
6. **Trust, Privacy & Limitations Section:**
   - Zero outbound network calls to suspicious URLs.
   - Clustering (`HDBSCAN`) shows linguistic/indicator similarity, not legal proof of criminal attribution.
   - No fabricated user metrics, testimonials, certifications, or 100% accuracy claims.
7. **Footer:**
   - Legal & Disclaimer, Privacy Policy, Security Policy, Help/Docs, Contact.
