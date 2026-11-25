# TRUSTLENS AI — Privacy-First Data Protection Architecture

> **Compliance Disclaimer:** Technical privacy controls are implemented in code, but formal regulatory compliance under India's Digital Personal Data Protection (DPDP) Act, 2023, the EU GDPR, or any other jurisdiction **cannot be claimed without independent legal and Data Protection Officer (DPO) verification**.

---

## 1. Data Collection Purposes & Minimization
1. **Fraud & Phishing Analysis (`fraud_detection_inference`):** Evaluates user-submitted text, URLs, or OCR-extracted screenshot text. Personal identifiers are masked before persistence.
2. **Investigation Case Management (`investigation_case_management`):** Organizes analyses, IOCs, and analyst notes. Private cases are strictly owner-isolated.
3. **Community Threat Reporting (`community_threat_reporting`):** Collects user-submitted fraud reports for human moderation; reporter identity is redacted in listings.
4. **Authentication & Session Security (`account_authentication`):** Stores `email`, `bcrypt` password hash, `role`, and `session_revoked_before`.
5. **Security & Privacy Auditing (`security_audit_logging`):** Logs authentication, consent updates, exports, and deletion events without storing plaintext secrets.

## 2. Consent Mechanisms
- Managed via `GET/PUT /api/v1/privacy/consent` (`backend/app/services/privacy_service.py`).
- Granular, revocable opt-in flags (`external_ioc_enrichment: false`, `community_report_public_listing: false`, `product_telemetry: false`, `security_notifications: true`).
- External IOC enrichment (`POST /api/v1/threat-intel/enrich`) strictly enforces `external_consent=True` and blocks PII/private IPs even when consented.

## 3. Data Retention Periods
- `analyses`: **90 days** (unless deleted earlier by the owner).
- `ioc_enrichment_cache`: **3600 seconds (<= 1 day)** TTL.
- `scam_reports` (pending/rejected): **90 days**.
- `audit_logs`: **365 days**.
- `user_accounts`: Active lifetime; erased upon account deletion.
- Dry-run enforcement preview via `POST /api/v1/privacy/retention/preview`.

## 4. Account & Analysis Deletion
- **Account Deletion:** `DELETE /api/v1/auth/account` (password-verified self-service erasure).
- **Analysis Deletion:** `DELETE /api/v1/analyses/{analysis_id}` (owner/admin-authorized deletion).

## 5. Data Export
- **Personal Data Portability:** `GET /api/v1/auth/export-data` exports the authenticated user's profile, analyses, and investigations.
- **PII-Scrubbed Threat Sharing:** `GET /api/v1/exports/stix` and `GET /api/v1/exports/misp` scrub phones, emails, and private IPs before export.

## 6. Sensitive Information Redaction & Encryption
- **Redaction:** `ml/preprocessing/text_preprocessor.py` and `CommunityScamReportService.redact_sensitive_text()` mask phones, emails, OTPs, UPIs, PAN, Aadhaar, and card numbers.
- **Encryption:** TLS/HSTS in transit; `bcrypt` password hashing; `Fernet` (AES-128-CBC + HMAC-SHA256) field-level encryption helper in `PrivacyProtectionService`.

## 7. Access Logs & Privacy Policy Requirements
- **Access Logs:** `GET /api/v1/privacy/access-logs` exposes user-scoped audit events from `audit_logs`.
- **Policy Endpoint:** `GET /api/v1/privacy/policy` serves machine-readable purposes, retention periods, user-rights endpoints, and jurisdictional notices.

## 8. Jurisdictional Evaluation (India DPDP Act 2023 & EU GDPR)
- **India DPDP Act, 2023:** Applies when processing digital personal data of Data Principals in India. Technical alignment includes itemized purpose notices (`/privacy/policy`), granular opt-in consent (`/privacy/consent`), data erasure (`/auth/account`, `/analyses/{id}`), and PII minimization.
- **EU GDPR:** Applies if offering services to or monitoring individuals in the EEA/UK. Technical alignment includes data portability (`/auth/export-data`), right to erasure, consent withdrawal, and retention limits.
- **Remaining Legal Steps:** Formal DPIA/DPO sign-off, Data Processing Agreements (DPAs) with cloud/MongoDB Atlas subprocessors, and published legal privacy notice.
