"""
Automated tests for Reproducible ML Training & Evaluation Pipeline:
- Dataset versioning, SHA-256 verification, and 0-overlap leakage gate
- Candidate registration never auto-promotes to Production
- Human-approved promotion & SHA-256 verification gate
- Rollback capability with promotion_history audit trail
"""

import json
from pathlib import Path
import pytest

from ml.pipeline import ReproducibleMLPipeline
from ml.registry.registry_manager import ModelRegistryManager, compute_sha256


def test_dataset_version_and_leakage_gate_passes():
    pipeline = ReproducibleMLPipeline()
    rep = pipeline.verify_dataset_version_and_leakage()
    assert rep["dataset_version"] == "2.0.5"
    assert rep["checksums_verified"] >= 10
    assert rep["leakage_checks"]["text"] == {"train_val_overlap": 0, "train_test_overlap": 0, "val_test_overlap": 0}
    assert rep["leakage_checks"]["urls"] == {"train_val_overlap": 0, "train_test_overlap": 0, "val_test_overlap": 0}


def test_candidate_registration_approval_and_rollback(tmp_path):
    # Create dummy artifacts in tmp_path
    art_v1 = tmp_path / "model_v1.joblib"
    art_v2 = tmp_path / "model_v2.joblib"
    art_v1.write_bytes(b"v1-artifact-bytes")
    art_v2.write_bytes(b"v2-artifact-bytes")

    reg_path = tmp_path / "registry.json"
    pipeline = ReproducibleMLPipeline(registry_path=str(reg_path), runs_dir=str(tmp_path / "runs"))

    # 1. Direct registration as Production is forbidden
    v1_entry = {
        "model_id": "test-text-v1",
        "model_name": "Text v1",
        "version": "1.0.0",
        "task": "text_classification",
        "artifact_path": str(art_v1),
        "artifact_checksum": compute_sha256(art_v1),
        "dataset_version": "2.0.5",
        "training_date": "2026-11-25T00:00:00Z",
        "evaluation_date": "2026-11-25T00:00:00Z",
        "training_configuration": {"seed": 42},
        "metrics": {"macro_f1": 0.95},
        "supported_languages": ["English"],
        "limitations": "None",
        "deployment_status": "Production",
    }
    with pytest.raises(PermissionError, match="Direct registration as 'Production' is forbidden"):
        pipeline.register_candidate(v1_entry)

    # 2. Register v1 as Evaluated, then promote with human approval
    v1_entry["deployment_status"] = "Evaluated"
    pipeline.register_candidate(v1_entry)
    with pytest.raises(PermissionError, match="human_approved_by is required"):
        pipeline.registry.promote_model("test-text-v1", "Production")

    pipeline.registry.promote_model("test-text-v1", "Production", human_approved_by="qa_lead")
    assert pipeline.registry.data["models"]["test-text-v1"]["deployment_status"] == "Production"

    # 3. Register v2 as Evaluated and promote -> v1 becomes Superseded
    v2_entry = dict(v1_entry, model_id="test-text-v2", version="2.0.0", artifact_path=str(art_v2), artifact_checksum=compute_sha256(art_v2), deployment_status="Evaluated")
    pipeline.register_candidate(v2_entry)
    pipeline.registry.promote_model("test-text-v2", "Production", human_approved_by="ml_lead")
    assert pipeline.registry.data["models"]["test-text-v2"]["deployment_status"] == "Production"
    assert pipeline.registry.data["models"]["test-text-v1"]["deployment_status"] == "Superseded"

    # 4. Rollback to v1 -> v2 becomes Superseded, v1 restored to Production, history logged
    pipeline.registry.rollback_model("text_classification", "test-text-v1", reason="Latency regression", human_approved_by="oncall_eng")
    assert pipeline.registry.data["models"]["test-text-v1"]["deployment_status"] == "Production"
    assert pipeline.registry.data["models"]["test-text-v2"]["deployment_status"] == "Superseded"
    history = pipeline.registry.data["promotion_history"]
    assert len(history) == 3
    assert history[-1]["action"] == "rollback"
    assert history[-1]["reason"] == "Latency regression"
