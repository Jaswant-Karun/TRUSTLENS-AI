"""
Tests for the TRUSTLENS AI Governed Dataset Acquisition Pipeline:
- 8-point provenance documentation completeness
- Commercial-use license gating (blocking non-commercial feeds by default)
- Zip Slip & path-traversal guards
- Schema validation, PII masking, intra/cross-dataset deduplication, and SHA-256 manifest
"""

import zipfile
from pathlib import Path
import pandas as pd
import pytest

from ml.data_pipeline.registry import DATASET_CATALOG, REQUIRED_PROVENANCE_FIELDS, list_datasets
from ml.data_pipeline.acquisition import (
    DatasetAcquisitionPipeline,
    normalize_content_hash,
    safe_dest_path,
    safe_extract_zip,
)


def test_catalog_has_all_eight_provenance_fields():
    assert len(DATASET_CATALOG) >= 7
    for did, spec in DATASET_CATALOG.items():
        for field in REQUIRED_PROVENANCE_FIELDS:
            assert field in spec, f"{did} missing {field}"
            assert spec[field] not in (None, "", []), f"{did}.{field} is empty"
        assert "allowed" in spec["permitted_commercial_usage"]
        assert "terms" in spec["permitted_commercial_usage"]


def test_commercial_license_gate_blocks_non_commercial_feed(tmp_path):
    pipeline = DatasetAcquisitionPipeline(data_root=tmp_path, allow_non_commercial=False)
    with pytest.raises(PermissionError, match="blocked for commercial ingestion"):
        pipeline.check_license_gate("urlhaus_community")

    commercial = {d["dataset_id"] for d in list_datasets(commercial_only=True)}
    assert {"scamshield", "sms_phishing", "legitphish", "uci_sms_spam", "phishtank_feed", "cisa_kev"}.issubset(commercial)
    assert "urlhaus_community" not in commercial


def test_path_traversal_and_zip_slip_blocked(tmp_path):
    with pytest.raises(ValueError, match="Unsafe path traversal"):
        safe_dest_path(tmp_path, "../escape.csv")

    bad_zip = tmp_path / "evil.zip"
    with zipfile.ZipFile(bad_zip, "w") as zf:
        zf.writestr("../../outside.txt", "malicious")

    with pytest.raises(ValueError, match="Zip Slip"):
        safe_extract_zip(bad_zip, tmp_path / "extract")


def test_ingestion_validation_dedup_and_provenance(tmp_path):
    # Create a sample TSV matching UCI SMS Spam format with duplicates, malformed row, and PII
    raw_tsv = tmp_path / "sms_sample.tsv"
    raw_tsv.write_text(
        "ham\tHey call me at 9876543210 tomorrow\n"
        "ham\tHey call me at 9876543210 tomorrow\n"  # intra-dataset duplicate
        "spam\tURGENT claim your prize now\n"
        "spam\tAlready seen in another corpus\n"
        "ham\t\n",  # malformed empty text
        encoding="utf-8",
    )
    existing_hash = normalize_content_hash("Already seen in another corpus")

    pipeline = DatasetAcquisitionPipeline(data_root=tmp_path, allow_non_commercial=False)
    record = pipeline.ingest_local_tabular(
        dataset_id="uci_sms_spam",
        local_path=raw_tsv,
        content_col="text",
        label_col="label",
        sep="\t",
        header=None,
        names=["label", "text"],
        existing_hashes={existing_hash},
    )

    stats = record["validation_and_dedup"]
    assert stats["raw_rows"] == 5
    assert stats["dropped_malformed"] == 1
    assert stats["intra_duplicates_removed"] == 1
    assert stats["cross_duplicates_removed"] == 1
    assert stats["clean_novel_rows"] == 2

    out_df = pd.read_parquet(record["stored_parquet"])
    assert len(out_df) == 2
    assert {"source_dataset", "license", "commercial_permitted", "content_sha256", "acquired_at_utc"}.issubset(out_df.columns)
    assert out_df["commercial_permitted"].all()
    # Verify phone PII masking occurred
    assert not out_df["sanitized_content"].str.contains("9876543210").any()
    assert (tmp_path / "dataset_catalog_manifest.json").exists()
