"""
TRUSTLENS AI - MongoDB Indexes Definition & Initialization
Ensures performant queries and unique constraints across all 10 collections.
"""

from typing import Dict, List, Tuple
from backend.app.core.logging import logger
from backend.app.database.manager import db_manager
from backend.app.database.collections import (
    COLL_USERS,
    COLL_ANALYSES,
    COLL_SUSPICIOUS_URLS,
    COLL_SCAM_REPORTS,
    COLL_SCAM_CAMPAIGNS,
    COLL_THREAT_INDICATORS,
    COLL_MODEL_REGISTRY,
    COLL_MODEL_EVALUATIONS,
    COLL_AUTOMATION_LOGS,
    COLL_AUDIT_LOGS,
)

INDEX_SPECIFICATIONS: Dict[str, List[Dict]] = {
    COLL_USERS: [
        {"keys": [("email", 1)], "unique": True},
        {"keys": [("role", 1)]},
        {"keys": [("created_at", -1)]},
    ],
    COLL_ANALYSES: [
        {"keys": [("analysis_id", 1)], "unique": True},
        {"keys": [("user_id", 1)]},
        {"keys": [("created_at", -1)]},
        {"keys": [("threat_level", 1)]},
        {"keys": [("analysis_type", 1)]},
    ],
    COLL_SUSPICIOUS_URLS: [
        {"keys": [("url", 1)], "unique": True},
        {"keys": [("risk_score", -1)]},
        {"keys": [("last_seen", -1)]},
    ],
    COLL_SCAM_REPORTS: [
        {"keys": [("report_id", 1)], "unique": True},
        {"keys": [("status", 1)]},
        {"keys": [("created_at", -1)]},
        {"keys": [("target_type", 1)]},
    ],
    COLL_SCAM_CAMPAIGNS: [
        {"keys": [("campaign_id", 1)], "unique": True},
        {"keys": [("status", 1)]},
        {"keys": [("last_activity", -1)]},
        {"keys": [("targeted_entity", 1)]},
    ],
    COLL_THREAT_INDICATORS: [
        {"keys": [("type", 1), ("value", 1)], "unique": True},
        {"keys": [("severity", 1)]},
        {"keys": [("last_seen", -1)]},
    ],
    COLL_MODEL_REGISTRY: [
        {"keys": [("model_id", 1)], "unique": True},
        {"keys": [("status", 1)]},
    ],
    COLL_MODEL_EVALUATIONS: [
        {"keys": [("evaluation_id", 1)], "unique": True},
        {"keys": [("created_at", -1)]},
    ],
    COLL_AUTOMATION_LOGS: [
        {"keys": [("log_id", 1)], "unique": True},
        {"keys": [("executed_at", -1)]},
        {"keys": [("workflow_name", 1)]},
    ],
    COLL_AUDIT_LOGS: [
        {"keys": [("audit_id", 1)], "unique": True},
        {"keys": [("timestamp", -1)]},
        {"keys": [("user_id", 1)]},
        {"keys": [("action", 1)]},
    ],
}


async def init_database_indexes() -> None:
    """Creates indexes across all collections."""
    if not db_manager.is_connected or db_manager.db is None:
        return

    logger.info("Verifying and building MongoDB Atlas indexes...")
    for coll_name, specs in INDEX_SPECIFICATIONS.items():
        try:
            coll = db_manager.db[coll_name]
            for spec in specs:
                keys = spec["keys"]
                unique = spec.get("unique", False)
                await coll.create_index(keys, unique=unique, background=True)
        except Exception as e:
            logger.warning(f"Note on index creation for '{coll_name}': {e}")
