# TRUSTLENS AI — Trust & Transparency Framework

1. **Supported Languages:** Evaluated on **English**, **Hindi (Devanagari)**, and **Hinglish**. **Tamil** and **Bengali** have `0` training/evaluation samples and are explicitly marked `unsupported_unverified`.
2. **Model Limitations:**
   - **Model 1 (Text, `v2.1`):** Linear TF-IDF + Calibrated LinearSVC; limited to evaluated languages.
   - **Model 2 (URL, `v2.2`):** Zero-hop offline XGBoost + lexical/brand/homograph signals; never visits target URLs and cannot prove server safety or malice.
   - **Model 3 (Tactics, `v2.3`):** Supports `9` verified tactics; `fake_investment` is `Blocked` due to `0` verified ground-truth labels.
   - **Model 4 (Campaigns, `v2.4`):** Unsupervised embedding similarity + HDBSCAN; does not constitute legal proof of identical organizational origin.
3. **Dataset Provenance:** `ScamShield` (MIT), `SMS Phishing` (CC BY 4.0), `LegitPhish` (CC BY 4.0), `UCI SMS Spam` (CC BY 4.0), `PhishTank` (Data Feeds ToU), `CISA KEV` (CC0 1.0), and `URLhaus` (non-commercial gated).
4. **Prediction Uncertainty:** Separates Platt-calibrated probabilities (Models 1 & 3) from uncalibrated tree/similarity scores (Models 2 & 4), returning `inconclusive` when evidence is insufficient.
5. **Data Handling Practices:** Automated PII masking, `90`-day retention for analyses/unverified reports, `365`-day audit logs, and zero automatic training from unverified user reports.
6. **Reporting & Moderation Procedures:** Community submissions enter as `pending`, transition through `reviewed`, `rejected`, or `confirmed`, and only `confirmed` reports influence `threat_indicators` or training candidates.
7. **Human Review Requirements:** Required for Production model promotion, community report confirmation, FP/FN feedback ground-truth verification, and high-uncertainty cases.
8. **User Rights:** Consent (`GET/PUT /api/v1/privacy/consent`), personal data export (`GET /api/v1/auth/export-data`), analysis deletion (`DELETE /api/v1/analyses/{id}`), account deletion (`DELETE /api/v1/auth/account`), and access logs (`GET /api/v1/privacy/access-logs`).
9. **Security Contact:** `security@trustlens.ai`.

**User-Facing Disclaimer:** TRUSTLENS AI provides statistical decision-support only. It does **not** claim universal fraud detection, 100% accuracy, or legal attribution.
