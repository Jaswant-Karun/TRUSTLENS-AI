"""
Automated tests for Model 3 (Fraud Tactic Classification v2.3):
- CentralModelLoader SHA-256 verification of promoted v2.3 production model
- Multi-label detection (>= 2 simultaneous tactics)
- Model-grounded linear saliency evidence extraction
- Transparent fake_investment advisory (zero fabricated labels)
- Confidence calibration & multi-label report completeness
"""

import json
from pathlib import Path

from backend.app.ml_engine.model_loader import CentralModelLoader
from ml.tactic_detection.infer import ScamTacticInferenceEngine


def test_registry_promotes_tactics_v23_with_verified_sha256():
    loader = CentralModelLoader()
    status = loader.verify_registry_artifacts()
    assert status.get("multilabel_tactic_detection") is True
    entry = loader.get_verified_entry("multilabel_tactic_detection")
    assert entry is not None
    assert entry["model_id"] == "trustlens-tactics-v2.3-candidate"
    assert entry["deployment_status"] == "Production"


def test_multilabel_tactic_detection_and_linear_saliency():
    engine = ScamTacticInferenceEngine()
    assert engine.is_loaded is True
    assert engine.model_version_tag == "trustlens-model3-calibrated-linear-v2.3"

    res = engine.predict(
        "URGENT: Your SBI bank account will be suspended today! Update KYC immediately and share OTP 482910."
    )
    assert res["tactic_count"] >= 2
    tactic_ids = {t["tactic_id"] for t in res["tactics"]}
    assert "urgency_time_pressure" in tactic_ids
    assert any(t["evidence_source"] == "linear_saliency" and len(t["evidence_tokens"]) > 0 for t in res["tactics"])


def test_fake_investment_advisory_without_fabrication():
    engine = ScamTacticInferenceEngine()
    res = engine.predict("Guaranteed return 50% daily profit on crypto trading! Invest today.")
    assert res["investment_advisory"] is not None
    assert res["investment_advisory"]["status"] == "unavailable_no_ground_truth_labels"


def test_calibration_and_multilabel_report_exists():
    rep_path = Path("ml/artifacts/tactic_detection/v2.3_candidate/calibration_and_multilabel_report.json")
    assert rep_path.exists()
    rep = json.loads(rep_path.read_text(encoding="utf-8"))
    assert rep["annotated_test_samples"] == 8563
    assert rep["mean_brier_score"] < 0.05
    assert rep["mean_ece"] < 0.05
