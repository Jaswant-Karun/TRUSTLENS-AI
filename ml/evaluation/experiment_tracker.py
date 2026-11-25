"""
TRUSTLENS AI - Phase 2.5: Reproducible Experiment Tracker
Aggregates all Phase 2.1-2.4 experiment runs strictly keyed by dataset_version (2.0.5)
and task, ensuring zero cross-dataset mixing.
"""

import json
from pathlib import Path
from datetime import datetime, timezone


def main():
    manifest = json.loads(Path("data/processed/dataset_manifest.json").read_text(encoding="utf-8"))

    text_eval = json.loads(Path("ml/artifacts/text_detection/v2.1_candidate/evaluation_report.json").read_text(encoding="utf-8"))
    text_meta = json.loads(Path("ml/artifacts/text_detection/v2.1_candidate/training_metadata.json").read_text(encoding="utf-8"))

    url_eval = json.loads(Path("ml/artifacts/url_detection/v2.2_candidate/evaluation_report.json").read_text(encoding="utf-8"))
    url_meta = json.loads(Path("ml/artifacts/url_detection/v2.2_candidate/training_metadata.json").read_text(encoding="utf-8"))

    tac_eval = json.loads(Path("ml/artifacts/tactic_detection/v2.3_candidate/evaluation_report.json").read_text(encoding="utf-8"))
    tac_meta = json.loads(Path("ml/artifacts/tactic_detection/v2.3_candidate/training_metadata.json").read_text(encoding="utf-8"))

    camp_eval = json.loads(Path("ml/artifacts/campaign_detection/v2.4_candidate/evaluation_report.json").read_text(encoding="utf-8"))

    experiments = []

    # 1. Text experiments
    for exp in text_eval["experiments"]:
        k = exp["model_key"]
        experiments.append({
            "experiment_id": f"exp-2.1-{k}",
            "task": "text_classification",
            "dataset_version": "2.0.5",
            "random_seed": 42,
            "splits": {"train": text_meta["train_samples"], "val": text_meta["val_samples"], "test": text_eval["test_samples"]},
            "dataset_hash_test": manifest["processed_files"]["text_test.parquet"]["sha256"],
            "model_configuration": exp["display_name"],
            "training_duration_sec": text_meta["models"][k]["train_duration_seconds"],
            "evaluation_metrics": {
                "accuracy": exp["accuracy"],
                "macro_f1": exp["macro_f1"],
                "weighted_f1": exp["weighted_f1"],
                "roc_auc_ovr_macro": exp["roc_auc_ovr_macro"],
                "threat_fpr": exp["threat_false_positive_rate"],
                "threat_fnr": exp["threat_false_negative_rate"],
            },
            "artifact_location": f"ml/artifacts/text_detection/v2.1_candidate/{k}_model.joblib",
        })

    # 2. URL experiments
    for exp in url_eval["experiments"]:
        k = exp["model_key"]
        experiments.append({
            "experiment_id": f"exp-2.2-{k}",
            "task": "url_phishing_classification",
            "dataset_version": "2.0.5",
            "random_seed": 42,
            "splits": {"train": url_meta["train_samples"], "val": url_meta["val_samples"], "test": url_eval["test_samples"]},
            "dataset_hash_test": manifest["processed_files"]["urls_test.parquet"]["sha256"],
            "model_configuration": exp["display_name"],
            "training_duration_sec": url_meta["models"][k]["train_duration_seconds"],
            "evaluation_metrics": {
                "accuracy": exp["accuracy"],
                "macro_f1": exp["macro_f1"],
                "roc_auc": exp["roc_auc"],
                "pr_auc": exp["pr_auc"],
                "fpr": exp["false_positive_rate"],
                "fnr": exp["false_negative_rate"],
            },
            "artifact_location": f"ml/artifacts/url_detection/v2.2_candidate/{k}.joblib",
        })

    # 3. Tactic experiments
    for exp in tac_eval["experiments"]:
        k = exp["model_key"]
        experiments.append({
            "experiment_id": f"exp-2.3-{k}",
            "task": "multilabel_tactic_detection",
            "dataset_version": "2.0.5",
            "random_seed": 42,
            "splits": {"train": tac_meta["train_samples"], "val": tac_meta["val_samples"], "test": tac_eval["test_samples"]},
            "dataset_hash_test": manifest["processed_files"]["text_test.parquet"]["sha256"],
            "model_configuration": exp["display_name"],
            "training_duration_sec": tac_meta["models"][k]["train_duration_seconds"],
            "evaluation_metrics": {
                "micro_f1": exp["micro_f1"],
                "macro_f1": exp["macro_f1"],
                "hamming_loss": exp["hamming_loss"],
            },
            "artifact_location": f"ml/artifacts/tactic_detection/v2.3_candidate/{k}.joblib",
        })

    # 4. Campaign experiments (stability sweep)
    for run in camp_eval["stability_sweep"]:
        mcs = run["min_cluster_size"]
        experiments.append({
            "experiment_id": f"exp-2.4-hdbscan-mcs{mcs}",
            "task": "unsupervised_campaign_clustering",
            "dataset_version": "2.0.5",
            "random_seed": 42,
            "splits": {"train_threat_subset": camp_eval["total_samples"]},
            "dataset_hash_train": manifest["processed_files"]["text_train.parquet"]["sha256"],
            "model_configuration": f"paraphrase-multilingual-MiniLM-L12-v2 + HDBSCAN(mcs={mcs})",
            "evaluation_metrics": {
                "clusters": run["clusters_discovered"],
                "noise_ratio": run["noise_ratio"],
                "silhouette_score": run["silhouette_score_non_noise"],
                "davies_bouldin": run["davies_bouldin_index"],
            },
            "artifact_location": "ml/artifacts/campaign_detection/v2.4_candidate/cluster_artifacts.joblib",
        })

    out_path = Path("ml/evaluation/experiments_v2.json")
    payload = {
        "tracker_version": "2.5.0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "total_experiments": len(experiments),
        "experiments": experiments,
    }
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Tracked {len(experiments)} experiments -> {out_path}")


if __name__ == "__main__":
    main()
