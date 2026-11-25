# TRUSTLENS AI — PRODUCT VISION

> **Tagline:** *"Detect the deception before people lose their money."*  
> **Scope:** Product Architecture Blueprint (grounded strictly in `c:\Users\jaswant karun\TRUSTLENS AI`)

---

## 1. Product Purpose

TRUSTLENS AI is an evidence-backed digital fraud intelligence and investigation platform designed to move beyond isolated "scam score" widgets or static admin dashboards. It connects suspicious communication intake (messages, URLs, screenshots) directly to explainable ML inference, indicator intelligence, similarity-based campaign discovery, human community review, and persistent investigation cases.

## 2. Core Product Principles

1. **Workflow-First, Not Widget-First:** Every screen supports a concrete user action—submit & inspect, correlate indicators, save/revisit a case, triage a community report, or export validated intelligence.
2. **Strict Provenance Separation:** The platform explicitly distinguishes:
   - **Automated ML Prediction** (with model ID/version and limitations),
   - **External / Stored Threat-Intelligence Match** (never equating "no match" with safety),
   - **Human-Reviewed Verdict** (authorized reviewer decision with timestamp and notes).
3. **Zero-Hop Safety:** Submitted URLs and screenshots are never visited, resolved, or executed; analysis relies strictly on offline lexical decomposition and local OCR text extraction.
4. **Honest Uncertainty:** Short, low-entropy, or conflicting inputs return `inconclusive` or `insufficient-evidence` rather than fabricated scores. No automated model claims 100% scam detection.

## 3. Core User Capabilities

1. Submit suspicious SMS, WhatsApp, email text, URLs, or screenshots.
2. Identify potential phishing, smishing, spam, and social-engineering tactics.
3. Inspect feature-level evidence (SHAP attributions, token saliency, extracted IOCs).
4. Explore related indicators and unsupervised campaign similarity candidates.
5. Save, annotate, and revisit persistent investigation cases (graph + timeline).
6. Submit community scam reports and allow authorized reviewers to adjudicate them.
7. Export supported intelligence in JSON (`trustlens-json-v1`) and STIX 2.1 bundles.
