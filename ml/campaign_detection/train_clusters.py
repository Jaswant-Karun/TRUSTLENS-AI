"""
TRUSTLENS AI - Model 4: Scam Campaign Discovery & Clustering Pipeline
Applies Multilingual Sentence Transformers, Cosine Distance, HDBSCAN & DBSCAN
to discover coordinated fraud campaigns and extract structured threat intelligence.
"""

import sys
import os
import re
import json
import time
from pathlib import Path
from typing import Dict, Any, List, Tuple
from collections import Counter, defaultdict
from urllib.parse import urlparse

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import numpy as np
import pandas as pd
import joblib
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.cluster import HDBSCAN, DBSCAN
from sklearn.metrics import silhouette_score, davies_bouldin_score
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer

from ml.campaign_detection.embeddings import CampaignEmbeddingEngine


def extract_iocs(text: str) -> Dict[str, List[str]]:
    """Extracts raw URLs, host domains, phone numbers, and UPI handles from message."""
    clean_t = str(text)

    # URLs
    urls = re.findall(r"https?://[^\s<>\"']+|www\.[^\s<>\"']+", clean_t)
    domains = []
    for u in urls:
        try:
            parsed = urlparse(u if "://" in u else "http://" + u)
            netloc = parsed.netloc.lower().split(":")[0]
            if netloc:
                domains.append(netloc)
        except Exception:
            pass

    # UPI IDs
    upis = re.findall(r"[\w.-]+@(?:okaxis|okhdfcbank|okicici|oksbi|paytm|ybl|apl|upi)", clean_t, re.IGNORECASE)

    # Phone numbers
    phones = re.findall(r"(?:\+91[-\s]?)?[6-9]\d{9}", clean_t)

    return {
        "urls": list(set(urls)),
        "domains": list(set(domains)),
        "upis": list(set(upis)),
        "phones": list(set(phones)),
    }


def extract_top_phrases(texts: List[str], top_n: int = 5) -> List[str]:
    """Extracts the most distinctive n-gram phrases for a campaign cluster."""
    if not texts or len(texts) < 2:
        return []
    try:
        vec = TfidfVectorizer(ngram_range=(2, 3), max_features=1000, stop_words="english")
        X = vec.fit_transform(texts)
        scores = np.asarray(X.sum(axis=0)).ravel()
        names = np.array(vec.get_feature_names_out())
        top_indices = np.argsort(scores)[::-1][:top_n]
        return [str(names[i]) for i in top_indices]
    except Exception:
        return []


def identify_targeted_entity(text: str) -> str:
    """Identifies the impersonated brand or institution from message text."""
    tl = text.lower()
    entities = {
        "SBI (State Bank of India)": ["sbi", "state bank"],
        "HDFC Bank": ["hdfc"],
        "ICICI Bank": ["icici"],
        "Punjab National Bank": ["pnb", "punjab national"],
        "State Electricity Board": ["electricity", "power disconnection", "bijli", "light cut"],
        "Traffic Police (e-Challan)": ["challan", "traffic police", "vehicle number", "parivahan"],
        "India Post / FedEx / Courier": ["speed post", "courier", "fedex", "mand order", "delivery pref", "parcel"],
        "KBC / Kaun Banega Crorepati": ["kbc", "lucky draw", "jio lucky", "sim card winner"],
        "Telegram Job Recruitment": ["telegram", "youtube like", "rating task", "daily income job"],
        "Income Tax Department": ["income tax", "refund approval", "it department"],
    }
    for brand, patterns in entities.items():
        if any(p in tl for p in patterns):
            return brand
    return "Generic / Unspecified Institution"


def evaluate_clusters(
    name: str, labels: np.ndarray, embeddings: np.ndarray, duration: float
) -> Dict[str, Any]:
    """Computes cluster quality, noise percentage, and silhouette metrics."""
    n_total = len(labels)
    unique_labels = set(labels)
    n_clusters = len(unique_labels - {-1})
    noise_count = int(np.sum(labels == -1))
    noise_pct = round(noise_count / n_total * 100, 2)

    # Compute silhouette and Davies-Bouldin only on non-noise samples
    clustered_mask = labels != -1
    n_clustered = int(np.sum(clustered_mask))

    sil_score = None
    db_score = None

    if n_clusters >= 2 and n_clustered > n_clusters:
        try:
            sil_score = round(float(silhouette_score(embeddings[clustered_mask], labels[clustered_mask], metric="euclidean")), 4)
            db_score = round(float(davies_bouldin_score(embeddings[clustered_mask], labels[clustered_mask])), 4)
        except Exception as e:
            print(f"[WARN] Metric calc failed for {name}: {e}")

    return {
        "algorithm": name,
        "total_samples": n_total,
        "clusters_discovered": n_clusters,
        "noise_samples": noise_count,
        "noise_percentage": noise_pct,
        "clustered_samples": n_clustered,
        "silhouette_score": sil_score,
        "davies_bouldin_index": db_score,
        "duration_seconds": round(duration, 2),
    }


def main():
    print("=" * 68)
    print("TRUSTLENS AI - MODEL 4: SCAM CAMPAIGN CLUSTERING & DISCOVERY")
    print("=" * 68)

    artifacts_dir = Path("ml/artifacts/campaign_detection")
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    # 1. Load Pure Threat Messages
    print("\n[1/5] Ingesting Verified Threat Records from Processed Store...")
    df_train = pd.read_parquet("data/processed/text_train.parquet")
    threat_df = df_train[
        (df_train["is_threat"] == 1) & (df_train["original_label"] != "General Spam / Telemarketing")
    ].copy().reset_index(drop=True)

    print(f"  Loaded {len(threat_df):,} verified attack messages across {threat_df['original_label'].nunique()} scam categories")

    # 2. Embedding Generation & Caching
    print("\n[2/5] Generating Normalized Multilingual Sentence Embeddings...")
    emb_cache_path = artifacts_dir / "threat_embeddings.npy"
    embedder = CampaignEmbeddingEngine()

    if emb_cache_path.exists():
        print(f"  Loading precomputed embeddings from {emb_cache_path.name}...")
        embeddings = np.load(emb_cache_path)
    else:
        t0_emb = time.time()
        print("  Encoding messages via sentence-transformers/all-MiniLM-L6-v2 (L2 normalized)...")
        texts_to_encode = threat_df["cleaned_text"].tolist()
        embeddings = embedder.encode(texts_to_encode, batch_size=128, show_progress_bar=True, normalize=True)
        np.save(emb_cache_path, embeddings)
        print(f"  Generated {embeddings.shape[0]:,} embeddings in {time.time() - t0_emb:.2f}s | Shape: {embeddings.shape}")

    # 3. Clustering Execution (HDBSCAN vs DBSCAN)
    print("\n[3/5] Executing Unsupervised Density Clustering...")

    # Algorithm A: HDBSCAN
    print("  -> Running HDBSCAN (min_cluster_size=25, min_samples=5, metric='euclidean')...")
    t0_hdb = time.time()
    hdb = HDBSCAN(
        min_cluster_size=25,
        min_samples=5,
        metric="euclidean",
        cluster_selection_method="eom",
        store_centers="centroid",
    )
    hdb_labels = hdb.fit_predict(embeddings)
    hdb_time = time.time() - t0_hdb
    hdb_eval = evaluate_clusters("HDBSCAN", hdb_labels, embeddings, hdb_time)
    print(f"     Clusters: {hdb_eval['clusters_discovered']} | Noise: {hdb_eval['noise_percentage']}% | Silhouette: {hdb_eval['silhouette_score']}")

    # Algorithm B: DBSCAN Baseline
    print("  -> Running DBSCAN Baseline (eps=0.35, min_samples=15, metric='cosine')...")
    t0_db = time.time()
    db = DBSCAN(eps=0.35, min_samples=15, metric="cosine")
    db_labels = db.fit_predict(embeddings)
    db_time = time.time() - t0_db
    db_eval = evaluate_clusters("DBSCAN Baseline", db_labels, embeddings, db_time)
    print(f"     Clusters: {db_eval['clusters_discovered']} | Noise: {db_eval['noise_percentage']}% | Silhouette: {db_eval['silhouette_score']}")

    # Select HDBSCAN as superior hierarchical density clustering algorithm
    selected_labels = hdb_labels
    threat_df["cluster_id"] = selected_labels

    # 4. Extract Structured Campaign Intelligence Dossiers
    print("\n[4/5] Compiling Threat Campaign Intelligence Dossiers...")
    campaign_dossiers = []
    cluster_centroids = {}
    cluster_exemplars = {}

    unique_clusters = sorted([c for c in set(selected_labels) if c != -1])

    for c_id in unique_clusters:
        c_mask = selected_labels == c_id
        c_indices = np.where(c_mask)[0]
        c_samples = threat_df.iloc[c_indices]
        c_embs = embeddings[c_indices]

        # Centroid
        centroid = c_embs.mean(axis=0)
        centroid = centroid / np.linalg.norm(centroid)
        cluster_centroids[int(c_id)] = centroid

        # Exemplar (sample closest to centroid)
        sims = np.dot(c_embs, centroid)
        exemplar_idx = c_indices[np.argmax(sims)]
        exemplar_text = threat_df.iloc[exemplar_idx]["cleaned_text"]
        cohesion = round(float(np.mean(sims)), 4)
        cluster_exemplars[int(c_id)] = exemplar_text

        # Aggregate IOCs and Phrases
        all_urls = []
        all_domains = []
        all_upis = []
        all_phones = []

        for txt in c_samples["cleaned_text"]:
            iocs = extract_iocs(txt)
            all_urls.extend(iocs["urls"])
            all_domains.extend(iocs["domains"])
            all_upis.extend(iocs["upis"])
            all_phones.extend(iocs["phones"])

        top_phrases = extract_top_phrases(c_samples["cleaned_text"].tolist(), top_n=5)
        target_entity = identify_targeted_entity(exemplar_text)

        # Category consensus
        top_cats = c_samples["original_label"].value_counts().head(2).to_dict()

        dossier = {
            "cluster_id": int(c_id),
            "campaign_name": f"Campaign Cluster #{c_id:02d} — {target_entity}",
            "sample_count": len(c_indices),
            "percentage_of_threats": round(len(c_indices) / len(threat_df) * 100, 2),
            "cluster_cohesion_score": cohesion,
            "targeted_institution": target_entity,
            "predominant_categories": top_cats,
            "exemplar_message": exemplar_text,
            "shared_phrases": top_phrases,
            "shared_indicators": {
                "unique_domains_count": len(set(all_domains)),
                "sample_domains": list(set(all_domains))[:6],
                "sample_urls": list(set(all_urls))[:4],
                "sample_upis": list(set(all_upis))[:4],
                "sample_phones": list(set(all_phones))[:4],
            },
            "soc_legal_disclaimer": "Similarity clustering denotes shared linguistic and infrastructure patterns; it does not constitute legal proof of identical organizational origin.",
        }
        campaign_dossiers.append(dossier)

    # Sort dossiers by sample count descending
    campaign_dossiers.sort(key=lambda x: x["sample_count"], reverse=True)
    print(f"  Compiled {len(campaign_dossiers)} structured campaign dossiers.")

    # 5. Visual 2D Cluster Projection & Saving Artifacts
    print("\n[5/5] Generating Visual Cluster Map & Saving Artifacts...")

    # TruncatedSVD for 2D visualization
    svd = TruncatedSVD(n_components=2, random_state=42)
    coords_2d = svd.fit_transform(embeddings)

    plt.figure(figsize=(11, 8))
    # Plot noise points in subtle grey
    noise_idx = np.where(selected_labels == -1)[0]
    plt.scatter(coords_2d[noise_idx, 0], coords_2d[noise_idx, 1], c="#cbd5e1", s=12, alpha=0.3, label=f"Unclustered Noise ({hdb_eval['noise_percentage']}%)")

    # Plot top 10 campaign clusters with distinct colors
    palette = sns.color_palette("tab10", n_colors=min(10, len(campaign_dossiers)))
    for rank, dos in enumerate(campaign_dossiers[:10]):
        c_id = dos["cluster_id"]
        idx = np.where(selected_labels == c_id)[0]
        color = palette[rank]
        lbl = f"C{c_id:02d}: {dos['targeted_institution'][:20]} (N={dos['sample_count']})"
        plt.scatter(coords_2d[idx, 0], coords_2d[idx, 1], color=color, s=25, alpha=0.75, label=lbl)

    plt.title("TRUSTLENS AI — Discovered Scam Campaign Clusters (HDBSCAN 2D Semantic Space)", fontsize=12, fontweight="bold")
    plt.xlabel("Semantic Latent Dimension 1", fontsize=10)
    plt.ylabel("Semantic Latent Dimension 2", fontsize=10)
    plt.grid(True, linestyle="--", alpha=0.3)
    plt.legend(bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=8)
    plt.tight_layout()
    plt.savefig(artifacts_dir / "campaign_clusters_2d.png", dpi=200)
    plt.close()

    # Save Configurations & Reports
    emb_config = {
        "model_name": "sentence-transformers/all-MiniLM-L6-v2",
        "embedding_dimension": 384,
        "normalization": "L2_unit_sphere",
        "distance_metric": "cosine",
    }
    with open(artifacts_dir / "embedding_config.json", "w", encoding="utf-8") as f:
        json.dump(emb_config, f, indent=2)

    clustering_config = {
        "selected_algorithm": "HDBSCAN",
        "hdbscan_params": {
            "min_cluster_size": 25,
            "min_samples": 5,
            "metric": "euclidean",
            "cluster_selection_method": "eom",
        },
        "dbscan_baseline_params": {
            "eps": 0.35,
            "min_samples": 15,
            "metric": "cosine",
        },
    }
    with open(artifacts_dir / "clustering_config.json", "w", encoding="utf-8") as f:
        json.dump(clustering_config, f, indent=2)

    with open(artifacts_dir / "campaign_dossiers.json", "w", encoding="utf-8") as f:
        json.dump(campaign_dossiers, f, indent=2)

    report = {
        "task": "Scam Campaign Discovery & Similarity Intelligence",
        "total_threat_samples": len(threat_df),
        "hdbscan_results": hdb_eval,
        "dbscan_results": db_eval,
        "top_campaigns_discovered": [
            {
                "cluster_id": d["cluster_id"],
                "name": d["campaign_name"],
                "size": d["sample_count"],
                "cohesion": d["cluster_cohesion_score"],
            }
            for d in campaign_dossiers[:8]
        ],
    }
    with open(artifacts_dir / "campaign_experiment_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    # Save cluster artifacts dictionary for instant inference lookups
    cluster_artifacts = {
        "centroids": cluster_centroids,
        "exemplars": cluster_exemplars,
        "dossiers": campaign_dossiers,
        "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
        "total_clusters": len(unique_clusters),
    }
    joblib.dump(cluster_artifacts, artifacts_dir / "cluster_artifacts.joblib")

    # Update main backend registry
    joblib.dump(cluster_artifacts, Path("ml/artifacts/campaign_clusterer.joblib"))

    print(f"\n[OK] All Model 4 campaign discovery artifacts saved to {artifacts_dir}")
    print("=" * 68)
    print("MODEL 4 CAMPAIGN DISCOVERY COMPLETED SUCCESSFULLY!")
    print("=" * 68)


if __name__ == "__main__":
    main()
