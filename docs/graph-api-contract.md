# TRUSTLENS AI — Cyber Threat Investigation Graph API Contract

> **API Specification:** v1.2 (Live Production)  
> **Base Path:** `/api/v1/investigations`  
> **Protocol:** REST JSON / HTTP 1.1 / HTTP 2  
> **Backend Framework:** FastAPI 0.115+ with AsyncIOMotor & Pydantic v2  

---

## 1. Overview & Architectural Principles

The Investigation Graph API delivers structured, evidence-backed cyber threat dossiers for the ThreatQ-inspired TRUSTLENS AI investigation workspace.

Key principles:
1. **Zero Data Fabrication:** Every node, edge, and timeline event derives strictly from persisted database records (`analyses`, `scam_campaigns`, `threat_indicators`, `suspicious_urls`, `scam_reports`) or calibrated ML model inferences.
2. **Deterministic Provenance:** All nodes and edges carry explicit `source` and `evidence_reference` fields linking back to raw tokens, SHAP scores, or analysis UUIDs.
3. **1-Hop Relationship Expansion:** The graph expansion endpoint validates and discovers newly correlated entities sharing common infrastructure (domains, IPs, sender phones, UPI handles) from MongoDB without generating speculative multi-hop connections.

---

## 2. API Endpoints Specification

### 2.1 `GET /api/v1/investigations`
Lists active investigation dossiers with metadata and object counts.

**Query Parameters:**
- `status` (*string*, optional): Filter by `active | in_progress | mitigated | archived`
- `severity` (*string*, optional): Filter by `critical | high | medium | low`
- `limit` (*integer*, default: 50, min: 1, max: 100): Maximum dossiers to return

**Response (HTTP 200 OK):**
```json
[
  {
    "id": "INV-2026-0011",
    "title": "Banking KYC Smishing Syndicate (Cluster #11)",
    "description": "Multilingual Smishing campaign targeting State Bank of India customers with urgent account freeze alerts.",
    "status": "active",
    "severity": "critical",
    "created_at": "2026-11-22T18:44:00Z",
    "updated_at": "2026-11-24T16:44:00Z",
    "objects_count": 10,
    "tasks_count": 2,
    "comments_count": 0,
    "tags": ["sbi_kyc", "smishing", "model1_bilstm", "cluster_11"]
  }
]
```

---

### 2.2 `POST /api/v1/investigations`
Creates and persists a new investigation dossier in MongoDB Atlas.

**Request Body:**
```json
{
  "title": "Operation Disconnection Lures (Electricity Extortion)",
  "description": "Urgent SMS claiming 9:30 PM power cutoff over unpaid bill.",
  "severity": "high",
  "tags": ["electricity_fraud", "urgency", "phone_ioc"],
  "seed_campaign_id": 42
}
```

**Response (HTTP 201 Created):**
```json
{
  "id": "INV-2026-7E76",
  "title": "Operation Disconnection Lures (Electricity Extortion)",
  "description": "Urgent SMS claiming 9:30 PM power cutoff over unpaid bill.",
  "status": "active",
  "severity": "high",
  "created_at": "2026-11-24T18:45:00Z",
  "updated_at": "2026-11-24T18:45:00Z",
  "objects_count": 1,
  "tasks_count": 1,
  "comments_count": 0,
  "tags": ["electricity_fraud", "urgency", "phone_ioc"],
  "sources": ["Analyst Submissions", "TRUSTLENS Real-Time Telemetry"],
  "attributes": {
    "Investigator": "SOC Threat Lead",
    "Incident ID": "INV-2026-7E76"
  },
  "visibility": "Organization"
}
```

---

### 2.3 `GET /api/v1/investigations/{investigation_id}`
Retrieves detailed dossier metadata for a specific investigation.

**Path Parameters:**
- `investigation_id` (*string*): Unique investigation identifier (e.g. `INV-2026-0011`)

**Response (HTTP 200 OK):**
```json
{
  "id": "INV-2026-0011",
  "title": "Banking KYC Smishing Syndicate (Cluster #11)",
  "description": "Multilingual Smishing campaign targeting State Bank of India customers with urgent account freeze alerts.",
  "status": "active",
  "severity": "critical",
  "created_at": "2026-11-22T18:44:00Z",
  "updated_at": "2026-11-24T16:44:00Z",
  "objects_count": 10,
  "tasks_count": 2,
  "comments_count": 0,
  "tags": ["sbi_kyc", "smishing", "model1_bilstm", "cluster_11"],
  "sources": ["TRUSTLENS ML Telemetry", "ScamShield Corpus", "Community Report #07a380c7", "CERT-In"],
  "attributes": {
    "Targeted Institution": "State Bank of India (PSU Banking)",
    "Campaign Hub": "HDBSCAN Cluster #11",
    "Primary Attack Vector": "SMS Phishing with Urgency Coercion"
  },
  "visibility": "Organization"
}
```

**Errors:**
- `HTTP 404 Not Found` if `investigation_id` is invalid or not found.

---

### 2.4 `GET /api/v1/investigations/{investigation_id}/graph`
Retrieves all graph nodes, technical properties, and evidence-backed relationship edges.

**Response (HTTP 200 OK):**
```json
{
  "investigation_id": "INV-2026-0011",
  "total_nodes": 10,
  "total_edges": 9,
  "nodes": [
    {
      "id": "node-c11-hub",
      "type": "campaign_cluster",
      "label": "Campaign Cluster #11 (SBI / PSU KYC Lures)",
      "properties": {
        "cluster_id": 11,
        "cluster_size": 47,
        "cohesion_score": 0.884,
        "severity": "critical",
        "isCentral": true,
        "x": 0,
        "y": 0
      },
      "source": "HDBSCAN Clustering Model (Model 4)",
      "verification_status": "verified",
      "created_at": "2026-11-22T18:44:00Z"
    },
    {
      "id": "node-c11-url",
      "type": "url",
      "label": "http://sbi-kyc-update.com",
      "properties": {
        "url": "http://sbi-kyc-update.com",
        "domain": "sbi-kyc-update.com",
        "risk_score": 0.985,
        "severity": "critical"
      },
      "source": "Model 2 Lexical Phishing Detector",
      "verification_status": "verified",
      "created_at": "2026-11-22T18:44:00Z"
    }
  ],
  "edges": [
    {
      "id": "e11-1",
      "source": "node-c11-msg1",
      "target": "node-c11-url",
      "relationship_type": "contains_url",
      "evidence_reference": "Extracted regex URL from SMS text",
      "created_at": "2026-11-24T18:44:00Z"
    }
  ]
}
```

---

### 2.5 `GET /api/v1/investigations/{investigation_id}/timeline`
Retrieves chronological multi-track timeline events.

**Response (HTTP 200 OK):**
```json
{
  "investigation_id": "INV-2026-0011",
  "total_events": 6,
  "timeline": [
    {
      "id": "t11-1",
      "event_type": "situation",
      "title": "First Observed Smishing Wave",
      "description": "High-volume SMS dispatch detected across cellular circles.",
      "related_object_ids": ["node-c11-phone1", "node-c11-msg1"],
      "timestamp": "2026-11-22T14:44:00Z",
      "source": "Telemetry Ingestion"
    },
    {
      "id": "t11-6",
      "event_type": "task",
      "title": "CERT-In & ISP Takedown Initiated",
      "description": "Emergency abuse notices dispatched to upstream registrar and CERT-In.",
      "related_object_ids": ["node-c11-advisory", "node-c11-domain"],
      "timestamp": "2026-11-24T16:44:00Z",
      "source": "SOC Automation Engine"
    }
  ]
}
```

---

### 2.6 `GET /api/v1/investigations/{investigation_id}/objects/{object_id}`
Retrieves single object details and connected relationships count.

**Response (HTTP 200 OK):**
```json
{
  "investigation_id": "INV-2026-0011",
  "relationships_count": 4,
  "object": {
    "id": "node-c11-hub",
    "type": "campaign_cluster",
    "label": "Campaign Cluster #11 (SBI / PSU KYC Lures)",
    "properties": {
      "cluster_id": 11,
      "cluster_size": 47,
      "cohesion_score": 0.884,
      "severity": "critical"
    },
    "source": "HDBSCAN Clustering Model (Model 4)",
    "verification_status": "verified",
    "created_at": "2026-11-22T18:44:00Z"
  }
}
```

---

### 2.7 `GET /api/v1/investigations/{investigation_id}/objects/{object_id}/relationships`
**1-Hop Relationship Expansion Endpoint:**
Returns currently connected objects in the investigation, and queries MongoDB (`threat_indicators`, `analyses`, `suspicious_urls`) for additional unlinked entities sharing identical IOCs, domains, or phone numbers.

**Response (HTTP 200 OK):**
```json
{
  "investigation_id": "INV-2026-0011",
  "object_id": "node-c11-phone1",
  "total_connected": 5,
  "connected_nodes": [
    {
      "id": "node-c11-hub",
      "type": "campaign_cluster",
      "label": "Campaign Cluster #11 (SBI / PSU KYC Lures)",
      "properties": { "cluster_id": 11 },
      "source": "HDBSCAN Clustering Model (Model 4)",
      "verification_status": "verified",
      "created_at": "2026-11-22T18:44:00Z"
    }
  ],
  "edges": [
    {
      "id": "e11-7",
      "source": "node-c11-hub",
      "target": "node-c11-phone1",
      "relationship_type": "references_indicator",
      "evidence_reference": "Shared sender phone pool extracted from cluster sample",
      "created_at": "2026-11-24T18:44:00Z"
    }
  ]
}
```

---

## 3. Node & Edge Type Definitions

### Approved Node Types (10 Categories)
1. `campaign_cluster`: Central HDBSCAN unsupervised campaign hub.
2. `message`: Suspicious text communication (SMS, WhatsApp, Email).
3. `url`: Phishing or credential harvesting web address.
4. `domain`: FQDN / Registered domain infrastructure.
5. `ip`: Hosting server IPv4/IPv6 address.
6. `tactic`: Behavioral social engineering tactic (e.g. Urgency, Fake Job).
7. `threat_indicator`: Technical IOC (Phone number, UPI handle, hash).
8. `user_report`: Community crowd-sourced incident report.
9. `source_reference`: External threat intelligence authority (e.g. CERT-In, URLhaus).
10. `scam_category`: High-level taxonomy category (e.g. Financial Fraud, Utility Extortion).

### Approved Relationship Edge Types
- `belongs_to_cluster`: Entity assigned to an unsupervised campaign.
- `contains_url`: Message body contains a suspicious URL.
- `resolves_to`: Domain resolves to an IP address or URL resolves to a domain.
- `exhibits_tactic`: Communication exhibits a detected social engineering tactic.
- `references_indicator`: Campaign or message references a phone number or UPI handle.
- `reported_by`: Incident corroborated by a community victim report.
- `attributed_to`: Attributed to external intelligence advisory or advisory notice.
- `targets_entity`: Targeted brand or institutional victim.
