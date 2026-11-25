"""
TRUSTLENS AI - CLI for Reproducible ML Pipeline, Approval Promotion & Rollback
Usage:
  python scripts/run_ml_pipeline.py --verify
  python scripts/run_ml_pipeline.py --promote <model_id> --approver "<name>"
  python scripts/run_ml_pipeline.py --rollback <task> <target_model_id> --reason "<reason>" --approver "<name>"
"""

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ml.pipeline import ReproducibleMLPipeline


def main() -> int:
    parser = argparse.ArgumentParser(description="TRUSTLENS AI Reproducible ML Pipeline")
    parser.add_argument("--verify", action="store_true", help="Verify dataset checksums, leakage, and registry state")
    parser.add_argument("--promote", type=str, help="Promote an Evaluated/Approved model_id to Production")
    parser.add_argument("--rollback", nargs=2, metavar=("TASK", "MODEL_ID"), help="Roll back TASK to MODEL_ID")
    parser.add_argument("--reason", type=str, default="Manual operator rollback", help="Rollback reason")
    parser.add_argument("--approver", type=str, help="Human approver name/ID")
    args = parser.parse_args()

    pipeline = ReproducibleMLPipeline()

    if args.verify:
        rep = pipeline.run_verification_pipeline(execute_training=False)
        print(json.dumps(rep, indent=2))
        return 0

    if args.promote:
        res = pipeline.registry.promote_model(args.promote, "Production", human_approved_by=args.approver)
        print(f"Promoted {args.promote} to Production (approved by {res['approved_by']})")
        return 0

    if args.rollback:
        task, target_id = args.rollback
        res = pipeline.registry.rollback_model(task, target_id, reason=args.reason, human_approved_by=args.approver)
        print(f"Rolled back {task} to {target_id} (approved by {res['approved_by']})")
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
