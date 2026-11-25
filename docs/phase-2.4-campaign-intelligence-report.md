# TRUSTLENS AI — PHASE 2.4: MULTILINGUAL SCAM CAMPAIGN SIMILARITY & CLUSTER INTELLIGENCE REPORT

> **Dataset Version:** `2.0.5` (`text_train.parquet` filtered to `smishing` + `scam`, `n = 5,488`)  
> **Candidate Artifacts Directory:** `ml/artifacts/campaign_detection/v2.4_candidate/` *(Existing 47-cluster artifacts preserved untouched)*  
> **Scripts Created:** `ml/campaign_detection/embed.py`, `cluster.py`, `evaluate.py`, `search.py`  
> **Date:** November 25, 2026

---

## 1. Existing Model & Artifact Audit (Preserved Untouched)

| Existing Artifact (`ml/artifacts/campaign_detection/`) | Size (bytes) | SHA-256 |
|---|---|---|
| `threat_embeddings.npy` | 8,778,368 | `2fb0c47188563e07858bca97ec57a36c7c1996f4a897389e32d04712f9db638f` |
| `cluster_artifacts.joblib` | 98,374 | `67813bb12e3b81870d17ad2b90fce97b90af8a2f5ef9f4a4f4dc7ccfec774448` |
| `campaign_dossiers.json` | 57,563 | `7feb42e02359448fc506e0d21f26f5abbc3f34fa1fde43dab21886cc1ea4e6d7` |
| `campaign_experiment_report.json` | 2,065 | `ef89122b220a267ffef58cd052c12e98e2b9d018cd6a986b71411ef96f23047b` |
| `clustering_config.json` | 290 | `2dab2ad7d2ab006cef2e6b83cae42fa3a4c9170f33e2b7dcc55cbb2948fbf7d6` |
| `embedding_config.json` | 163 | `a5d9adab7a26c8023ad9679bdaa26212f019e3ea155a500de1fdc84d8671d870` |
| `campaign_clusters_2d.png` | 729,887 | `80ebe95c63bb323ba319b314c65ad8598a65ed10e0f80aae05cfcc8d6673f93e` |

- **Baseline Model:** `sentence-transformers/all-MiniLM-L6-v2` (384-dim, English-centric), HDBSCAN (`min_cluster_size=25, min_samples=5`), `5,715` samples -> **47 clusters**, `50.76%` noise, Silhouette `0.3209`, Davies-Bouldin `1.3339`.

---

## 2. Multilingual Embedding & Clustering Validation (`v2.4_candidate`)

- **Embedding Model:** `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (384 dimensions, L2 unit-sphere normalized, cosine metric).
- **Source Corpus (`n = 5,488`):** `3,443` `smishing` + `2,045` `scam` from leak-free `text_train.parquet` (`4,701` English, `400` Hindi, `387` Hinglish; `5,094` unique `text_group_id`s).
- **Encoding Time:** `161.14s` on Intel i5-12450H CPU (`batch_size=64`).

### Objective Comparison vs. Existing 47-Cluster Baseline

| Run / Parameter | Samples | Clusters | Clustered | Noise (%) | Silhouette (Non-Noise) | Davies-Bouldin |
|---|---|---|---|---|---|---|
| Existing Baseline (`all-MiniLM-L6-v2`, mcs=25) | 5,715 | **47** | 2,814 | 50.76% | **0.3209** | **1.3339** |
| **v2.4 (`paraphrase-multilingual`, mcs=25)** | 5,488 | **43** | 2,468 | 55.03% | 0.3163 | 1.3828 |
| v2.4 Stability (`min_cluster_size=20`) | 5,488 | 53 | 2,445 | 55.45% | 0.3485 | 1.3768 |
| v2.4 Stability (`min_cluster_size=35`) | 5,488 | 34 | 2,370 | 56.81% | 0.2843 | 1.4890 |

- **Cluster Size Distribution (`mcs=25`):** Min `25` | Median `41.0` | Max `250`.
- **Average Near-Duplicate Concentration:** `0.1608` (`16.08%` template overlap within clusters; e.g., Cluster #30 has `0.4%` concentration, whereas Cluster #41 SBI YONO PAN lures has `36.24%`).
- **Objective Assessment:** The multilingual embedding model does **not** automatically outperform the English-centric baseline on raw Silhouette (`0.3163` vs `0.3209`) or noise ratio (`55.03%` vs `50.76%`), because multilingual embedding spaces disperse cross-lingual variations slightly more widely. However, `search.py` demonstrates accurate cross-lingual Hinglish nearest-neighbor retrieval (`sim=0.6853` for `"Aapka SBI khata band ho jayega..."`).

---

## 3. Campaign Intelligence Dossier Schema & Governance

Every generated cluster in `v2.4_candidate/campaign_dossiers.json` includes:
- `cluster_id`, `record_count`, `unique_text_groups`, `near_duplicate_concentration`
- `similarity_evidence` (`mean_cosine_similarity`, `min_cosine_similarity`)
- `representative_examples`, `shared_indicators` (`top_domains`, `top_urls`, `top_phones`, `top_upis`)
- `source_records_sample_ids`, `language_distribution`
- `review_status`: `"Candidate similarity cluster — Under review"`
- `embedding_model_version` & `clustering_version`
- **Mandatory Attribution Disclaimer:**
  > *"Candidate Similarity Cluster: Grouping reflects mathematical and linguistic embedding similarity only; it does not confirm a shared criminal organization or coordinated threat actor."*

> **Stop Condition Honored:** Reproducible clustering, stability validation, and nearest-neighbor retrieval are complete. Existing artifacts were preserved untouched.
