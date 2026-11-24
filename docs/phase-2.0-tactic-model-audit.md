# TRUSTLENS AI — PHASE 2.0: SOCIAL-ENGINEERING TACTIC DETECTOR AUDIT (MODEL 3)

> **Directory Audited:** `ml/tactic_detection/` & `ml/artifacts/tactic_detection/`  
> **Audit Date:** November 25, 2026  

---

## 1. Ground-Truth Annotation Audit

A critical audit check was performed to ensure tactic labels were **NOT** fabricated using simple keyword rules:
- **Annotation Source:** `ml/tactic_detection/taxonomy.py` deterministically maps **genuine multi-head human/dataset annotations** from the ScamShield corpus (`head1_social_engineering`, `head2_scam_intent`, and `metadata.has_otp`).
- **Supported Tactics (9 of 10):**
  1. `urgency_time_pressure` (`head1.urgency == 1`)
  2. `threats_intimidation` (`head1.fear == 1` or `head2` in `['Electricity Disconnection', 'Traffic e-Challan']`)
  3. `otp_credential_requests` (`head2 == 'OTP / Credential Theft'` or `metadata.has_otp`)
  4. `financial_manipulation` (`head1.financial_pressure == 1` or `head2 == 'Loan Scam'`)
  5. `authority_impersonation` (`head1.authority_impersonation == 1` or `head2` in `['Traffic e-Challan', 'Fake KYC']`)
  6. `fake_employment` (`head2 == 'Telegram Job'`)
  7. `account_suspension` (`head2 == 'Bank Account Freeze'` or `('Fake KYC' and fear == 1)`)
  8. `prize_reward_scams` (`head1.reward_bait == 1` or `head2 == 'Lottery / Prize'`)
  9. `refund_payment_manipulation` (`head2` in `['UPI Fraud', 'Courier Scam']`)
- **Explicitly Blocked / Unavailable Tactic (1 of 10):**
  - `fake_investment` (`TACTIC_FAKE_INVESTMENT`): Explicitly marked `supported: False` with reason: *"UNAVAILABLE: No verified ground-truth training annotations exist in benchmark dataset. Model not fabricated."*

---

## 2. Model Architecture & Saved Artifacts

- **Training Script:** `ml/tactic_detection/train_models.py` (Executed on 69,286 train / 8,192 val / 8,202 test ScamShield records).
- **Architecture:** `OneVsRestClassifier(CalibratedClassifierCV(LinearSVC))` over Word+Char `FeatureUnion` TF-IDF (`vectorizer.joblib`, 2.17 MB) with validation-tuned per-label decision thresholds (`thresholds.json`).
- **Saved Artifacts:**
  - `ml/artifacts/tactic_detection/best_tactic_model.joblib` (12,974,273 bytes)
  - `ml/artifacts/tactic_detection/vectorizer.joblib` (2,174,573 bytes)
  - `ml/artifacts/tactic_detection/thresholds.json` (303 bytes)
  - `ml/artifacts/tactic_detection/tactic_metadata.json` & `tactic_experiment_report.json`

---

## 3. Per-Label Evaluation Metrics (8,202 Held-Out Test Samples)

**Winning Model (One-vs-Rest Calibrated LinearSVC):**
- **Micro F1:** `0.9513` | **Macro F1:** `0.9313` | **Weighted F1:** `0.9511` | **Hamming Loss:** `0.0039`

| Tactic Key | Precision | Recall | F1 Score | PR-AUC | Test Support | Tuned Threshold |
|---|---|---|---|---|---|---|
| `urgency_time_pressure` | 0.9397 | 0.9698 | 0.9545 | 0.9721 | 530 | 0.30 |
| `threats_intimidation` | 0.9373 | 0.9755 | 0.9560 | 0.9633 | 245 | 0.20 |
| `otp_credential_requests` | 0.9643 | 0.9310 | 0.9474 | 0.9647 | 29 | 0.34 |
| `financial_manipulation` | 0.9643 | 0.9095 | 0.9361 | 0.9631 | 475 | 0.76 |
| `authority_impersonation` | 0.9450 | 0.9329 | 0.9389 | 0.9732 | 313 | 0.60 |
| `fake_employment` | 0.6800 | 0.7083 | 0.6939 | 0.8710 | 24 | 0.44 |
| `account_suspension` | 0.9355 | 0.9720 | 0.9534 | 0.9683 | 107 | 0.86 |
| `prize_reward_scams` | 0.9435 | 0.9665 | 0.9549 | 0.9750 | 985 | 0.64 |
| `refund_payment_manipulation` | 0.9249 | 0.9512 | 0.9379 | 0.9479 | 246 | 0.68 |
| `fake_investment` | N/A | N/A | N/A | N/A | 0 | **BLOCKED** |

---

## 4. Audit Conclusions
- **Annotation Integrity:** **VERIFIED** (Genuine multi-head dataset annotations; zero synthetic keyword labeling).
- **Backend Integration:** **VERIFIED** (`ml_engine.predict_tactics` returns real calibrated predictions and explicitly flags `fake_investment` as unsupported).
- **Overall Status:** **VERIFIED** for 9 supported tactics; **BLOCKED** for `fake_investment` due to absent training labels.
