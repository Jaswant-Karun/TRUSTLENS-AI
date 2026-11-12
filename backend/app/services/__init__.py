"""
TRUSTLENS AI - Services Package
"""

from backend.app.services.risk_service import risk_service, TransparentRiskAggregationService
from backend.app.services.auth_service import auth_service, AuthenticationService
from backend.app.services.analysis_service import threat_analysis_service, ThreatAnalysisService
from backend.app.services.ocr_service import ocr_service, ScreenshotOCRService
from backend.app.services.campaign_service import campaign_service, CampaignIntelligenceService
from backend.app.services.model_service import model_service, ModelManagementService
from backend.app.services.report_service import report_service, CommunityScamReportService
from backend.app.services.ml_service import ml_service, MLOrchestrationService
from backend.app.services.training_service import training_orchestrator, TrainingOrchestratorService
from backend.app.services.automation_service import automation_service, AutomationService

__all__ = [
    "risk_service",
    "TransparentRiskAggregationService",
    "auth_service",
    "AuthenticationService",
    "threat_analysis_service",
    "ThreatAnalysisService",
    "ocr_service",
    "ScreenshotOCRService",
    "campaign_service",
    "CampaignIntelligenceService",
    "model_service",
    "ModelManagementService",
    "report_service",
    "CommunityScamReportService",
    "ml_service",
    "MLOrchestrationService",
    "training_orchestrator",
    "TrainingOrchestratorService",
    "automation_service",
    "AutomationService",
]

