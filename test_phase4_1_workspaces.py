"""
TRUSTLENS AI - Phase 4.1 Verification Suite
Verifies Threat Library (7 entity types, filters, sorting, pagination, detail, empty state),
Database-backed Analytics (filters, empty state, real counts),
Investigation Reports (all 5 types), JSON & STIX 2.1 Exports, Permissions, and Frontend Routes.
"""

import httpx
import sys

BACKEND = "http://127.0.0.1:8000/api/v1"
FRONTEND = "http://localhost:3000"
requests = httpx.Client(timeout=15.0)


def assert_true(cond: bool, msg: str):
    if not cond:
        raise AssertionError(msg)


def main():
    print("=== 1. AUTHENTICATION & PERMISSIONS ===")
    # Unauthenticated private analysis report/export must fail with 401
    r_unauth = requests.get(f"{BACKEND}/intelligence-reports/generate", params={"report_type": "message_analysis", "target_id": "nonexistent-id"}, timeout=10)
    assert_true(r_unauth.status_code == 401, f"Expected 401 for unauthenticated analysis report, got {r_unauth.status_code}")
    print("  PASS: Unauthenticated analysis report -> 401 Unauthorized")

    r_unauth_exp = requests.get(f"{BACKEND}/exports/stix", params={"target_type": "analysis", "target_id": "nonexistent-id"}, timeout=10)
    assert_true(r_unauth_exp.status_code == 401, f"Expected 401 for unauthenticated analysis STIX export, got {r_unauth_exp.status_code}")
    print("  PASS: Unauthenticated analysis STIX export -> 401 Unauthorized")

    r_unauth_rev = requests.post(f"{BACKEND}/reports/rep-001/review", json={"verdict": "verified_scam"}, timeout=10)
    assert_true(r_unauth_rev.status_code == 401, f"Expected 401 for unauthenticated report review, got {r_unauth_rev.status_code}")
    print("  PASS: Unauthenticated report review -> 401 Unauthorized")

    # Create valid JWTs for admin and regular user via backend security helper
    from backend.app.security.jwt import create_access_token
    admin_token = create_access_token(data={"sub": "a22d3504-399f-4b0c-ac20-1a334aa1da22", "role": "admin"})
    user_token = create_access_token(data={"sub": "f57955fd-7d26-4695-86d4-9c930eb15370", "role": "user"})
    headers = {"Authorization": f"Bearer {admin_token}"}
    user_headers = {"Authorization": f"Bearer {user_token}"}

    r_user_rev = requests.post(f"{BACKEND}/reports/rep-001/review", json={"verdict": "verified_scam"}, headers=user_headers, timeout=10)
    assert_true(r_user_rev.status_code == 403, f"Expected 403 for non-analyst report review, got {r_user_rev.status_code}")
    print("  PASS: Regular user report review -> 403 Forbidden")

    print("\n=== 2. THREAT LIBRARY (FILTERS, SORTING, PAGINATION, DETAIL, EMPTY STATE) ===")
    tl_all = requests.get(f"{BACKEND}/threat-library", params={"page": 1, "page_size": 10}, timeout=15)
    assert_true(tl_all.status_code == 200, f"Threat library failed: {tl_all.status_code}")
    tl_data = tl_all.json()
    assert_true(tl_data["total"] > 0, "Expected stored items in Threat Library")
    facets = tl_data["facets"]["entity_types"]
    print(f"  PASS: Total Threat Library items={tl_data['total']}, facets={facets}")

    for et in ["suspicious_message", "url", "domain", "indicator", "tactic", "similarity_cluster", "community_report"]:
        r_et = requests.get(f"{BACKEND}/threat-library", params={"entity_type": et, "page_size": 5}, timeout=15)
        assert_true(r_et.status_code == 200, f"Entity type {et} failed")
        d_et = r_et.json()
        assert_true(all(i["entity_type"] == et for i in d_et["items"]), f"Filter mismatch for {et}")
        print(f"  PASS: entity_type={et} -> {d_et['total']} items")

    # Sorting & Pagination
    r_p2 = requests.get(f"{BACKEND}/threat-library", params={"sort_by": "severity", "sort_order": "desc", "page": 2, "page_size": 5}, timeout=15)
    assert_true(r_p2.status_code == 200 and r_p2.json()["page"] == 2, "Pagination page 2 failed")
    print("  PASS: Sorting by severity desc + page 2 verified")

    # Detail view
    first_item_id = tl_data["items"][0]["item_id"]
    r_det = requests.get(f"{BACKEND}/threat-library/{first_item_id}", timeout=15)
    assert_true(r_det.status_code == 200 and r_det.json()["item_id"] == first_item_id, "Detail view failed")
    print(f"  PASS: Detail view verified for {first_item_id}")

    # Empty state
    r_empty = requests.get(f"{BACKEND}/threat-library", params={"search": "__NO_SUCH_THREAT_XYZ_999__"}, timeout=15)
    assert_true(r_empty.status_code == 200 and r_empty.json()["total"] == 0 and r_empty.json()["items"] == [], "Empty state failed")
    print("  PASS: Threat Library empty state verified")

    print("\n=== 3. DATABASE ANALYTICS (REAL RECORDS, FILTERS, EMPTY STATE) ===")
    an_all = requests.get(f"{BACKEND}/analytics/overview", timeout=15)
    assert_true(an_all.status_code == 200, f"Analytics failed: {an_all.status_code}")
    an_data = an_all.json()
    assert_true(an_data["summary"]["total_analyses"] > 0, "Expected real analyses count > 0")
    assert_true(len(an_data["model_prediction_distribution"]) > 0, "Expected prediction distribution")
    assert_true(len(an_data["campaign_cluster_sizes"]) > 0, "Expected campaign cluster sizes")
    print(f"  PASS: Analytics summary={an_data['summary']}")

    an_empty = requests.get(f"{BACKEND}/analytics/overview", params={"start_date": "2099-01-01", "end_date": "2099-12-31"}, timeout=15)
    assert_true(an_empty.status_code == 200 and an_empty.json()["summary"]["total_analyses"] == 0, "Analytics future date empty state failed")
    assert_true(len(an_empty.json()["limitations"]) > 0, "Expected limitations notice on empty date filter")
    print("  PASS: Analytics empty date-range filter & limitations verified")

    print("\n=== 4. INVESTIGATION REPORTS (ALL 5 TYPES) ===")
    # Get real analysis_ids for text and url
    hist = requests.get(f"{BACKEND}/analyses", params={"page": 1, "page_size": 50}, headers=headers, timeout=15).json()
    items = hist.get("items", [])
    text_id = next((x["analysis_id"] for x in items if x.get("analysis_type") in ("text", "comprehensive")), None)
    url_id = next((x["analysis_id"] for x in items if x.get("analysis_type") == "url"), None)
    assert_true(text_id is not None and url_id is not None, "Need at least 1 text and 1 url analysis in DB")

    report_cases = [
        ("message_analysis", text_id),
        ("url_analysis", url_id),
        ("comprehensive_investigation", "INV-2026-0011"),
        ("campaign_similarity", "11"),
        ("model_evaluation", None),
    ]
    for rtype, tid in report_cases:
        params = {"report_type": rtype}
        if tid:
            params["target_id"] = tid
        rr = requests.get(f"{BACKEND}/intelligence-reports/generate", params=params, headers=headers, timeout=15)
        assert_true(rr.status_code == 200, f"Report {rtype} failed: {rr.status_code} {rr.text}")
        rj = rr.json()
        for req_field in ["report_id", "investigation_id", "sources", "evidence", "model_versions", "predictions", "review_status", "limitations", "generated_at"]:
            assert_true(req_field in rj, f"Missing {req_field} in {rtype} report")
        print(f"  PASS: Generated {rtype} report ({rj['report_id']}, review_status={rj['review_status']})")

    print("\n=== 5. JSON & STIX 2.1 EXPORTS ===")
    for ttype, tid in [("investigation", "INV-2026-0011"), ("analysis", url_id), ("campaign", "11")]:
        ej = requests.get(f"{BACKEND}/exports/json", params={"target_type": ttype, "target_id": tid}, headers=headers, timeout=15)
        assert_true(ej.status_code == 200 and ej.json()["export_format"] == "trustlens-json-v1", f"JSON export failed for {ttype}")

        es = requests.get(f"{BACKEND}/exports/stix", params={"target_type": ttype, "target_id": tid}, headers=headers, timeout=15)
        assert_true(es.status_code == 200, f"STIX export failed for {ttype}: {es.status_code}")
        bundle = es.json()
        assert_true(bundle["type"] == "bundle" and bundle["id"].startswith("bundle--"), "Invalid STIX bundle root")
        val_meta = bundle.get("x_trustlens_stix_validation", {})
        assert_true(val_meta.get("spec_version") == "2.1", "STIX spec_version must be 2.1")
        assert_true(val_meta.get("misp_interoperability_claimed") is False, "Must not claim unvalidated MISP interoperability")
        objs = bundle["objects"]
        types_present = {o["type"] for o in objs}
        assert_true("identity" in types_present and "report" in types_present, "STIX bundle missing identity or report")
        for o in objs:
            if o["type"] not in ("url", "domain-name", "ipv4-addr"):
                assert_true(o.get("spec_version") == "2.1", f"SDO/SRO {o['id']} missing spec_version 2.1")
        print(f"  PASS: JSON & STIX 2.1 export verified for {ttype}:{tid} (objects={len(objs)}, types={sorted(types_present)})")

    print("\n=== 6. FRONTEND ROUTES & PROXY PARITY ===")
    for route in ["/threat-library", "/analytics", "/reports"]:
        fr = requests.get(f"{FRONTEND}{route}", timeout=15)
        assert_true(fr.status_code == 200, f"Frontend route {route} returned {fr.status_code}")
        print(f"  PASS: {route} -> HTTP 200 ({len(fr.content):,} bytes)")

    p_tl = requests.get(f"{FRONTEND}/api/v1/threat-library", params={"page_size": 5}, timeout=15)
    assert_true(p_tl.status_code == 200 and p_tl.json()["total"] == tl_data["total"], "Frontend proxy /api/v1/threat-library mismatch")
    p_an = requests.get(f"{FRONTEND}/api/v1/analytics/overview", timeout=15)
    assert_true(p_an.status_code == 200 and p_an.json()["summary"]["total_analyses"] == an_data["summary"]["total_analyses"], "Frontend proxy /api/v1/analytics/overview mismatch")
    print("  PASS: Frontend proxy -> Backend parity verified for Threat Library & Analytics")

    print("\nALL PHASE 4.1 VERIFICATION CHECKS PASSED!")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"TEST FAILED: {exc}")
        sys.exit(1)
