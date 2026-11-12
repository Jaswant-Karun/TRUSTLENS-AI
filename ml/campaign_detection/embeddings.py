"""
TRUSTLENS AI - Model 4: Multilingual Sentence Embeddings Engine
Generates normalized dense semantic vector representations for similarity and clustering.
"""

import sys
import os
import time
from pathlib import Path
from typing import List, Union, Optional
import numpy as np
import torch

from sentence_transformers import SentenceTransformer


class CampaignEmbeddingEngine:
    """Production embedding generator for Model 4."""

    DEFAULT_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or self.DEFAULT_MODEL_NAME
        torch.set_num_threads(min(8, os.cpu_count() or 4))
        self.model = SentenceTransformer(self.model_name)
        self.dimension = 384

    def encode(
        self,
        texts: Union[str, List[str]],
        batch_size: int = 128,
        show_progress_bar: bool = False,
        normalize: bool = True,
    ) -> np.ndarray:
        """
        Encodes single or batch texts into normalized L2 dense embeddings.
        With normalize=True, dot product equals cosine similarity.
        """
        if isinstance(texts, str):
            texts = [texts]

        if not texts:
            return np.empty((0, self.dimension), dtype=np.float32)

        with torch.no_grad():
            embeddings = self.model.encode(
                texts,
                batch_size=batch_size,
                show_progress_bar=show_progress_bar,
                normalize_embeddings=normalize,
                convert_to_numpy=True,
            )

        return embeddings.astype(np.float32)

    def similarity(self, emb_a: np.ndarray, emb_b: np.ndarray) -> np.ndarray:
        """Computes cosine similarity between two sets of L2-normalized vectors."""
        # For L2-normalized vectors, cosine similarity is simply the matrix dot product
        return np.dot(emb_a, emb_b.T)
