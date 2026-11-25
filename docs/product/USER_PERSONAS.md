# TRUSTLENS AI — USER PERSONAS & PERMISSION MATRIX

> **Grounded in:** `backend/app/security/dependencies.py` (`user`, `analyst`, `admin`) and `backend/app/api/routes/*`.

---

## 1. Product Personas

### A. Individual User (`role: "user"`)
- **Goals:** Check suspicious messages, links, or screenshots before clicking or paying; understand warning signs; save personal scan history; report scams.
- **Capabilities:** Submit `/analyze/*` scans; view own `/analyses` history; submit `/reports`; view public Threat Library & Investigations.
- **Restrictions:** Cannot review/verify community reports (`403`); cannot view other users' private analyses (`403`/`404`); cannot trigger ML training or promote models (`403`).

### B. Security Analyst (`role: "analyst"`)
- **Goals:** Triage multi-vector threats, inspect 1-hop indicator relationships, build investigation cases, and export STIX 2.1 / JSON intelligence.
- **Capabilities:** All Individual User capabilities + view all `/analyses` + execute 1-hop graph expansion + generate/export reports + trigger/inspect `/automation/*` and `/training/jobs` (submit/compare).
- **Restrictions:** Cannot promote candidate ML models to production (`require_admin` -> `403`).

### C. Reviewer / Moderator (`role: "analyst"` or `"admin"` via `require_analyst_or_admin`)
- **Note on Existing Architecture:** Currently implemented as a capability of `analyst` and `admin` roles on `POST /api/v1/reports/{id}/review`. A separate `moderator` role is not yet defined in `dependencies.py`; if needed later, it maps cleanly to report-review-only scope.
- **Capabilities:** Examine submitted community reports, assign social-engineering tactics, record verdict (`verified_scam | under_review | benign`) and notes, and trigger indicator extraction.

### D. Organization Administrator (`role: "admin"`)
- **Goals:** Govern ML model promotion, oversee audit logs, and manage system configuration.
- **Capabilities:** All Analyst capabilities + `POST /api/v1/training/jobs/{id}/promote` (`require_admin` + `approval_token`) + full access to audit/automation pipelines.
- **Gap Identified:** User/role management CRUD endpoints (`/users`, `/organizations`) do not yet exist in `backend/app/api/routes/auth.py` and are documented as a Phase 2+ requirement if multi-tenant orgs are enabled.

---

## 2. Role Permission Matrix

| Capability | Anonymous | `user` | `analyst` | `admin` |
| :--- | :---: | :---: | :---: | :---: |
| Submit `/analyze/text`, `/url`, `/image`, `/comprehensive` | Yes | Yes | Yes | Yes |
| Submit community report (`POST /reports`) | Yes | Yes | Yes | Yes |
| View own analysis history (`GET /analyses`) | No (`401`) | Own only | All | All |
| Export private analysis (`GET /exports/*?target_type=analysis`) | No (`401`) | Own only | All | All |
| Review community reports (`POST /reports/{id}/review`) | No (`401`) | No (`403`) | Yes | Yes |
| Submit/compare training jobs & run automation endpoints | No (`401`) | No (`403`) | Yes | Yes |
| Promote candidate model (`POST /training/jobs/{id}/promote`) | No (`401`) | No (`403`) | No (`403`) | Yes |
