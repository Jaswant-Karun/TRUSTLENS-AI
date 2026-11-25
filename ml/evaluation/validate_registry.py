"""
TRUSTLENS AI - Phase 2.5: Automated Registry Integrity & Promotion Policy Checks
Verifies:
1. All required metadata fields exist on every registered model.
2. Every non-blocked artifact exists on disk and passes live SHA-256 checksum verification.
3. Experiment tracking records cleanly separate dataset versions.
4. Promotion policy strictly blocks unapproved or blocked Production promotions.
"""

import sys
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ml.registry.registry_manager import ModelRegistryManager, compute_sha256, REQUIRED_FIELDS, VALID_STATUSES


def main():
    print("=" * 70)
    print("TRUSTLENS AI - PHASE 2.5: REGISTRY & POLICY VALIDATION")
    print("=" * 70)

    mgr = ModelRegistryManager("ml/registry/models_registry_v2.json")
    models = mgr.data.get("models", {})
    assert len(models) >= 6, f"Expected >= 6 registered models, got {len(models)}"

    for mid, m in models.items():
        for f in REQUIRED_FIELDS:
            assert f in m and m[f] is not None, f"Missing field '{f}' in {mid}"
        assert m["deployment_status"] in VALID_STATUSES

        if m["deployment_status"] != "Blocked":
            art_path = Path(m["artifact_path"])
            assert art_path.exists(), f"Missing artifact on disk: {art_path}"
            actual_sha = compute_sha256(art_path)
            assert actual_sha == m["artifact_checksum"], f"Checksum mismatch for {mid}!"
            print(f"  PASS [{m['deployment_status']}]: {mid} (SHA-256 verified)")
        else:
            print(f"  PASS [Blocked]: {mid} (Explicitly blocked, no artifact)")

    # Verify Experiment Tracker
    exp_data = json.loads(Path("ml/evaluation/experiments_v2.json").read_text(encoding="utf-8"))
    assert exp_data["total_experiments"] >= 10
    for e in exp_data["experiments"]:
        assert e["dataset_version"] == "2.0.5", "Mixed dataset version detected!"
    print(f"  PASS: {exp_data['total_experiments']} experiments isolated to dataset_version=2.0.5")

    # Verify Promotion Policy Gating (must raise PermissionError without human_approved_by)
    try:
        mgr.promote_model("trustlens-text-v2.1-candidate", "Production", human_approved_by=None)
        raise AssertionError("Promotion succeeded without human approval!")
    except PermissionError:
        print("  PASS: Promotion policy blocked unapproved Production promotion")

    try:
        mgr.promote_model("trustlens-tactic-fake-investment", "Approved", human_approved_by="Lead")
        raise AssertionError("Blocked model was promoted!")
    except PermissionError:
        print("  PASS: Promotion policy blocked promotion of Blocked model")

    print("\nALL PHASE 2.5 AUTOMATED CHECKS PASSED!")


if __name__ == "__main__":
    main()
