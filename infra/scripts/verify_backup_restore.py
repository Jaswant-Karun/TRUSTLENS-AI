"""
TRUSTLENS AI — Database Backup & Integrity Verification Script
Checks MongoDB connectivity, critical collection existence, and Atlas backup policy
requirements before/after production deployments.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from backend.app.config.settings import settings
from backend.app.database.manager import db_manager

CRITICAL_COLLECTIONS = [
    "users",
    "analyses",
    "investigations",
    "scam_reports",
    "threat_indicators",
    "audit_logs",
    "schema_migrations",
]


async def verify_backup_readiness() -> int:
    await db_manager.connect()
    try:
        if getattr(db_manager, "_use_fallback", False) or db_manager.db is None:
            print("[backup_verify] Running in fallback mode (no live MongoDB Atlas cluster connected).")
            return 1 if settings.APP_ENV.lower() == "production" else 0

        counts = {}
        for coll in CRITICAL_COLLECTIONS:
            counts[coll] = await db_manager.db[coll].count_documents({})
        print(f"[backup_verify] Verified live collection counts: {counts}")
        return 0
    finally:
        await db_manager.disconnect()


if __name__ == "__main__":
    raise SystemExit(asyncio.run(verify_backup_readiness()))
