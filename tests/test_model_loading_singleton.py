"""
TRUSTLENS AI - Model Loading Singleton Verification Test
Verifies that repeated and concurrent instantiations reuse the same SentenceTransformer instance.
"""

from concurrent.futures import ThreadPoolExecutor
from ml.campaign_detection.embeddings import CampaignEmbeddingEngine


def test_sentence_transformer_singleton_reuse():
    e1 = CampaignEmbeddingEngine()
    e2 = CampaignEmbeddingEngine()
    assert e1.model is e2.model, "Expected CampaignEmbeddingEngine instances to share the same SentenceTransformer model"


def test_concurrent_model_initialization_reuses_instance():
    def create_engine(_):
        return CampaignEmbeddingEngine().model

    with ThreadPoolExecutor(max_workers=4) as pool:
        models = list(pool.map(create_engine, range(4)))

    first = models[0]
    assert all(m is first for m in models), "Concurrent initializations created duplicate SentenceTransformer instances"
