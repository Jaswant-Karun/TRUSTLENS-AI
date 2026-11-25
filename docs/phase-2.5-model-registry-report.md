# TRUSTLENS AI — PHASE 2.5: MODEL EVALUATION, EXPERIMENT TRACKING & MODEL REGISTRY REPORT

> **Registry File:** [`ml/registry/models_registry_v2.json`](file:///c:/Users/jaswant%20karun/TRUSTLENS%20AI/ml/registry/models_registry_v2.json)  
> **Experiment Tracker:** [`ml/evaluation/experiments_v2.json`](file:///c:/Users/jaswant%20karun/TRUSTLENS%20AI/ml/evaluation/experiments_v2.json)  
> **Validation Suite:** [`ml/evaluation/validate_registry.py`](file:///c:/Users/jaswant%20karun/TRUSTLENS%20AI/ml/evaluation/validate_registry.py)  
> **Date:** November 25, 2026

---

## 1. Registered Models Inventory (`7` Entries)

| Model ID | Version | Task | Dataset Version | Status | SHA-256 Verified |
|---|---|---|---|---|---|
| `trustlens-text-v1.0-prod` | `1.0.0` | Text Classification | `1.0.0` | **Production** | ✅ |
| `trustlens-text-v2.1-candidate` | `2.1.0-candidate` | Text Classification | `2.0.5` | **Evaluated** | ✅ |
| `trustlens-url-v1.0-prod` | `1.0.0` | URL Phishing | `1.0.0` | **Production** | ✅ |
| `trustlens-url-v2.2-candidate` | `2.2.0-candidate` | URL Phishing | `2.0.5` | **Evaluated** | ✅ |
| `trustlens-tactics-v2.3-candidate` | `2.3.0-candidate` | Multi-Label Tactics | `2.0.5` | **Evaluated** | ✅ |
| `trustlens-tactic-fake-investment` | `0.0.0-blocked` | Multi-Label Tactics | `2.0.5` | **Blocked** | N/A |
| `trustlens-campaign-v2.4-candidate` | `2.4.0-candidate` | Campaign Clustering | `2.0.5` | **Evaluated** | ✅ |

---

## 2. Governance & Promotion Policy

Implemented in `ml/registry/registry_manager.py`:
- **6 Lifecycle States:** `Development`, `Evaluated`, `Approved`, `Production`, `Deprecated`, `Blocked`.
- **Human Approval Gate:** Calling `promote_model(..., target_status="Production")` without a non-empty `human_approved_by` raises `PermissionError`.
- **Blocked Guard:** `Blocked` models (such as `trustlens-tactic-fake-investment`) cannot be promoted under any circumstance until unblocked with verified data.
- **No Auto-Promotion:** Existing `v1.0.0` production artifacts remain active until explicit human sign-off.

---

## 3. Automated Validation Results (`validate_registry.py`)

- ✅ All 7 registered models contain all 14 required metadata fields (`model_id`, `version`, `task`, `artifact_path`, `artifact_checksum`, `dataset_version`, `training_date`, `evaluation_date`, `training_configuration`, `metrics`, `supported_languages`, `limitations`, `deployment_status`).
- ✅ All 6 active artifact files passed live SHA-256 integrity checks on disk.
- ✅ All 11 tracked experiments in `experiments_v2.json` are strictly isolated to `dataset_version="2.0.5"` (`random_seed=42`).
- ✅ Promotion policy tests passed (blocked unapproved `Production` promotion and `Blocked` model promotion).
