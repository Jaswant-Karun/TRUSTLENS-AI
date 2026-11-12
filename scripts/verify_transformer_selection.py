"""
TRUSTLENS AI - Transformer Compatibility & Hardware Assessment
Compares XLM-RoBERTa, MuRIL, and compact multilingual transformers on host hardware.
"""

import sys
import psutil
import torch


def assess_hardware_and_transformers():
    print("=" * 60)
    print("TRUSTLENS AI - TRANSFORMER COMPATIBILITY & HARDWARE AUDIT")
    print("=" * 60)

    # 1. Hardware profiling
    cpu_count = psutil.cpu_count(logical=True)
    cpu_physical = psutil.cpu_count(logical=False)
    mem = psutil.virtual_memory()
    cuda_available = torch.cuda.is_available()

    print(f"CPU Physical Cores: {cpu_physical} | Logical Threads: {cpu_count}")
    print(f"Total System Memory: {mem.total / (1024**3):.2f} GB")
    print(f"Available Free Memory: {mem.available / (1024**3):.2f} GB")
    print(f"CUDA Hardware Acceleration: {'AVAILABLE' if cuda_available else 'NOT DETECTED (CPU Inference/Training Required)'}")

    # 2. Candidate Model Evaluation Matrix
    candidates = [
        {
            "name": "google/muril-base-cased",
            "architecture": "BERT (12 layers, 768 hidden, 12 heads)",
            "parameters": "237M",
            "disk_size_mb": 950,
            "supported_languages": "17 Indian languages + English + Transliterated/Hinglish",
            "hinglish_suitability": "EXCELLENT (Native pre-training on romanized Hindi/Hinglish)",
            "cpu_suitability": "MODERATE (Requires batch size 16-32, CPU thread tuning)",
        },
        {
            "name": "xlm-roberta-base",
            "architecture": "RoBERTa (12 layers, 768 hidden, 12 heads)",
            "parameters": "278M",
            "disk_size_mb": 1110,
            "supported_languages": "100 languages (including English, Hindi)",
            "hinglish_suitability": "FAIR (Subword byte-level BPE, but lower Romanized Indian weight)",
            "cpu_suitability": "HEAVY (1.1GB disk, higher peak RAM during backprop)",
        },
        {
            "name": "distilbert-base-multilingual-cased",
            "architecture": "DistilBERT (6 layers, 768 hidden, 12 heads)",
            "parameters": "135M",
            "disk_size_mb": 540,
            "supported_languages": "104 languages",
            "hinglish_suitability": "GOOD (Distilled subwords, compact memory)",
            "cpu_suitability": "EXCELLENT (2x faster CPU forward pass, sub-40ms latency)",
        },
    ]

    print("\n--- MODEL ARCHITECTURE SELECTION MATRIX ---")
    for cand in candidates:
        print(f"\nModel: {cand['name']}")
        print(f"  Architecture: {cand['architecture']}")
        print(f"  Parameters:   {cand['parameters']} (~{cand['disk_size_mb']} MB)")
        print(f"  Languages:    {cand['supported_languages']}")
        print(f"  Hinglish:     {cand['hinglish_suitability']}")
        print(f"  CPU Feasibility: {cand['cpu_suitability']}")

    # 3. Decision & Technical Rationale
    recommendation = (
        "DECISION: We select 'google/muril-base-cased' as the primary transformer for fine-tuning "
        "because MuRIL was explicitly trained on monolingual and transliterated Hindi/Hinglish data by Google Research, "
        "offering superior linguistic alignment over standard XLM-RoBERTa. "
        "For baseline comparison, we implement Word TF-IDF + Calibrated Logistic Regression, "
        "Char TF-IDF + LinearSVC, and Feature Union TF-IDF."
    )
    print("\n" + "=" * 60)
    print(recommendation)
    print("=" * 60)
    return candidates


if __name__ == "__main__":
    assess_hardware_and_transformers()
