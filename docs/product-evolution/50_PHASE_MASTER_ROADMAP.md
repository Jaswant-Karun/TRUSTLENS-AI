# TRUSTLENS AI — 50-PHASE MASTER IMPLEMENTATION ROADMAP

> **Starting Baseline:** Phase 3.0 Complete (`remediation/phase-0.5`, `84` passing backend tests, Next.js 14 production build passing).  
> **Structure:** 50 sequential, dependency-aware engineering phases organized across 7 major tracks (Phases 3.1 – 3.50). Each phase specifies Objective, Reuse, Implementation, Dependencies, Deliverables, Acceptance Criteria, Required Tests, and Risks.

---

## Track A: Product Architecture, Design System & Public Website (Phases 3.1 – 3.9)

### Phase 3.1 — Next.js Route-Group Separation (`(public)` vs `(app)`)
- **Objective:** Separate public product routes from the authenticated `AppShell` without breaking existing routes.
- **Reuse:** `frontend/app/layout.tsx`, `frontend/components/AppShell.tsx`, `frontend/app/globals.css`.
- **Implement:** Create `(public)` and `(app)` route groups; move `AppShell` wrapping into `(app)/layout.tsx`; keep existing `/dashboard`, `/analyze/*`, `/investigations/*` URLs intact.
- **Dependencies:** Phase 3.0.
- **Deliverables:** Clean route-group structure; zero sidebar on public routes.
- **Acceptance Criteria:** Public routes render without sidebar; all existing authenticated routes build and resolve.
- **Required Tests:** `tsc --noEmit`, `npm run lint`, `npm run build`, route resolution smoke test.
- **Risks:** Broken relative imports or middleware redirects.

### Phase 3.2 — Product Design System Tokens & Typography Standardization
- **Objective:** Define cohesive design tokens (colors, spacing, elevation, typography, focus rings) supporting both public product pages and analyst workspaces.
- **Reuse:** `frontend/tailwind.config.ts`, `frontend/app/globals.css`.
- **Implement:** Tokenize semantic surface, accent, status, and accessible contrast variables (`WCAG AA`).
- **Dependencies:** Phase 3.1.
- **Deliverables:** Updated `globals.css` & `tailwind.config.ts` tokens + UI primitive audit.
- **Acceptance Criteria:** Contrast ratios `>= 4.5:1` on text; zero visual regressions on existing analysis panels.
- **Required Tests:** `npm run build`, automated contrast/axe check.
- **Risks:** Theme drift between public pages and dark SOC workspace.

### Phase 3.3 — Public Landing Page (`/`) Hero, Workflow & Honest Capabilities
- **Objective:** Build the public product landing page replacing `redirect("/dashboard")`.
- **Reuse:** `frontend/app/page.tsx`, `lucide-react`, `framer-motion`.
- **Implement:** Hero section, 4-step "How It Works", evidence-backed ML capabilities, supported languages (`English`, `Hindi`, `Hinglish`), trust & limitations section, legal/help footer.
- **Dependencies:** Phase 3.1, 3.2.
- **Deliverables:** Production `/` landing page with zero fabricated metrics or claims.
- **Acceptance Criteria:** Loads in `< 2s` locally; accurately reflects tested capabilities only.
- **Required Tests:** `npm run build`, Playwright/Chrome mobile+desktop responsiveness check.
- **Risks:** Overclaiming unverified accuracy or languages.

### Phase 3.4 — Central Circular Navigation Component
- **Objective:** Implement the interactive Central Circular Navigation control per `CIRCULAR_NAVIGATION_INTERACTION_SPEC.md`.
- **Reuse:** `framer-motion`, `lucide-react`.
- **Implement:** Collapsed center hub, 5 radial primary actions (`Analyze Message`, `Inspect URL`, `Scan Screenshot`, `Investigations`, `Threat Intelligence`), keyboard (`Tab`, `Enter`, `Arrows`, `Escape`), `useReducedMotion()`, mobile responsive layout.
- **Dependencies:** Phase 3.2, 3.3.
- **Deliverables:** Reusable `CircularNavigation.tsx` component integrated on `/`.
- **Acceptance Criteria:** Smooth mouse/touch/keyboard expand & collapse; zero clipping at `360px` width.
- **Required Tests:** Unit/component interaction test + keyboard accessibility + reduced-motion test.
- **Risks:** Touch-target overlap on small mobile screens.

### Phase 3.5 — Public Documentation, Privacy, How-It-Works & Help Pages
- **Objective:** Publish `/how-it-works`, `/privacy`, and `/docs` explaining zero-hop URL safety, OCR limits, and data handling.
- **Reuse:** `(public)` layout and design tokens.
- **Implement:** Static/MDX-backed informational pages with clear security/privacy disclosures.
- **Dependencies:** Phase 3.2.
- **Deliverables:** 3 public informational routes linked from navbar and footer.
- **Acceptance Criteria:** All footer and navbar links resolve (`HTTP 200`).
- **Required Tests:** Link checker + `npm run build`.
- **Risks:** Outdated documentation diverging from backend limits.

### Phase 3.6 — Public Sign-In & Sign-Up UX (`/login`, `/register`)
- **Objective:** Deliver dedicated, accessible authentication pages connected to `/api/v1/auth/login` and `/register`.
- **Reuse:** `frontend/lib/api.ts`, `backend/app/api/routes/auth.py`.
- **Implement:** Form validation, password strength meter, explicit consent checkbox on registration, `next=` redirect support, error handling.
- **Dependencies:** Phase 3.1, 3.2.
- **Deliverables:** `/login` and `/register` pages with persistent JWT session handling.
- **Acceptance Criteria:** Valid user can register, sign in, and reach `/analyze`; invalid credentials show safe error messages.
- **Required Tests:** E2E auth flow test (valid, invalid, duplicate email, `next=` redirect).
- **Risks:** Token storage XSS exposure if handled carelessly.

### Phase 3.7 — Authenticated App Shell Simplification (Role-Aware Navigation)
- **Objective:** Replace the 14-item static left sidebar with a clean product top-nav + compact mobile drawer + role-gated analyst menu.
- **Reuse:** `TopNavbar.tsx`, `Breadcrumb.tsx`, `AppShell.tsx`.
- **Implement:** Primary nav (`Analyze`, `History`, `Investigations`, `Intelligence`, `Reports`) + Account menu + Analyst/Admin submenu.
- **Dependencies:** Phase 3.1, 3.6.
- **Deliverables:** Refactored `AppShell.tsx` preserving all existing deep links.
- **Acceptance Criteria:** Regular users see 5 clean core destinations; admins/analysts retain access to `/models` and `/analytics`.
- **Required Tests:** Role-based UI visibility test + mobile drawer test.
- **Risks:** Breaking bookmarks to `/dashboard` (keep `/dashboard` functional or aliased).

### Phase 3.8 — Unified Analysis Studio (`/analyze`)
- **Objective:** Unify Text, URL, Screenshot OCR, and Multi-Modal analysis under one streamlined entry point.
- **Reuse:** `AnalyzeModeTabs.tsx`, `ScanWorkbench.tsx`, `AnalysisResultPanel.tsx`.
- **Implement:** Tabbed mode switcher preserving `/analyze/text`, `/analyze/url`, `/analyze/image` deep links, clear input limits, and one-click "Attach to Investigation".
- **Dependencies:** Phase 3.7.
- **Deliverables:** Unified `/analyze` experience with progressive evidence disclosure.
- **Acceptance Criteria:** All 3 modalities submit, display evidence, and save to `/api/v1/analyses`.
- **Required Tests:** API + frontend integration tests for text, URL, and image upload.
- **Risks:** Large bundle size if OCR/chart components aren't code-split.

### Phase 3.9 — New-User Onboarding & Empty-State Guidance
- **Objective:** Guide first-time authenticated users from zero records to their first scan and investigation without dummy data.
- **Reuse:** `EmptyState.tsx`, `EmptyInvestigationState.tsx`.
- **Implement:** Actionable empty states in History, Investigations, and Reports with direct links to `/analyze` and safe sample-prompt templates (user-triggered, never auto-seeded).
- **Dependencies:** Phase 3.7, 3.8.
- **Deliverables:** Honest, interactive onboarding & empty states.
- **Acceptance Criteria:** Zero fake records; new user can run first scan in 1 click.
- **Required Tests:** Empty-state render & CTA navigation test.
- **Risks:** Confusing sample prompts with real persisted user history.

---

## Track B: Account Security, Auth Lifecycle & Privacy Controls (Phases 3.10 – 3.16)

### Phase 3.10 — Production Secrets Guard & Startup Index Enforcement
- **Objective:** Fail fast in production if `SECRET_KEY` or `ADMIN_DEFAULT_PASSWORD` are defaults, and run `ensure_indexes()` cleanly on startup.
- **Reuse:** `backend/app/core/config.py`, `backend/app/database/indexes.py`.
- **Implement:** Startup validation guard when `APP_ENV=production`; apply `investigations.owner_id_1` index.
- **Dependencies:** Phase 3.0.
- **Deliverables:** Hardened config startup + `owner_id_1` index active in MongoDB.
- **Acceptance Criteria:** `db.investigations.getIndexes()` includes `owner_id_1`; prod boot rejects dev fallback secrets.
- **Required Tests:** Config validation unit test + MongoDB `explain()` on `owner_id` query.
- **Risks:** Breaking local dev if `APP_ENV` check is misconfigured.

### Phase 3.11 — Refresh Token Rotation & Server-Side Session Revocation
- **Objective:** Add short-lived access tokens + revocable refresh tokens in MongoDB for web and future Android clients.
- **Reuse:** `backend/app/security/jwt.py`, `backend/app/services/auth_service.py`.
- **Implement:** `POST /api/v1/auth/refresh`, `POST /api/v1/auth/logout` (token revocation), `user_sessions` collection with TTL index.
- **Dependencies:** Phase 3.10.
- **Deliverables:** Stateful revocation + seamless token refresh.
- **Acceptance Criteria:** Revoked refresh tokens return `401`; rotated tokens invalidate prior refresh token.
- **Required Tests:** Pytest suite for refresh, rotation reuse detection, and logout revocation.
- **Risks:** Clock skew or race conditions on concurrent refresh calls.

### Phase 3.12 — Email Verification Flow
- **Objective:** Verify user email ownership upon registration using signed, time-limited verification tokens.
- **Reuse:** `auth_service.py`, `users` collection.
- **Implement:** `email_verified` flag, `POST /api/v1/auth/verify-email`, `POST /api/v1/auth/resend-verification`, pluggable SMTP/transactional mail adapter.
- **Dependencies:** Phase 3.11.
- **Deliverables:** Email verification endpoints + UI banner/status.
- **Acceptance Criteria:** Unverified users cannot perform high-abuse actions until verified (configurable).
- **Required Tests:** Expired/invalid/valid token verification pytest.
- **Risks:** Email deliverability / SMTP misconfiguration blocking signups in dev.

### Phase 3.13 — Secure Password Recovery & Change-Password Flow
- **Objective:** Enable self-service password reset and authenticated password change with session invalidation.
- **Reuse:** `backend/app/security/password.py`, `auth_service.py`.
- **Implement:** `POST /api/v1/auth/forgot-password`, `POST /api/v1/auth/reset-password`, `POST /api/v1/auth/change-password`.
- **Dependencies:** Phase 3.12.
- **Deliverables:** Generic non-enumerating reset responses + UI pages.
- **Acceptance Criteria:** Resetting password revokes all active refresh sessions; response never reveals whether email exists.
- **Required Tests:** Enumeration prevention, token expiry, and single-use reset tests.
- **Risks:** Account takeover if reset tokens are logged or predictable.

### Phase 3.14 — Tiered Rate Limiting & Brute-Force Protection
- **Objective:** Protect `/auth/*`, `/analyze/*`, and `/reports` against credential stuffing and API abuse.
- **Reuse:** `backend/app/middleware/rate_limit.py`.
- **Implement:** Per-IP + per-user sliding-window limits (`429 Retry-After`) and temporary account lockout telemetry.
- **Dependencies:** Phase 3.10.
- **Deliverables:** Hardened rate-limit middleware + audit events on lockouts.
- **Acceptance Criteria:** Rapid failed logins trigger `429`; legitimate traffic remains unaffected.
- **Required Tests:** Automated burst-request pytest verifying `429` + headers.
- **Risks:** False lockouts behind shared NAT/corporate proxies.

### Phase 3.15 — User Profile, Consent Management & Personal Data Export
- **Objective:** Give users visibility and control over their profile, ML/telemetry consent, and personal data portability.
- **Reuse:** `frontend/app/settings/page.tsx`, `auth.py`.
- **Implement:** `GET/PATCH /api/v1/auth/profile`, consent flags (`allow_anonymized_ml_review`), `GET /api/v1/auth/export-data` (JSON bundle of user's own profile, analyses, and private investigations).
- **Dependencies:** Phase 3.11.
- **Deliverables:** Profile & Privacy Settings UI + self-service export endpoint.
- **Acceptance Criteria:** Export contains only the authenticated user's records; zero cross-user leakage.
- **Required Tests:** Export completeness & BOLA isolation pytest.
- **Risks:** Large export payloads timing out for heavy users (paginate/stream).

### Phase 3.16 — Self-Service Account Deletion (Web + Play Store Compliance)
- **Objective:** Implement irreversible account deletion and data erasure/anonymization for GDPR & Google Play compliance.
- **Reuse:** `users`, `analyses`, `investigations`, `audit_logs`.
- **Implement:** `DELETE /api/v1/auth/account` (password re-confirmation), public `/account/delete` web page, cascading deletion of personal analyses & `Private` investigations, anonymization of shared audit trails.
- **Dependencies:** Phase 3.15.
- **Deliverables:** In-app & web account deletion flow.
- **Acceptance Criteria:** Deleted user cannot log in; personal PII is removed from MongoDB.
- **Required Tests:** End-to-end deletion + post-deletion `401` login check.
- **Risks:** Breaking referential integrity on shared `Organization` investigations (reassign or anonymize author).

---

## Track C: Real-World Data Acquisition & Dataset Engineering (Phases 3.17 – 3.22)

### Phase 3.17 — Dataset Manifest & License Governance Automation
- **Objective:** Enforce programmatic license, SHA-256, and usage-tier checks on every dataset before preprocessing.
- **Reuse:** `data/dataset_manifest.json`, `ml/preprocessing/`.
- **Implement:** Manifest validator CLI rejecting datasets without verified license, provenance URL, and usage tier (`train | eval | threat_intel_only`).
- **Dependencies:** Phase 3.0.
- **Deliverables:** `ml/datasets/validate_manifest.py` + CI check.
- **Acceptance Criteria:** Unlicensed or unhashed files fail validation.
- **Required Tests:** Unit tests with valid/missing-license manifests.
- **Risks:** Ambiguous third-party Hugging Face licenses.

### Phase 3.18 — Benign & Multilingual Hindi/Indic Corpus Acquisition
- **Objective:** Acquire properly licensed Hindi (Devanagari), Hinglish, Bengali, and Tamil benign + scam datasets to fix Hindi `0.5455` recall and verify regional languages.
- **Reuse:** `ml/preprocessing/dataset_cleaner.py`, `data/dataset_manifest.json`.
- **Implement:** Ingest vetted MIT/CC-BY/Apache-2.0 multilingual corpora (e.g., IndicNLP/AI4Bharat benign text + curated multilingual scam advisories).
- **Dependencies:** Phase 3.17.
- **Deliverables:** Versioned raw + cleaned multilingual parquet datasets in `data/processed/v2/`.
- **Acceptance Criteria:** Balanced Hindi representation (`>= 5,000` train, `>= 1,000` test); explicit language tags.
- **Required Tests:** Schema, encoding (UTF-8 NFC), and language-distribution verification script.
- **Risks:** Domain shift between news/wiki benign Hindi and conversational SMS/WhatsApp Hindi.

### Phase 3.19 — Modern Benign & Phishing URL Corpus Acquisition
- **Objective:** Eliminate the `15.33%` URL false-positive rate by expanding training/calibration data with modern legitimate URLs (Tranco Top-1M) and verified phishing feeds (URLhaus CC0).
- **Reuse:** `ml/preprocessing/url_preprocessor.py`, `data/raw/legitphish/`.
- **Implement:** Offline lexical feature extraction over Tranco benign URLs (with realistic deep paths/query params) + URLhaus phishing URLs, zero outbound HTTP calls.
- **Dependencies:** Phase 3.17.
- **Deliverables:** `urls_v2_train/val/test.parquet` with `domain_group_id` grouping.
- **Acceptance Criteria:** Zero root-domain overlap between train and test splits; zero live URL fetches.
- **Required Tests:** Domain-leakage assertion test + zero-network-call verification.
- **Risks:** Popularity bias if Tranco only includes root domains instead of full paths.

### Phase 3.20 — PII Redaction & Consented Community Report Curation Pipeline
- **Objective:** Build a human-in-the-loop pipeline converting explicitly consented `scam_reports` into redacted evaluation/training candidates.
- **Reuse:** `backend/app/services/report_service.py`, `scam_reports` collection.
- **Implement:** Regex + NER PII scrubber (phone numbers, OTPs, PAN/Aadhaar, emails, names) + reviewer approval status (`approved_for_ml`).
- **Dependencies:** Phase 3.15, 3.17.
- **Deliverables:** `ml/datasets/curate_reports.py` + reviewer workflow.
- **Acceptance Criteria:** Zero unredacted PII in exported ML candidate files; unconsented reports excluded.
- **Required Tests:** Synthetic PII redaction unit test suite (`100%` pass on test patterns).
- **Risks:** Residual PII leaking into training corpora.

### Phase 3.21 — Near-Duplicate Deduplication & Frozen Golden Evaluation Benchmark
- **Objective:** Prevent train/test leakage across all corpora and freeze an untouched `data/golden_eval/` benchmark.
- **Reuse:** `ml/preprocessing/dataset_cleaner.py`.
- **Implement:** SimHash/MinHash near-duplicate clustering + `StratifiedGroupKFold` split generator + frozen SHA-256 golden holdout.
- **Dependencies:** Phase 3.18, 3.19, 3.20.
- **Deliverables:** Immutable `data/golden_eval/` benchmark across English, Hindi, Hinglish, URLs, and Tactics.
- **Acceptance Criteria:** `0` exact or near-duplicate overlaps between train and `golden_eval`.
- **Required Tests:** Automated leakage audit script.
- **Risks:** Over-aggressive deduplication removing valid template variations.

### Phase 3.22 — Fake Investment / Crypto Scam Tactic Annotation Sprint
- **Objective:** Collect and dual-annotate verified `fake_investment` ground-truth examples so the currently `UNAVAILABLE` 10th tactic can be legitimately trained.
- **Reuse:** `ml/artifacts/tactic_detection/tactic_metadata.json` taxonomy.
- **Implement:** Curate verified investment/crypto/task-scam advisories & consented reports with inter-annotator agreement (`Cohen's kappa >= 0.80`).
- **Dependencies:** Phase 3.20, 3.21.
- **Deliverables:** Verified `fake_investment` labeled dataset slice.
- **Acceptance Criteria:** Clear annotation guidelines + kappa >= 0.80.
- **Required Tests:** Label distribution & agreement audit script.
- **Risks:** Confusion between legitimate fintech alerts and investment scams.

---

## Track D: Machine Learning Remediation, Calibration & Governance (Phases 3.23 – 3.31)

### Phase 3.23 — Hindi & Multilingual Text Model Remediation
- **Objective:** Raise Hindi Devanagari recall from `0.5455` to `>= 0.88` while maintaining English `>= 0.96` and overall FPR `< 2%`.
- **Reuse:** `ml/text_detection/`, `ml/campaign_detection/embeddings.py` (multilingual MiniLM).
- **Implement:** Compare class-weighted Char+Word TF-IDF LinearSVC vs multilingual embedding/XLM-R/MuRIL-lite classifier (`ml/notebooks/02_train_muril_transformer_gpu.ipynb`) within RAM/latency budgets.
- **Dependencies:** Phase 3.18, 3.21.
- **Deliverables:** Candidate `text_detection` v2 artifact + per-language confusion matrices.
- **Acceptance Criteria:** Hindi recall `>= 0.88`, English F1 `>= 0.96`, FPR `< 0.02` on `golden_eval`.
- **Required Tests:** Per-language evaluation suite + inference latency benchmark (`< 50ms` CPU).
- **Risks:** Transformer model exceeding `2 GB` Render RAM budget (benchmark RSS carefully).

### Phase 3.24 — Phishing URL Model Retraining & FPR Calibration
- **Objective:** Reduce URL false-positive rate from `15.33%` to `< 2.0%` on modern benign URLs without sacrificing recall.
- **Reuse:** `ml/url_detection/`, XGBoost + SHAP pipeline.
- **Implement:** Expand lexical/structural features (e.g., punycode/IDN homograph indicators, brand-in-subdomain vs registrable domain, entropy), retrain on `urls_v2`, apply isotonic/Platt probability calibration.
- **Dependencies:** Phase 3.19, 3.21.
- **Deliverables:** Candidate `url_detection` v2 XGBoost artifact + SHAP schema.
- **Acceptance Criteria:** `golden_eval` FPR `< 0.02`, Recall `>= 0.95`, zero outbound network calls.
- **Required Tests:** Balanced modern-URL FPR stress test + SHAP stability test.
- **Risks:** Overfitting to Tranco top domains.

### Phase 3.25 — Tactic Classifier Expansion (Enabling `fake_investment`)
- **Objective:** Retrain multi-label OvR/classifier chain to support all 10 tactics including `fake_investment`.
- **Reuse:** `ml/tactic_detection/`, `thresholds.json`.
- **Implement:** Train & tune per-label thresholds on `v2` tactic corpus; update `tactic_metadata.json`.
- **Dependencies:** Phase 3.22, 3.23.
- **Deliverables:** 10-tactic calibrated model + updated PR curves.
- **Acceptance Criteria:** Macro F1 `>= 0.90`, `fake_investment` F1 `>= 0.85` on `golden_eval`.
- **Required Tests:** Per-label precision/recall threshold test.
- **Risks:** Label co-occurrence skew lowering precision on rare tactics.

### Phase 3.26 — Probability Calibration & Risk Engine Recalibration
- **Objective:** Align `TransparentRiskAggregationService` thresholds with calibrated v2 model probabilities and Brier score targets.
- **Reuse:** `backend/app/services/risk_service.py`, `tests/test_risk_engine.py`.
- **Implement:** Reliability diagrams, Brier score validation (`< 0.03`), and `inconclusive` band tuning.
- **Dependencies:** Phase 3.23, 3.24, 3.25.
- **Deliverables:** Updated risk aggregation policy & calibration report.
- **Acceptance Criteria:** Clean inputs return `clean`/`low` with `< 2%` false alarm; missing inputs return `inconclusive`.
- **Required Tests:** `tests/test_risk_engine.py` + calibration curve checks.
- **Risks:** Over-confident probabilities triggering false `critical` alerts.

### Phase 3.27 — Evidence & Explainability Enhancement (User-Friendly Explanations)
- **Objective:** Translate technical SHAP/TF-IDF weights into clear, plain-language consumer explanations alongside analyst details.
- **Reuse:** `ml/explainability/explainer.py`, `AnalysisResultPanel.tsx`.
- **Implement:** Plain-language reason templates mapped from top SHAP features, highlighted text spans, and detected tactics.
- **Dependencies:** Phase 3.24, 3.25, 3.26.
- **Deliverables:** Dual-tier explanation payload (`summary_reasons` + `technical_evidence`).
- **Acceptance Criteria:** Every `medium+` prediction includes >= 2 human-readable evidence reasons.
- **Required Tests:** Explanation contract test across text, URL, and image results.
- **Risks:** Misleading explanations if feature attribution doesn't match calibrated score.

### Phase 3.28 — Campaign Re-Clustering Pipeline & Incremental Assignment
- **Objective:** Automate periodic HDBSCAN campaign discovery over newly confirmed threats and nearest-cluster assignment for incoming scans.
- **Reuse:** `ml/campaign_detection/`, `campaign_service.py` (Phase 2.4 sync).
- **Implement:** Scheduled offline clustering job producing versioned `campaign_dossiers.json` + safe sync preserving `verified` DB records.
- **Dependencies:** Phase 2.4, 3.23.
- **Deliverables:** Reproducible campaign refresh job + silhouette/Davies-Bouldin quality gate.
- **Acceptance Criteria:** New clusters never overwrite `verification_status == "verified"` DB records.
- **Required Tests:** Idempotent sync + quality-gate regression test.
- **Risks:** Cluster ID drift across runs (mitigate via stable centroid/signature matching).

### Phase 3.29 — OCR Pipeline Hardening (Multilingual & Screenshot Noise)
- **Objective:** Improve OCR accuracy on compressed WhatsApp/Telegram screenshots in English & Devanagari Hindi.
- **Reuse:** `backend/app/services/ocr_service.py`.
- **Implement:** Preprocessing (adaptive thresholding, deskew, upscaling) + multi-language OCR config (`eng+hin`) + graceful fallback when OCR yields low/empty text (`inconclusive`).
- **Dependencies:** Phase 3.23.
- **Deliverables:** Hardened `ocr_service.py` with language-aware extraction.
- **Acceptance Criteria:** Cleanly handles blurry/empty screenshots without false positives; passes 10 MB / MIME / `PIL.Image.verify()` security checks.
- **Required Tests:** Synthetic noisy-screenshot & empty-image pytest suite.
- **Risks:** Tesseract memory/CPU spikes under concurrent image uploads.

### Phase 3.30 — Model Registry Sync, Shadow Evaluation & Rollback Gate
- **Objective:** Fix `model_registry.json` metadata discrepancies (e.g., supported languages) and add automated shadow/canary comparison before promotion.
- **Reuse:** `ml/artifacts/model_registry.json`, `ml/evaluation/validate_registry.py`, `backend/app/services/training_service.py`.
- **Implement:** Registry schema validator + automated `golden_eval` gate blocking promotion if any metric regresses.
- **Dependencies:** Phase 3.23–3.28.
- **Deliverables:** Synchronized `model_registry.json` + automated promotion gate.
- **Acceptance Criteria:** Registry metadata matches actual `model_metadata.json` and `golden_eval` results 100%.
- **Required Tests:** `test_model_validation.py` + promotion rollback test.
- **Risks:** Stale SHA-256 hashes breaking `CentralModelLoader` startup.

### Phase 3.31 — Inference Latency, Memory Profiling & Caching Optimization
- **Objective:** Ensure combined v2 ML runtime stays within `< 1.2 GB` RSS and `< 100ms` p95 text/URL inference latency on CPU.
- **Reuse:** `ml/campaign_detection/embeddings.py` singleton, `backend/app/ml_engine/`.
- **Implement:** Memory/latency profiler CI benchmark + optional LRU caching for repeated normalized URL/text hashes.
- **Dependencies:** Phase 3.30.
- **Deliverables:** Performance benchmark report (`p50/p95/p99`, RSS MB).
- **Acceptance Criteria:** RSS `< 1.2 GB`, p95 text+tactic+URL `< 100ms` on standard CPU.
- **Required Tests:** Load/concurrency benchmark (`test_model_loading_singleton.py` extended).
- **Risks:** Unbounded in-memory cache causing slow RSS growth (use bounded `OrderedDict`/LRU).

---

## Track E: Investigation, Threat Intelligence & Automation Maturity (Phases 3.32 – 3.38)

### Phase 3.32 — Investigation Collaboration & Reviewer Workflow
- **Objective:** Support `Organization` investigation sharing, role-based reviewer assignment, and status workflow transitions (`open -> in_progress -> resolved`).
- **Reuse:** `investigation_service.py`, `InvestigationWorkspace.tsx`.
- **Implement:** Collaborator/reviewer assignment field, timeline events for assignments, and UI status controls.
- **Dependencies:** Phase 2.3, 3.7.
- **Deliverables:** Reviewer assignment + status transition UI & API.
- **Acceptance Criteria:** Only owner/admin/assigned reviewer can modify; timeline records every transition.
- **Required Tests:** RBAC + timeline transition pytest.
- **Risks:** Unauthorized privilege escalation via assignment endpoint.

### Phase 3.33 — Investigation Evidence Export (JSON & STIX 2.1 Bundle)
- **Objective:** Allow analysts to export an investigation's graph, notes, timeline, and IOCs in verified JSON and STIX 2.1 formats.
- **Reuse:** `backend/app/api/routes/exports.py`.
- **Implement:** Investigation-scoped export endpoints enforcing `Private` BOLA checks and redacting internal secrets.
- **Dependencies:** Phase 3.32.
- **Deliverables:** `GET /api/v1/investigations/{id}/export?format=json|stix`.
- **Acceptance Criteria:** STIX output validates against STIX 2.1 schema; unauthorized users receive `403`.
- **Required Tests:** Schema validation + BOLA export pytest.
- **Risks:** Leaking private notes in shared exports without warning.

### Phase 3.34 — Community Scam Reporting & Moderation Queue
- **Objective:** Connect user-submitted `/reports` cleanly to reviewer triage, deduplication, and `threat_indicators` promotion.
- **Reuse:** `backend/app/api/routes/reports.py`, `frontend/app/reports/page.tsx`.
- **Implement:** Streamlined submission form, reviewer triage queue (`approve | reject | duplicate`), and audit logging.
- **Dependencies:** Phase 3.7, 3.20.
- **Deliverables:** End-to-end community report submission & moderation workflow.
- **Acceptance Criteria:** Non-reviewers get `403` on `/review`; approved IOCs appear in Threat Library.
- **Required Tests:** Report lifecycle + RBAC pytest.
- **Risks:** Spam submissions flooding moderation queue (mitigated by Phase 3.14 rate limits).

### Phase 3.35 — Safe Automated Threat Intelligence Feed Ingestion (URLhaus / Official Feeds)
- **Objective:** Harden `n8n` / backend feed ingestion (`POST /api/v1/automation/ingest-feed`) with strict validation, deduplication, and provenance.
- **Reuse:** `backend/app/api/routes/automation.py`, `threat_indicators` unique index, `n8n/workflows/`.
- **Implement:** Domain/URL canonicalization, feed provenance (`URLhaus_Threat_Feed`), TTL/staleness tracking, and HMAC/secret verification.
- **Dependencies:** Phase 3.19.
- **Deliverables:** Production-hardened feed ingestion + Threat Library UI sync.
- **Acceptance Criteria:** Zero duplicate `threat_indicators`; invalid webhook secret returns `401`/`403`.
- **Required Tests:** `test_n8n_automation.py` extended with malformed feed & secret-mismatch tests.
- **Risks:** Upstream feed outages or false-positive domains entering `threat_indicators`.

### Phase 3.36 — ML Drift, Calibration & Production Monitoring
- **Objective:** Monitor live prediction distributions, `inconclusive` rate, OCR failure rate, and latency without storing raw sensitive text.
- **Reuse:** `backend/app/api/v1/routers/telemetry.py`, `analytics_service.py`.
- **Implement:** Aggregate daily telemetry metrics (score histograms, language distribution, latency p95, error rates) surfaced in `/models` and `/analytics` for admins.
- **Dependencies:** Phase 3.30, 3.31.
- **Deliverables:** Privacy-safe ML observability metrics & drift alerts.
- **Acceptance Criteria:** Zero raw message PII in monitoring metrics; alerts trigger on `inconclusive` spike.
- **Required Tests:** Telemetry aggregation unit & API tests.
- **Risks:** Metric skew from automated health checks/bots.

### Phase 3.37 — Browser E2E Regression Suite (Playwright)
- **Objective:** Eliminate the Phase 2.5 browser-testing gap with an automated headless Playwright suite covering all critical web user journeys.
- **Reuse:** `frontend/`, `tests/`.
- **Implement:** Playwright tests for Landing + Circular Nav, Register/Login, Text/URL/Image scan, Attach to Investigation, Notes, Timeline refresh, Campaigns, and mobile viewports (`390x844`).
- **Dependencies:** Phase 3.8, 3.16.
- **Deliverables:** Automated CI-runnable `frontend/e2e/` Playwright suite.
- **Acceptance Criteria:** All critical user journeys pass on desktop & mobile viewports in headless Chromium.
- **Required Tests:** `npx playwright test` passing 100%.
- **Risks:** Flaky timing on ML inference responses (use deterministic waits).

### Phase 3.38 — Frontend Dependency & Security Modernization
- **Objective:** Resolve the `next@14.2.35` `npm audit` advisories and clean up remaining React hook/lint warnings.
- **Reuse:** `frontend/package.json`.
- **Implement:** Evaluate and apply patched Next.js security release (or controlled 15.x migration), resolve `react-hooks/exhaustive-deps` warnings, re-run `npm audit`.
- **Dependencies:** Phase 3.37 (regression safety net).
- **Deliverables:** Clean `npm audit` (0 critical/high) + `0` ESLint warnings.
- **Acceptance Criteria:** Full Playwright + `tsc` + `lint` + `build` pass post-upgrade.
- **Required Tests:** Full frontend build & Playwright suite.
- **Risks:** Breaking App Router / Framer Motion compatibility on major Next upgrade.

---

## Track F: Android Mobile Application Development (Phases 3.39 – 3.45)

### Phase 3.39 — Mobile Project Initialization (React Native / Expo TypeScript)
- **Objective:** Bootstrap `mobile/` Expo TypeScript workspace sharing API contracts with the FastAPI backend.
- **Reuse:** `backend/app/schemas/*`, `frontend/lib/api.ts` patterns.
- **Implement:** Expo SDK setup, TypeScript strict config, environment config, navigation skeleton, `expo-secure-store` token persistence.
- **Dependencies:** Phase 3.11 (refresh tokens).
- **Deliverables:** Runnable `mobile/` Android dev build connecting to local/staging FastAPI.
- **Acceptance Criteria:** App boots on Android emulator/device and reaches `/api/v1/health`.
- **Required Tests:** Jest unit tests + Android emulator smoke boot.
- **Risks:** Localhost networking differences on Android emulator (`10.0.2.2`).

### Phase 3.40 — Mobile Authentication, Biometrics & Session Management
- **Objective:** Implement Sign In, Sign Up, email verification prompt, refresh-token rotation, and optional biometric unlock on Android.
- **Reuse:** `/api/v1/auth/*` (Phases 3.11–3.13).
- **Implement:** SecureStore JWT storage, automatic 401 refresh interceptor, Sign Out.
- **Dependencies:** Phase 3.11, 3.12, 3.39.
- **Deliverables:** Complete mobile auth flow.
- **Acceptance Criteria:** Tokens never stored in `AsyncStorage` plaintext; expired session refreshes transparently.
- **Required Tests:** Auth flow integration & SecureStore mock tests.
- **Risks:** Token loss on OS backup/restore (disable backup for SecureStore keys).

### Phase 3.41 — Mobile Core Analysis & Result Presentation UI
- **Objective:** Build mobile-native Text, URL, and Screenshot Picker analysis screens with clear evidence cards.
- **Reuse:** `/api/v1/analyze/*`, Phase 3.27 explanation contract.
- **Implement:** Paste/type input, Android Photo Picker (`READ_MEDIA_IMAGES` minimized), calibrated risk gauge, plain-language reasons, and offline error states.
- **Dependencies:** Phase 3.27, 3.40.
- **Deliverables:** Mobile Analyze + Result screens.
- **Acceptance Criteria:** All 3 modalities return real backend ML results with accessible typography and loading states.
- **Required Tests:** Component + API integration tests on Android emulator.
- **Risks:** Large camera screenshots exceeding 10 MB (compress client-side before upload).

### Phase 3.42 — Android Share-Sheet Intent Integration (`ACTION_SEND`)
- **Objective:** Allow Android users to share suspicious text or URLs directly from WhatsApp, SMS, or browsers into TRUSTLENS AI.
- **Reuse:** Phase 3.41 analysis screen.
- **Implement:** Android intent filter for `text/plain` -> deep-link directly into pre-filled Analyze screen.
- **Dependencies:** Phase 3.41.
- **Deliverables:** Working Share-to-TRUSTLENS workflow on Android.
- **Acceptance Criteria:** Sharing a URL or SMS from another app opens TRUSTLENS AI pre-populated for 1-tap scan (zero `READ_SMS` permission needed).
- **Required Tests:** ADB intent dispatch test (`am start -a android.intent.action.SEND`).
- **Risks:** Malformed intent extras crashing app on cold start.

### Phase 3.43 — Mobile History, Investigations & Community Reporting
- **Objective:** Bring personal scan history, read/note access on investigations, and scam reporting to Android.
- **Reuse:** `/api/v1/analyses`, `/api/v1/investigations`, `/api/v1/reports`.
- **Implement:** Paginated history list, investigation summary + notes, report submission.
- **Dependencies:** Phase 3.40, 3.41.
- **Deliverables:** Mobile History, Investigation detail, and Report screens.
- **Acceptance Criteria:** Records created on mobile appear on web and vice versa.
- **Required Tests:** Cross-platform persistence verification test.
- **Risks:** Slow mobile networks causing duplicate note/report taps (add idempotency/disable-on-submit).

### Phase 3.44 — Consented Push Notifications (FCM) & In-App Account Deletion
- **Objective:** Implement opt-in threat alert notifications (Android 13+ runtime permission) and mandatory in-app account deletion.
- **Reuse:** Phase 3.16 (`DELETE /api/v1/auth/account`).
- **Implement:** FCM device token registration (opt-in only), notification preferences, in-app Settings -> Export Data & Delete Account.
- **Dependencies:** Phase 3.16, 3.40.
- **Deliverables:** Play-compliant notification consent & account deletion UI.
- **Acceptance Criteria:** Zero notifications sent without explicit opt-in; account deletion removes mobile session and backend account.
- **Required Tests:** Consent toggle + deletion E2E test.
- **Risks:** Play Store rejection if account deletion is buried or broken.

### Phase 3.45 — Mobile Hardening, Release Signing & Crash/ANR Telemetry
- **Objective:** Configure ProGuard/R8, TLS certificate/network security config, release keystore management, and privacy-safe crash reporting.
- **Reuse:** `mobile/` EAS/Gradle config.
- **Implement:** Production AAB build pipeline, disable cleartext HTTP in release, strip debug logs.
- **Dependencies:** Phase 3.44.
- **Deliverables:** Signed release `.aab` + security checklist verification.
- **Acceptance Criteria:** Release `.aab` passes static security scan (no hardcoded secrets, no cleartext traffic).
- **Required Tests:** Release AAB smoke test on physical/emulator Android device.
- **Risks:** Lost upload keystore (use Play App Signing).

---

## Track G: Cloud Production Deployment, Play Store Release & Continuous Improvement (Phases 3.46 – 3.50)

### Phase 3.46 — Staging Cloud Environment & MongoDB Atlas Hardening
- **Objective:** Provision staging backend (`>= 2 GB RAM` per `render.yaml`), staging Next.js frontend, and MongoDB Atlas with automated backups & TLS.
- **Reuse:** `render.yaml`, `backend/app/database/indexes.py`.
- **Implement:** Infrastructure-as-code / env secret injection, MongoDB Atlas IP/VPC rules, automated backup verification, `ensure_indexes()` migration.
- **Dependencies:** Phase 3.10, 3.31.
- **Deliverables:** Live staging environment mirroring production topology.
- **Acceptance Criteria:** Health check `200`, all indexes active, automated DB backup verified.
- **Required Tests:** Staging smoke suite + load test.
- **Risks:** Cold-start timeouts or OOM if deployed on `< 2 GB` RAM tier.

### Phase 3.47 — Full Penetration Test, Security Audit & Load Testing
- **Objective:** Conduct pre-launch OWASP API/Web security testing and sustained load testing against staging.
- **Reuse:** `docs/audit/SECURITY_AUDIT.md`, `tests/test_phase2_5_e2e_workflow.py`.
- **Implement:** Automated DAST/OWASP ZAP scan, BOLA/auth fuzzing, k6/Locust load test on `/analyze/*` and `/investigations/*`.
- **Dependencies:** Phase 3.38, 3.46.
- **Deliverables:** Pre-release Security & Load Sign-Off Report.
- **Acceptance Criteria:** Zero critical/high security findings; error rate `< 0.5%` under target concurrency.
- **Required Tests:** Security scan + load test report.
- **Risks:** Rate limiter or MongoDB connection pool exhaustion under load.

### Phase 3.48 — Production Web & API Launch
- **Objective:** Deploy validated TRUSTLENS AI web platform and FastAPI backend to production with rollback runbook and uptime alerts.
- **Reuse:** Staging deployment config (Phase 3.46).
- **Implement:** Production DNS/TLS, CORS origin lock, health monitoring, error alerting, documented rollback procedure.
- **Dependencies:** Phase 3.47.
- **Deliverables:** Live production website (`/`), authenticated web app, and API.
- **Acceptance Criteria:** Post-deploy smoke tests pass; zero console/500 errors; monitoring active.
- **Required Tests:** Read-only production smoke suite.
- **Risks:** Misconfigured `ALLOWED_ORIGINS` or missing env vars.

### Phase 3.49 — Google Play Console Closed Testing & Play Store Launch
- **Objective:** Complete Google Play Data Safety form, privacy disclosures, closed testing track, and staged production rollout (`10% -> 50% -> 100%`).
- **Reuse:** Phase 3.45 signed `.aab`, Phase 3.5 `/privacy`, Phase 3.16 `/account/delete`.
- **Implement:** Store listing (honest capabilities, no unverified accuracy claims), Data Safety declaration, closed beta feedback fixes, staged rollout.
- **Dependencies:** Phase 3.45, 3.48.
- **Deliverables:** Published TRUSTLENS AI Android app on Google Play Store.
- **Acceptance Criteria:** Passes Google Play policy review; crash-free rate `>= 99.5%` in closed testing.
- **Required Tests:** Pre-launch report (Firebase Test Lab / Play Console) + staged rollout monitoring.
- **Risks:** Play Store review rejection due to financial/impersonation metadata wording (use clear defensive/educational framing).

### Phase 3.50 — Continuous ML Retraining, Multilingual Expansion & Feedback Loop
- **Objective:** Establish ongoing quarterly dataset curation, golden-eval benchmarking, Hindi/Tamil/Bengali model updates, and user feedback loop.
- **Reuse:** Phases 3.20–3.30 MLOps & governance pipeline.
- **Implement:** Quarterly consented-report curation, drift-triggered retraining, shadow evaluation, and safe versioned rollout.
- **Dependencies:** Phase 3.48, 3.49.
- **Deliverables:** Continuous MLOps cadence + quarterly model quality reports.
- **Acceptance Criteria:** Every model update beats or matches `golden_eval` baseline across all supported languages before promotion.
- **Required Tests:** Automated `golden_eval` regression gate on every release candidate.
- **Risks:** Concept drift as scammers adopt new LLM-generated phishing templates.
