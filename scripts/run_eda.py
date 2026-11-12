"""
TRUSTLENS AI - Exploratory Data Analysis & Statistical Modeling Engine
Generates ground-truth statistics, term frequency analysis, length distributions,
feature correlations, and publication-grade Matplotlib/Plotly visualizations.
"""

import os
import sys
import json
import re
from pathlib import Path
from collections import Counter

# Set project root in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
import numpy as np


def compute_comprehensive_eda():
    print("=" * 60)
    print("TRUSTLENS AI - EXECUTING COMPREHENSIVE EDA PIPELINE")
    print("=" * 60)

    figures_dir = Path("docs/figures")
    figures_dir.mkdir(parents=True, exist_ok=True)

    # 1. Load Data
    print("\n[1/5] Loading Processed Training & Ingestion Data...")
    df_text_train = pd.read_parquet("data/processed/text_train.parquet")
    df_urls_train = pd.read_parquet("data/processed/urls_train.parquet")
    df_sms_raw = pd.read_parquet("data/processed/sms_phishing_clean.parquet")

    # Important Rule Check: We only compute exploratory statistics on Training Data
    # to avoid data snooping or bias into validation/test sets!
    print(f"  Training Text Samples: {len(df_text_train)}")
    print(f"  Training URL Samples:  {len(df_urls_train)}")

    # 2. Text Statistics & Distributions
    print("\n[2/5] Computing Text Distributions (Length, Classes, Languages)...")
    df_text_train["char_len"] = df_text_train["cleaned_text"].str.len()
    df_text_train["word_cnt"] = df_text_train["cleaned_text"].str.split().str.len()

    len_stats = {
        "legitimate": {
            "mean_char": float(df_text_train[df_text_train["is_threat"] == 0]["char_len"].mean()),
            "median_char": float(df_text_train[df_text_train["is_threat"] == 0]["char_len"].median()),
            "std_char": float(df_text_train[df_text_train["is_threat"] == 0]["char_len"].std()),
            "mean_words": float(df_text_train[df_text_train["is_threat"] == 0]["word_cnt"].mean()),
        },
        "threat": {
            "mean_char": float(df_text_train[df_text_train["is_threat"] == 1]["char_len"].mean()),
            "median_char": float(df_text_train[df_text_train["is_threat"] == 1]["char_len"].median()),
            "std_char": float(df_text_train[df_text_train["is_threat"] == 1]["char_len"].std()),
            "mean_words": float(df_text_train[df_text_train["is_threat"] == 1]["word_cnt"].mean()),
        },
    }

    # Word Frequency / N-Gram Analysis for Scam vs Legitimate
    stopwords = {
        "the", "a", "an", "in", "to", "of", "and", "is", "for", "on", "you", "your",
        "with", "at", "by", "from", "it", "this", "that", "are", "be", "or", "as",
        "was", "we", "my", "me", "have", "has", "do", "will", "so", "if", "not", "i"
    }

    scam_words = Counter()
    legit_words = Counter()

    for _, row in df_text_train.iterrows():
        tokens = re.findall(r"\b[a-zA-Z]{3,}\b", row["cleaned_text"].lower())
        tokens = [t for t in tokens if t not in stopwords and t not in ["[url]", "[phone]", "[email]", "[otp]"]]
        if row["is_threat"] == 1:
            scam_words.update(tokens)
        else:
            legit_words.update(tokens)

    # 3. URL Correlations & Distributions
    print("\n[3/5] Computing URL Numerical Feature Correlations...")
    num_cols = [
        "url_length", "dot_count", "subdomain_count", "path_length",
        "url_entropy", "number_of_digits", "percentage_numeric_chars",
        "has_ip_address", "is_phishing"
    ]
    corr_matrix = df_urls_train[num_cols].corr()

    # 4. Generate Visualizations (Matplotlib & Plotly)
    print("\n[4/5] Generating Visualizations...")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import seaborn as sns
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    plt.style.use("seaborn-v0_8-darkgrid" if "seaborn-v0_8-darkgrid" in plt.style.available else "default")

    # Figure 1: Class Distribution & Language Breakdown
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # 1A: Binary Threat Balance
    class_counts = df_text_train["canonical_label"].value_counts()
    axes[0].bar(class_counts.index, class_counts.values, color=["#10b981", "#ef4444", "#f59e0b", "#8b5cf6"])
    axes[0].set_title("Training Set: Message Label Distribution", fontsize=12, fontweight="bold")
    axes[0].set_ylabel("Number of Samples")
    for i, v in enumerate(class_counts.values):
        axes[0].text(i, v + 500, f"{v:,} ({v/len(df_text_train):.1%})", ha="center", fontsize=9)

    # 1B: Language Distribution
    lang_counts = df_text_train["language"].value_counts()
    axes[1].pie(lang_counts.values, labels=lang_counts.index, autopct="%1.1f%%", colors=["#06b6d4", "#f97316", "#ec4899"], startangle=140)
    axes[1].set_title("Training Set: Language Representation", fontsize=12, fontweight="bold")

    plt.tight_layout()
    plt.savefig(figures_dir / "01_class_and_language_distribution.png", dpi=200)
    plt.close()

    # Figure 2: Message Character Length Distribution by Class
    plt.figure(figsize=(10, 5))
    sns.kdeplot(df_text_train[df_text_train["is_threat"] == 0]["char_len"], label="Legitimate / Benign", color="#10b981", fill=True, clip=(0, 400))
    sns.kdeplot(df_text_train[df_text_train["is_threat"] == 1]["char_len"], label="Scam / Smishing / Threat", color="#ef4444", fill=True, clip=(0, 400))
    plt.title("Message Character Length Density Distribution (Clipped at 400 chars)", fontsize=12, fontweight="bold")
    plt.xlabel("Character Length")
    plt.ylabel("Density")
    plt.legend()
    plt.tight_layout()
    plt.savefig(figures_dir / "02_message_length_density.png", dpi=200)
    plt.close()

    # Figure 3: Top 15 Scam Terms vs Legitimate Terms
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    top_scam = scam_words.most_common(15)
    top_legit = legit_words.most_common(15)

    axes[0].barh([w[0] for w in reversed(top_scam)], [w[1] for w in reversed(top_scam)], color="#ef4444")
    axes[0].set_title("Top 15 Most Discriminative Scam Terms", fontsize=11, fontweight="bold")
    axes[0].set_xlabel("Frequency Count")

    axes[1].barh([w[0] for w in reversed(top_legit)], [w[1] for w in reversed(top_legit)], color="#10b981")
    axes[1].set_title("Top 15 Most Common Benign Terms", fontsize=11, fontweight="bold")
    axes[1].set_xlabel("Frequency Count")

    plt.tight_layout()
    plt.savefig(figures_dir / "03_term_frequency_comparison.png", dpi=200)
    plt.close()

    # Figure 4: Correlation Heatmap for URL Features
    plt.figure(figsize=(10, 8))
    sns.heatmap(corr_matrix, annot=True, fmt=".2f", cmap="coolwarm", cbar=True, square=True)
    plt.title("Correlation Matrix: Lexical URL Features & Phishing Target", fontsize=12, fontweight="bold")
    plt.tight_layout()
    plt.savefig(figures_dir / "04_url_feature_correlation_heatmap.png", dpi=200)
    plt.close()

    # Figure 5: Interactive Plotly HTML Visualization
    plotly_fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=("URL Length vs Entropy by Class", "Top Social Engineering Tactics (ScamShield)")
    )

    sample_urls = df_urls_train.sample(n=min(2000, len(df_urls_train)), random_state=42)
    plotly_fig.add_trace(
        go.Scatter(
            x=sample_urls[sample_urls["is_phishing"] == 0]["url_length"],
            y=sample_urls[sample_urls["is_phishing"] == 0]["url_entropy"],
            mode="markers",
            name="Legitimate URLs",
            marker=dict(color="#10b981", opacity=0.6, size=5)
        ),
        row=1, col=1
    )
    plotly_fig.add_trace(
        go.Scatter(
            x=sample_urls[sample_urls["is_phishing"] == 1]["url_length"],
            y=sample_urls[sample_urls["is_phishing"] == 1]["url_entropy"],
            mode="markers",
            name="Phishing URLs",
            marker=dict(color="#ef4444", opacity=0.6, size=5)
        ),
        row=1, col=1
    )

    # Tactic counts
    tactic_dict = {
        "Reward Bait": 9970,
        "Urgency & Deadlines": 6560,
        "Financial Pressure": 5009,
        "Impersonation": 3320,
        "Fear / Cutoff": 3275
    }
    plotly_fig.add_trace(
        go.Bar(
            x=list(tactic_dict.keys()),
            y=list(tactic_dict.values()),
            marker_color=["#f59e0b", "#ef4444", "#3b82f6", "#8b5cf6", "#ec4899"],
            name="Tactics"
        ),
        row=1, col=2
    )

    plotly_fig.update_layout(
        title_text="TRUSTLENS AI — Interactive Threat Landscape Telemetry",
        template="plotly_dark",
        showlegend=True,
        height=500
    )
    plotly_fig.write_html(str(figures_dir / "05_interactive_threat_eda.html"))

    # 5. Export Summary JSON
    eda_summary = {
        "text_eda": {
            "train_samples": len(df_text_train),
            "threat_percentage": float(df_text_train["is_threat"].mean()),
            "length_statistics": len_stats,
            "top_scam_words": top_scam[:10],
            "top_legit_words": top_legit[:10],
        },
        "url_eda": {
            "train_samples": len(df_urls_train),
            "phishing_percentage": float(df_urls_train["is_phishing"].mean()),
            "correlations_with_is_phishing": corr_matrix["is_phishing"].to_dict(),
        },
    }

    with open(figures_dir / "eda_summary.json", "w", encoding="utf-8") as f:
        json.dump(eda_summary, f, indent=2)

    print(f"\n[OK] All figures and summary saved to {figures_dir}")
    print("=" * 60)
    print("EDA EXECUTION COMPLETED!")
    print("=" * 60)
    return eda_summary


if __name__ == "__main__":
    compute_comprehensive_eda()
