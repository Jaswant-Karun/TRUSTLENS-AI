# TRUSTLENS AI — PHASE 2.0: CAMPAIGN CLUSTERING & DISCOVERY AUDIT (MODEL 4)

> **Directory Audited:** `ml/campaign_detection/` & `ml/artifacts/campaign_detection/`  
> **Audit Date:** November 25, 2026  

---

## 1. Clustering Pipeline & Embedding Model Audit

- **Source Records Clustered:** **5,715** verified threat messages from `data/processed/text_train.parquet` (filtered by `is_threat == 1` and `original_label != 'General Spam / Telemarketing'`).
- **Embedding Model:** `sentence-transformers/all-MiniLM-L6-v2` (384 dimensions, L2 unit-sphere normalized).
  - **CRITICAL MULTILINGUAL FINDING:** Despite documentation describing Model 4 as "Multilingual", `all-MiniLM-L6-v2` is predominantly an **English-trained model**. Cross-lingual Hindi/Devanagari and Hinglish clustering quality is limited compared to `paraphrase-multilingual-MiniLM-L12-v2`.
- **HDBSCAN Parameters (`clustering_config.json`):**
  - `min_cluster_size`: `25`
  - `min_samples`: `5`
  - `metric`: `euclidean` (equivalent to cosine ranking on L2-normalized vectors)
  - `cluster_selection_method`: `eom`
- **DBSCAN Baseline Parameters:** `eps=0.35`, `min_samples=15`, `metric='cosine'`.

---

## 2. Clustering Results & Reproducibility

| Algorithm | Samples | Clusters | Clustered Samples | Noise Samples (%) | Silhouette Score | Davies-Bouldin |
|---|---|---|---|---|---|---|
| **HDBSCAN (Selected)** | 5,715 | **47** | 2,814 | 2,901 (**50.76%**) | **0.3209** | **1.3339** |
| DBSCAN Baseline | 5,715 | 6 | 4,371 | 1,344 (23.52%) | 0.0292 | 2.1190 |

- **Metric Discrepancy Found:** `campaign_experiment_report.json` records `silhouette_score: 0.3209`, whereas `model_dashboard_data.json` / dashboard UI displays `0.449`. This discrepancy indicates stale/mismatched metadata in the dashboard summary JSON relative to the actual HDBSCAN experiment report.
- **Reproducibility:** **VERIFIED.** Precomputed embeddings are cached in `ml/artifacts/campaign_detection/threat_embeddings.npy` (8,778,368 bytes), and centroids/exemplars are persisted in `cluster_artifacts.joblib` (98,374 bytes) and `campaign_dossiers.json` (57,563 bytes).
- **Legal & Attribution Boundary:** Clusters denote unsupervised semantic and lexical overlap only; they do **not** establish forensically confirmed criminal organizations.

---

## 3. Integration with Persisted Analyses & Investigations
- **Runtime Inference:** Verified via `ml_engine.match_campaign(...)`. Incoming messages are encoded into 384-dim embeddings and matched via cosine similarity against the 47 persisted centroids (e.g., `campaign_id=43, sim=0.9207`).
- **Database Connection:** Persisted `analyses` documents in MongoDB store `campaign_association` results, and Phase 1.2 Investigations (`INV-2026-0011`, `INV-2026-0006`) materialize Cluster #11 and Cluster #06 directly into graph topologies.

---

## 4. Maturity Classification
- **Overall Status:** **PARTIAL** (Genuine HDBSCAN pipeline and artifacts exist and run inference cleanly, but embedding model is English-centric and dashboard Silhouette metric has a reporting discrepancy).
