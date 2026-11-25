# TRUSTLENS AI — PHASE 2.3: SOCIAL-ENGINEERING TACTIC MULTI-LABEL DETECTION REPORT

> **Dataset Version:** `2.0.5` (ScamShield annotated subset: `68,552` train / `8,565` val / `8,563` test; Mendeley SMS unannotated rows excluded)  
> **Candidate Artifacts Directory:** `ml/artifacts/tactic_detection/v2.3_candidate/` *(Production artifacts preserved untouched)*  
> **Scripts Created:** `ml/tactic_detection/labels.py`, `train.py`, `evaluate.py`, `predict.py`  
> **Date:** November 25, 2026

---

## 1. Label Audit & Integrity Policy

All 10 target labels were audited against genuine multi-head ScamShield annotations (`head1_social_engineering`, `head2_scam_intent`, `metadata.has_otp`) **without manufacturing labels via keyword rules**:

- **9 Supported Labels (Trained & Evaluated):**
  1. `urgency_time_pressure` (`head1.urgency == 1`)
  2. `threats_intimidation` (`head1.fear == 1` or `head2` in `['Electricity Disconnection', 'Traffic e-Challan']`)
  3. `otp_credential_requests` (`head2 == 'OTP / Credential Theft'` or `metadata.has_otp == True`)
  4. `bank_impersonation` (`head1.authority_impersonation == 1` and `head2` in `['Fake KYC', 'Bank Account Freeze', 'Loan Scam']`)
  5. `government_impersonation` (`head2` in `['Traffic e-Challan', 'Electricity Disconnection']`)
  6. `fake_employment` (`head2 == 'Telegram Job'`)
  7. `prize_reward_manipulation` (`head1.reward_bait == 1` or `head2 == 'Lottery / Prize'`)
  8. `account_suspension_threats` (`head2 == 'Bank Account Freeze'` or `('Fake KYC' and fear == 1)`)
  9. `refund_payment_manipulation` (`head2` in `['UPI Fraud', 'Courier Scam']`)
- **1 Unavailable / Blocked Label:**
  - `fake_investment` (`TACTIC_FAKE_INVESTMENT`): **BLOCKED** — Zero verified ground-truth training annotations exist.

---

## 2. Human Annotation Workflow Specification (For `fake_investment`)

To unblock `fake_investment` in future phases without synthetic keyword labeling:
- **Label Definition:** Messages promising unrealistic, guaranteed, or risk-free returns on cryptocurrency, stock tips, forex, or Ponzi/task-deposit schemes.
- **Positive Example:** *"Join our VIP crypto trading group! Deposit ₹5,000 today and earn guaranteed 40% weekly profit."*
- **Negative Example:** *"Your mutual fund SIP of ₹5,000 has been processed by HDFC AMC."*
- **Workflow Controls:**
  - Multi-label JSON schema supporting concurrent tactic tags (`urgency_time_pressure`, `fake_investment`, `refund_payment_manipulation`).
  - Dual-annotator independent labeling with `annotator_id`, `decision` (`positive | negative | uncertain`), and `rationale_span`.
  - Mandatory reviewer adjudication (`reviewer_id`, `adjudicated_label`) for all `uncertain` or disagreed items, preserving full provenance (`source_dataset`, `annotated_at_utc`).

---

## 3. Held-Out Test Set Evaluation (`n = 8,563` Annotated Samples)

| Model | Micro F1 | Macro F1 | Hamming Loss | Latency (ms/msg) | Size (MB) |
|---|---|---|---|---|---|
| One-vs-Rest Logistic Regression (Balanced) | 0.9403 | 0.9386 | 0.0041 | 0.0075 ms | 5.499 MB |
| **One-vs-Rest Calibrated LinearSVC (Balanced)** | **0.9566** | **0.9521** | **0.0030** | 0.0162 ms | 16.498 MB |

### Per-Label Performance (`ovr_linearsvc`)
| Tactic Label | Precision | Recall | F1 Score | PR-AUC | Support | Tuned Threshold |
|---|---|---|---|---|---|---|
| `urgency_time_pressure` | 0.9369 | 0.9659 | **0.9512** | 0.9634 | 646 | 0.40 |
| `threats_intimidation` | 0.9459 | 0.9663 | **0.9560** | 0.9892 | 326 | 0.20 |
| `otp_credential_requests` | 1.0000 | 0.9886 | **0.9943** | 1.0000 | 88 | 0.65 |
| `bank_impersonation` | 0.9000 | 0.9706 | **0.9340** | 0.9639 | 102 | 0.25 |
| `government_impersonation` | 0.9545 | 0.9767 | **0.9655** | 0.9968 | 43 | 0.15 |
| `fake_employment` | 0.8800 | 0.8980 | **0.8889** | 0.9514 | 49 | 0.40 |
| `prize_reward_manipulation` | 0.9594 | 0.9653 | **0.9623** | 0.9703 | 979 | 0.40 |
| `account_suspension_threats` | 0.9699 | 0.9556 | **0.9627** | 0.9877 | 135 | 0.50 |
| `refund_payment_manipulation` | 0.9326 | 0.9765 | **0.9540** | 0.9764 | 255 | 0.20 |
| `fake_investment` | — | — | — | — | 0 | **BLOCKED** |

![Multi-Label Precision-Recall Curves](file:///c:/Users/jaswant%20karun/TRUSTLENS%20AI/docs/screenshots/tactic_pr_curves_v2.3.png)

---

## 4. Error Analysis: Real False Positive & False Negative Examples

- **False Positives (Sampled from Test Set):**
  - `bank_impersonation` (`p=0.3099`): *"Delhi Police se bol raha hoon. Aapke naam par registered account illegal activities mein use hua hai."* (Police impersonation misattributed to bank due to "account").
  - `threats_intimidation` (`p=0.3309`): *"Dear User Your P.YATM K Y C have be expire today please call customer care no.[PHONE] immediately your P.YATM account suspen 24hrs"*
- **False Negatives (Sampled from Test Set):**
  - `urgency_time_pressure` (`p=0.3831`, threshold `0.40`): *"Please confirm your details for shipment today, otherwise your parcel will be returned to the retailer:"*

---

## 5. Saved Artifacts & SHA-256 Checksums (`ml/artifacts/tactic_detection/v2.3_candidate/`)

| Artifact | Size (MB) | SHA-256 |
|---|---|---|
| `ovr_linearsvc.joblib` | 16.498 MB | `0216bc8c71504e6afe6eeefabeebc83881bc278969c3264f76ffd231f56ddcd4` |
| `ovr_logreg.joblib` | 5.499 MB | `9fdbd9a5054e280c521916662ccea38c26ada3eea2668b7edebb6c303c89529a` |
| `vectorizer.joblib` | 2.17 MB | `248f3382467ea3adf2bd23b431c1be166663c36a72ff7c4f0f909eb7b3a01a2d` |

> **Stop Condition Honored:** `fake_investment` remains explicitly blocked/unavailable pending human annotation. Production artifacts and backend routes were not modified.
