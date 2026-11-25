# TRUSTLENS AI — PHASE 5.0: KNOWN LIMITATIONS & REMAINING ISSUES

> **Date:** November 25, 2026

---

## 1. Machine Learning & Detection Limitations

1. **URL Classifier False Positive Rate (`15.33%` on held-out sample):** On `300` balanced held-out URLs from `urls_test.parquet`, the URL detector achieved `0.9233` accuracy with `0` false negatives (`FNR=0.0`) but `23` false positives out of `150` legitimate URLs (`FPR=0.1533`). Benign URLs with complex query strings or unusual TLDs may require analyst review.
2. **No Universal Scam Guarantee:** No static NLP, lexical URL, or clustering model can detect 100% of novel social-engineering lures, zero-day phishing domains, or out-of-distribution languages.
3. **Zero-Hop Static Inspection:** URL analysis never resolves DNS, fetches remote HTML, or detonates payloads in a sandbox.
4. **HDBSCAN Cluster Attribution:** Campaign similarity clusters (`47` dossiers) reflect mathematical embedding density and do not establish legal threat-actor attribution.

---

## 2. Security & Dependency Remaining Issues

1. **Missing Root `.env` File:** Local execution uses fallback development secrets in [`settings.py`](file:///c:/Users/jaswant%20karun/TRUSTLENS%20AI/backend/app/config/settings.py) (`DEBUG=True`). A production `.env` must be provisioned before deployment.
2. **Next.js Dependency Advisories:** `npm audit` reported `2` vulnerabilities (`1` critical, `1` high) in `next@14.2.35`. Upgrade `next` before production release.
3. **Python `pip-audit` Not Run:** `.venv` is managed via `uv` without `pip`/`pip-audit` installed (`NOT TESTED`).

---

## 3. Infrastructure & Testing Gaps

1. **n8n Daemon Not Running Locally:** Live n8n server import and webhook trigger execution on port `5678` is `BLOCKED` locally; all 6 workflow JSONs and backend endpoints were validated directly.
2. **Interactive Browser Canvas FPS:** Visual frame-rate profiling of ThreatQ graph zoom/pan in a live Chromium session was `NOT TESTED` in Phase 5.0 (verified via SSR + API + TypeScript build).
