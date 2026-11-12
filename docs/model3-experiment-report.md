# TRUSTLENS AI — Model 3: Multi-Label Social Engineering & Scam Tactic Detection
## Experiment, Architecture & Explainability Report

- **Model Identifier:** `trustlens-model3-scam-tactic-v1`
- **Module Path:** `ml/tactic_detection/`
- **Artifacts Path:** `ml/artifacts/tactic_detection/`
- **Dataset Source:** ScamShield Multilingual Dataset (`train.jsonl`, `val.jsonl`, `test.jsonl`)
- **Evaluator Hardware:** Intel Core i5-12450H CPU (8 Cores / 12 Threads), 16 GB RAM, Windows 11
- **Status:** Verified, Evaluated on Holdout Test Set, and Integrated with FastAPI ML Service

---

## 1. Executive Summary & Objective

Model 3 identifies the specific psychological coercion tactics and social engineering vectors employed in deceptive digital messages. Attackers rarely rely on a single technique; real-world scam communications frequently combine urgency, entity impersonation, and threats of financial loss into multi-stage manipulation schemes.

Model 3 frames this as a **multi-label binary classification problem**, where a single message can exhibit zero, one, or multiple co-occurring tactics simultaneously.

---

## 2. Target Tactics & Ground-Truth Annotation Strategy

The platform targets 10 manipulation tactics. To uphold the core development rule (**never fabricate model results or training labels**), all target tactics were cross-examined against ground-truth annotations from the ScamShield benchmark (`head1_social_engineering`, `head2_scam_intent`, and `metadata` flags):

| Tactic Code | Target Tactic Display Name | Ground Truth Mapping Criteria | Train Support ($N=69,286$) | Status |
| :--- | :--- | :--- | :---: | :---: |
| `TACTIC_URGENCY` | **Urgency and time pressure** | `head1_social_engineering['urgency'] == 1` | 5,436 (7.85%) | **Trained** |
| `TACTIC_INTIMIDATION` | **Threats and intimidation** | `head1_social_engineering['fear'] == 1` OR `Electricity Disconnection` OR `Traffic e-Challan` | 2,910 (4.20%) | **Trained** |
| `TACTIC_CREDENTIAL_THEFT` | **OTP and credential requests** | `head2_scam_intent == 'OTP / Credential Theft'` OR `metadata['has_otp'] == True` | 829 (1.20%) | **Trained** |
| `TACTIC_FINANCIAL_PRESSURE` | **Financial manipulation** | `head1_social_engineering['financial_pressure'] == 1` OR `Loan Scam` | 4,078 (5.89%) | **Trained** |
| `TACTIC_AUTHORITY_IMPERSONATION` | **Bank or government impersonation** | `head1_social_engineering['authority_impersonation'] == 1` OR `Traffic e-Challan` OR `Fake KYC` | 3,259 (4.70%) | **Trained** |
| `TACTIC_FAKE_EMPLOYMENT` | **Fake employment opportunities** | `head2_scam_intent == 'Telegram Job'` | 311 (0.45%) | **Trained** |
| `TACTIC_FAKE_INVESTMENT` | **Fake investment opportunities** | *No verified ground-truth annotations exist in the benchmark dataset.* | 0 (0.00%) | **Unavailable** |
| `TACTIC_ACCOUNT_SUSPENSION` | **Account suspension threats** | `head2_scam_intent == 'Bank Account Freeze'` OR (`Fake KYC` AND `fear == 1`) | 1,190 (1.72%) | **Trained** |
| `TACTIC_REWARD_BAIT` | **Prize and reward scams** | `head1_social_engineering['reward_bait'] == 1` OR `Lottery / Prize` | 8,049 (11.62%) | **Trained** |
| `TACTIC_PAYMENT_MANIPULATION` | **Refund and payment manipulation** | `head2_scam_intent in ['UPI Fraud', 'Courier Scam']` | 2,210 (3.19%) | **Trained** |

### Policy on Missing / Unsupported Labels (`fake_investment`):
> [!IMPORTANT]
> In strict compliance with the project rule (*"If a tactic cannot be supported by training labels, mark it as unavailable rather than inventing a trained classifier"*), `fake_investment` is registered as **`UNAVAILABLE`**. 
> When user messages mention investment terms, the inference engine outputs an explicit system advisory explaining the absence of ground-truth labels rather than returning a fabricated classification score.

---

## 3. Multi-Label Co-occurrence & Partitioning

Analysis of the 69,286 training samples illustrates the multi-label nature of real-world scam operations:
- **0 Tactics Active:** 52,451 samples (75.70%) — Legitimate benign messages and neutral telemarketing.
- **1 Tactic Active:** 9,862 samples (14.23%) — Single-vector scams (e.g. isolated lottery bait).
- **2 Tactics Active:** 4,194 samples (6.05%) — Common pairs (e.g. `Urgency` + `Account Suspension`).
- **3 Tactics Active:** 1,260 samples (1.82%) — e.g. `Urgency` + `Authority Impersonation` + `Account Suspension`.
- **4 Tactics Active:** 1,355 samples (1.96%) — High-intensity coercion attacks.
- **5 Tactics Active:** 162 samples (0.23%) — Complex multi-stage smishing campaigns.

Data partitions utilized:
- **Train Split:** 69,286 samples
- **Validation Split:** 8,192 samples (used exclusively for decision threshold tuning)
- **Holdout Test Split:** 8,202 samples (quarantined benchmark)

---

## 4. Modeling Architecture & Candidate Comparison

### Feature Representation:
A multilingual `FeatureUnion` combining word and subword character n-grams:
1. **Word N-grams:** Range (1, 2), max 25,000 features, sublinear TF scaling, min_df=3.
2. **Character N-grams:** Range (3, 5), analyzer `char_wb`, max 35,000 features, sublinear TF scaling, min_df=5 (captures multilingual subwords in Hindi, Hinglish, Tamil, Bengali).
Total feature dimensionality: **60,000 features**.

### Threshold Tuning Strategy:
Because tactics have varying class support (from 0.45% for fake employment to 11.62% for prize scams), a uniform 0.50 threshold is suboptimal. On the validation split ($N=8,192$), each label threshold $\tau_j \in [0.10, 0.90]$ was optimized to maximize validation $F_1$.

### Benchmark Comparison on Holdout Test Set ($N=8,202$):

| Multi-Label Algorithm | Micro F1 | Macro F1 | Weighted F1 | Hamming Loss | Inference Latency | Train Duration |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Model A: One-vs-Rest Logistic Regression (Balanced)** | 0.9382 | 0.8949 | 0.9385 | 0.0050 | **0.0023 ms** | 21.41 s |
| **Model B: One-vs-Rest Calibrated LinearSVC (Platt Scaling)** | **0.9513** | **0.9313** | **0.9511** | **0.0039** | **0.0390 ms** | 105.14 s |

**Selected Production Model:** **Model B (One-vs-Rest Calibrated LinearSVC)** achieved superior Macro F1 (**0.9313**) and lowest Hamming Loss (**0.0039**, meaning fewer than 4 incorrect label decisions per 1,000 assignments).

---

## 5. Per-Label Evaluation Breakdown (Holdout Test Set $N=8,202$)

All metrics below are computed on the untouched holdout test partition:

| Tactic | Support | Precision | Recall | F1-Score | PR-AUC | Tuned $\tau^*$ |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Urgency and Time Pressure** | 530 | 0.9397 | 0.9698 | **0.9545** | 0.9721 | 0.30 |
| **Threats and Intimidation** | 245 | 0.9373 | 0.9755 | **0.9560** | 0.9633 | 0.20 |
| **OTP and Credential Requests** | 29 | 0.9643 | 0.9310 | **0.9474** | 0.9647 | 0.34 |
| **Financial Manipulation** | 475 | 0.9643 | 0.9095 | **0.9361** | 0.9631 | 0.50 |
| **Bank or Govt Impersonation** | 313 | 0.9547 | 0.9425 | **0.9486** | 0.9854 | 0.36 |
| **Fake Employment Opportunities** | 24 | 0.7917 | 0.7917 | **0.7917** | 0.8818 | 0.36 |
| **Account Suspension Threats** | 107 | 0.9358 | 0.9533 | **0.9444** | 0.9616 | 0.44 |
| **Prize and Reward Scams** | 985 | 0.9524 | 0.9756 | **0.9639** | 0.9778 | 0.34 |
| **Refund and Payment Manipulation**| 246 | 0.9390 | 0.9390 | **0.9390** | 0.9753 | 0.50 |
| **Fake Investment Opportunities** | 0 | N/A | N/A | N/A | N/A | N/A (Unavailable) |

---

## 6. Output Format & Explainability

For every incoming digital communication, the inference engine outputs:
1. `tactic_id`: Machine-readable unique identifier
2. `tactic_name`: Standardized SOC threat name
3. `tactic_code`: Unified taxonomy classification code
4. `threat_level`: Critical / High / Medium / Low severity tag
5. `confidence`: Calibrated posterior probability $P(y_j = 1 \mid x)$
6. `threshold_applied`: Validation-calibrated decision threshold
7. `explanation`: Domain-specific behavioral threat analysis
8. `evidence_tokens`: Concrete tokens and context spans extracted from the message

### Example Live Predictions:

```json
// Test Case 1: Complex Multi-Vector Smishing Message
"Dear SBI Customer, your bank account will be blocked today within 24 hours. Update KYC immediately."

{
  "tactic_count": 5,
  "primary_vector": "Urgency and Time Pressure",
  "tactics": [
    {
      "tactic_name": "Urgency and Time Pressure",
      "threat_level": "HIGH",
      "confidence": 1.0000,
      "evidence_tokens": ["immediate", "today", "24 hours"]
    },
    {
      "tactic_name": "Bank or Government Impersonation",
      "threat_level": "HIGH",
      "confidence": 1.0000,
      "evidence_tokens": ["sbi"]
    },
    {
      "tactic_name": "Threats and Intimidation",
      "threat_level": "CRITICAL",
      "confidence": 0.9999,
      "evidence_tokens": ["block"]
    },
    {
      "tactic_name": "Account Suspension Threats",
      "threat_level": "HIGH",
      "confidence": 0.9965,
      "evidence_tokens": ["blocked", "block", "kyc"]
    },
    {
      "tactic_name": "Financial Manipulation",
      "threat_level": "HIGH",
      "confidence": 0.7696,
      "evidence_tokens": ["rs"]
    }
  ]
}
```

---

## 7. Operational Integrity & Anti-Fabrication Principles

- **No Keyword-as-Proof Rule:** Keyword presence alone does **not** trigger a fraud detection. Classifications are produced solely by the calibrated multi-label vector model.
- **Unavailable Tactic Handling:** Messages with crypto/trading keywords receive a transparent notice that `fake_investment` is unclassified by ML due to dataset constraints, upholding platform trust.
- **Visual Artifacts Stored:**
  - Precision-Recall curves: `ml/artifacts/tactic_detection/pr_curves.png`
  - Co-occurrence correlation matrix: `ml/artifacts/tactic_detection/label_cooccurrence.png`
