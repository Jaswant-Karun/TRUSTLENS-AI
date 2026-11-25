"""
TRUSTLENS AI - Phase 2.4: Multilingual Threat Embedding Generator
Generates L2-normalized 384-dim embeddings using paraphrase-multilingual-MiniLM-L12-v2
on the leak-free Phase 2.0.5 threat corpus (smishing + scam, n=5,488).
Saves candidate artifacts under ml/artifacts/campaign_detection/v2.4_candidate/.
"""

import os
import sys
import json
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import numpy as np
import pandas as pd
import torch
from sentence_transformers import SentenceTransformer

MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


def main():
    print("=" * 70)
    print("TRUSTLENS AI - PHASE 2.4: MULTILINGUAL EMBEDDING GENERATION")
    print("=" * 70)

    out_dir = Path("ml/artifacts/campaign_detection/v2.4_candidate")
    out_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_parquet("data/processed/text_train.parquet")
    threats = df[(df["is_threat"] == 1) & (df["canonical_label"] != "spam")].copy().reset_index(drop=True)
    print(f"Loaded {len(threats):,} verified threat messages (smishing + scam).")
    print(f"Languages: {threats['language'].value_counts().to_dict()}")

    torch.set_num_threads(min(8, os.cpu_count() or 4))
    print(f"\nLoading {MODEL_NAME} on CPU...")
    model = SentenceTransformer(MODEL_NAME)

    t0 = time.perf_counter()
    texts = threats["cleaned_text"].fillna("").tolist()
    with torch.no_grad():
        embeddings = model.encode(
            texts,
            batch_size=64,
            show_progress_bar=False,
            normalize_embeddings=True,
            convert_to_numpy=True,
        ).astype(np.float32)
    elapsed = round(time.perf_counter() - t0, 2)

    np.save(out_dir / "threat_embeddings.npy", embeddings)
    cols_to_save = ["id", "raw_text", "cleaned_text", "language", "canonical_label", "text_group_id", "source_dataset"]
    threats[cols_to_save].to_parquet(out_dir / "threat_records.parquet", index=False)

    emb_cfg = {
        "phase": "2.4",
        "dataset_version": "2.0.5",
        "model_name": MODEL_NAME,
        "embedding_dimension": int(embeddings.shape[1]),
        "sample_count": int(embeddings.shape[0]),
        "normalization": "L2_unit_sphere",
        "distance_metric": "cosine",
        "encoding_duration_seconds": elapsed,
    }
    with open(out_dir / "embedding_config.json", "w", encoding="utf-8") as f:
        json.dump(emb_cfg, f, indent=2)

    print(f"Encoded {embeddings.shape} in {elapsed}s -> saved to {out_dir}")


if __name__ == "__main__":
    main()
