"""
TRUSTLENS AI - CLI Entrypoint for Governed Dataset Acquisition & Catalog Export
Usage:
  python scripts/acquire_datasets.py --list
  python scripts/acquire_datasets.py --export-catalog
"""

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ml.data_pipeline import DatasetAcquisitionPipeline, DATASET_CATALOG


def main() -> int:
    parser = argparse.ArgumentParser(description="TRUSTLENS AI Governed Dataset Acquisition Pipeline")
    parser.add_argument("--list", action="store_true", help="List all cataloged datasets and commercial-use status")
    parser.add_argument("--export-catalog", action="store_true", help="Export full 8-point catalog to data/dataset_catalog_manifest.json")
    parser.add_argument("--allow-non-commercial", action="store_true", help="Allow research-only datasets (e.g. URLhaus community)")
    args = parser.parse_args()

    pipeline = DatasetAcquisitionPipeline(allow_non_commercial=args.allow_non_commercial)

    if args.list:
        for did, spec in DATASET_CATALOG.items():
            allowed = spec["permitted_commercial_usage"]["allowed"]
            print(f"- {did:20s} | license={spec['license']['name']:40s} | commercial={allowed}")
        return 0

    if args.export_catalog:
        catalog = pipeline.export_catalog_documentation()
        out = Path("data/dataset_catalog_manifest.json")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(catalog, indent=2), encoding="utf-8")
        print(f"Exported {len(catalog['datasets'])} dataset provenance entries to {out}")
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
