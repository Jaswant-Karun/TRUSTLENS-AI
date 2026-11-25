"""
TRUSTLENS AI — Idempotent Database Migration & Index Runner
Applies MongoDB indexes and records applied migration versions in `schema_migrations`.
"""

import asyncio
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from backend.app.core.logging import logger
from backend.app.database.indexes import init_database_indexes
from backend.app.database.manager import db_manager


MIGRATIONS = [
    ("2026_11_25_001_core_indexes", "Ensure core MongoDB collection indexes"),
    ("2026_11_25_002_device_push_tokens", "Ensure unique index on device_push_tokens"),
]


async def run_migrations() -> None:
    await db_manager.connect()
    try:
        await init_database_indexes()
        if db_manager.db is not None:
            await db_manager.db["device_push_tokens"].create_index(
                [("user_id", 1), ("device_token", 1)],
                unique=True,
                name="idx_user_device_token",
            )
            mig_coll = db_manager.db["schema_migrations"]
            for mig_id, description in MIGRATIONS:
                existing = await mig_coll.find_one({"migration_id": mig_id})
                if not existing:
                    await mig_coll.insert_one(
                        {
                            "migration_id": mig_id,
                            "description": description,
                            "applied_at": datetime.now(timezone.utc),
                        }
                    )
                    logger.info(f"Applied migration: {mig_id}")
        logger.info("All database migrations verified.")
    finally:
        await db_manager.disconnect()


if __name__ == "__main__":
    asyncio.run(run_migrations())
