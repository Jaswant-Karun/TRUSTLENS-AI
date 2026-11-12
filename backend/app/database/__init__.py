"""
TRUSTLENS AI - Database Package
"""

from backend.app.database.manager import db_manager, get_db
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
    get_users_collection,
    get_analyses_collection,
    get_urls_collection,
    get_reports_collection,
    get_campaigns_collection,
    get_indicators_collection,
    get_models_collection,
    get_evaluations_collection,
    get_automations_collection,
    get_audit_collection,
)
from backend.app.database.indexes import init_database_indexes

__all__ = [
    "db_manager",
    "get_db",
    "init_database_indexes",
    "COLL_USERS",
    "COLL_ANALYSES",
    "COLL_SUSPICIOUS_URLS",
    "COLL_SCAM_REPORTS",
    "COLL_SCAM_CAMPAIGNS",
    "COLL_THREAT_INDICATORS",
    "COLL_MODEL_REGISTRY",
    "COLL_MODEL_EVALUATIONS",
    "COLL_AUTOMATION_LOGS",
    "COLL_AUDIT_LOGS",
    "get_users_collection",
    "get_analyses_collection",
    "get_urls_collection",
    "get_reports_collection",
    "get_campaigns_collection",
    "get_indicators_collection",
    "get_models_collection",
    "get_evaluations_collection",
    "get_automations_collection",
    "get_audit_collection",
]

