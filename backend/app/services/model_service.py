"""
TRUSTLENS AI - Model Management Service
Reads and exposes production model registry metadata, metrics, and training histories.
"""

from typing import Dict, Any, List, Optional
import json
from pathlib import Path


class ModelManagementService:
    """Provides model metadata, metrics, and lineage."""

    REGISTRY_PATH = Path("ml/artifacts/model_registry.json")
    DASHBOARD_PATH = Path("ml/artifacts/model_dashboard_data.json")
    TRAINING_HISTORY_PATH = Path("ml/artifacts/training_history.json")
    EVALUATION_HISTORY_PATH = Path("ml/artifacts/evaluation_history.json")

    def _load_json(self, path: Path) -> Dict[str, Any]:
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def get_models_registry(self) -> Dict[str, Any]:
        """Returns registered production models, semantic versions, and hashes."""
        return self._load_json(self.REGISTRY_PATH)

    def get_models_metrics(self) -> Dict[str, Any]:
        """Returns consolidated held-out test evaluation benchmarks for frontend dashboard."""
        return self._load_json(self.DASHBOARD_PATH)

    def get_experiment_history(self) -> Dict[str, Any]:
        """Returns historical training runs and benchmark progressions."""
        return self._load_json(self.TRAINING_HISTORY_PATH)


model_service = ModelManagementService()
