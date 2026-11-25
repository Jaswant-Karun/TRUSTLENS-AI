"""
TRUSTLENS AI - Phase 2.4: Cosine Similarity & Nearest-Neighbor Retrieval
Queries the v2.4 multilingual campaign centroids and returns nearest-neighbor threat records
with cosine similarity evidence and legal disclaimer.
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import joblib
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer

from ml.preprocessing.text_preprocessor import text_preprocessor
from ml.campaign_detection.embed import MODEL_NAME


class CandidateCampaignSearchEngine:
    def __init__(self, artifact_dir: str = "ml/artifacts/campaign_detection/v2.4_candidate"):
        self.artifact_dir = Path(artifact_dir)
        self.is_loaded = False
        self.model = None
        self.centroids = {}
        self.dossiers = {}
        self.embeddings = None
        self.records_df = None
        self._load()

    def _load(self):
        art_path = self.artifact_dir / "cluster_artifacts.joblib"
        dos_path = self.artifact_dir / "campaign_dossiers.json"
        emb_path = self.artifact_dir / "threat_embeddings.npy"
        rec_path = self.artifact_dir / "threat_records.parquet"
        if not all(p.exists() for p in [art_path, dos_path, emb_path, rec_path]):
            return

        self.model = SentenceTransformer(MODEL_NAME)
        self.centroids = joblib.load(art_path)["centroids"]
        with open(dos_path, "r", encoding="utf-8") as f:
            for d in json.load(f):
                self.dossiers[d["cluster_id"]] = d
        self.embeddings = np.load(emb_path)
        self.records_df = pd.read_parquet(rec_path)
        self.is_loaded = True

    def search(self, raw_text: str, top_k_neighbors: int = 3) -> Dict[str, Any]:
        if not self.is_loaded:
            return {"status": "unavailable", "error": "Candidate v2.4 campaign artifacts not loaded."}

        norm = text_preprocessor.preprocess(raw_text, mask_personal_data=True)
        q_emb = self.model.encode([norm["cleaned_text"]], normalize_embeddings=True, convert_to_numpy=True)[0]

        # 1. Nearest cluster centroid
        best_cid, best_sim = -1, -1.0
        for cid, cent in self.centroids.items():
            sim = float(np.dot(q_emb, cent))
            if sim > best_sim:
                best_sim = sim
                best_cid = cid

        # 2. Nearest-neighbor messages
        all_sims = np.dot(self.embeddings, q_emb)
        top_idx = np.argsort(all_sims)[::-1][:top_k_neighbors]
        neighbors = [
            {
                "id": str(self.records_df.iloc[i]["id"]),
                "similarity": round(float(all_sims[i]), 4),
                "language": str(self.records_df.iloc[i]["language"]),
                "text_preview": str(self.records_df.iloc[i]["cleaned_text"])[:120],
            }
            for i in top_idx
        ]

        matched_dossier = self.dossiers.get(best_cid)
        return {
            "query_language": norm["language"],
            "nearest_cluster_id": best_cid,
            "centroid_cosine_similarity": round(best_sim, 4),
            "review_status": matched_dossier["review_status"] if matched_dossier else "Unassigned",
            "nearest_neighbors": neighbors,
            "model_version": "paraphrase-multilingual-MiniLM-L12-v2 + hdbscan-v2.4",
            "disclaimer": (
                "Textual similarity indicates semantic overlap only and does not prove a shared criminal source."
            ),
        }


if __name__ == "__main__":
    engine = CandidateCampaignSearchEngine()
    print(json.dumps(engine.search("Aapka SBI khata band ho jayega, turant KYC update karein"), indent=2, ensure_ascii=False))
