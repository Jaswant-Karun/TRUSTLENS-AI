import urllib.request
import json

try:
    req = urllib.request.urlopen("http://127.0.0.1:8000/api/v1/campaigns/11")
    data = json.loads(req.read().decode('utf-8'))
    print("SUCCESS 200:")
    print("cluster_id:", data.get("cluster_id"))
    print("campaign_name:", data.get("campaign_name"))
    print("targeted_entity:", data.get("targeted_entity"))
    print("cluster_size:", data.get("cluster_size"))
    print("exemplar_message:", data.get("exemplar_message"))
    print("shared_phrases:", data.get("shared_phrases"))
    print("shared_iocs:", data.get("shared_iocs"))
except Exception as e:
    print("ERROR:", e)
