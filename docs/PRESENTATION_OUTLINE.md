# TRUSTLENS AI — 12-SLIDE PRESENTATION OUTLINE

1. **Title:** TRUSTLENS AI — Multilingual Digital Fraud Intelligence & Threat Investigation Graph (*"Detect the deception before people lose their money."*)
2. **Problem:** Rapid growth of multilingual smishing (English/Hindi/Hinglish), short-lived phishing URLs, and UPI/KYC impersonation scams.
3. **Existing Limitations:** Static blacklists miss new domains; opaque confidence scores lack auditability; siloed scanners lack campaign/graph context.
4. **Proposed Solution:** Zero-hop multi-modal ML + transparent risk calibration + ThreatQ-inspired investigation graph + STIX 2.1 reporting + n8n orchestration.
5. **Product Demonstration:** Live walkthrough of `/analyze/text`, `/analyze/url`, `/investigations/INV-2026-0011`, `/threat-library`, `/analytics`, and `/reports` (3-minute script).
6. **Technical Architecture:** Next.js 14 proxy -> FastAPI + `CentralModelLoader` (SHA-256) -> MongoDB (11 collections) -> n8n (6 exported workflows).
7. **Machine-Learning Methodology:** Model 1 (Word+Char TF-IDF + Calibrated LinearSVC), Model 2 (16-feature Lexical XGBoost + SHAP), Model 3 (OvR LinearSVC for 9 tactics), Model 4 (Multilingual MiniLM + HDBSCAN).
8. **Dataset & Evaluation:** Group-aware splits (`text_group_id`, `domain_group_id`; seed `42`); Model 1 (`0.9760` Macro F1), Model 2 (`0.9998` benchmark F1; `0.9233` acc / `0.1533` FPR on balanced `n=300` spot check), Model 3 (`0.9513` Micro F1), Model 4 (`47` clusters).
9. **Innovation & Differentiation:** Clear separation of ML inference, threat intel, and human review; explicit `INCONCLUSIVE` fallback; 1-hop graph expansion; zero-hop URL safety.
10. **Impact:** Enables faster, evidence-backed SOC triage, structured STIX 2.1 sharing, and auditable community report verification.
11. **Security & Privacy:** `bcrypt` (`rounds=12`), `HS256` JWTs, RBAC (`401`/`403`), OWASP headers, `PIL.Image.verify()` upload checks, zero-hop URL handling, and redacted n8n alerts.
12. **Limitations & Roadmap:** Hindi recall (`0.5455`), URL FPR (`0.1533`), `next@14.2.35` npm advisories, and cloud provisioning (`Vercel`/`Render`/`Atlas`/`n8n`) next steps.
