import urllib.request
import urllib.parse
import json

base_url = "http://127.0.0.1:8000/api/v1"

def test_api():
    print("Testing GET /investigations...")
    res = urllib.request.urlopen(f"{base_url}/investigations")
    invs = json.loads(res.read().decode("utf-8"))
    print(f"  Status: {res.status}, Count: {len(invs)}")
    for inv in invs:
        print(f"  - [{inv['id']}] {inv['title']} (Severity: {inv.get('severity')}, Objects: {inv.get('objects_count')})")
        
    sample_id = invs[0]["id"]
    print(f"\nTesting GET /investigations/{sample_id}...")
    res = urllib.request.urlopen(f"{base_url}/investigations/{sample_id}")
    detail = json.loads(res.read().decode("utf-8"))
    print(f"  Status: {res.status}, Title: {detail['title']}, Sources: {detail.get('sources')}")

    print(f"\nTesting GET /investigations/{sample_id}/graph...")
    res = urllib.request.urlopen(f"{base_url}/investigations/{sample_id}/graph")
    graph = json.loads(res.read().decode("utf-8"))
    print(f"  Status: {res.status}, Nodes: {graph['total_nodes']}, Edges: {graph['total_edges']}")
    if graph["nodes"]:
        print(f"  First node: {graph['nodes'][0]['id']} ({graph['nodes'][0]['type']}) - {graph['nodes'][0]['label']}")

    print(f"\nTesting GET /investigations/{sample_id}/timeline...")
    res = urllib.request.urlopen(f"{base_url}/investigations/{sample_id}/timeline")
    timeline = json.loads(res.read().decode("utf-8"))
    print(f"  Status: {res.status}, Events: {timeline['total_events']}")
    if timeline["timeline"]:
        print(f"  First event: {timeline['timeline'][0]['title']} ({timeline['timeline'][0]['event_type']})")

    first_node_id = graph["nodes"][0]["id"]
    print(f"\nTesting GET /investigations/{sample_id}/objects/{first_node_id}...")
    res = urllib.request.urlopen(f"{base_url}/investigations/{sample_id}/objects/{first_node_id}")
    obj_data = json.loads(res.read().decode("utf-8"))
    print(f"  Status: {res.status}, Object: {obj_data['object']['label']}, Connected: {obj_data['relationships_count']}")

    print(f"\nTesting GET /investigations/{sample_id}/objects/{first_node_id}/relationships...")
    res = urllib.request.urlopen(f"{base_url}/investigations/{sample_id}/objects/{first_node_id}/relationships")
    rels = json.loads(res.read().decode("utf-8"))
    print(f"  Status: {res.status}, Connected Nodes: {rels['total_connected']}, Edges: {len(rels['edges'])}")

    print(f"\nTesting POST /investigations...")
    post_payload = json.dumps({
        "title": "UPI QR Code Job Offer Extortion Ring",
        "description": "Cross-platform UPI payment extraction lures observed in victim reports.",
        "severity": "high",
        "tags": ["upi_fraud", "qr_code", "extortion"]
    }).encode("utf-8")
    req = urllib.request.Request(f"{base_url}/investigations", data=post_payload, headers={"Content-Type": "application/json"})
    res = urllib.request.urlopen(req)
    created = json.loads(res.read().decode("utf-8"))
    print(f"  Status: {res.status}, Created ID: {created['id']}, Title: {created['title']}")

test_api()
