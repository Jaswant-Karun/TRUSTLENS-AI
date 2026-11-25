"""
TRUSTLENS AI — Remote ML Artifact Sync & SHA-256 Verification
Keeps large binary model weights outside Git in object storage (S3/R2/GCS)
and verifies all Production/Approved artifacts via CentralModelLoader at boot.
"""

import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from backend.app.ml_engine.model_loader import CentralModelLoader


def main() -> int:
    remote_uri = os.getenv("MODEL_ARTIFACTS_URI", "").strip()
    local_dir = Path(os.getenv("ML_ARTIFACTS_DIR", "ml/artifacts"))
    local_dir.mkdir(parents=True, exist_ok=True)

    if remote_uri.startswith("s3://"):
        print(f"[sync_model_artifacts] Syncing artifacts from {remote_uri} -> {local_dir}")
        subprocess.run(["aws", "s3", "sync", remote_uri, str(local_dir)], check=True)
    elif remote_uri:
        print(f"[sync_model_artifacts] Custom MODEL_ARTIFACTS_URI='{remote_uri}' configured; ensure mounted/synced.")

    loader = CentralModelLoader("ml/registry/models_registry_v2.json")
    status = loader.verify_registry_artifacts()
    if loader.verification_errors:
        print(f"[sync_model_artifacts] Verification errors: {loader.verification_errors}", file=sys.stderr)
        return 1

    print(f"[sync_model_artifacts] Verified {len(loader.verified_models)} approved models: {status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
