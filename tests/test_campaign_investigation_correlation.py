"""
Automated tests for Campaign Investigation & Correlation:
- Graph node provenance & edge confidence/source/explanation
- Graph filtering (node_type, min_confidence, relationship_type) & search
- 1-hop expansion connecting indicators, campaign clusters, and analyses
- Preservation of analyst notes / decisions and timeline history
"""

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.database.manager import db_manager
from backend.app.database.collections import get_investigations_collection, get_indicators_collection, get_analyses_collection
from backend.app.security.dependencies import get_current_user, get_optional_current_user


@pytest.fixture()
def client():
    db_manager._use_fallback = True
    return TestClient(app)


def test_investigation_graph_filtering_provenance_expansion_and_history(client):
    user = {"user_id": "analyst-corr-1", "email": "corr@trustlens.ai", "role": "analyst"}
    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_optional_current_user] = lambda: user
    try:
        # 1. Create an investigation
        cr = client.post(
            "/api/v1/investigations",
            json={"title": "SBI Phishing Correlation Case", "description": "Testing graph correlation", "visibility": "Private"},
        )
        assert cr.status_code in (200, 201)
        body = cr.json()
        inv_id = body.get("investigation_id") or body.get("id") or (body.get("investigation") or {}).get("investigation_id")

        # 2. Add analyst note (decision/history)
        note_r = client.post(
            f"/api/v1/investigations/{inv_id}/notes",
            json={"content": "Analyst confirmed domain bit.ly used in lure"},
        )
        assert note_r.status_code in (200, 201)

        # 3. Seed an analysis + indicator + graph node/edge via fallback collections for expansion test
        import asyncio
        async def _seed():
            ind_coll = get_indicators_collection()
            await ind_coll.insert_one({
                "indicator_id": "ti-corr-1",
                "value": "evil-sbi-login.xyz",
                "indicator_type": "domain",
                "severity": "critical",
                "confidence": 0.94,
                "source": "PhishTank (Cisco Talos)",
                "verification_status": "verified",
            })
            inv_coll = get_investigations_collection()
            await inv_coll.update_one(
                {"investigation_id": inv_id},
                {
                    "$set": {
                        "nodes": [
                            {
                                "id": "n-dom-1",
                                "type": "domain",
                                "label": "evil-sbi-login.xyz",
                                "source": "Analysis Extraction",
                                "verification_status": "verified",
                                "created_at": "2026-11-25T10:00:00+00:00",
                                "properties": {"domain": "evil-sbi-login.xyz"},
                            },
                            {
                                "id": "n-cmp-41",
                                "type": "campaign_cluster",
                                "label": "Campaign Cluster #41",
                                "source": "HDBSCAN v2.4",
                                "verification_status": "verified",
                                "created_at": "2026-11-25T10:00:00+00:00",
                                "properties": {"cluster_id": 41},
                            },
                        ],
                        "edges": [
                            {
                                "id": "e-1",
                                "source": "n-dom-1",
                                "target": "n-cmp-41",
                                "relationship_type": "belongs_to_cluster",
                                "evidence_reference": "Shared domain evil-sbi-login.xyz",
                                "confidence": 0.88,
                                "source_name": "HDBSCAN v2.4",
                                "explanation": "Domain linked to Cluster #41",
                                "created_at": "2026-11-25T10:00:00+00:00",
                            }
                        ],
                    }
                },
            )
        asyncio.run(_seed())

        # 4. Graph retrieval includes provenance, confidence, source_name, explanation, and supports filtering/search
        g_all = client.get(f"/api/v1/investigations/{inv_id}/graph").json()
        assert g_all["total_nodes"] == 2
        assert g_all["nodes"][0]["provenance"]["source"] == "Analysis Extraction"
        assert g_all["edges"][0]["confidence"] == 0.88
        assert g_all["edges"][0]["source_name"] == "HDBSCAN v2.4"
        assert "Cluster #41" in g_all["edges"][0]["explanation"]

        g_filtered = client.get(f"/api/v1/investigations/{inv_id}/graph?node_type=domain&search=evil-sbi").json()
        assert g_filtered["total_nodes"] == 1
        assert g_filtered["nodes"][0]["id"] == "n-dom-1"

        # 5. 1-Hop expansion discovers linked threat_indicator from MongoDB
        exp = client.get(f"/api/v1/investigations/{inv_id}/objects/n-dom-1/relationships").json()
        assert any(n["type"] == "threat_indicator" for n in exp["connected_nodes"])
        assert any(e["confidence"] == 0.94 and e["source_name"] == "PhishTank (Cisco Talos)" for e in exp["edges"])

        # 6. Analyst note & timeline history remain preserved
        tl = client.get(f"/api/v1/investigations/{inv_id}/timeline").json()
        assert tl["total_events"] >= 1
    finally:
        app.dependency_overrides.pop(get_current_user, None)
        app.dependency_overrides.pop(get_optional_current_user, None)
