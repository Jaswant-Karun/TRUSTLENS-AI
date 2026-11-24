import urllib.request
import urllib.parse
import json

base_url = "http://localhost:3000/api/v1"
html_base = "http://localhost:3000"

results = []

def run_test(name, func):
    try:
        val = func()
        print(f"PASS: {name} -> {val}")
        results.append((name, "PASS", val))
    except Exception as e:
        print(f"FAIL: {name} -> {e}")
        results.append((name, "FAIL", str(e)))

# Test 1: List investigations
def test_list_investigations():
    res = urllib.request.urlopen(f"{base_url}/investigations")
    assert res.status == 200
    data = json.loads(res.read().decode("utf-8"))
    assert len(data) >= 3, f"Expected at least 3 investigations, got {len(data)}"
    ids = [d["id"] for d in data]
    return f"Status {res.status}, Count: {len(data)}, IDs: {ids}"

# Test 2: Get investigation detail
def test_get_detail():
    res = urllib.request.urlopen(f"{base_url}/investigations/INV-2026-0011")
    assert res.status == 200
    data = json.loads(res.read().decode("utf-8"))
    assert data["id"] == "INV-2026-0011"
    assert data["title"]
    assert "sources" in data
    return f"Status {res.status}, Title: '{data['title']}', Sources: {len(data['sources'])}"

# Test 3: Get graph topology
def test_get_graph():
    res = urllib.request.urlopen(f"{base_url}/investigations/INV-2026-0011/graph")
    assert res.status == 200
    data = json.loads(res.read().decode("utf-8"))
    assert data["total_nodes"] >= 10, f"Expected >= 10 nodes, got {data['total_nodes']}"
    assert data["total_edges"] >= 9, f"Expected >= 9 edges, got {data['total_edges']}"
    return f"Status {res.status}, Nodes: {data['total_nodes']}, Edges: {data['total_edges']}"

# Test 4: Get timeline events
def test_get_timeline():
    res = urllib.request.urlopen(f"{base_url}/investigations/INV-2026-0011/timeline")
    assert res.status == 200
    data = json.loads(res.read().decode("utf-8"))
    assert data["total_events"] >= 5
    return f"Status {res.status}, Total events: {data['total_events']}"

# Test 5: 1-Hop Relationship Expansion
def test_1hop_expansion():
    res = urllib.request.urlopen(f"{base_url}/investigations/INV-2026-0011/objects/node-c11-hub/relationships")
    assert res.status == 200
    data = json.loads(res.read().decode("utf-8"))
    assert data["total_connected"] >= 4
    return f"Status {res.status}, 1-Hop Connected Entities: {data['total_connected']}, Edges: {len(data['edges'])}"

# Test 6: Missing investigation 404
def test_missing_404():
    try:
        urllib.request.urlopen(f"{base_url}/investigations/INV-DOES-NOT-EXIST")
        raise AssertionError("Expected 404 error")
    except urllib.error.HTTPError as e:
        assert e.code == 404
        return f"HTTP {e.code} correctly returned for missing dossier"

# Test 7: Invalid object ID 404
def test_invalid_object_404():
    try:
        urllib.request.urlopen(f"{base_url}/investigations/INV-2026-0011/objects/node-invalid-999")
        raise AssertionError("Expected 404 error")
    except urllib.error.HTTPError as e:
        assert e.code == 404
        return f"HTTP {e.code} correctly returned for invalid object"

# Test 8: Create new investigation (POST)
def test_create_investigation():
    payload = json.dumps({
        "title": "Operation Disconnection Lures (Electricity Extortion)",
        "description": "Urgent SMS claiming 9:30 PM power cutoff over unpaid bill.",
        "severity": "high",
        "tags": ["electricity_fraud", "urgency", "phone_ioc"]
    }).encode("utf-8")
    req = urllib.request.Request(f"{base_url}/investigations", data=payload, headers={"Content-Type": "application/json"})
    res = urllib.request.urlopen(req)
    assert res.status == 201
    created = json.loads(res.read().decode("utf-8"))
    assert created["id"].startswith("INV-")
    return f"Status {res.status}, Created: {created['id']} - '{created['title']}'"

# Test 9: HTML investigations directory
def test_html_directory():
    res = urllib.request.urlopen(f"{html_base}/investigations")
    assert res.status == 200
    html = res.read().decode("utf-8")
    assert len(html) > 5000
    return f"Status {res.status}, Length: {len(html)} bytes"

# Test 10: HTML investigation workspace
def test_html_workspace():
    res = urllib.request.urlopen(f"{html_base}/investigations/INV-2026-0011")
    assert res.status == 200
    html = res.read().decode("utf-8")
    assert len(html) > 5000
    return f"Status {res.status}, Length: {len(html)} bytes"

run_test("List Investigations", test_list_investigations)
run_test("Get Investigation Detail", test_get_detail)
run_test("Get Graph Topology", test_get_graph)
run_test("Get Timeline Events", test_get_timeline)
run_test("1-Hop Relationship Expansion", test_1hop_expansion)
run_test("Missing Investigation 404 Handling", test_missing_404)
run_test("Invalid Object 404 Handling", test_invalid_object_404)
run_test("Create Investigation (POST)", test_create_investigation)
run_test("Render Investigations Directory HTML", test_html_directory)
run_test("Render Investigation Workspace HTML", test_html_workspace)

print(f"\nIntegration Test Suite Finished: {len([r for r in results if r[1] == 'PASS'])} / {len(results)} PASSED.")
