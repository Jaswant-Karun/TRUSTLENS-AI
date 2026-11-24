import asyncio
import json
import pandas as pd
from collections import Counter
from backend.app.database.manager import db_manager
from backend.app.database.collections import get_analyses_collection
from ml.url_detection.features import extract_url_features, FEATURE_COLUMNS
from backend.app.ml_engine.engine import ml_engine

async def audit_db_analyses():
    print("=== 1. MONGODB 138 ANALYSES PROVENANCE ===")
    await db_manager.connect()
    coll = get_analyses_collection()
    docs = await coll.find({}).to_list(None)
    print(f"Total analyses in MongoDB: {len(docs)}")

    users = Counter()
    types = Counter()
    threats = Counter()
    channels = Counter()
    m1_versions = Counter()
    m2_versions = Counter()
    m3_versions = Counter()
    payload_texts = []
    dates = []

    for d in docs:
        users[str(d.get("user_id"))] += 1
        types[str(d.get("analysis_type"))] += 1
        threats[str(d.get("threat_level"))] += 1
        payload = d.get("input_payload", {})
        channels[str(payload.get("channel"))] += 1
        
        txt = payload.get("text") or payload.get("url") or ""
        payload_texts.append(txt)
        
        if d.get("text_model"):
            m1_versions[str(d["text_model"].get("model_version"))] += 1
        if d.get("url_model"):
            m2_versions[str(d["url_model"].get("model_version"))] += 1
        if d.get("tactic_model"):
            m3_versions[str(d["tactic_model"].get("model_version"))] += 1
        if d.get("created_at"):
            dates.append(str(d["created_at"])[:10])

    print("By user_id:", dict(users))
    print("By analysis_type:", dict(types))
    print("By threat_level:", dict(threats))
    print("By channel:", dict(channels))
    print("Model 1 versions:", dict(m1_versions))
    print("Model 2 versions:", dict(m2_versions))
    print("Model 3 versions:", dict(m3_versions))
    print("Date distribution:", dict(Counter(dates)))
    
    unique_payloads = len(set(payload_texts))
    print(f"Unique input payloads: {unique_payloads} / {len(docs)} (Duplicates: {len(docs) - unique_payloads})")
    top_dups = Counter(payload_texts).most_common(5)
    print("Top 5 repeated payloads:")
    for txt, cnt in top_dups:
        if cnt > 1:
            print(f"  [{cnt}x] {txt[:70]}")

    await db_manager.disconnect()

def audit_url_feature_parity():
    print("\n=== 2. URL FEATURE EXTRACTION PARITY CHECK ===")
    df = pd.read_parquet("data/processed/urls_test.parquet").head(3)
    for idx, row in df.iterrows():
        url = row["URL"]
        extracted = extract_url_features(url)
        mismatches = []
        for col in FEATURE_COLUMNS:
            ds_val = float(row[col])
            ex_val = float(extracted[col])
            if abs(ds_val - ex_val) > 0.01:
                mismatches.append((col, ds_val, ex_val))
        print(f"URL: {url[:50]} | Label: {row['is_phishing']} | Mismatches ({len(mismatches)}): {mismatches[:5]}")

def audit_safe_inference():
    print("\n=== 3. SAFE INFERENCE VERIFICATION ON LOADED ARTIFACTS ===")
    print("Engine status:", ml_engine.get_status())
    
    # Text
    t_res = ml_engine.predict_text("Dear Customer, Your SBI account will be blocked today. Click http://sbi-kyc-update.com")
    print(f"Model 1 (Text): is_threat={t_res.get('is_threat')}, conf={t_res.get('confidence')}, version={t_res.get('model_version')}")
    
    # URL
    u_res = ml_engine.predict_url("http://sbi-kyc-update.com/login.php")
    print(f"Model 2 (URL): is_phishing={u_res.get('is_phishing')}, risk={u_res.get('risk_score')}, version={u_res.get('model_version')}")
    
    # Tactics
    tac_res = ml_engine.predict_tactics("URGENT: Your electricity will be disconnected tonight at 9:30 PM. Call immediately.")
    print(f"Model 3 (Tactics): count={tac_res.get('tactic_count')}, tactics={[t['tactic_id'] for t in tac_res.get('tactics', [])]}")
    
    # Campaign
    c_res = ml_engine.match_campaign("Dear Customer your SBI account is suspended due to KYC. Update now.")
    print(f"Model 4 (Campaign): matched={c_res.get('matched')}, campaign_id={c_res.get('campaign_id')}, sim={c_res.get('similarity_score')}")

async def main():
    await audit_db_analyses()
    audit_url_feature_parity()
    audit_safe_inference()

asyncio.run(main())
