"""
TRUSTLENS AI - Model 4 Independent Campaign Benchmark
Benchmarks the 47 v1.0 clusters (all-MiniLM-L6-v2) vs 43 v2.4 clusters (paraphrase-multilingual-MiniLM-L12-v2)
against the independently held-out v2.0.5 test split (3,117 threat + 5,473 legitimate messages):
- Inter-centroid separation (mean & max pairwise centroid cosine similarity)
- Independent threat match coverage (high >= 0.70, moderate >= 0.50) by language
- False correlation rate on independent legitimate messages
"""

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import joblib
import numpy as np
import pandas as pd

from ml.campaign_detection.embeddings import get_shared_sentence_transformer


def benchmark_model(name: str, artifacts_path: Path, model_name: str, test_df: pd.DataFrame) -> dict:
    data = joblib.load(artifacts_path)
    centroids = data["centroids"]
    c_ids = sorted(centroids.keys())
    C = np.vstack([centroids[cid] for cid in c_ids]).astype(np.float32)
    # Ensure L2 normalized
    C = C / np.linalg.norm(C, axis=1, keepdims=True)

    # Inter-centroid separation
    sim_mat = np.dot(C, C.T)
    np.fill_diagonal(sim_mat, -1.0)
    max_inter_sim = float(sim_mat.max())
    upper_tri = sim_mat[np.triu_indices_from(sim_mat, k=1)]
    mean_inter_sim = float(upper_tri.mean())

    st = get_shared_sentence_transformer(model_name)
    # Sample 1,500 stratified test messages (including all Hindi & Hinglish) for fast CPU benchmarking
    hi = test_df[test_df["language"] == "Hindi"]
    hg = test_df[test_df["language"] == "Hinglish"]
    en_t = test_df[(test_df["language"] == "English") & (test_df["is_threat"] == 1)].sample(n=400, random_state=42)
    en_l = test_df[(test_df["language"] == "English") & (test_df["is_threat"] == 0)].sample(n=400, random_state=42)
    eval_df = pd.concat([hi, hg, en_t, en_l], ignore_index=True)

    embs = st.encode(eval_df["cleaned_text"].fillna("").tolist(), batch_size=64, normalize_embeddings=True, show_progress_bar=False)
    sims = np.dot(embs, C.T)
    max_sims = sims.max(axis=1)

    threat_mask = (eval_df["is_threat"] == 1).values
    legit_mask = (eval_df["is_threat"] == 0).values

    out = {
        "model": name,
        "embedding_model": model_name,
        "num_clusters": len(c_ids),
        "inter_centroid_mean_sim": round(mean_inter_sim, 4),
        "inter_centroid_max_sim": round(max_inter_sim, 4),
        "eval_samples": len(eval_df),
        "threat_samples": int(threat_mask.sum()),
        "legit_samples": int(legit_mask.sum()),
        "threat_high_match_rate_070": round(float((max_sims[threat_mask] >= 0.70).mean()), 4),
        "threat_moderate_plus_match_rate_050": round(float((max_sims[threat_mask] >= 0.50).mean()), 4),
        "legit_false_correlation_rate_070": round(float((max_sims[legit_mask] >= 0.70).mean()), 4),
        "legit_false_correlation_rate_050": round(float((max_sims[legit_mask] >= 0.50).mean()), 4),
        "by_language_threat_match_050": {},
    }
    for lang in ["English", "Hindi", "Hinglish"]:
        m = threat_mask & (eval_df["language"] == lang).values
        if m.sum() > 0:
            out["by_language_threat_match_050"][lang] = {
                "samples": int(m.sum()),
                "match_050": round(float((max_sims[m] >= 0.50).mean()), 4),
                "match_070": round(float((max_sims[m] >= 0.70).mean()), 4),
            }
    return out


def main():
    test_df = pd.read_parquet("data/processed/text_test.parquet")
    res_v1 = benchmark_model(
        "v1.0_47_clusters",
        Path("ml/artifacts/campaign_detection/cluster_artifacts.joblib"),
        "sentence-transformers/all-MiniLM-L6-v2",
        test_df,
    )
    res_v24 = benchmark_model(
        "v2.4_43_clusters",
        Path("ml/artifacts/campaign_detection/v2.4_candidate/cluster_artifacts.joblib"),
        "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        test_df,
    )
    report = {"v1.0_47_clusters": res_v1, "v2.4_43_clusters": res_v24}
    out_path = Path("ml/artifacts/campaign_detection/v2.4_candidate/independent_benchmark_report.json")
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
