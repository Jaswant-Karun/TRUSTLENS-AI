"""
TRUSTLENS AI - Reproducible ML Training & Evaluation Pipeline
Enforces:
- Dataset versioning & SHA-256 verification
- Zero-leakage group-aware split verification (text_group_id, domain_group_id)
- Training configuration & experiment tracking
- Candidate-only artifact registration (never auto-replaces Production)
- Human-approved promotion & rollback via ModelRegistryManager
"""

import json
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional

import pandas as pd

from ml.registry.registry_manager import ModelRegistryManager, compute_sha256


class ReproducibleMLPipeline:
    """Orchestrates reproducible verification, training, evaluation, and gated promotion."""

    def __init__(
        self,
        manifest_path: str = "data/processed/dataset_manifest.json",
        registry_path: str = "ml/registry/models_registry_v2.json",
        runs_dir: str = "ml/evaluation/pipeline_runs",
    ):
        self.manifest_path = Path(manifest_path)
        self.registry = ModelRegistryManager(registry_path=registry_path)
        self.runs_dir = Path(runs_dir)
        self.runs_dir.mkdir(parents=True, exist_ok=True)

    def verify_dataset_version_and_leakage(self) -> Dict[str, Any]:
        """
        Verifies dataset manifest SHA-256 checksums and asserts zero group overlap
        across train, validation, and test splits for both text and URL corpora.
        """
        if not self.manifest_path.exists():
            raise FileNotFoundError(f"Dataset manifest not found: {self.manifest_path}")

        manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        processed_dir = self.manifest_path.parent
        checksum_results: Dict[str, bool] = {}

        for fname, info in manifest.get("processed_files", {}).items():
            fpath = processed_dir / fname
            if not fpath.exists():
                raise FileNotFoundError(f"Processed dataset split missing: {fpath}")
            actual = compute_sha256(fpath)
            if actual != info["sha256"]:
                raise ValueError(f"Dataset SHA-256 mismatch for {fname}: expected {info['sha256']}, got {actual}")
            checksum_results[fname] = True

        leakage_checks: Dict[str, Dict[str, int]] = {}
        for prefix, group_col in [("text", "text_group_id"), ("urls", "domain_group_id")]:
            tr = pd.read_parquet(processed_dir / f"{prefix}_train.parquet", columns=[group_col])
            va = pd.read_parquet(processed_dir / f"{prefix}_val.parquet", columns=[group_col])
            te = pd.read_parquet(processed_dir / f"{prefix}_test.parquet", columns=[group_col])
            g_tr, g_va, g_te = set(tr[group_col]), set(va[group_col]), set(te[group_col])
            overlaps = {
                "train_val_overlap": len(g_tr & g_va),
                "train_test_overlap": len(g_tr & g_te),
                "val_test_overlap": len(g_va & g_te),
            }
            if any(v > 0 for v in overlaps.values()):
                raise ValueError(f"Data leakage detected in {prefix} splits ({group_col}): {overlaps}")
            leakage_checks[prefix] = overlaps

        return {
            "dataset_version": manifest.get("manifest_version"),
            "random_seed": manifest.get("random_seed"),
            "checksums_verified": len(checksum_results),
            "leakage_checks": leakage_checks,
        }

    def register_candidate(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        """
        Registers a newly trained/evaluated model strictly as 'Development' or 'Evaluated'.
        Never automatically promotes to 'Production'.
        """
        if entry.get("deployment_status") == "Production":
            raise PermissionError("Direct registration as 'Production' is forbidden. Register as 'Evaluated' and approve separately.")
        self.registry.register_model(entry)
        self.registry.save()
        return entry

    def run_verification_pipeline(self, execute_training: bool = False) -> Dict[str, Any]:
        """
        Runs dataset integrity & leakage checks, tracks configuration & experiments,
        and writes a reproducible pipeline run report without altering Production models.
        """
        run_id = f"run-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{uuid.uuid4().hex[:6]}"
        dataset_report = self.verify_dataset_version_and_leakage()

        training_executed: List[str] = []
        if execute_training:
            # Run reproducible candidate training scripts (all write to v2.x_candidate, never Production)
            for script in [
                "ml/text_detection/train.py",
                "ml/url_detection/train.py",
                "ml/tactic_detection/train.py",
            ]:
                subprocess.run([sys.executable, script], check=True)
                training_executed.append(script)

        # Refresh experiment tracker
        exp_path = Path("ml/evaluation/experiments_v2.json")
        exp_count = 0
        if exp_path.exists():
            exp_data = json.loads(exp_path.read_text(encoding="utf-8"))
            exp_count = exp_data.get("total_experiments", len(exp_data.get("experiments", [])))

        prod_models = {
            mid: m["version"]
            for mid, m in self.registry.data.get("models", {}).items()
            if m.get("deployment_status") == "Production"
        }

        report = {
            "run_id": run_id,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "dataset_verification": dataset_report,
            "execute_training": execute_training,
            "training_scripts_executed": training_executed,
            "tracked_experiments": exp_count,
            "active_production_models": prod_models,
            "auto_promotion_blocked": True,
        }
        out_file = self.runs_dir / f"{run_id}.json"
        out_file.write_text(json.dumps(report, indent=2), encoding="utf-8")
        return report
