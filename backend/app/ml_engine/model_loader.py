"""
TRUSTLENS AI - Phase 3.0: Central Approved Model Loader
Loads ONLY models with deployment_status in {'Production', 'Approved'} from ml/registry/models_registry_v2.json.
Verifies live SHA-256 checksums before loading; refuses missing, corrupt, Development, or Blocked artifacts.
"""

import json
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional
from backend.app.core.logging import logger

APPROVED_STATUSES = {"Production", "Approved"}


def compute_sha256(filepath: Path) -> str:
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


class CentralModelLoader:
    """Centralized, checksum-verified model registry loader."""

    def __init__(self, registry_path: str = "ml/registry/models_registry_v2.json"):
        self.registry_path = Path(registry_path)
        self.verified_models: Dict[str, Dict[str, Any]] = {}
        self.verification_errors: Dict[str, str] = {}

    def verify_registry_artifacts(self) -> Dict[str, bool]:
        """
        Verifies all Approved/Production models in registry:
        - Checks deployment_status is Production or Approved
        - Checks artifact file exists on disk
        - Checks live SHA-256 matches registered artifact_checksum
        """
        self.verified_models.clear()
        self.verification_errors.clear()

        if not self.registry_path.exists():
            logger.error(f"Model registry not found at {self.registry_path}")
            return {}

        with open(self.registry_path, "r", encoding="utf-8") as f:
            reg = json.load(f)

        status_by_task: Dict[str, bool] = {}

        for model_id, entry in reg.get("models", {}).items():
            dep_status = entry.get("deployment_status")
            task = entry.get("task", "unknown")

            # Strictly ignore non-approved / blocked / development models
            if dep_status not in APPROVED_STATUSES:
                continue

            art_path = Path(entry.get("artifact_path", ""))
            expected_sha = entry.get("artifact_checksum", "")

            if not art_path.exists():
                err = f"Artifact missing on disk: {art_path}"
                logger.error(f"[{model_id}] {err}")
                self.verification_errors[model_id] = err
                status_by_task[task] = False
                continue

            actual_sha = compute_sha256(art_path)
            if actual_sha != expected_sha:
                err = f"SHA-256 checksum mismatch for {art_path} (expected {expected_sha[:12]}, got {actual_sha[:12]})"
                logger.error(f"[{model_id}] {err}")
                self.verification_errors[model_id] = err
                status_by_task[task] = False
                continue

            self.verified_models[model_id] = entry
            status_by_task[task] = True
            logger.info(f"[{model_id}] Verified & approved (v{entry.get('version')}, SHA-256 OK)")

        return status_by_task

    def is_task_approved_and_verified(self, task_name: str) -> bool:
        return any(m.get("task") == task_name for m in self.verified_models.values())

    def get_verified_entry(self, task_name: str) -> Optional[Dict[str, Any]]:
        for m in self.verified_models.values():
            if m.get("task") == task_name:
                return m
        return None
