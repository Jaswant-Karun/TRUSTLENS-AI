"""
TRUSTLENS AI - Phase 3.1: Unified Fraud Risk Assessment & Evidence Aggregator
Implements documented, calibration-aware risk aggregation:
- Prevents double-counting correlated text/tactic signals.
- Detects missing primary models or irreconcilable conflicts -> returns INCONCLUSIVE.
- Distinguishes verified threat-intel/human-reviewed reports from unverified submissions.
- Never treats missing threat-intel or LOW status as a guarantee of safety.
"""

from typing import Dict, Any, List, Optional
from ml.risk_engine.evidence import EvidenceRecord, build_evidence_records


class UnifiedRiskEngine:
    """Policy-driven risk aggregator across ML models, TI feeds, and human reviews."""

    POLICY_VERSION = "3.1.0"

    def assess(
        self,
        text_result: Optional[Dict[str, Any]] = None,
        url_result: Optional[Dict[str, Any]] = None,
        tactic_result: Optional[Dict[str, Any]] = None,
        campaign_result: Optional[Dict[str, Any]] = None,
        threat_intel_match: Optional[Dict[str, Any]] = None,
        community_report: Optional[Dict[str, Any]] = None,
        input_type: str = "text",
    ) -> Dict[str, Any]:
        evidence_records: List[EvidenceRecord] = build_evidence_records(
            text_result=text_result,
            url_result=url_result,
            tactic_result=tactic_result,
            campaign_result=campaign_result,
            threat_intel_match=threat_intel_match,
            community_report=community_report,
        )

        # 1. Check availability of primary model for the given input_type
        text_unavail = text_result is not None and (
            text_result.get("status") in ("unavailable", "error") or text_result.get("is_threat") is None
        )
        url_unavail = url_result is not None and (
            url_result.get("status") in ("unavailable", "error") or url_result.get("is_phishing") is None
        )

        # Verified independent overrides
        ti_verified_hit = bool(
            threat_intel_match and threat_intel_match.get("matched") and threat_intel_match.get("verified", True)
        )
        human_verified_scam = bool(
            community_report and str(community_report.get("review_status", "")).lower() == "verified_scam"
        )
        human_verified_benign = bool(
            community_report and str(community_report.get("review_status", "")).lower() == "benign"
        )

        # Missing primary model without verified human/TI override -> INCONCLUSIVE
        if (input_type == "text" and (text_result is None or text_unavail)) and not (ti_verified_hit or human_verified_scam):
            return self._build_response(
                status="INCONCLUSIVE",
                score=None,
                rationale="Primary Text Scam Classifier is unavailable and no verified threat-intelligence or human adjudication exists.",
                conflicts=["Primary model unavailable"],
                evidence_records=evidence_records,
            )

        if (input_type == "url" and (url_result is None or url_unavail)) and not (ti_verified_hit or human_verified_scam):
            return self._build_response(
                status="INCONCLUSIVE",
                score=None,
                rationale="Primary URL Phishing Classifier is unavailable and no verified threat-intelligence or human adjudication exists.",
                conflicts=["Primary model unavailable"],
                evidence_records=evidence_records,
            )

        # 2. Extract independent calibrated probabilities
        text_prob: Optional[float] = None
        if text_result and not text_unavail:
            raw_conf = float(text_result.get("confidence", 0.5))
            text_prob = raw_conf if text_result.get("is_threat") else (1.0 - raw_conf)

        url_prob: Optional[float] = None
        if url_result and not url_unavail:
            url_prob = float(url_result.get("risk_score", 0.0))

        # 3. Detect Conflicting Signals
        conflicts: List[str] = []
        if text_prob is not None and url_prob is not None:
            if text_prob < 0.25 and url_prob >= 0.80:
                conflicts.append("Text classifier scored benign (<0.25) while embedded URL scored high phishing risk (>=0.80).")
            elif text_prob >= 0.80 and url_prob < 0.20:
                conflicts.append("Text classifier scored high threat (>=0.80) while embedded URL scored low lexical risk (<0.20).")

        tactic_count = len(tactic_result.get("tactics", [])) if (tactic_result and tactic_result.get("status") != "unavailable") else 0
        if text_prob is not None and text_prob < 0.25 and tactic_count >= 2:
            conflicts.append(f"Text classifier scored benign ({text_prob:.2f}) while Tactic classifier detected {tactic_count} coercion tactics.")

        if human_verified_benign and ((text_prob and text_prob >= 0.75) or (url_prob and url_prob >= 0.75)):
            conflicts.append("Human reviewer adjudicated benign, conflicting with high automated ML threat score.")

        # 4. Policy-Driven Aggregation (No arbitrary averaging; no double-counting correlated text+tactic)
        # Base score comes from the strongest independent calibrated signal (Text vs URL)
        base_score = 0.0
        if text_prob is not None and url_prob is not None:
            # Independent modalities: use max calibrated risk (a benign message carrying a phishing URL is still high risk)
            base_score = max(text_prob, url_prob)
        elif url_prob is not None:
            base_score = url_prob
        elif text_prob is not None:
            base_score = text_prob

        # Correlated Tactic corroboration: bounded modifier (+0.05 max) ONLY if text_prob >= 0.35 (prevents double-counting or false escalation on benign text)
        tactic_modifier = 0.0
        if tactic_count > 0 and base_score >= 0.35:
            tactic_modifier = min(0.05, 0.025 * tactic_count)

        # Campaign similarity corroboration: bounded modifier (+0.05 max) ONLY if matched=True and similarity >= 0.75
        campaign_modifier = 0.0
        if campaign_result and campaign_result.get("matched") and float(campaign_result.get("similarity_score", 0.0)) >= 0.75:
            if base_score >= 0.35:
                campaign_modifier = 0.05

        aggregated_score = min(1.0, round(base_score + tactic_modifier + campaign_modifier, 4))

        # Independent verified overrides
        if ti_verified_hit or human_verified_scam:
            aggregated_score = max(aggregated_score, 0.90)

        # Unverified community report note (does NOT raise score)
        unverified_note = ""
        if community_report and not (human_verified_scam or human_verified_benign):
            unverified_note = " An unverified community report is attached for analyst context only and did not alter the risk score."

        # Conflict -> INCONCLUSIVE if human adjudication conflicts with ML OR severe text-vs-tactic conflict in uncertain band
        if human_verified_benign and base_score >= 0.75:
            return self._build_response(
                status="INCONCLUSIVE",
                score=aggregated_score,
                rationale="Conflict between human benign adjudication and high automated ML risk score requires senior analyst review.",
                conflicts=conflicts,
                evidence_records=evidence_records,
            )

        if text_prob is not None and 0.20 <= text_prob <= 0.55 and tactic_count >= 2 and not (ti_verified_hit or human_verified_scam or (url_prob and url_prob >= 0.75)):
            return self._build_response(
                status="INCONCLUSIVE",
                score=aggregated_score,
                rationale=f"Ambiguous text signal ({text_prob:.2f}) conflicts with {tactic_count} detected coercion tactics; manual review required." + unverified_note,
                conflicts=conflicts,
                evidence_records=evidence_records,
            )

        # 5. Map Aggregated Score to Policy Statuses
        if aggregated_score >= 0.85:
            status = "CRITICAL"
            rationale = f"High-confidence threat signal (score={aggregated_score:.4f}) corroborated by independent evidence." + unverified_note
        elif aggregated_score >= 0.65:
            status = "HIGH"
            rationale = f"Strong threat indicators detected (score={aggregated_score:.4f})." + unverified_note
        elif aggregated_score >= 0.35:
            status = "MODERATE"
            rationale = f"Moderate or borderline suspicious indicators detected (score={aggregated_score:.4f}). Exercise caution." + unverified_note
        else:
            status = "LOW"
            rationale = (
                f"Low automated risk indicators (score={aggregated_score:.4f}). "
                "NOTE: LOW status is not a guarantee of safety, especially for novel URLs without threat-intelligence matches."
                + unverified_note
            )

        return self._build_response(
            status=status,
            score=aggregated_score,
            rationale=rationale,
            conflicts=conflicts,
            evidence_records=evidence_records,
        )

    def _build_response(
        self,
        status: str,
        score: Optional[float],
        rationale: str,
        conflicts: List[str],
        evidence_records: List[EvidenceRecord],
    ) -> Dict[str, Any]:
        return {
            "policy_version": self.POLICY_VERSION,
            "risk_status": status,
            "aggregated_risk_score": score,
            "is_safety_guarantee": False,
            "rationale": rationale,
            "conflicts_detected": conflicts,
            "evidence_count": len(evidence_records),
            "evidence_records": [e.model_dump() for e in evidence_records],
            "safety_disclaimer": (
                "Automated risk statuses (including LOW) do not guarantee safety. "
                "Absence of an external threat-intelligence match never certifies an unknown URL as safe."
            ),
        }


unified_risk_engine = UnifiedRiskEngine()
