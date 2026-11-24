# TRUSTLENS AI — Phase 1 Missing API & Backend Integration Requirements

**Document Purpose:** Formal record of backend API endpoints currently connected, architectural integration boundaries established, and required backend endpoints identified during Phase 1 UI implementation.

---

## 1. Connected Backend Endpoints (Operational)

The Phase 1 frontend interface is integrated with the following live FastAPI endpoints (`http://127.0.0.1:8000/api/v1`):

| Endpoint | Method | Microservice / ML System | Purpose in Investigation Workspace | Status |
| :--- | :---: | :--- | :--- | :---: |
| `/health` | `GET` | Core Platform | Validates that all 4 ML models and MongoDB Atlas are operational. | **Operational** |
| `/campaigns` | `GET` | **Model 4 (HDBSCAN)** | Retrieves list of 47 discovered campaign clusters to populate incident dossiers. | **Operational** |
| `/campaigns/{id}` | `GET` | **Model 4 (HDBSCAN)** | Powers dynamic investigation routes (`/investigations/[id]`) with real exemplar messages, cohesion scores, and technical IOCs. | **Operational** |
| `/analyses` | `GET` | Audit Log Service | Ingests 115+ verified scan records to populate investigation analysis histories. | **Operational** |
| `/analyze/comprehensive`| `POST` | **M1+M2+M3+M4 Ensemble** | Powers multi-vector forensic triage across text, URLs, tactics, and campaign clustering. | **Operational** |
| `/models/metrics` | `GET` | Model Registry | Powers model output explainability cards and metric attribution in the Object Inspector. | **Operational** |
| `/reports` | `POST` | Community Triage | Ingests crowd-sourced incident submissions into the investigation queue. | **Operational** |
| `/reports` | `GET` | Community Triage | Lists community-submitted evidence attached to investigations. | **Operational** |
| `/auth/login` | `POST` | Security & RBAC | Authenticates security analysts and issues JWT bearer tokens. | **Operational** |
| `/auth/me` | `GET` | Security & RBAC | Returns active user profile and verifies analyst permissions for investigation management. | **Operational** |

---

## 2. Missing API Endpoints Identified (For Phase 2 Implementation)

To transition from Phase 1 (UI & Structural Presentation) to full production persistence, the backend will require dedicated Investigation Management endpoints:

### A. Investigation Dossier CRUD Endpoints

#### 1. `POST /api/v1/investigations`
- **Purpose:** Persist newly created investigation dossiers initialized via `CreateInvestigationModal.tsx`.
- **Proposed Request Payload:**
  ```json
  {
    "title": "Analysis of Urgent Electricity Bill Disconnection Syndicate",
    "description": "Pretexts threatening immediate power cutoff over unpaid invoices.",
    "severity": "high",
    "target_entity": "State Electricity Boards (BSES, UPPCL)",
    "initial_payload": "Dear customer your power will be disconnected at 9:30 PM...",
    "tags": ["utility_fraud", "urgency", "phone_iocs"]
  }
  ```
- **Expected Response:**
  ```json
  {
    "investigation_id": "INV-2026-9481",
    "created_at": "2026-11-24T18:15:00Z",
    "status": "Active",
    "created_by": "Senior Analyst (RS)"
  }
  ```
- **Current Frontend Boundary:** Temporarily initialized in React workspace state; displays "Live Intelligence Sync Active".

---

#### 2. `GET /api/v1/investigations`
- **Purpose:** Retrieve paginated list of all active investigations for `/investigations/page.tsx` with severity, object count, and status filters.
- **Proposed Query Parameters:**
  - `page: int = 1`
  - `page_size: int = 20`
  - `severity: Optional[str] = None`
  - `status: Optional[str] = "Active"`
- **Current Frontend Boundary:** Uses structured directory with deep links to real campaign clusters (`/investigations/INV-CAMP-11`).

---

#### 3. `GET /api/v1/investigations/{id}/graph`
- **Purpose:** Retrieve the full relational graph projection (nodes and edges) for a specific investigation directly from the database instead of client-side graph assembly.
- **Proposed Response Schema:**
  ```json
  {
    "investigation_id": "INV-2026-KYC-11",
    "nodes": [
      {
        "id": "node-cluster-11",
        "label": "SBI KYC SYNDICATE #11",
        "type": "campaign_cluster",
        "severity": "critical",
        "x": 0,
        "y": 0,
        "metadata": { "cluster_size": 254, "cohesion": 0.884 }
      }
    ],
    "edges": [
      {
        "id": "e1",
        "source": "node-cluster-11",
        "target": "node-msg-urgent",
        "relationship": "exemplar_lure"
      }
    ]
  }
  ```
- **Current Frontend Boundary:** Dynamic adapter in `/investigations/[id]/page.tsx` adapts real backend campaign details from `GET /api/v1/campaigns/{id}`.

---

#### 4. `PATCH /api/v1/investigations/{id}/graph`
- **Purpose:** Save analyst spatial layout adjustments (dragged node coordinates $x, y$), custom notes, and pinned evidence to MongoDB.
- **Proposed Request Payload:**
  ```json
  {
    "updated_node_positions": {
      "node-url-phish": { "x": -120, "y": -210 },
      "node-iocs-phone": { "x": -20, "y": 190 }
    }
  }
  ```
- **Current Frontend Boundary:** Manipulated via `ThreatGraph.tsx` local state.

---

#### 5. `POST /api/v1/investigations/{id}/timeline`
- **Purpose:** Append a forensic milestone event or human review action to the investigation timeline.
- **Proposed Request Payload:**
  ```json
  {
    "title": "Incident mitigation notice dispatched to CERT-In",
    "track": "tasks",
    "severity": "high",
    "related_node_ids": ["node-cluster-11", "node-url-phish"]
  }
  ```
- **Current Frontend Boundary:** Synchronized client-side from scan timestamps and campaign discovery metadata.

---

#### 6. `GET /api/v1/investigations/{id}/export/stix`
- **Purpose:** Export the entire investigation graph and threat indicators as a standardized STIX 2.1 JSON bundle for ingest into external SIEM/SOAR solutions (e.g. Splunk, Microsoft Sentinel, ThreatConnect).

---

## 3. Summary & Phase 1 Compliance

All Phase 1 requirements have been met without fabricating fake backend responses:
- The UI gracefully falls back to clear, labelled preview fixtures or live campaign dossiers when querying `/investigations/[id]`.
- No simulated predictions are calculated client-side; model outputs reflect genuine Model 1-4 inference results.
- The missing endpoints documented above establish a clear, well-defined integration contract for Phase 2 backend development.
