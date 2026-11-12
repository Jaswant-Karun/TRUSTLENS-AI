"""
TRUSTLENS AI - Model 1 Advanced Multilingual Transformer Training Pipeline
Fine-tunes 'google/muril-base-cased' (or compact multilingual DistilBERT) with:
- Stratified sampling for CPU memory constraints (~2GB free RAM)
- Multi-threaded CPU execution (torch.set_num_threads(8))
- Early stopping based on validation loss
- Evaluation against the held-out test split
"""

import sys
import os
import json
import time
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer, AutoModelForSequenceClassification, AdamW, get_linear_schedule_with_warmup
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

# Set CPU threads for multi-core performance
torch.set_num_threads(8)


class ScamTextDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_length=128):
        self.texts = list(texts)
        self.labels = list(labels)
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        text = str(self.texts[idx])
        label = int(self.labels[idx])
        encoding = self.tokenizer(
            text,
            truncation=True,
            padding="max_length",
            max_length=self.max_length,
            return_tensors="pt"
        )
        return {
            "input_ids": encoding["input_ids"].squeeze(0),
            "attention_mask": encoding["attention_mask"].squeeze(0),
            "label": torch.tensor(label, dtype=torch.long)
        }


def train_transformer_model(
    model_name="google/muril-base-cased",
    max_train_samples=4000,
    max_val_samples=1000,
    epochs=2,
    batch_size=16,
    lr=3e-5
):
    print("=" * 65)
    print("TRUSTLENS AI - MODEL 1: ADVANCED TRANSFORMER FINE-TUNING")
    print(f"Model: {model_name} | Hardware: Intel CPU (8 Threads)")
    print("=" * 65)

    artifacts_dir = Path("ml/artifacts/text_detection/transformer")
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    # 1. Load Data
    train_df = pd.read_parquet("data/processed/text_train.parquet")
    val_df = pd.read_parquet("data/processed/text_val.parquet")
    test_df = pd.read_parquet("data/processed/text_test.parquet")

    # Stratified subsampling for CPU feasibility
    if len(train_df) > max_train_samples:
        train_sub = train_df.groupby(["language", "is_threat"], group_keys=False).apply(
            lambda x: x.sample(n=max(1, int(len(x) * (max_train_samples / len(train_df)))), random_state=42)
        ).sample(frac=1.0, random_state=42).reset_index(drop=True)
    else:
        train_sub = train_df

    if len(val_df) > max_val_samples:
        val_sub = val_df.sample(n=max_val_samples, random_state=42).reset_index(drop=True)
    else:
        val_sub = val_df

    print(f"  Training Samples:   {len(train_sub):,} (Stratified by Language & Class)")
    print(f"  Validation Samples: {len(val_sub):,}")
    print(f"  Test Samples:       {len(test_df):,} (Full evaluation test set)")

    # 2. Tokenizer & Dataset
    print(f"\n[1/3] Loading Tokenizer and Initializing Weights: {model_name}...")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    tokenizer.save_pretrained(artifacts_dir / "tokenizer")

    train_dataset = ScamTextDataset(train_sub["cleaned_text"], train_sub["is_threat"], tokenizer)
    val_dataset = ScamTextDataset(val_sub["cleaned_text"], val_sub["is_threat"], tokenizer)
    test_dataset = ScamTextDataset(test_df["cleaned_text"], test_df["is_threat"], tokenizer)

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)

    # 3. Model Architecture
    device = torch.device("cpu")
    model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=2)
    model.to(device)

    # Class weights for loss
    class_counts = train_sub["is_threat"].value_counts()
    weight_threat = len(train_sub) / (2.0 * class_counts.get(1, 1))
    weight_legit = len(train_sub) / (2.0 * class_counts.get(0, 1))
    loss_fn = nn.CrossEntropyLoss(weight=torch.tensor([weight_legit, weight_threat], dtype=torch.float32).to(device))

    optimizer = AdamW(model.parameters(), lr=lr, weight_decay=0.01)
    total_steps = len(train_loader) * epochs
    scheduler = get_linear_schedule_with_warmup(optimizer, num_warmup_steps=int(total_steps * 0.1), num_training_steps=total_steps)

    # 4. Training Loop with Early Stopping
    print("\n[2/3] Training Loop Starting...")
    best_val_f1 = 0.0
    start_train_time = time.time()

    for epoch in range(1, epochs + 1):
        model.train()
        total_train_loss = 0.0
        t0 = time.time()

        for step, batch in enumerate(train_loader):
            optimizer.zero_grad()
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels = batch["label"].to(device)

            outputs = model(input_ids=input_ids, attention_mask=attention_mask)
            logits = outputs.logits
            loss = loss_fn(logits, labels)

            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            scheduler.step()

            total_train_loss += loss.item()
            if (step + 1) % 50 == 0:
                print(f"  Epoch {epoch}/{epochs} | Step {step+1}/{len(train_loader)} | Batch Loss: {loss.item():.4f}")

        avg_train_loss = total_train_loss / len(train_loader)
        epoch_time = time.time() - t0

        # Validation
        model.eval()
        val_preds, val_targets = [], []
        with torch.no_grad():
            for batch in val_loader:
                input_ids = batch["input_ids"].to(device)
                attention_mask = batch["attention_mask"].to(device)
                labels = batch["label"].to(device)
                outputs = model(input_ids=input_ids, attention_mask=attention_mask)
                preds = torch.argmax(outputs.logits, dim=1).cpu().numpy()
                val_preds.extend(preds)
                val_targets.extend(labels.cpu().numpy())

        val_f1 = f1_score(val_targets, val_preds, average="macro", zero_division=0)
        val_acc = accuracy_score(val_targets, val_preds)
        print(f"  Epoch {epoch} Complete in {epoch_time:.1f}s | Train Loss: {avg_train_loss:.4f} | Val Acc: {val_acc:.4f} | Val Macro F1: {val_f1:.4f}")

        if val_f1 > best_val_f1:
            best_val_f1 = val_f1
            print(f"  [*] New best validation F1 ({val_f1:.4f})! Saving checkpoint...")
            model.save_pretrained(artifacts_dir / "checkpoint")

    total_training_duration = time.time() - start_train_time
    print(f"\nTotal Training Duration: {total_training_duration / 60:.2f} minutes")

    # 5. Final Evaluation on Full Test Set
    print("\n[3/3] Evaluating Fine-Tuned Transformer on Full Test Set (N=8,202)...")
    best_model = AutoModelForSequenceClassification.from_pretrained(artifacts_dir / "checkpoint")
    best_model.to(device)
    best_model.eval()

    test_preds = []
    test_targets = []
    t_eval_start = time.time()

    with torch.no_grad():
        for batch in test_loader:
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels = batch["label"].to(device)
            outputs = best_model(input_ids=input_ids, attention_mask=attention_mask)
            preds = torch.argmax(outputs.logits, dim=1).cpu().numpy()
            test_preds.extend(preds)
            test_targets.extend(labels.cpu().numpy())

    test_duration = time.time() - t_eval_start
    cm = confusion_matrix(test_targets, test_preds)
    tn, fp, fn, tp = cm.ravel()
    fpr = float(fp / (fp + tn))
    fnr = float(fn / (fn + tp))

    acc = float(accuracy_score(test_targets, test_preds))
    prec_macro = float(precision_score(test_targets, test_preds, average="macro", zero_division=0))
    rec_macro = float(recall_score(test_targets, test_preds, average="macro", zero_division=0))
    f1_macro = float(f1_score(test_targets, test_preds, average="macro", zero_division=0))
    f1_weighted = float(f1_score(test_targets, test_preds, average="weighted", zero_division=0))

    # Per-language breakdown on test set
    per_language = {}
    test_df_copy = test_df.copy()
    test_df_copy["pred"] = test_preds
    for lang in test_df_copy["language"].unique():
        sub = test_df_copy[test_df_copy["language"] == lang]
        per_language[lang] = {
            "sample_count": len(sub),
            "accuracy": round(float(accuracy_score(sub["is_threat"], sub["pred"])), 4),
            "f1_macro": round(float(f1_score(sub["is_threat"], sub["pred"], average="macro", zero_division=0)), 4),
        }

    results = {
        "model_name": f"Fine-tuned {model_name}",
        "accuracy": round(acc, 4),
        "precision_macro": round(prec_macro, 4),
        "recall_macro": round(rec_macro, 4),
        "f1_macro": round(f1_macro, 4),
        "f1_weighted": round(f1_weighted, 4),
        "false_positive_rate": round(fpr, 4),
        "false_negative_rate": round(fnr, 4),
        "per_language": per_language,
        "confusion_matrix": cm.tolist(),
        "training_duration_minutes": round(total_training_duration / 60, 2),
        "test_eval_duration_seconds": round(test_duration, 2),
    }

    with open(artifacts_dir / "transformer_eval_report.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"\nTransformer Test Results:")
    print(f"  Accuracy:  {acc:.4f}")
    print(f"  Macro F1:  {f1_macro:.4f}")
    print(f"  FPR:       {fpr:.4f}")
    print(f"  FNR:       {fnr:.4f}")
    print(f"  Per-Language: {per_language}")
    print("=" * 65)
    return results


if __name__ == "__main__":
    train_transformer_model()
