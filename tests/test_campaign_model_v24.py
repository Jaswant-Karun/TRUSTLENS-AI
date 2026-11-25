"""
Automated tests for Model 4 (Campaign Clustering v2.4):
- CentralModelLoader SHA-256 verification of promoted v2.4 production model
- Independent benchmark report verifying false-correlation reduction vs 47 v1.0 clusters
- Evidence-backed IOC & tactic correlation with preserved provenance and non-attribution disclaimer
"""

import json
from pathlib import Path

from backend.app.ml_engine.model_loader import CentralModelLoader
from ml.campaign_detection.infer import CampaignInferenceEngine


def test_registry_promotes_campaign_v24_with_verified_sha256():
    loader = CentralModelLoader()
    status = loader.verify_registry_artifacts()
    assert status.get("unsupervised_campaign_clustering") is True
    entry = loader.get_verified_entry("unsupervised_campaign_clustering")
    assert entry is not None
    assert entry["model_id"] == "trustlens-campaign-v2.4-candidate"
    assert entry["deployment_status"] == "Production"


def test_independent_benchmark_confirms_false_correlation_reduction():
    rep_path = Path("ml/artifacts/campaign_detection/v2.4_candidate/independent_benchmark_report.json")
    assert rep_path.exists()
    rep = json.loads(rep_path.read_text(encoding="utf-8"))
    v1 = rep["v1.0_47_clusters"]
    v24 = rep["v2.4_43_clusters"]
    assert v1["num_clusters"] == 47
    assert v24["num_clusters"] == 43
    assert v24["legit_false_correlation_rate_070"] < v1["legit_false_correlation_rate_070"]
    assert v24["inter_centroid_mean_sim"] < v1["inter_centroid_mean_sim"]


def test_evidence_backed_correlation_and_provenance():
    engine = CampaignInferenceEngine()
    assert engine.is_loaded is True
    assert engine.is_v24 is True

    # Semantic match with shared IOC (bit.ly domain present in SBI YONO cluster #41)
    res_ioc = engine.match_campaign(
        "Dear SBI user your SBI YONO Account will be block today Please click https://bit.ly/sbi-kyc to update PAN",
        verified_tactics=["urgency_time_pressure", "bank_impersonation"],
    )
    assert res_ioc["campaign_id"] != -1
    assert res_ioc["correlation_strength"] == "corroborated_ioc_and_semantic"
    assert "bit.ly" in res_ioc["shared_domain_matches"]
    assert len(res_ioc["evidence_relationships"]) >= 2
    assert res_ioc["correlation_provenance"]["clustering_version"] == "hdbscan-v2.4"
    assert "does not prove" in res_ioc["correlation_provenance"]["non_attribution_notice"].lower()

    # Semantic-only match (no shared IOC) must NOT claim corroborated IOC proof
    res_sem = engine.match_campaign("Dear SBI user your SBI YONO Account will be block today update PAN")
    assert res_sem["correlation_strength"] in ("semantic_similarity_only", "none")
    assert "does not constitute legal proof" in res_sem["legal_disclaimer"].lower()
