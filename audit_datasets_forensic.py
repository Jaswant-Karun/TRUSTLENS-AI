import os
import json
import pandas as pd

def inspect_df(name, path, df):
    print(f"\n=== {name} ({path}) ===")
    print(f"Shape: {df.shape[0]} rows x {df.shape[1]} cols")
    print(f"Columns: {list(df.columns)}")
    nulls = df.isnull().sum().to_dict()
    print(f"Missing values: { {k: v for k, v in nulls.items() if v > 0} }")
    
    # Check duplicates
    try:
        dups = df.duplicated().sum()
        print(f"Exact row duplicates: {dups}")
        for col in ["text", "message", "Message", "url", "URL", "TEXT"]:
            if col in df.columns:
                c_dups = df[col].duplicated().sum()
                print(f"Duplicate '{col}': {c_dups}")
    except Exception as e:
        print(f"Dup check error: {e}")

    # Check label distribution
    for lbl in ["label", "Label", "LABEL", "is_phishing", "status", "target", "category", "scam_type"]:
        if lbl in df.columns:
            print(f"Class distribution ({lbl}): {df[lbl].value_counts(dropna=False).to_dict()}")

    # Check language distribution
    for lang in ["language", "lang", "detected_language"]:
        if lang in df.columns:
            print(f"Language distribution ({lang}): {df[lang].value_counts(dropna=False).to_dict()}")

# 1. Raw LegitPhish
p = "data/raw/legitphish/url_features_extracted1.csv"
if os.path.exists(p):
    inspect_df("Raw LegitPhish", p, pd.read_csv(p))

# 2. Raw SMS Phishing
p = "data/raw/sms_phishing/Dataset_5971.csv"
if os.path.exists(p):
    inspect_df("Raw SMS Phishing (5971)", p, pd.read_csv(p))

# 3. Raw ScamShield JSONL
for split in ["train", "val", "test"]:
    p = f"data/raw/scamshield/{split}.jsonl"
    if os.path.exists(p):
        inspect_df(f"Raw ScamShield {split}", p, pd.read_json(p, lines=True))

# 4. Processed Parquets
processed_dir = "data/processed"
for f in sorted(os.listdir(processed_dir)):
    if f.endswith(".parquet"):
        p = os.path.join(processed_dir, f)
        inspect_df(f"Processed {f}", p, pd.read_parquet(p))
