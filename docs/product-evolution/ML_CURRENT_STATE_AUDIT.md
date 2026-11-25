# TRUSTLENS AI — MACHINE LEARNING CURRENT STATE AUDIT

> **Phase:** 3.0 Audit (No Retraining Performed)  
> **Sources Inspected:** `ml/artifacts/model_registry.json`, `ml/artifacts/*/model_metadata.json`, `ml/artifacts/*/*experiment_report.json`, `data/dataset_manifest.json`, `docs/audit/ML_AUDIT.md`, `docs/audit/PHASE_0_5_FINAL_REPORT.md`

---

## 1. Model-by-Model Forensic Audit

### Model 1: Multilingual Digital Scam Message Detector (`trustlens-model-1-text-scam`)
1. **Actual Training Data:** `ScamShield` (`sidzzz07/scamshield-dataset`, MIT) + `SMS Phishing Dataset` (`10.17632/f45bkkt8pr.1`, CC BY 4.0) combined into `data/processed/text_train.parquet` (`69,501` train / `8,202` test).
2. **Licensing:** MIT + CC BY 4.0 (compatible with commercial & open-source use with attribution).
3. **Language Coverage:** English (`n=7,668` test), Hindi Devanagari (`n=460` test), Hinglish (`n=74` test). **Registry Discrepancy Found:** `ml/artifacts/model_registry.json` still lists `"Bengali"` and `"Tamil"`, whereas `ml/artifacts/text_detection/model_metadata.json` explicitly states: *"Tamil is NOT claimed as supported because the evaluated dataset does not contain Tamil records."*
4. **Label Distribution & Split:** `StratifiedGroupKFold` grouped by `text_group_id` to prevent near-duplicate leakage. Heavily skewed toward English (`93.5%` of test set).
5. **Training Methodology:** FeatureUnion (Word TF-IDF 1–3 n-grams + Char TF-IDF 2–5 n-grams, `max_features=100,000`) + `LinearSVC` with 3-fold Platt scaling calibration.
6. **Evaluation Metrics:** Overall (`n=8,202`): Accuracy `0.9777`, Macro F1 `0.9760`, ROC-AUC `0.9960`, Brier `0.0178`, FPR `0.0168`.
7. **Known Limitations (Critical):**
   - **Hindi Recall = `0.5455` (`n=460`):** Severe under-recall on Devanagari Hindi compared to English (`0.9690`), driven by class/language imbalance (`460` vs `7,668`) and TF-IDF vocabulary sparsity across Devanagari script.
   - **Bengali/Tamil Unverified:** Listed in `model_registry.json` without test support.
8. **Production Readiness:** Ready for **English & Hinglish**; **Conditional / Limited for Hindi** until multilingual data balancing and transformer/char-level remediation are completed.

### Model 2: Lexical & Structural Phishing URL Detector (`trustlens-model-2-phishing-url`)
1. **Actual Training Data:** `LegitPhish` (`10.17632/hx4m73v2sf.2`, CC BY 4.0, `101,219` URLs). Split into `70,610` train / `15,131` test via `StratifiedGroupKFold` (`domain_group_id`).
2. **Training Methodology:** XGBoost (`n_estimators=200`, `max_depth=6`, `lr=0.1`) over 16 zero-hop lexical/structural features + SHAP `TreeExplainer`.
3. **Evaluation Metrics:** Benchmark (`n=15,131`): Accuracy `0.9998`, F1 `0.9998`, ROC-AUC `1.0000`. **However**, Phase 5.0 held-out `urls_test.parquet` spot check (`n=300`) recorded Accuracy `0.9233`, **23 False Positives (`FPR = 15.33%`)**, 0 False Negatives.
4. **Known Limitations (Critical):**
   - **15.33% False-Positive Rate:** Benchmark `0.9998` reflects `LegitPhish` distribution homogeneity (e.g., `https_flag`, `path_length`, `tld_popularity` shortcuts). Modern legitimate SaaS/CDN/tracking URLs with long query paths or non-`.com` TLDs trigger false positives.
   - **Zero-Hop Only:** Intentionally does not inspect live DNS/WHOIS/TLS/HTML, which protects user/server safety but limits detection of compromised legitimate domains.
5. **Production Readiness:** **Needs Calibration & Benign URL Expansion** before consumer/Play Store launch to bring FPR below `2%` on modern web URLs.

### Model 3: Multi-Label Social Engineering Tactic Detector (`trustlens-model-3-tactic-detector`)
1. **Training Data & Methodology:** `69,286` train / `8,192` val / `8,202` test from ScamShield multi-head annotations; One-vs-Rest Calibrated `LinearSVC` with per-label threshold tuning (`ml/artifacts/tactic_detection/thresholds.json`).
2. **Evaluation Metrics:** Micro F1 `0.9513`, Macro F1 `0.9313`, Hamming Loss `0.0039` across `9` active tactics.
3. **Known Limitations:** `fake_investment` is explicitly marked `UNAVAILABLE` (zero verified ground-truth positives). Also inherits Hindi recall weakness from TF-IDF representation.
4. **Production Readiness:** **Production Ready** for the 9 supported tactics in English/Hinglish.

### Model 4: Scam Campaign Similarity & Clustering (`ml/artifacts/campaign_detection/`)
1. **Data & Methodology:** `paraphrase-multilingual-MiniLM-L12-v2` embeddings + `HDBSCAN` (`min_cluster_size=25`, `min_samples=5`) over `5,715` threat samples.
2. **Metrics:** `47` clusters discovered, `2,901` noise (`50.76%`), Silhouette `0.3209`, Davies-Bouldin `1.3339` (outperforming DBSCAN `0.0292`).
3. **Known Limitations:** Unsupervised linguistic/IOC similarity only; **never constitutes legal proof of common criminal attribution**. Static `campaign_dossiers.json` requires periodic re-clustering as new threats arrive.
4. **Production Readiness:** **Production Ready** (synced to MongoDB `scam_campaigns` in Phase 2.4).

---

## 2. Inference Architecture & Memory Status

- **Real Inference Confirmed:** All predictions come from SHA-256-verified `.joblib` / `SentenceTransformer` artifacts in `CentralModelLoader`.
- **Singleton Remediation Verified (Phase 0.5):** `get_shared_sentence_transformer()` reduced Python RSS from `958.96 MB` to `750.12 MB` (`-21.8%`).
- **Hosting Constraint:** `render.yaml` requires `plan: standard` (`2 GB RAM`) because `750+ MB` RSS exceeds 512 MB starter tiers.
