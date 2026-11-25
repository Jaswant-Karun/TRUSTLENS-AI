"""
TRUSTLENS AI - Phase 2.5: Versioned Model Registry & Promotion Policy Manager
Manages all Production, Evaluated, Development, and Blocked models with SHA-256 verification
and strict human-approval gating for Production promotion.
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

VALID_STATUSES = {"Development", "Evaluated", "Approved", "Production", "Deprecated", "Blocked"}

REQUIRED_FIELDS = [
    "model_id",
    "model_name",
    "version",
    "task",
    "artifact_path",
    "artifact_checksum",
    "dataset_version",
    "training_date",
    "evaluation_date",
    "training_configuration",
    "metrics",
    "supported_languages",
    "limitations",
    "deployment_status",
]


def compute_sha256(filepath: Path) -> str:
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


class ModelRegistryManager:
    def __init__(self, registry_path: str = "ml/registry/models_registry_v2.json"):
        self.registry_path = Path(registry_path)
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        self.data: Dict[str, Any] = {"registry_version": "2.5.0", "models": {}}
        if self.registry_path.exists():
            with open(self.registry_path, "r", encoding="utf-8") as f:
                self.data = json.load(f)

    def register_model(self, entry: Dict[str, Any]) -> None:
        status = entry.get("deployment_status")
        if status not in VALID_STATUSES:
            raise ValueError(f"Invalid deployment_status '{status}'. Must be one of {VALID_STATUSES}")
        for field in REQUIRED_FIELDS:
            if field not in entry or entry[field] is None:
                raise ValueError(f"Missing required registry field '{field}' for {entry.get('model_id')}")
        self.data["models"][entry["model_id"]] = entry

    def promote_model(self, model_id: str, target_status: str, human_approved_by: Optional[str] = None) -> Dict[str, Any]:
        """
        Enforces strict Promotion Policy:
        - Production requires explicit human_approved_by and prior Evaluated/Approved status.
        - Blocked models cannot be promoted.
        """
        if target_status not in VALID_STATUSES:
            raise ValueError(f"Invalid target_status '{target_status}'")
        if model_id not in self.data["models"]:
            raise KeyError(f"Model '{model_id}' not found in registry")

        model = self.data["models"][model_id]
        current = model["deployment_status"]

        if current == "Blocked":
            raise PermissionError(f"Model '{model_id}' is Blocked and cannot be promoted.")

        if target_status == "Production":
            if not human_approved_by or not human_approved_by.strip():
                raise PermissionError("Production promotion denied: explicit human_approved_by is required.")
            if current not in ("Evaluated", "Approved"):
                raise PermissionError(f"Production promotion denied: model status must be Evaluated or Approved (current: {current}).")
            model["approved_by"] = human_approved_by
            model["approved_at_utc"] = datetime.now(timezone.utc).isoformat()

        model["deployment_status"] = target_status
        self.save()
        return model

    def save(self) -> None:
        self.data["last_updated_utc"] = datetime.now(timezone.utc).isoformat()
        with open(self.registry_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2)


def build_registry_from_artifacts() -> ModelRegistryManager:
    mgr = ModelRegistryManager()
    mgr.data = {"registry_version": "2.5.0", "models": {}}

    # 1. Text Detection (v2.1 Candidate - Evaluated)
    t_meta = json.loads(Path("ml/artifacts/text_detection/v2.1_candidate/training_metadata.json").read_text(encoding="utf-8"))
    t_eval = json.loads(Path("ml/artifacts/text_detection/v2.1_candidate/evaluation_report.json").read_text(encoding="utf-8"))
    t_best = t_eval["selected_model_summary"]
    t_art = Path("ml/artifacts/text_detection/v2.1_candidate/union_tfidf_linearsvc_model.joblib")
    mgr.register_model({
        "model_id": "trustlens-text-v2.1-candidate",
        "model_name": t_best["display_name"],
        "version": "2.1.0-candidate",
        "task": "text_classification",
        "artifact_path": str(t_art).replace("\\", "/"),
        "artifact_checksum": t_meta["artifact_sha256"][t_art.name],
        "dataset_version": t_meta["dataset_version"],
        "training_date": t_meta["trained_at_utc"],
        "evaluation_date": t_meta["trained_at_utc"],
        "training_configuration": {"random_seed": t_meta["random_seed"], "classes": t_meta["labels"]},
        "metrics": {
            "accuracy": t_best["accuracy"],
            "macro_f1": t_best["macro_f1"],
            "weighted_f1": t_best["weighted_f1"],
            "roc_auc_ovr_macro": t_best["roc_auc_ovr_macro"],
            "threat_fpr": t_best["threat_false_positive_rate"],
            "threat_fnr": t_best["threat_false_negative_rate"],
            "latency_ms": t_best["inference_latency_ms_per_sample"],
        },
        "supported_languages": ["English", "Hindi", "Hinglish"],
        "limitations": "Linear TF-IDF baseline; Tamil and Bengali unsupported (0 samples).",
        "deployment_status": "Evaluated",
    })

    # 2. Text Detection Production (v1.0.0 - Production)
    p1 = Path("ml/artifacts/text_detection/best_model.joblib")
    mgr.register_model({
        "model_id": "trustlens-text-v1.0-prod",
        "model_name": "FeatureUnion + Calibrated LinearSVC (v1.0)",
        "version": "1.0.0",
        "task": "text_classification",
        "artifact_path": str(p1).replace("\\", "/"),
        "artifact_checksum": compute_sha256(p1),
        "dataset_version": "1.0.0",
        "training_date": "2026-11-12T23:42:53Z",
        "evaluation_date": "2026-11-12T23:42:53Z",
        "training_configuration": {"binary_classification": True},
        "metrics": {"accuracy": 0.9777, "macro_f1": 0.976, "roc_auc": 0.996},
        "supported_languages": ["English", "Hindi", "Hinglish"],
        "limitations": "Trained on v1.0.0 splits; Hindi threat recall 54.55%.",
        "deployment_status": "Production",
    })

    # 3. URL Detection (v2.2 Candidate - Evaluated)
    u_meta = json.loads(Path("ml/artifacts/url_detection/v2.2_candidate/training_metadata.json").read_text(encoding="utf-8"))
    u_eval = json.loads(Path("ml/artifacts/url_detection/v2.2_candidate/evaluation_report.json").read_text(encoding="utf-8"))
    u_best = u_eval["selected_model_summary"]
    u_art = Path("ml/artifacts/url_detection/v2.2_candidate/xgboost_model.joblib")
    mgr.register_model({
        "model_id": "trustlens-url-v2.2-candidate",
        "model_name": u_best["display_name"],
        "version": "2.2.0-candidate",
        "task": "url_phishing_classification",
        "artifact_path": str(u_art).replace("\\", "/"),
        "artifact_checksum": u_meta["artifact_sha256"][u_art.name],
        "dataset_version": u_meta["dataset_version"],
        "training_date": u_meta["trained_at_utc"],
        "evaluation_date": u_meta["trained_at_utc"],
        "training_configuration": {"random_seed": u_meta["random_seed"], "feature_count": u_meta["feature_count"]},
        "metrics": {
            "accuracy": u_best["accuracy"],
            "macro_f1": u_best["macro_f1"],
            "roc_auc": u_best["roc_auc"],
            "pr_auc": u_best["pr_auc"],
            "fpr": u_best["false_positive_rate"],
            "fnr": u_best["false_negative_rate"],
            "latency_ms": u_best["inference_latency_ms_per_sample"],
        },
        "supported_languages": ["URL-Agnostic (Lexical/Structural)"],
        "limitations": "Zero-hop lexical features alone do not prove malice or safety.",
        "deployment_status": "Evaluated",
    })

    # 4. URL Detection Production (v1.0.0 - Production)
    p2 = Path("ml/artifacts/url_detection/best_url_model.joblib")
    mgr.register_model({
        "model_id": "trustlens-url-v1.0-prod",
        "model_name": "XGBoost Classifier (v1.0)",
        "version": "1.0.0",
        "task": "url_phishing_classification",
        "artifact_path": str(p2).replace("\\", "/"),
        "artifact_checksum": compute_sha256(p2),
        "dataset_version": "1.0.0",
        "training_date": "2026-11-12T23:42:53Z",
        "evaluation_date": "2026-11-12T23:42:53Z",
        "training_configuration": {"feature_count": 16},
        "metrics": {"accuracy": 0.9998, "macro_f1": 0.9998, "roc_auc": 1.0},
        "supported_languages": ["URL-Agnostic"],
        "limitations": "Trained on v1.0.0 ungrouped URL splits.",
        "deployment_status": "Production",
    })

    # 5. Tactic Detection (v2.3 Candidate - Evaluated)
    tac_meta = json.loads(Path("ml/artifacts/tactic_detection/v2.3_candidate/training_metadata.json").read_text(encoding="utf-8"))
    tac_eval = json.loads(Path("ml/artifacts/tactic_detection/v2.3_candidate/evaluation_report.json").read_text(encoding="utf-8"))
    tac_best = tac_eval["selected_model_summary"]
    tac_art = Path("ml/artifacts/tactic_detection/v2.3_candidate/ovr_linearsvc.joblib")
    mgr.register_model({
        "model_id": "trustlens-tactics-v2.3-candidate",
        "model_name": tac_best["display_name"],
        "version": "2.3.0-candidate",
        "task": "multilabel_tactic_detection",
        "artifact_path": str(tac_art).replace("\\", "/"),
        "artifact_checksum": tac_meta["artifact_sha256"][tac_art.name],
        "dataset_version": tac_meta["dataset_version"],
        "training_date": tac_meta["trained_at_utc"],
        "evaluation_date": tac_meta["trained_at_utc"],
        "training_configuration": {"random_seed": tac_meta["random_seed"], "supported_labels": 9},
        "metrics": {
            "micro_f1": tac_best["micro_f1"],
            "macro_f1": tac_best["macro_f1"],
            "hamming_loss": tac_best["hamming_loss"],
            "latency_ms": tac_best["inference_latency_ms_per_sample"],
        },
        "supported_languages": ["English", "Hindi", "Hinglish"],
        "limitations": "9 of 10 tactics supported. 'fake_investment' is Blocked due to missing ground-truth labels.",
        "deployment_status": "Evaluated",
    })

    # 5b. Tactic Detection Production (v1.0.0 - Production)
    p3 = Path("ml/artifacts/tactic_detection/best_tactic_model.joblib")
    mgr.register_model({
        "model_id": "trustlens-tactics-v1.0-prod",
        "model_name": "One-vs-Rest Calibrated LinearSVC (v1.0)",
        "version": "1.0.0",
        "task": "multilabel_tactic_detection",
        "artifact_path": str(p3).replace("\\", "/"),
        "artifact_checksum": compute_sha256(p3),
        "dataset_version": "1.0.0",
        "training_date": "2026-11-12T17:43:46Z",
        "evaluation_date": "2026-11-12T17:43:46Z",
        "training_configuration": {"supported_labels": 9},
        "metrics": {"micro_f1": 0.9513, "macro_f1": 0.9313, "hamming_loss": 0.0039},
        "supported_languages": ["English", "Hindi", "Hinglish"],
        "limitations": "9 of 10 tactics supported; fake_investment unavailable.",
        "deployment_status": "Production",
    })

    # 6. Blocked Model Entry: Fake Investment Tactic
    mgr.register_model({
        "model_id": "trustlens-tactic-fake-investment",
        "model_name": "Fake Investment Tactic Classifier",
        "version": "0.0.0-blocked",
        "task": "multilabel_tactic_detection",
        "artifact_path": "NONE",
        "artifact_checksum": "NONE",
        "dataset_version": "2.0.5",
        "training_date": "NOT_TRAINED",
        "evaluation_date": "NOT_EVALUATED",
        "training_configuration": {"status": "blocked_pending_human_annotation"},
        "metrics": {},
        "supported_languages": [],
        "limitations": "Blocked: 0 verified training annotations exist.",
        "deployment_status": "Blocked",
    })

    # 7. Campaign Clustering (v2.4 Candidate - Evaluated)
    c_eval = json.loads(Path("ml/artifacts/campaign_detection/v2.4_candidate/evaluation_report.json").read_text(encoding="utf-8"))
    c_art = Path("ml/artifacts/campaign_detection/v2.4_candidate/cluster_artifacts.joblib")
    c_p = c_eval["primary_run_min_cluster_size_25"]
    mgr.register_model({
        "model_id": "trustlens-campaign-v2.4-candidate",
        "model_name": "Multilingual MiniLM-L12-v2 + HDBSCAN",
        "version": "2.4.0-candidate",
        "task": "unsupervised_campaign_clustering",
        "artifact_path": str(c_art).replace("\\", "/"),
        "artifact_checksum": compute_sha256(c_art),
        "dataset_version": "2.0.5",
        "training_date": "2026-11-25T05:45:00Z",
        "evaluation_date": "2026-11-25T05:47:00Z",
        "training_configuration": {"min_cluster_size": 25, "min_samples": 5, "embedding_dim": 384},
        "metrics": {
            "clusters_discovered": c_p["clusters_discovered"],
            "noise_ratio": c_p["noise_ratio"],
            "silhouette_score": c_p["silhouette_score_non_noise"],
            "davies_bouldin": c_p["davies_bouldin_index"],
        },
        "supported_languages": ["English", "Hindi", "Hinglish"],
        "limitations": "Unsupervised semantic similarity only; does not confirm shared criminal origin.",
        "deployment_status": "Evaluated",
    })

    # 7b. Campaign Clustering Production (v1.0.0 - Production)
    p4 = Path("ml/artifacts/campaign_detection/cluster_artifacts.joblib")
    mgr.register_model({
        "model_id": "trustlens-campaign-v1.0-prod",
        "model_name": "MiniLM-L6-v2 + HDBSCAN (v1.0)",
        "version": "1.0.0",
        "task": "unsupervised_campaign_clustering",
        "artifact_path": str(p4).replace("\\", "/"),
        "artifact_checksum": compute_sha256(p4),
        "dataset_version": "1.0.0",
        "training_date": "2026-11-12T18:00:00Z",
        "evaluation_date": "2026-11-12T18:00:00Z",
        "training_configuration": {"min_cluster_size": 25, "min_samples": 5},
        "metrics": {"clusters_discovered": 47, "silhouette_score": 0.3209},
        "supported_languages": ["English"],
        "limitations": "English-centric embeddings; similarity does not prove shared criminal source.",
        "deployment_status": "Production",
    })

    mgr.save()
    print(f"Registered {len(mgr.data['models'])} models in {mgr.registry_path}")
    return mgr


if __name__ == "__main__":
    build_registry_from_artifacts()
