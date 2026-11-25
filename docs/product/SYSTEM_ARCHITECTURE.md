# TRUSTLENS AI — SYSTEM ARCHITECTURE

> **Stack:** Next.js 14 (Vercel) -> FastAPI Python 3.12 (Render Standard 2GB) -> MongoDB Atlas / Local -> Hosted n8n

---

## 1. Layered Architecture & Strict Boundaries

```mermaid
flowchart TB
    subgraph Presentation["Presentation Layer (Next.js 14)"]
        UI["Investigations / Analyze / Threat Library / Analytics / Reports"]
        PROXY["/api/v1/* Rewrite Proxy (next.config.mjs)"]
    end
    subgraph API["API & Security Layer (FastAPI)"]
        MW["CORS + SecurityHeaders + RateLimit + RequestLogging"]
        RT["v1 Domain Routers + Pydantic Validation + RBAC"]
    end
    subgraph Services["Business Logic & Evidence Layer"]
        SVC["Analysis / Investigation / ThreatLibrary / Analytics / Reporting / Automation"]
        RISK["TransparentRiskAggregationService"]
    end
    subgraph ML["ML Inference Layer (Python Only)"]
        LDR["CentralModelLoader (SHA-256) + Shared SentenceTransformer Singleton"]
        MOD["M1 LinearSVC | M2 XGBoost+SHAP | M3 OvR Tactics | M4 HDBSCAN"]
    end
    subgraph Data["Persistence & External"]
        DB[("MongoDB (11 Collections)")]
        N8N["n8n Orchestrator (6 Workflows — No Core ML)"]
    end

    UI --> PROXY --> MW --> RT --> SVC
    SVC --> RISK
    SVC --> LDR --> MOD
    SVC --> DB
    N8N -->|"Authenticated REST + Webhook Secret"| RT
```

## 2. Boundary Rules
- **n8n Responsibility:** Scheduling, webhook triggers, secret checks, HTTP retries, and routing only. All ML inference, deduplication, and risk scoring remain in Python services.
- **ML Runtime Constraint:** Shared `get_shared_sentence_transformer` singleton (`750.12 MB` RSS) requires Render Standard (`2 GB` RAM); `.joblib`/`.pt` binaries are excluded from Git and require persistent disk or startup object-storage sync.
