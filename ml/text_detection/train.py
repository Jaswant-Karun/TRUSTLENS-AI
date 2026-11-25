"""
TRUSTLENS AI - Phase 2.1: Multilingual Text Scam Detection Training Pipeline
Trains 3 reproducible baseline pipelines on leak-free group-aware splits:
1. Word TF-IDF (1-2) + Logistic Regression (balanced)
2. Char_wb TF-IDF (3-5) + Logistic Regression (balanced)
3. FeatureUnion (Word + Char_wb TF-IDF) + Calibrated LinearSVC (balanced)

Saves all artifacts under ml/artifacts/text_detection/v2.1_candidate/
without overwriting existing production artifacts.
"""

import os
import sys
import json
import time
import shutil
import hashlib
from pathlib import Path
from datetime import datetime, timezone

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import yaml
import joblib
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import FeatureUnion
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import accuracy_score, f1_score


def compute_sha256(filepath: Path) -> str:
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def build_vectorizer(model_key: str, cfg: dict):
    if model_key == "word_tfidf_logreg":
        return TfidfVectorizer(
            ngram_range=tuple(cfg["word_ngram_range"]),
            max_features=cfg["max_features"],
            sublinear_tf=cfg["sublinear_tf"],
            strip_accents=None,  # Preserve Devanagari diacritics
        )
    elif model_key == "char_tfidf_logreg":
        return TfidfVectorizer(
            analyzer="char_wb",
            ngram_range=tuple(cfg["char_ngram_range"]),
            max_features=cfg["max_features"],
            sublinear_tf=cfg["sublinear_tf"],
        )
    elif model_key == "union_tfidf_linearsvc":
        return FeatureUnion([
            (
                "word_tfidf",
                TfidfVectorizer(
                    ngram_range=tuple(cfg["word_ngram_range"]),
                    max_features=cfg["word_max_features"],
                    sublinear_tf=cfg["sublinear_tf"],
                    strip_accents=None,
                ),
            ),
            (
                "char_tfidf",
                TfidfVectorizer(
                    analyzer="char_wb",
                    ngram_range=tuple(cfg["char_ngram_range"]),
                    max_features=cfg["char_max_features"],
                    sublinear_tf=cfg["sublinear_tf"],
                ),
            ),
        ])
    else:
        raise ValueError(f"Unknown model_key: {model_key}")


def build_classifier(model_key: str, cfg: dict, seed: int):
    if model_key in ("word_tfidf_logreg", "char_tfidf_logreg"):
        return LogisticRegression(
            C=cfg["C"],
            class_weight=cfg["class_weight"],
            max_iter=cfg["max_iter"],
            random_state=seed,
            solver="lbfgs",
        )
    elif model_key == "union_tfidf_linearsvc":
        base_svc = LinearSVC(
            C=cfg["C"],
            class_weight=cfg["class_weight"],
            max_iter=cfg["max_iter"],
            random_state=seed,
        )
        return CalibratedClassifierCV(
            estimator=base_svc,
            method="sigmoid",
            cv=cfg.get("calibration_cv", 3),
        )
    else:
        raise ValueError(f"Unknown model_key: {model_key}")


def main():
    print("=" * 70)
    print("TRUSTLENS AI - PHASE 2.1: TEXT SCAM DETECTION MODEL TRAINING")
    print("=" * 70)

    config_path = Path("ml/text_detection/config.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    seed = int(config["random_seed"])
    out_dir = Path(config["artifacts"]["output_dir"])
    out_dir.mkdir(parents=True, exist_ok=True)

    label_map = {int(k): v for k, v in config["labels"].items()}
    inv_label_map = {v: k for k, v in label_map.items()}

    # 1. Load Train and Validation Splits ONLY (Keep Test isolated)
    print("\n[1/3] Loading Train and Validation Splits...")
    train_df = pd.read_parquet(config["dataset"]["train_path"])
    val_df = pd.read_parquet(config["dataset"]["val_path"])

    text_col = config["dataset"]["text_column"]
    lbl_col = config["dataset"]["label_column"]

    X_train_raw = train_df[text_col].fillna("").tolist()
    y_train = train_df[lbl_col].map(inv_label_map).astype(int).values

    X_val_raw = val_df[text_col].fillna("").tolist()
    y_val = val_df[lbl_col].map(inv_label_map).astype(int).values

    print(f"  Train samples: {len(X_train_raw):,} | Val samples: {len(X_val_raw):,}")
    print(f"  Classes: {label_map}")

    # Save label mapping and config copy
    with open(out_dir / "label_mapping.json", "w", encoding="utf-8") as f:
        json.dump(label_map, f, indent=2)
    shutil.copyfile(config_path, out_dir / "config.yaml")

    # 2. Train each baseline pipeline
    print("\n[2/3] Training Reproducible Baselines...")
    trained_summary = {}
    artifact_hashes = {}

    for model_key, m_cfg in config["models"].items():
        print(f"\n  -> Training {m_cfg['display_name']} ({model_key})...")
        t0 = time.perf_counter()

        vectorizer = build_vectorizer(model_key, m_cfg)
        X_train_vec = vectorizer.fit_transform(X_train_raw)
        X_val_vec = vectorizer.transform(X_val_raw)

        clf = build_classifier(model_key, m_cfg, seed)
        clf.fit(X_train_vec, y_train)
        train_sec = round(time.perf_counter() - t0, 2)

        # Validation check
        y_val_pred = clf.predict(X_val_vec)
        val_acc = round(float(accuracy_score(y_val, y_val_pred)), 4)
        val_f1_mac = round(float(f1_score(y_val, y_val_pred, average="macro", zero_division=0)), 4)

        vec_path = out_dir / f"{model_key}_vectorizer.joblib"
        mod_path = out_dir / f"{model_key}_model.joblib"
        joblib.dump(vectorizer, vec_path)
        joblib.dump(clf, mod_path)

        vec_mb = round(vec_path.stat().st_size / (1024 * 1024), 3)
        mod_mb = round(mod_path.stat().st_size / (1024 * 1024), 3)

        artifact_hashes[vec_path.name] = compute_sha256(vec_path)
        artifact_hashes[mod_path.name] = compute_sha256(mod_path)

        trained_summary[model_key] = {
            "display_name": m_cfg["display_name"],
            "train_duration_seconds": train_sec,
            "val_accuracy": val_acc,
            "val_macro_f1": val_f1_mac,
            "vectorizer_size_mb": vec_mb,
            "model_size_mb": mod_mb,
            "total_artifact_size_mb": round(vec_mb + mod_mb, 3),
        }
        print(
            f"     Done in {train_sec}s | Val Acc: {val_acc:.4f} | Val Macro F1: {val_f1_mac:.4f} "
            f"| Size: {vec_mb + mod_mb:.2f} MB"
        )

    # 3. Save Training Metadata
    print("\n[3/3] Writing Training Metadata...")
    metadata = {
        "phase": "2.1",
        "dataset_version": config["dataset"]["version"],
        "random_seed": seed,
        "train_samples": len(X_train_raw),
        "val_samples": len(X_val_raw),
        "labels": label_map,
        "trained_at_utc": datetime.now(timezone.utc).isoformat(),
        "models": trained_summary,
        "artifact_sha256": artifact_hashes,
    }
    with open(out_dir / "training_metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print(f"Training artifacts saved to {out_dir}")


if __name__ == "__main__":
    main()
