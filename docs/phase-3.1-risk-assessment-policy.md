# TRUSTLENS AI — PHASE 3.1: UNIFIED FRAUD RISK ASSESSMENT POLICY (`v3.1.0`)

> **Implementation:** [`ml/risk_engine/aggregator.py`](file:///c:/Users/jaswant%20karun/TRUSTLENS%20AI/ml/risk_engine/aggregator.py)  
> **Date:** November 25, 2026

---

## 1. Core Aggregation Principles

1. **No Arbitrary Score Averaging:** Different modalities (Text vs. URL) and correlated models (Text vs. Tactic) are never blindly averaged.
2. **Non-Double-Counting Correlated Signals:** Because Model 1 (Text Scam) and Model 3 (Social-Engineering Tactics) both analyze the exact same message text via TF-IDF, Model 3 is treated as a bounded corroboration modifier (`+0.025` per tactic, capped at `+0.05`, applied **only** when base risk $\ge 0.35$).
3. **Independent Modality Precedence:** When a message carries an embedded URL, Text (Model 1) and URL (Model 2) are independent modalities; the base score takes `max(text_prob, url_prob)` and explicitly logs any modality conflict.
4. **Source Trustworthiness & Human Verification:**
   - **Verified Threat-Intel Hit** or **Human-Adjudicated `verified_scam`:** Floors aggregated risk at `0.90` (`CRITICAL`).
   - **Unverified Community Reports (`unverified`, `pending`):** Preserved in evidence records with `verification_state="unverified"` and **never** inflate automated risk scores.
5. **No False Safety Guarantees:** Missing threat-intelligence matches or `LOW` risk scores never certify an unknown URL or message as safe (`is_safety_guarantee: false`).

---

## 2. Output Risk Statuses & Thresholds

| Status | Score / Condition | Required Evidence & Policy Semantics |
|---|---|---|
| **`CRITICAL`** | Score $\ge 0.85$ (or Verified TI / Human Scam) | High-confidence threat signal corroborated by calibrated ML or verified human/TI evidence. |
| **`HIGH`** | $0.65 \le \text{Score} < 0.85$ | Strong threat indicators detected by primary calibrated classifier. |
| **`MODERATE`** | $0.35 \le \text{Score} < 0.65$ | Borderline or moderate suspicious indicators; analyst or user caution advised. |
| **`LOW`** | Score $< 0.35$ (No conflicts) | Low automated risk indicators. **Explicitly NOT a guarantee of safety.** |
| **`INCONCLUSIVE`** | Primary model unavailable OR irreconcilable conflict | Triggered when primary model is `unavailable` (without verified TI/human override), when human `benign` adjudication conflicts with high ML risk ($\ge 0.75$), or when ambiguous text ($0.20\text{--}0.55$) conflicts with $\ge 2$ coercion tactics. |
