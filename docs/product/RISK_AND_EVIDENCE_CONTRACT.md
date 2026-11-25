# TRUSTLENS AI — RISK AND EVIDENCE CONTRACT

> **Grounded in:** `backend/app/schemas/analysis.py` (`AnalysisResultResponse`, `RiskAssessmentSummary`) and `backend/app/services/risk_service.py` (`TransparentRiskAggregationService`).

---

## 1. Separation of Signal Provenance

Every fraud assessment response MUST preserve four distinct layers without conflating them:

1. **ML Prediction (`text_model`, `url_model`, `tactic_model`, `campaign_association`):**
   - Includes exact `model_id` / `model_version`, raw predicted label, and calibrated score where evaluated (e.g., Platt-scaled LinearSVC).
   - If a model is unavailable, its status is explicitly `"unavailable"` (never substituted with a default confidence).
2. **Threat-Intelligence Match (`threat_intel_match` / `extracted_iocs`):**
   - Indicates whether extracted URLs/domains/indicators matched stored `threat_indicators` or `suspicious_urls`.
   - **Rule:** Absence of a threat-intelligence match MUST NOT be presented as proof of safety.
3. **Supporting Evidence (`explainability`, `transparency_breakdown`):**
   - Token saliency, SHAP feature attributions, and extracted IOCs with provenance.
4. **Human Review Decision (`verification_status`, `scam_reports.status`):**
   - Explicitly separates `"automated_inference"` from `"verified"` human adjudications (`reviewed_by`, `reviewed_at`, `review_notes`).

## 2. Risk Statuses & Aggregation Policy

Supported `threat_level` values: `clean`, `low`, `medium` (moderate), `high`, `critical`, `inconclusive`.

- **`inconclusive` / `insufficient-evidence`:** Returned immediately when input has `< 2` tokens without a URL, when OCR extracts no readable text, or when all models are unavailable.
- **No Arbitrary Averaging:** `TransparentRiskAggregationService.assess_risk()` weights signals based on signal availability and domain reliability (e.g., `url_weight = 0.85` for URL-only vs `0.40` when paired with `text_weight = 0.35`, `tactic_weight = 0.15`), and attenuates benign branding keywords when Model 1 classifies text as legitimate without coercive tactics.
- **Similarity Caveat:** Campaign clustering (`HDBSCAN`) denotes embedding proximity only—never confirmed criminal attribution.
