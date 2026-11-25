"""
TRUSTLENS AI - Phase 3.1: Structured Evidence Record Builder
Constructs standardized, provenance-preserving EvidenceRecord objects from:
- Text classifier, URL classifier, Tactic classifier, Campaign similarity
- External threat-intelligence matches, Human-reviewed community reports
"""

import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class EvidenceRecord(BaseModel):
    evidence_id: str = Field(..., description="Unique evidence item identifier")
    source: str = Field(..., description="Originating model, feed, or human analyst source")
    model_version: str = Field(..., description="Exact model or source version string")
    prediction: Any = Field(..., description="Original source prediction output (preserved)")
    confidence_status: str = Field(..., description="calibrated | uncalibrated | unavailable | human_verified | unverified")
    timestamp: str = Field(..., description="UTC ISO-8601 timestamp")
    verification_state: str = Field(..., description="verified | automated_inference | unverified | unavailable")
    explanation: str = Field(..., description="Human-readable rationale for this evidence")
    limitations: str = Field(..., description="Explicit limitations of this evidence source")
    raw_output: Optional[Dict[str, Any]] = Field(None, description="Unmodified original source payload")


def build_evidence_records(
    text_result: Optional[Dict[str, Any]] = None,
    url_result: Optional[Dict[str, Any]] = None,
    tactic_result: Optional[Dict[str, Any]] = None,
    campaign_result: Optional[Dict[str, Any]] = None,
    threat_intel_match: Optional[Dict[str, Any]] = None,
    community_report: Optional[Dict[str, Any]] = None,
) -> List[EvidenceRecord]:
    now_iso = datetime.now(timezone.utc).isoformat()
    records: List[EvidenceRecord] = []

    # 1. Text Classifier Evidence
    if text_result is not None:
        is_unavail = text_result.get("status") in ("unavailable", "error") or text_result.get("is_threat") is None
        records.append(EvidenceRecord(
            evidence_id=f"ev-text-{uuid.uuid4().hex[:8]}",
            source="TRUSTLENS Text Scam Classifier (Model 1)",
            model_version=str(text_result.get("model_version", "unavailable")),
            prediction="unavailable" if is_unavail else ("threat" if text_result.get("is_threat") else "legitimate"),
            confidence_status="unavailable" if is_unavail else "calibrated",
            timestamp=now_iso,
            verification_state="unavailable" if is_unavail else "automated_inference",
            explanation=(
                text_result.get("error", "Text classifier unavailable.")
                if is_unavail
                else f"Classified as {'threat' if text_result.get('is_threat') else 'legitimate'} "
                     f"(calibrated probability={text_result.get('confidence', 0.0):.4f}, "
                     f"language={text_result.get('detected_language', 'Unknown')})."
            ),
            limitations="TF-IDF linear features; lower semantic coverage on unseen languages outside En/Hi/Hinglish.",
            raw_output=text_result,
        ))

    # 2. URL Classifier Evidence
    if url_result is not None:
        is_unavail = url_result.get("status") in ("unavailable", "error") or url_result.get("is_phishing") is None
        records.append(EvidenceRecord(
            evidence_id=f"ev-url-{uuid.uuid4().hex[:8]}",
            source="TRUSTLENS Zero-Hop URL Classifier (Model 2)",
            model_version=str(url_result.get("model_version", "unavailable")),
            prediction="unavailable" if is_unavail else ("phishing" if url_result.get("is_phishing") else "legitimate"),
            confidence_status="unavailable" if is_unavail else "calibrated",
            timestamp=now_iso,
            verification_state="unavailable" if is_unavail else "automated_inference",
            explanation=(
                url_result.get("error", "URL classifier unavailable.")
                if is_unavail
                else f"Zero-hop lexical inspection scored phishing risk={url_result.get('risk_score', 0.0):.4f}."
            ),
            limitations="Lexical/structural features alone do not prove malice or guarantee safety.",
            raw_output=url_result,
        ))

    # 3. Tactic Classifier Evidence (Correlated with Text)
    if tactic_result is not None:
        is_unavail = tactic_result.get("status") in ("unavailable", "error")
        tactics = [t.get("tactic_name") for t in tactic_result.get("tactics", [])]
        records.append(EvidenceRecord(
            evidence_id=f"ev-tactic-{uuid.uuid4().hex[:8]}",
            source="TRUSTLENS Tactic Classifier (Model 3)",
            model_version=str(tactic_result.get("model_version", "unavailable")),
            prediction="unavailable" if is_unavail else (tactics if tactics else ["none_detected"]),
            confidence_status="unavailable" if is_unavail else "calibrated",
            timestamp=now_iso,
            verification_state="unavailable" if is_unavail else "automated_inference",
            explanation=(
                tactic_result.get("error", "Tactic classifier unavailable.")
                if is_unavail
                else f"Detected {len(tactics)} psychological coercion tactic(s): {', '.join(tactics) if tactics else 'None'}."
            ),
            limitations="Correlated with Model 1 text input; fake_investment tactic is blocked/unavailable.",
            raw_output=tactic_result,
        ))

    # 4. Campaign Similarity Evidence
    if campaign_result is not None:
        is_unavail = campaign_result.get("status") in ("unavailable", "error")
        sim = campaign_result.get("similarity_score", 0.0)
        matched = campaign_result.get("matched", False)
        records.append(EvidenceRecord(
            evidence_id=f"ev-campaign-{uuid.uuid4().hex[:8]}",
            source="TRUSTLENS Campaign Similarity Engine (Model 4)",
            model_version=str(campaign_result.get("model_version", "hdbscan-v1.0")),
            prediction="unavailable" if is_unavail else (f"cluster_{campaign_result.get('campaign_id')}" if matched else "novel_unclustered"),
            confidence_status="unavailable" if is_unavail else "uncalibrated",
            timestamp=now_iso,
            verification_state="unavailable" if is_unavail else "automated_inference",
            explanation=(
                campaign_result.get("error", "Campaign matcher unavailable.")
                if is_unavail
                else f"Cosine similarity={sim:.4f} against HDBSCAN campaign centroids (matched={matched})."
            ),
            limitations="Semantic similarity does not prove shared criminal organization or intent.",
            raw_output=campaign_result,
        ))

    # 5. External Threat Intelligence
    if threat_intel_match is not None:
        is_hit = bool(threat_intel_match.get("matched", False))
        records.append(EvidenceRecord(
            evidence_id=f"ev-ti-{uuid.uuid4().hex[:8]}",
            source=str(threat_intel_match.get("feed_name", "External Threat Intelligence")),
            model_version="threat-intel-lookup-v1",
            prediction="ioc_matched" if is_hit else "no_match_found",
            confidence_status="human_verified" if (is_hit and threat_intel_match.get("verified")) else "uncalibrated",
            timestamp=now_iso,
            verification_state="verified" if (is_hit and threat_intel_match.get("verified")) else "unverified",
            explanation=(
                f"Matched known IOC in {threat_intel_match.get('feed_name', 'feed')}."
                if is_hit
                else "No external threat-intelligence match found. Absence of a match does NOT guarantee safety."
            ),
            limitations="External feeds have ingestion lag; novel/zero-day phishing URLs are frequently absent.",
            raw_output=threat_intel_match,
        ))

    # 6. Human-Reviewed / Community Report
    if community_report is not None:
        rev_status = str(community_report.get("review_status", "unverified")).lower()
        is_verified_scam = rev_status == "verified_scam"
        is_verified_benign = rev_status == "benign"
        records.append(EvidenceRecord(
            evidence_id=f"ev-report-{uuid.uuid4().hex[:8]}",
            source=f"Community Report ({community_report.get('report_id', 'unknown')})",
            model_version="human-review-workflow-v1",
            prediction=rev_status,
            confidence_status="human_verified" if (is_verified_scam or is_verified_benign) else "unverified",
            timestamp=now_iso,
            verification_state="verified" if (is_verified_scam or is_verified_benign) else "unverified",
            explanation=(
                f"Human-adjudicated report verdict: {rev_status}."
                if (is_verified_scam or is_verified_benign)
                else f"Unverified community submission (status={rev_status}); treated as non-authoritative."
            ),
            limitations="Unverified user submissions may contain false reports or benign misunderstandings.",
            raw_output=community_report,
        ))

    return records
