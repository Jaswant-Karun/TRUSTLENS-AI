"""
TRUSTLENS AI - Ground-Truth Dataset Inspection & Audit
Inspects raw datasets, columns, data types, missing values, duplicates, class distributions, and overlapping records.
"""

import json
import pandas as pd
from pathlib import Path


def audit_sms_phishing():
    print("=" * 60)
    print("1. AUDITING SMS PHISHING DATASET (Mendeley)")
    print("=" * 60)
    csv_path = Path("data/raw/sms_phishing/Dataset_5971.csv")
    df = pd.read_csv(csv_path)
    print(f"File: {csv_path}")
    print(f"Shape: {df.shape[0]} rows, {df.shape[1]} columns")
    print("\nColumns and Types:")
    for col, dtype in df.dtypes.items():
        print(f"  - {col}: {dtype} (Nulls: {df[col].isnull().sum()})")
    
    print("\nFirst 3 rows:")
    print(df.head(3))
    
    label_cols = [c for c in df.columns if "label" in c.lower() or "class" in c.lower() or "type" in c.lower()]
    print(f"\nPotential label columns: {label_cols}")
    for col in label_cols:
        print(f"\nValue counts for '{col}':")
        print(df[col].value_counts(dropna=False))
        
    text_cols = [c for c in df.columns if "text" in c.lower() or "msg" in c.lower() or "message" in c.lower()]
    print(f"\nPotential text columns: {text_cols}")
    if text_cols:
        tcol = text_cols[0]
        exact_dups = df.duplicated(subset=[tcol]).sum()
        print(f"Duplicate messages in '{tcol}': {exact_dups} ({exact_dups/len(df):.2%})")
    
    return df


def audit_legitphish():
    print("\n" + "=" * 60)
    print("2. AUDITING LEGITPHISH URL DATASET (Mendeley)")
    print("=" * 60)
    csv_path = Path("data/raw/legitphish/url_features_extracted1.csv")
    df = pd.read_csv(csv_path)
    print(f"File: {csv_path}")
    print(f"Shape: {df.shape[0]} rows, {df.shape[1]} columns")
    print("\nColumns and Types:")
    for col, dtype in df.dtypes.items():
        print(f"  - {col}: {dtype} (Nulls: {df[col].isnull().sum()})")
    
    print("\nFirst 3 rows:")
    print(df.head(3))
    
    label_cols = [c for c in df.columns if "label" in c.lower() or "class" in c.lower() or "result" in c.lower()]
    print(f"\nPotential label columns: {label_cols}")
    for col in label_cols:
        print(f"\nValue counts for '{col}':")
        print(df[col].value_counts(dropna=False))
        
    url_cols = [c for c in df.columns if "url" in c.lower()]
    print(f"\nURL columns: {url_cols}")
    if url_cols:
        ucol = url_cols[0]
        exact_dups = df.duplicated(subset=[ucol]).sum()
        print(f"Duplicate URLs in '{ucol}': {exact_dups} ({exact_dups/len(df):.2%})")

    return df


def audit_scamshield():
    print("\n" + "=" * 60)
    print("3. AUDITING SCAMSHIELD MULTILINGUAL DATASET (Hugging Face)")
    print("=" * 60)
    splits = ["train.jsonl", "val.jsonl", "test.jsonl"]
    total_records = 0
    all_keys = set()
    label_counts = {}
    
    for split in splits:
        p = Path("data/raw/scamshield") / split
        count = 0
        samples = []
        with open(p, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    item = json.loads(line)
                    count += 1
                    all_keys.update(item.keys())
                    if len(samples) < 2:
                        samples.append(item)
                    label = str(item.get("label", item.get("class", "unknown")))
                    label_counts[label] = label_counts.get(label, 0) + 1
        print(f"Split {split}: {count} records")
        print(f"  Sample 0 keys: {list(samples[0].keys()) if samples else 'none'}")
        if samples:
            print(f"  Sample 0: {samples[0]}")
        total_records += count
        
    print(f"\nTotal ScamShield records across splits: {total_records}")
    print(f"Union of keys: {all_keys}")
    print(f"Label distribution across all splits: {label_counts}")


if __name__ == "__main__":
    audit_sms_phishing()
    audit_legitphish()
    audit_scamshield()

