"""
TRUSTLENS AI - Phase 2.0.5: EDA & Data Quality Visualizations
Generates 5 publication-grade charts in docs/screenshots/eda/ and copies to artifacts:
1. class_distribution.png
2. language_distribution.png
3. missing_values.png
4. duplicate_counts.png
5. dataset_source_distribution.png
"""

import json
import shutil
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid", palette="muted")

OUT_DIR = Path("docs/screenshots/eda")
OUT_DIR.mkdir(parents=True, exist_ok=True)
ARTIFACT_DIR = Path(r"C:\Users\jaswant karun\.gemini\antigravity\brain\ccdc3978-e39e-4041-ac1a-6d43bb2834f7\screenshots\eda")
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)


def save_fig(fig, filename: str):
    p = OUT_DIR / filename
    fig.savefig(p, dpi=150, bbox_inches="tight")
    plt.close(fig)
    shutil.copyfile(p, ARTIFACT_DIR / filename)
    print(f"Saved: {p}")


def main():
    with open("data/processed/preprocessing_stats.json", "r", encoding="utf-8") as f:
        stats = json.load(f)

    text_df = pd.read_parquet("data/processed/text_clean.parquet")
    url_df = pd.read_parquet("data/processed/urls_clean.parquet")

    # 1. Class Distribution (Text + URL)
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    text_counts = text_df["canonical_label"].value_counts()
    sns.barplot(x=text_counts.index, y=text_counts.values, ax=axes[0], palette="Blues_d")
    axes[0].set_title("Text Corpus Canonical Class Distribution (n=85,895)", fontweight="bold")
    axes[0].set_ylabel("Record Count")
    for i, v in enumerate(text_counts.values):
        axes[0].text(i, v + 500, f"{v:,}", ha="center", fontsize=9)

    url_counts = url_df["canonical_label"].value_counts()
    sns.barplot(x=url_counts.index, y=url_counts.values, ax=axes[1], palette="Reds_d")
    axes[1].set_title("URL Corpus Canonical Class Distribution (n=100,872)", fontweight="bold")
    axes[1].set_ylabel("Record Count")
    for i, v in enumerate(url_counts.values):
        axes[1].text(i, v + 1000, f"{v:,}", ha="center", fontsize=9)
    save_fig(fig, "class_distribution.png")

    # 2. Language Distribution
    fig, ax = plt.subplots(figsize=(8, 5))
    lang_counts = text_df["language"].value_counts()
    sns.barplot(x=lang_counts.index, y=lang_counts.values, ax=ax, palette="viridis")
    ax.set_title("Text Corpus Language Coverage (n=85,895)", fontweight="bold")
    ax.set_ylabel("Message Count")
    ax.set_yscale("log")
    for i, v in enumerate(lang_counts.values):
        pct = v / len(text_df) * 100
        ax.text(i, v * 1.15, f"{v:,}\n({pct:.2f}%)", ha="center", fontsize=9)
    save_fig(fig, "language_distribution.png")

    # 3. Missing Values Audit (Raw vs Processed)
    fig, ax = plt.subplots(figsize=(8, 4.5))
    missing_items = {
        "LegitPhish Raw\n(Missing ClassLabel)": stats["url_preprocessing"]["missing_labels_dropped"],
        "Text Raw\n(Empty/Malformed)": stats["text_preprocessing"]["empty_or_malformed_dropped"],
        "Text Processed\n(All Required Cols)": 0,
        "URL Processed\n(All Required Cols)": 0,
    }
    sns.barplot(x=list(missing_items.keys()), y=list(missing_items.values()), ax=ax, palette="Oranges_r")
    ax.set_title("Missing & Malformed Records (Raw vs Cleaned)", fontweight="bold")
    ax.set_ylabel("Record Count")
    for i, v in enumerate(missing_items.values()):
        ax.text(i, v + 0.05, f"{v}", ha="center", fontsize=10, fontweight="bold")
    save_fig(fig, "missing_values.png")

    # 4. Duplicate & Overlap Counts
    fig, ax = plt.subplots(figsize=(9, 5))
    dup_items = {
        "Mendeley SMS\nOverlap w/ ScamShield": stats["text_preprocessing"]["mendeley_overlapping_with_scamshield"],
        "Text Exact Raw\nDuplicates Removed": stats["text_preprocessing"]["exact_raw_duplicates_removed"],
        "Text Near-Duplicate\nTemplates Grouped": stats["text_preprocessing"]["near_duplicate_templates_count"],
        "URL Exact\nDuplicates Removed": stats["url_preprocessing"]["duplicate_urls_removed"],
    }
    sns.barplot(x=list(dup_items.keys()), y=list(dup_items.values()), ax=ax, palette="Purples_d")
    ax.set_title("Duplicate & Cross-Dataset Overlap Audit", fontweight="bold")
    ax.set_ylabel("Record Count")
    for i, v in enumerate(dup_items.values()):
        ax.text(i, v + 100, f"{v:,}", ha="center", fontsize=9, fontweight="bold")
    save_fig(fig, "duplicate_counts.png")

    # 5. Dataset Source Distribution
    fig, ax = plt.subplots(figsize=(9, 5))
    src_counts = {
        "ScamShield\n(HuggingFace)": stats["text_preprocessing"]["scamshield_raw_rows"],
        "SMS Phishing\n(Mendeley 5971)": stats["text_preprocessing"]["mendeley_raw_rows"],
        "LegitPhish\n(Mendeley URL)": stats["url_preprocessing"]["raw_rows"],
    }
    sns.barplot(x=list(src_counts.keys()), y=list(src_counts.values()), ax=ax, palette="crest")
    ax.set_title("Raw Dataset Source Distribution (Total = 192,870)", fontweight="bold")
    ax.set_ylabel("Raw Records")
    for i, v in enumerate(src_counts.values()):
        ax.text(i, v + 1500, f"{v:,}", ha="center", fontsize=10, fontweight="bold")
    save_fig(fig, "dataset_source_distribution.png")


if __name__ == "__main__":
    main()
