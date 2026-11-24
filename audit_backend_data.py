import os
import json
import asyncio
from backend.app.database.manager import db_manager
from backend.app.database.collections import (
    get_campaigns_collection,
    get_analyses_collection,
    get_indicators_collection,
    get_urls_collection,
    get_reports_collection
)

async def check_data():
    print("=== Checking ml/artifacts ===")
    dossiers_path = "ml/artifacts/campaign_detection/campaign_dossiers.json"
    if os.path.exists(dossiers_path):
        with open(dossiers_path, "r", encoding="utf-8") as f:
            dossiers = json.load(f)
        print(f"campaign_dossiers.json found: {len(dossiers)} dossiers")
        if dossiers:
            sample = dossiers[0]
            print(f"Sample dossier keys: {list(sample.keys())}")
            print(f"Sample cluster_id: {sample.get('cluster_id')}, name: {sample.get('campaign_name') or sample.get('name')}")
            print(f"Sample targeted: {sample.get('targeted_institution') or sample.get('targeted_entity')}")
            print(f"Sample shared_iocs: {sample.get('shared_indicators') or sample.get('shared_iocs')}")
    else:
        print("campaign_dossiers.json NOT found")

    print("\n=== Checking Database Collections ===")
    await db_manager.connect()
    print("Database connected:", db_manager.is_connected)
    
    colls = {
        "campaigns": get_campaigns_collection(),
        "analyses": get_analyses_collection(),
        "indicators": get_indicators_collection(),
        "urls": get_urls_collection(),
        "reports": get_reports_collection()
    }
    for name, coll in colls.items():
        count = await coll.count_documents({})
        print(f"Collection '{name}' count: {count}")
        if count > 0:
            sample = await coll.find_one({})
            sample.pop("_id", None)
            print(f"  Sample from '{name}': {list(sample.keys())}")
            
    await db_manager.disconnect()

asyncio.run(check_data())
