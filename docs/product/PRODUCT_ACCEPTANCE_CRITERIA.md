# TRUSTLENS AI — PRODUCT ACCEPTANCE CRITERIA

---

1. **Live ML Traceability:** Every valid message, URL, or readable screenshot submission reaches FastAPI, executes the SHA-256 verified ML models, and returns `model_version`, evidence, and `limitations`.
2. **No Fabricated Safety or Confidence:** Missing threat-intel matches never display as "safe"; unavailable models return `"unavailable"`; low-token/unreadable inputs return `"inconclusive"` or `"insufficient-evidence"`.
3. **Provenance Distinction:** UI and reports visibly distinguish **ML Prediction**, **Threat Intel Match**, and **Human Review**.
4. **Persistent Investigations:** Created investigations (`POST /api/v1/investigations`) and graph/timeline records persist in MongoDB across restarts; 1-hop expansion returns real stored links or explicitly labeled similarity candidates.
5. **RBAC Enforcement:** Unauthenticated users receive `401` on `/analyses` and private exports; `role: "user"` receives `403` on `/reports/{id}/review` and `/training/jobs`; non-admins receive `403` on `/training/jobs/{id}/promote`.
6. **Zero-Hop URL Guarantee:** URL analysis performs lexical feature extraction only, with zero outbound network connections to submitted URLs.
7. **Export Integrity:** JSON (`trustlens-json-v1`) and STIX 2.1 exports validate strictly (`spec_version: "2.1"`, `misp_interoperability_claimed: false`).
