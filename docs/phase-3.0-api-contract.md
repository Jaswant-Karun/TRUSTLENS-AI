# TRUSTLENS AI — PHASE 3.0: BACKEND ML INFERENCE & GOVERNANCE API CONTRACT

> **API Base Prefix:** `/api/v1`  
> **Protocol:** REST JSON / Multipart Form Data  
> **OpenAPI Docs:** `http://127.0.0.1:8000/docs`

---

## 1. Threat Analysis Endpoints

### `POST /api/v1/analyze/text`
Classifies SMS, WhatsApp, or Email communications using Model 1 (Text Scam), Model 3 (Tactics), Model 4 (Campaigns), and SHAP/Linear explainability.
- **Request Body:** `{"text": "<1..10000 chars>", "channel": "sms|whatsapp|email|auto", "sender": "<optional>"}`
- **Response (`AnalysisResultResponse`):** Includes `analysis_id`, `analysis_type`, `threat_level`, `confidence`, `risk_score`, `risk_assessment`, `text_model` (`model_version`, `is_threat`, `confidence`), `url_model`, `tactic_model`, `campaign_association`, `extracted_iocs`, `explainability`, `processing_time_ms`, `created_at`.

### `POST /api/v1/analyze/url`
Performs zero-hop offline lexical inspection using Model 2 (XGBoost) + SHAP TreeExplainer. Never connects to target URLs.
- **Request Body:** `{"url": "<valid url string>"}`
- **Response:** `AnalysisResultResponse` with `url_model` (`is_phishing`, `risk_score`, `model_version`, `features`) and `explainability.url_evidence`.

### `POST /api/v1/analyze/image`
Validates uploaded screenshot (`JPEG/PNG/WebP`, max `10 MB`), performs OCR, and runs multi-model analysis (`completed` or `insufficient-evidence`).

### `POST /api/v1/analyze/comprehensive`
Unified endpoint routing URL-only payloads to `/analyze/url` and text/mixed payloads to `/analyze/text`.

---

## 2. Model Governance & Analysis History Endpoints

- `GET /api/v1/models`: Returns registered models and artifact SHA-256 metadata.
- `GET /api/v1/models/metrics`: Returns held-out test benchmarks across all 4 tracks.
- `GET /api/v1/models/{model_id}`: Returns detailed registry entry for a specific `model_id` (or `HTTP 404`).
- `GET /api/v1/analyses`: Returns paginated user/analyst scan history from MongoDB `analyses`.
- `GET /api/v1/analyses/{analysis_id}`: Returns detailed persisted scan record by UUID (or `HTTP 404`).

---

## 3. Unavailable Model Safety Contract
If any model fails SHA-256 verification or is missing on disk:
```json
{
  "status": "unavailable",
  "error": "Model artifact is not loaded.",
  "is_threat": null,
  "confidence": 0.0
}
```
Unavailable models are **never** reported as `clean`, `safe`, or `legitimate`.
