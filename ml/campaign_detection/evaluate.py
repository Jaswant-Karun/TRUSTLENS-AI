"""
TRUSTLENS AI - Phase 2.4: Cluster Validation & Stability Evaluation
Measures cluster-size distribution, noise ratio, silhouette score, Davies-Bouldin index,
stability across min_cluster_size=[20, 25, 35], and compares against the existing 47-cluster baseline.
"""

import sys
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import numpy as np
import pandas as pd
from sklearn.cluster import HDBSCAN
from sklearn.metrics import silhouette_score, davies_bouldin_score


def eval_params(embeddings: np.ndarray, min_cluster_size: int) -> dict:
    hdb = HDBSCAN(min_cluster_size=min_cluster_size, min_samples=5, metric="euclidean", cluster_selection_method="eom")
    labels = hdb.fit_predict(embeddings)
    n_clusters = len(set(labels) - {-1})
    noise_count = int(np.sum(labels == -1))
    noise_ratio = round(noise_count / len(labels), 4)
    mask = labels != -1

    sil = None
    db = None
    if n_clusters >= 2 and mask.sum() > n_clusters:
        sil = round(float(silhouette_score(embeddings[mask], labels[mask], metric="euclidean")), 4)
        db = round(float(davies_bouldin_score(embeddings[mask], labels[mask])), 4)

    sizes = [int(np.sum(labels == c)) for c in set(labels) if c != -1]
    return {
        "min_cluster_size": min_cluster_size,
        "clusters_discovered": n_clusters,
        "clustered_samples": int(mask.sum()),
        "noise_samples": noise_count,
        "noise_ratio": noise_ratio,
        "silhouette_score_non_noise": sil,
        "davies_bouldin_index": db,
        "cluster_size_min": min(sizes) if sizes else 0,
        "cluster_size_median": float(np.median(sizes)) if sizes else 0.0,
        "cluster_size_max": max(sizes) if sizes else 0,
    }


def main():
    print("=" * 70)
    print("TRUSTLENS AI - PHASE 2.4: CLUSTER VALIDATION & STABILITY AUDIT")
    print("=" * 70)

    out_dir = Path("ml/artifacts/campaign_detection/v2.4_candidate")
    embeddings = np.load(out_dir / "threat_embeddings.npy")

    stability_runs = []
    for mcs in [20, 25, 35]:
        res = eval_params(embeddings, mcs)
        stability_runs.append(res)
        print(
            f"  min_cluster_size={mcs}: Clusters={res['clusters_discovered']} | "
            f"Noise={res['noise_ratio']:.2%} | Silhouette={res['silhouette_score_non_noise']} | DB={res['davies_bouldin_index']}"
        )

    # Load existing 47-cluster baseline report for objective comparison
    baseline_path = Path("ml/artifacts/campaign_detection/campaign_experiment_report.json")
    with open(baseline_path, "r", encoding="utf-8") as f:
        baseline_report = json.load(f)

    # Load dossiers to summarize duplicate concentration
    with open(out_dir / "campaign_dossiers.json", "r", encoding="utf-8") as f:
        dossiers = json.load(f)

    avg_dup_conc = round(float(np.mean([d["near_duplicate_concentration"] for d in dossiers])), 4) if dossiers else 0.0

    report = {
        "phase": "2.4",
        "embedding_model": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        "total_samples": int(embeddings.shape[0]),
        "primary_run_min_cluster_size_25": stability_runs[1],
        "stability_sweep": stability_runs,
        "average_near_duplicate_concentration": avg_dup_conc,
        "baseline_comparison_47_clusters": baseline_report.get("hdbscan_results", {}),
    }

    with open(out_dir / "evaluation_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"\nCluster validation report saved to {out_dir / 'evaluation_report.json'}")


if __name__ == "__main__":
    main()
