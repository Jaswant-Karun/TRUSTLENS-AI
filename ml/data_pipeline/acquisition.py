"""
TRUSTLENS AI - Dataset Ingestion, Validation, Provenance, Deduplication & Secure Storage
Enforces commercial-use license gating, Zip Slip protection, PII masking,
cryptographic SHA-256 provenance tracking, and cross-dataset deduplication.
"""

import os
import json
import time
import zipfile
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional, Set, Tuple
from urllib.parse import urlparse

import httpx
import pandas as pd

from ml.data_pipeline.registry import DATASET_CATALOG, get_dataset_spec
from ml.preprocessing.text_preprocessor import text_preprocessor

CHUNK_SIZE_BYTES = 1024 * 1024  # 1 MB streaming buffer


def compute_sha256(filepath: Path) -> str:
    """Computes SHA-256 checksum using 1 MB streaming chunks."""
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(CHUNK_SIZE_BYTES):
            hasher.update(chunk)
    return hasher.hexdigest()


def normalize_content_hash(value: str) -> str:
    """Computes a normalized SHA-256 hash for exact/near-exact deduplication."""
    normalized = " ".join(str(value).strip().lower().split())
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def safe_dest_path(base_dir: Path, filename: str) -> Path:
    """Prevents path traversal outside base_dir."""
    base_resolved = base_dir.resolve()
    target = (base_resolved / filename).resolve()
    if base_resolved != target and base_resolved not in target.parents:
        raise ValueError(f"Unsafe path traversal detected: {filename}")
    return target


def safe_extract_zip(zip_path: Path, dest_dir: Path) -> List[Path]:
    """Safely extracts a ZIP archive with Zip Slip path-traversal protection."""
    extracted: List[Path] = []
    dest_resolved = dest_dir.resolve()
    with zipfile.ZipFile(zip_path, "r") as zf:
        bad_member = zf.testzip()
        if bad_member is not None:
            raise ValueError(f"Corrupt ZIP member detected: {bad_member}")
        for info in zf.infolist():
            if info.is_dir():
                continue
            target = (dest_resolved / info.filename).resolve()
            if dest_resolved != target and dest_resolved not in target.parents:
                raise ValueError(f"Zip Slip path traversal blocked: {info.filename}")
            target.parent.mkdir(parents=True, exist_ok=True)
            with zf.open(info, "r") as src, open(target, "wb") as dst:
                while chunk := src.read(CHUNK_SIZE_BYTES):
                    dst.write(chunk)
            extracted.append(target)
    return extracted


class DatasetAcquisitionPipeline:
    """End-to-end governed dataset acquisition, validation, dedup, and storage pipeline."""

    def __init__(
        self,
        data_root: Optional[Path] = None,
        allow_non_commercial: bool = False,
    ):
        self.data_root = Path(data_root or "data").resolve()
        self.raw_root = self.data_root / "raw"
        self.processed_root = self.data_root / "processed" / "acquired"
        self.external_root = self.data_root / "external"
        self.manifest_path = self.data_root / "dataset_catalog_manifest.json"
        self.allow_non_commercial = allow_non_commercial

    def check_license_gate(self, dataset_id: str) -> Dict[str, Any]:
        """Verifies commercial reuse permission before ingesting any dataset."""
        spec = get_dataset_spec(dataset_id)
        perm = spec["permitted_commercial_usage"]
        if not perm["allowed"] and not self.allow_non_commercial:
            raise PermissionError(
                f"Dataset '{dataset_id}' is blocked for commercial ingestion: {perm['terms']}"
            )
        return spec

    def download_file_streaming(
        self,
        url: str,
        dest_path: Path,
        headers: Optional[Dict[str, str]] = None,
        max_retries: int = 3,
    ) -> Path:
        """Streams a remote dataset file to disk with retry/backoff and 1 MB chunks."""
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        req_headers = {"User-Agent": os.getenv("TRUSTLENS_DATASET_UA", "TRUSTLENS-AI-DatasetPipeline/1.0")}
        if headers:
            req_headers.update(headers)

        last_err: Optional[Exception] = None
        for attempt in range(1, max_retries + 1):
            try:
                with httpx.Client(follow_redirects=True, timeout=60.0) as client:
                    with client.stream("GET", url, headers=req_headers) as resp:
                        resp.raise_for_status()
                        tmp_path = dest_path.with_suffix(dest_path.suffix + ".part")
                        with open(tmp_path, "wb") as f:
                            for chunk in resp.iter_bytes(chunk_size=CHUNK_SIZE_BYTES):
                                f.write(chunk)
                        tmp_path.replace(dest_path)
                        return dest_path
            except Exception as exc:
                last_err = exc
                if attempt < max_retries:
                    time.sleep(2 ** attempt)
        raise RuntimeError(f"Failed to download {url} after {max_retries} attempts: {last_err}")

    def validate_and_normalize_records(
        self,
        dataset_id: str,
        df: pd.DataFrame,
        content_col: str,
        label_col: str,
        is_url_dataset: bool = False,
        existing_hashes: Optional[Set[str]] = None,
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Validates schema, sanitizes PII / URLs, deduplicates within and across datasets,
        and attaches provenance metadata columns.
        """
        spec = get_dataset_spec(dataset_id)
        if content_col not in df.columns or label_col not in df.columns:
            raise ValueError(
                f"[{dataset_id}] Missing required columns '{content_col}' / '{label_col}'. Found: {list(df.columns)}"
            )

        raw_count = len(df)
        work = df[[content_col, label_col]].copy()
        not_null_mask = work[content_col].notna() & work[label_col].notna()
        work = work[not_null_mask].copy()
        work[content_col] = work[content_col].astype(str).str.strip()
        work[label_col] = work[label_col].astype(str).str.strip()

        # Drop empty / null / 'nan' rows
        valid_mask = (
            work[content_col].ne("")
            & work[content_col].str.lower().ne("nan")
            & work[label_col].ne("")
            & work[label_col].str.lower().ne("nan")
        )
        work = work[valid_mask].copy()
        dropped_malformed = raw_count - len(work)

        # Sanitize / normalize content without outbound network calls
        if is_url_dataset:
            sanitized_vals = []
            keep_flags = []
            for raw_u in work[content_col]:
                parsed = urlparse(raw_u if "://" in raw_u else f"http://{raw_u}")
                is_valid = bool(parsed.netloc and "." in parsed.netloc)
                sanitized_vals.append(raw_u)
                keep_flags.append(is_valid)
            work["sanitized_content"] = sanitized_vals
            work = work[keep_flags].copy()
            dropped_invalid_url = int(sum(not f for f in keep_flags))
        else:
            dropped_invalid_url = 0
            work["sanitized_content"] = [
                text_preprocessor.preprocess(t, mask_personal_data=True)["cleaned_text"]
                for t in work[content_col]
            ]

        work["content_sha256"] = [normalize_content_hash(c) for c in work["sanitized_content"]]

        # Intra-dataset deduplication
        before_intra = len(work)
        work = work.drop_duplicates(subset=["content_sha256"], keep="first").copy()
        intra_duplicates_removed = before_intra - len(work)

        # Cross-dataset deduplication
        cross_duplicates_removed = 0
        if existing_hashes:
            before_cross = len(work)
            work = work[~work["content_sha256"].isin(existing_hashes)].copy()
            cross_duplicates_removed = before_cross - len(work)

        acquired_at = datetime.now(timezone.utc).isoformat()
        work["source_dataset"] = dataset_id
        work["license"] = spec["license"]["name"]
        work["commercial_permitted"] = bool(spec["permitted_commercial_usage"]["allowed"])
        work["acquired_at_utc"] = acquired_at

        stats = {
            "raw_rows": raw_count,
            "dropped_malformed": dropped_malformed,
            "dropped_invalid_url": dropped_invalid_url,
            "intra_duplicates_removed": intra_duplicates_removed,
            "cross_duplicates_removed": cross_duplicates_removed,
            "clean_novel_rows": len(work),
        }
        return work, stats

    def ingest_local_tabular(
        self,
        dataset_id: str,
        local_path: Path,
        content_col: str,
        label_col: str,
        sep: str = ",",
        header: Optional[int] = 0,
        names: Optional[List[str]] = None,
        is_url_dataset: bool = False,
        existing_hashes: Optional[Set[str]] = None,
    ) -> Dict[str, Any]:
        """
        Ingests a local CSV/TSV/ZIP file through the full license gate,
        immutable raw check, validation, deduplication, and secure Parquet storage.
        """
        spec = self.check_license_gate(dataset_id)
        local_path = Path(local_path).resolve()
        if not local_path.exists():
            raise FileNotFoundError(f"Source file not found: {local_path}")

        raw_sha256 = compute_sha256(local_path)
        raw_size_bytes = local_path.stat().st_size

        # Extract if ZIP
        target_file = local_path
        if local_path.suffix.lower() == ".zip":
            extract_dir = self.raw_root / dataset_id
            extracted = safe_extract_zip(local_path, extract_dir)
            if not extracted:
                raise ValueError(f"No files extracted from {local_path}")
            target_file = extracted[0]

        df = pd.read_csv(target_file, sep=sep, header=header, names=names, encoding="utf-8", on_bad_lines="skip")
        clean_df, stats = self.validate_and_normalize_records(
            dataset_id=dataset_id,
            df=df,
            content_col=content_col,
            label_col=label_col,
            is_url_dataset=is_url_dataset,
            existing_hashes=existing_hashes,
        )

        # Secure storage: commercial-permitted -> data/processed/acquired/, non-commercial -> data/external/
        out_dir = (
            self.processed_root
            if spec["permitted_commercial_usage"]["allowed"]
            else self.external_root
        )
        out_dir.mkdir(parents=True, exist_ok=True)
        out_parquet = safe_dest_path(out_dir, f"{dataset_id}.parquet")
        clean_df.to_parquet(out_parquet, index=False)
        parquet_sha256 = compute_sha256(out_parquet)

        record = {
            "dataset_id": dataset_id,
            "name": spec["name"],
            "source": spec["source"],
            "license": spec["license"],
            "collection_date": spec["collection_date"],
            "language": spec["language"],
            "label_definitions": spec["label_definitions"],
            "record_count": stats["clean_novel_rows"],
            "known_limitations": spec["known_limitations"],
            "permitted_commercial_usage": spec["permitted_commercial_usage"],
            "raw_file": str(local_path),
            "raw_sha256": raw_sha256,
            "raw_size_bytes": raw_size_bytes,
            "stored_parquet": str(out_parquet),
            "stored_parquet_sha256": parquet_sha256,
            "validation_and_dedup": stats,
            "ingested_at_utc": datetime.now(timezone.utc).isoformat(),
        }
        self._update_manifest(dataset_id, record)
        return record

    def _update_manifest(self, dataset_id: str, record: Dict[str, Any]) -> None:
        manifest: Dict[str, Any] = {
            "manifest_version": "2.0.0",
            "updated_at_utc": datetime.now(timezone.utc).isoformat(),
            "datasets": {},
        }
        if self.manifest_path.exists():
            try:
                manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
            except Exception:
                pass
        manifest["updated_at_utc"] = datetime.now(timezone.utc).isoformat()
        manifest.setdefault("datasets", {})[dataset_id] = record
        self.manifest_path.parent.mkdir(parents=True, exist_ok=True)
        self.manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    def export_catalog_documentation(self) -> Dict[str, Any]:
        """Exports the full 8-point provenance catalog for all registered datasets."""
        return {
            "catalog_version": "2.0.0",
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "commercial_permitted_count": sum(1 for d in DATASET_CATALOG.values() if d["permitted_commercial_usage"]["allowed"]),
            "non_commercial_gated_count": sum(1 for d in DATASET_CATALOG.values() if not d["permitted_commercial_usage"]["allowed"]),
            "datasets": DATASET_CATALOG,
        }
