# TRUSTLENS AI — Documented Fraud Tactic Taxonomy (`v2.3`)

Model 3 (`trustlens-tactics-v2.3-candidate`, `One-vs-Rest Calibrated LinearSVC`) maps verified ScamShield multi-head annotations (`head1_social_engineering`, `head2_scam_intent`, `metadata`) to **9 trainable social-engineering and fraud tactics**, while explicitly keeping `fake_investment` **Blocked** due to 0 verified ground-truth labels.

| Tactic ID | Display Name | Code | High-Level Fraud Category | Training Source (Verified Labels Only) | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `urgency_time_pressure` | Urgency and Time Pressure | `TACTIC_URGENCY` | Social Engineering | `head1.urgency == 1` | **Supported (v2.3)** |
| `threats_intimidation` | Threats and Intimidation | `TACTIC_INTIMIDATION` | Social Engineering | `head1.fear == 1` OR `head2 in ['Electricity Disconnection', 'Traffic e-Challan']` | **Supported (v2.3)** |
| `otp_credential_requests` | OTP or Credential Requests | `TACTIC_CREDENTIAL_THEFT` | Identity Theft / Phishing | `head2 == 'OTP / Credential Theft'` OR `metadata.has_otp == True` | **Supported (v2.3)** |
| `bank_impersonation` | Bank Impersonation | `TACTIC_BANK_IMPERSONATION` | Impersonation | `head1.authority_impersonation == 1` AND `head2 in ['Fake KYC', 'Bank Account Freeze', 'Loan Scam']` | **Supported (v2.3)** |
| `government_impersonation` | Government Impersonation | `TACTIC_GOV_IMPERSONATION` | Impersonation | `head2 in ['Traffic e-Challan', 'Electricity Disconnection']` | **Supported (v2.3)** |
| `fake_employment` | Fake Employment | `TACTIC_FAKE_EMPLOYMENT` | Employment Scams | `head2 == 'Telegram Job'` | **Supported (v2.3)** |
| `prize_reward_manipulation` | Prize and Reward Manipulation | `TACTIC_REWARD_BAIT` | Financial Fraud / Social Engineering | `head1.reward_bait == 1` OR `head2 == 'Lottery / Prize'` | **Supported (v2.3)** |
| `account_suspension_threats` | Account Suspension Threats | `TACTIC_ACCOUNT_SUSPENSION` | Phishing / Social Engineering | `head2 == 'Bank Account Freeze'` OR (`head2 == 'Fake KYC'` AND `head1.fear == 1`) | **Supported (v2.3)** |
| `refund_payment_manipulation` | Refund and Payment Manipulation | `TACTIC_PAYMENT_MANIPULATION` | Financial Fraud | `head2 in ['UPI Fraud', 'Courier Scam']` | **Supported (v2.3)** |
| `fake_investment` | Fake Investment | `TACTIC_FAKE_INVESTMENT` | Investment Scams | **0 verified ground-truth labels** (advisory notice only; no fabricated training examples) | **Blocked** |
