# TRUSTLENS AI — MODEL CARD TEMPLATE

## 1. Model Details
- **Model ID:** `<trustlens-track-version>`
- **Model Name:** `<Human-readable display name>`
- **Version:** `<Semantic version>`
- **Task:** `<text_classification | url_phishing_classification | multilabel_tactic_detection | unsupervised_campaign_clustering>`
- **Architecture:** `<Algorithm & hyperparameter summary>`
- **Artifact Path & SHA-256:** `<Path and cryptographic hash>`
- **Deployment Status:** `<Development | Evaluated | Approved | Production | Deprecated | Blocked>`

## 2. Intended Use & Scope
- **Primary Use Case:** `<What threat intelligence task this model performs>`
- **Supported Languages / Inputs:** `<Explicitly validated languages/input formats>`
- **Out-of-Scope Uses:** `<Uses that are unsafe or unsupported>`

## 3. Training & Evaluation Data
- **Dataset Version:** `<e.g., 2.0.5>`
- **Split Methodology:** `<e.g., StratifiedGroupKFold on text_group_id / domain_group_id, seed=42>`
- **Train / Validation / Test Counts:** `<Exact sample counts>`
- **Label Mapping:** `<Exact mapping from original labels to canonical labels>`

## 4. Quantitative Evaluation Metrics (Task-Appropriate)
- **Primary Metrics:** `<Macro F1, ROC-AUC, PR-AUC, Hamming Loss, or Silhouette/Davies-Bouldin>`
- **Error Rates & Latency:** `<FPR, FNR, ms/sample, artifact MB>`
- **Subgroup / Language Breakdown:** `<Per-language or per-TLD generalization metrics>`

## 5. Explainability & Limitations
- **Attribution Method:** `<e.g., Linear hyperplane weights * TF-IDF, SHAP TreeExplainer, Cosine similarity>`
- **Known Limitations & Biases:** `<Explicit performance gaps, unsupported languages, or blocked labels>`
- **Safety / Attribution Disclaimer:** `<e.g., Lexical URL score does not prove malice/safety; clusters do not prove criminal origin>`
