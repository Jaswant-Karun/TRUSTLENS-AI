"""
TRUSTLENS AI - Phase 2.4: HDBSCAN Multilingual Campaign Clustering
Clusters 5,488 threat embeddings, extracts shared IOCs, near-duplicate concentrations,
language distributions, and outputs candidate similarity dossiers.
"""

import re
import sys
import json
import time
import hashlib
from pathlib import Path
from urllib.parse import urlparse
from collections import Counter

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import joblib
import numpy as np
import pandas as pd
from sklearn.cluster import HDBSCAN

LEGAL_DISCLAIMER = (
    "Candidate Similarity Cluster: Grouping reflects mathematical and linguistic embedding similarity only; "
    "it does not confirm a shared criminal organization or coordinated threat actor."
)


def extract_iocs(text: str) -> dict:
    clean_t = str(text)
    urls = re.findall(r"https?://[^\s<>\"']+|www\.[^\s<>\"']+", clean_t)
    domains = []
    for u in urls:
        try:
            netloc = urlparse(u if "://" in u else "http://" + u).netloc.lower().split(":")[0]
            if netloc:
                domains.append(netloc)
        except Exception:
            pass
    upis = re.findall(r"[\w.-]+@(?:okaxis|okhdfcbank|okicici|oksbi|paytm|ybl|apl|upi)", clean_t, re.IGNORECASE)
    phones = re.findall(r"(?:\+91[-\s]?)?[6-9]\d{9}", clean_t)
    return {"urls": urls, "domains": domains, "upis": upis, "phones": phones}


def main():
    print("=" * 70)
    print("TRUSTLENS AI - PHASE 2.4: HDBSCAN MULTILINGUAL CLUSTERING")
    print("=" * 70)

    out_dir = Path("ml/artifacts/campaign_detection/v2.4_candidate")
    embeddings = np.load(out_dir / "threat_embeddings.npy")
    df = pd.read_parquet(out_dir / "threat_records.parquet")

    params = {
        "min_cluster_size": 25,
        "min_samples": 5,
        "metric": "euclidean",
        "cluster_selection_method": "eom",
    }

    t0 = time.perf_counter()
    hdb = HDBSCAN(**params, store_centers="centroid")
    labels = hdb.fit_predict(embeddings)
    duration = round(time.perf_counter() - t0, 2)

    df["cluster_id"] = labels
    df.to_parquet(out_dir / "clustered_records.parquet", index=False)

    unique_clusters = sorted([int(c) for c in set(labels) if c != -1])
    dossiers = []
    centroids = {}

    for c_id in unique_clusters:
        mask = labels == c_id
        c_df = df[mask]
        c_embs = embeddings[mask]

        centroid = c_embs.mean(axis=0)
        centroid = centroid / np.linalg.norm(centroid)
        centroids[c_id] = centroid

        sims = np.dot(c_embs, centroid)
        top_rep_idx = np.argsort(sims)[::-1][:2]
        representatives = [c_df.iloc[i]["cleaned_text"] for i in top_rep_idx]

        all_urls, all_domains, all_upis, all_phones = [], [], [], []
        for raw_t in c_df["raw_text"]:
            iocs = extract_iocs(raw_t)
            all_urls.extend(iocs["urls"])
            all_domains.extend(iocs["domains"])
            all_upis.extend(iocs["upis"])
            all_phones.extend(iocs["phones"])

        unique_groups = int(c_df["text_group_id"].nunique())
        dup_concentration = round(1.0 - (unique_groups / max(1, len(c_df))), 4)

        dossiers.append({
            "cluster_id": c_id,
            "record_count": int(len(c_df)),
            "unique_text_groups": unique_groups,
            "near_duplicate_concentration": dup_concentration,
            "similarity_evidence": {
                "mean_cosine_similarity": round(float(np.mean(sims)), 4),
                "min_cosine_similarity": round(float(np.min(sims)), 4),
            },
            "representative_examples": representatives,
            "shared_indicators": {
                "top_domains": [k for k, _ in Counter(all_domains).most_common(5)],
                "top_urls": [k for k, _ in Counter(all_urls).most_common(5)],
                "top_phones": [k for k, _ in Counter(all_phones).most_common(5)],
                "top_upis": [k for k, _ in Counter(all_upis).most_common(5)],
            },
            "source_records_sample_ids": c_df["id"].head(10).tolist(),
            "language_distribution": c_df["language"].value_counts().to_dict(),
            "review_status": "Candidate similarity cluster — Under review",
            "embedding_model_version": "paraphrase-multilingual-MiniLM-L12-v2",
            "clustering_version": "hdbscan-v2.4",
            "disclaimer": LEGAL_DISCLAIMER,
        })

    dossiers.sort(key=lambda d: d["record_count"], reverse=True)
    with open(out_dir / "campaign_dossiers.json", "w", encoding="utf-8") as f:
        json.dump(dossiers, f, indent=2, ensure_ascii=False)

    joblib.dump({"centroids": centroids, "params": params}, out_dir / "cluster_artifacts.joblib")
    with open(out_dir / "clustering_config.json", "w", encoding="utf-8") as f:
        json.dump({"algorithm": "HDBSCAN", "params": params, "duration_seconds": duration}, f, indent=2)

    print(f"Discovered {len(unique_clusters)} clusters | Noise: {int(np.sum(labels == -1)):,} / {len(labels):,} ({np.mean(labels == -1):.2%}) in {duration}s")


if __name__ == "__main__":
    main()
