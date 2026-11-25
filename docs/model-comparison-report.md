# TRUSTLENS AI — TASK-SCOPED MODEL COMPARISON REPORT (DATASET v2.0.5)

> **Policy:** Models are compared strictly within their respective tasks using task-appropriate metrics on identical leak-free `dataset_version = 2.0.5` held-out test splits (`random_seed = 42`). Cross-task metric comparisons (e.g., URL accuracy vs. Text F1) are never performed.

---

## Task 1: Multilingual Text Scam Classification (`text_test.parquet`, `n = 8,590`, 4 Classes)

| Candidate Model | Accuracy | Macro F1 | Weighted F1 | ROC-AUC (OvR) | Threat FPR | Threat FNR | Latency | Size |
|---|---|---|---|---|---|---|---|---|
| `word_tfidf_logreg` | 0.9601 | 0.9394 | 0.9603 | 0.9929 | 0.0354 | 0.0263 | 0.0474 ms | 3.374 MB |
| `char_tfidf_logreg` | 0.9683 | 0.9510 | 0.9685 | 0.9958 | 0.0292 | **0.0209** | 0.2026 ms | 3.826 MB |
| **`union_tfidf_linearsvc` (Selected)** | **0.9783** | **0.9629** | **0.9783** | **0.9974** | **0.0139** | 0.0221 | 0.3166 ms | 10.184 MB |

---

## Task 2: Zero-Hop Phishing URL Classification (`urls_test.parquet`, `n = 14,411`, `9,076` Unseen Domains)

| Candidate Model | Accuracy | Precision | Recall | Macro F1 | ROC-AUC | PR-AUC | FPR | FNR | Latency | Size |
|---|---|---|---|---|---|---|---|---|---|---|
| `logistic_regression` | 0.9966 | **0.9992** | 0.9954 | 0.9964 | 0.9997 | 0.9999 | **0.0013** | 0.0046 | 0.00016 ms | 0.0009 MB |
| `random_forest` | 0.9970 | 0.9953 | 1.0000 | 0.9968 | 1.0000 | 1.0000 | 0.0081 | 0.0000 | 0.00772 ms | 2.3531 MB |
| **`xgboost_model` (Selected)** | **0.9990** | 0.9983 | **1.0000** | **0.9989** | **1.0000** | **1.0000** | 0.0028 | **0.0000** | 0.00261 ms | 0.2999 MB |

---

## Task 3: Multi-Label Social-Engineering Tactic Detection (`text_test.parquet` annotated, `n = 8,563`, 9 Labels)

| Candidate Model | Micro F1 | Macro F1 | Hamming Loss | Latency | Size |
|---|---|---|---|---|---|
| `ovr_logreg` | 0.9403 | 0.9386 | 0.0041 | 0.0075 ms | 5.499 MB |
| **`ovr_linearsvc` (Selected)** | **0.9566** | **0.9521** | **0.0030** | 0.0162 ms | 16.498 MB |

*(Note: `fake_investment` is `Blocked` across all candidates due to 0 training labels.)*

---

## Task 4: Unsupervised Campaign Similarity Clustering (`text_train.parquet` threats, `n = 5,488`)

| Configuration | Clusters | Clustered | Noise Ratio | Silhouette (Non-Noise) | Davies-Bouldin |
|---|---|---|---|---|---|
| `HDBSCAN(min_cluster_size=20)` | 53 | 2,445 | 55.45% | **0.3485** | **1.3768** |
| **`HDBSCAN(min_cluster_size=25)` (Primary)** | **43** | **2,468** | **55.03%** | 0.3163 | 1.3828 |
| `HDBSCAN(min_cluster_size=35)` | 34 | 2,370 | 56.81% | 0.2843 | 1.4890 |
