"""
TRUSTLENS AI - Documented Real-World Dataset Acquisition Pipeline
Provides verified dataset catalog, ingestion, validation, provenance tracking,
deduplication, and secure storage with commercial-use license gating.
"""

from ml.data_pipeline.registry import DATASET_CATALOG, get_dataset_spec, list_datasets
from ml.data_pipeline.acquisition import DatasetAcquisitionPipeline

__all__ = [
    "DATASET_CATALOG",
    "get_dataset_spec",
    "list_datasets",
    "DatasetAcquisitionPipeline",
]
