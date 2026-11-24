import asyncio
import json
from backend.app.database.manager import db_manager
from backend.app.database.collections import get_analyses_collection, get_indicators_collection, get_urls_collection

async def inspect():
    await db_manager.connect()
    analyses_coll = get_analyses_collection()
    cursor = analyses_coll.find({}).limit(3)
    items = await cursor.to_list(3)
    for i, it in enumerate(items):
        it.pop("_id", None)
        print(f"--- Analysis #{i+1} ---")
        print(json.dumps(it, default=str, indent=2))
        
    print("\n--- Indicators ---")
    ind_cursor = get_indicators_collection().find({}).limit(5)
    inds = await ind_cursor.to_list(5)
    for ind in inds:
        ind.pop("_id", None)
        print(json.dumps(ind, default=str))

    await db_manager.disconnect()

asyncio.run(inspect())
