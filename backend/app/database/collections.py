"""
TRUSTLENS AI - Database Collection Names & Accessors
Defines standard identifiers for all 10 MongoDB Atlas collections.
"""

from backend.app.database.manager import db_manager

# 10 Official Collection Identifiers
COLL_USERS = "users"
COLL_ANALYSES = "analyses"
COLL_SUSPICIOUS_URLS = "suspicious_urls"
COLL_SCAM_REPORTS = "scam_reports"
COLL_SCAM_CAMPAIGNS = "scam_campaigns"
COLL_THREAT_INDICATORS = "threat_indicators"
COLL_MODEL_REGISTRY = "model_registry"
COLL_MODEL_EVALUATIONS = "model_evaluations"
COLL_AUTOMATION_LOGS = "automation_logs"
COLL_AUDIT_LOGS = "audit_logs"

ALL_COLLECTIONS = [
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
]


def get_users_collection():
    return db_manager.get_collection(COLL_USERS)


def get_analyses_collection():
    return db_manager.get_collection(COLL_ANALYSES)


def get_urls_collection():
    return db_manager.get_collection(COLL_SUSPICIOUS_URLS)


def get_reports_collection():
    return db_manager.get_collection(COLL_SCAM_REPORTS)


def get_campaigns_collection():
    return db_manager.get_collection(COLL_SCAM_CAMPAIGNS)


def get_indicators_collection():
    return db_manager.get_collection(COLL_THREAT_INDICATORS)


def get_models_collection():
    return db_manager.get_collection(COLL_MODEL_REGISTRY)


def get_evaluations_collection():
    return db_manager.get_collection(COLL_MODEL_EVALUATIONS)


def get_automations_collection():
    return db_manager.get_collection(COLL_AUTOMATION_LOGS)


def get_audit_collection():
    return db_manager.get_collection(COLL_AUDIT_LOGS)


# Convenience Aliases
get_model_registry_collection = get_models_collection
get_model_evaluations_collection = get_evaluations_collection
get_automation_logs_collection = get_automations_collection
get_audit_logs_collection = get_audit_collection
get_threat_indicators_collection = get_indicators_collection
get_suspicious_urls_collection = get_urls_collection

