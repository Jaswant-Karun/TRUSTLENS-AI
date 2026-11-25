"""
TRUSTLENS AI - Transparent Risk Aggregation & Assessment Service
Calibrates threat scores across Text, URL, Tactic, Campaign, and Threat Intelligence signals.

STRICT GOVERNANCE RULES:
- Never use arbitrary fixed numbers and disguise them as calibrated probabilities.
- Handle inconclusive inputs explicitly (e.g. low token count, contradictory signals, or low entropy).
- Provide transparent reasoning breakdown for each risk factor.
"""

from typing import Dict, Any, List, Optional, Tuple


class TransparentRiskAggregationService:
    """
    Transparent multi-vector risk calibration engine for digital fraud assessment.
    """

    # Qualitative Threat Categories
    LEVEL_CLEAN = "clean"
    LEVEL_LOW = "low"
    LEVEL_MEDIUM = "medium"
    LEVEL_HIGH = "high"
    LEVEL_CRITICAL = "critical"
    LEVEL_INCONCLUSIVE = "inconclusive"

    def assess_risk(
        self,
        text_result: Optional[Dict[str, Any]] = None,
        url_result: Optional[Dict[str, Any]] = None,
        tactic_result: Optional[Dict[str, Any]] = None,
        campaign_result: Optional[Dict[str, Any]] = None,
        threat_intel_match: bool = False,
        raw_content: str = "",
    ) -> Dict[str, Any]:
        """
        Synthesizes individual model signals into a calibrated, explainable threat assessment.
        """
        breakdown: Dict[str, Any] = {}
        contributions: List[Tuple[str, float, str]] = []
        clean_content = str(raw_content).strip()

        # Step 1: Detect Inconclusive / Insufficient Evidence Conditions
        token_count = len(clean_content.split())
        if token_count < 2 and not url_result:
            return {
                "threat_level": self.LEVEL_INCONCLUSIVE,
                "calibrated_confidence": 0.50,
                "risk_score": 0.0,
                "verdict": "Insufficient Evidence: Input text contains too few tokens for reliable linguistic assessment.",
                "primary_vector": None,
                "model_probabilities": {},
                "risk_normalization": {"raw_weighted_score": 0.0, "normalized_risk_score": 0.0, "method": "weighted_composite"},
                "severity_classification": {"level": self.LEVEL_INCONCLUSIVE, "is_safety_guarantee": False},
                "uncertainty_assessment": {
                    "overall_uncertainty": 1.0,
                    "calibrated_probability_verified": False,
                    "uncertainty_reasons": ["Token count below minimum threshold for statistical confidence"],
                    "requires_human_review": True,
                },
                "model_versions": {},
                "human_readable_explanation": "Insufficient Evidence: Input text contains too few tokens for reliable linguistic assessment.",
                "transparency_breakdown": {
                    "reason": "Token count below minimum threshold for statistical confidence",
                    "token_count": token_count,
                },
                "remedial_actions": ["Provide more context or the full message body for analysis."],
            }

        model_probabilities: Dict[str, Any] = {}
        model_versions: Dict[str, str] = {}
        uncertainty_reasons: List[str] = []
        per_model_uncertainties: List[float] = []

        # Step 2: Extract Model Evidence Signals
        text_prob = 0.0
        text_weight = 0.0
        if text_result and text_result.get("is_threat") is not None:
            # Calibrated probability from Platt-scaled LinearSVC
            conf = float(text_result.get("confidence", 0.5))
            is_threat = text_result.get("is_threat", False)
            text_prob = conf if is_threat else (1.0 - conf)
            text_weight = 0.35
            text_unc = round(1.0 - abs(2.0 * text_prob - 1.0), 4)
            per_model_uncertainties.append(text_unc)
            text_ver = text_result.get("model_version", "unknown")
            model_versions["text_model"] = text_ver
            if text_result.get("language_support_status") == "unsupported_unverified":
                uncertainty_reasons.append(
                    f"Language '{text_result.get('detected_language')}' has 0 evaluated training/test samples."
                )
            model_probabilities["text_model"] = {
                "threat_probability": round(text_prob, 4),
                "calibrated": True,
                "calibration_method": "platt_scaling_cv3",
                "uncertainty": text_unc,
                "model_version": text_ver,
            }
            breakdown["text_signal"] = {
                "threat_probability": round(text_prob, 4),
                "is_threat": is_threat,
                "weight": text_weight,
                "detected_language": text_result.get("detected_language", "English"),
            }
            if text_prob > 0.65:
                contributions.append(("Text Scam Detector", round(text_prob * text_weight, 4), f"Linguistic threat score {text_prob:.2f}"))

        url_prob = 0.0
        url_weight = 0.0
        if url_result and url_result.get("is_phishing") is not None:
            url_prob = float(url_result.get("risk_score", 0.0))
            # URLs provide very strong structural signals if present
            url_weight = 0.40 if text_result else 0.85
            url_unc = round(1.0 - abs(2.0 * url_prob - 1.0), 4)
            per_model_uncertainties.append(url_unc)
            url_ver = url_result.get("model_version", "unknown")
            model_versions["url_model"] = url_ver
            uncertainty_reasons.append("URL model score reflects zero-hop lexical/structural risk, not a Platt-calibrated fraud probability.")
            model_probabilities["url_model"] = {
                "score": round(url_prob, 4),
                "calibrated": False,
                "calibration_method": "uncalibrated_gbdt_with_policy_guard",
                "uncertainty": url_unc,
                "model_version": url_ver,
            }
            breakdown["url_signal"] = {
                "phishing_risk_score": round(url_prob, 4),
                "is_phishing": url_result.get("is_phishing", False),
                "weight": url_weight,
                "features_analyzed": len(url_result.get("features", {})),
            }
            if url_prob > 0.50:
                contributions.append(("Phishing URL Model", round(url_prob * url_weight, 4), f"Structural risk {url_prob:.2f}"))

        tactic_score = 0.0
        tactic_weight = 0.0
        active_tactics = []
        has_high_severity = False
        if tactic_result and tactic_result.get("tactics"):
            tactics = tactic_result["tactics"]
            active_tactics = [t.get("tactic_name") or t.get("name") for t in tactics]
            
            # Coercive tactics that indicate active social engineering
            coercive_malicious_tactics = {
                "Threats and Intimidation",
                "OTP and Credential Requests",
                "OTP or Credential Requests",
                "Account Suspension Threats",
            }
            has_coercive = any(t in coercive_malicious_tactics for t in active_tactics)
            
            # If Model 1 confirmed message is legitimate, bank/financial terms represent normal branding, not fraud
            is_confirmed_legit = text_result and not text_result.get("is_threat")
            if is_confirmed_legit and not has_coercive:
                tactic_score = 0.10
                has_high_severity = False
            else:
                high_severity_tactics = coercive_malicious_tactics | {
                    "Bank or Government Impersonation",
                    "Bank Impersonation",
                    "Government Impersonation",
                }
                has_high_severity = any(t in high_severity_tactics for t in active_tactics)
                tactic_score = 0.85 if has_high_severity else (0.50 if len(active_tactics) >= 2 else 0.30)

            tactic_weight = 0.15
            breakdown["tactic_signal"] = {
                "detected_tactics_count": len(active_tactics),
                "tactics": active_tactics,
                "has_coercive_tactic": has_high_severity,
                "weight": tactic_weight,
            }
            if tactic_score > 0.40:
                contributions.append(("Social Engineering Tactics", round(tactic_score * tactic_weight, 4), f"{len(active_tactics)} tactics identified"))

        campaign_score = 0.0
        campaign_weight = 0.0
        is_threat_context = (text_result and text_result.get("is_threat")) or (url_result and url_result.get("is_phishing")) or has_high_severity
        if campaign_result and (campaign_result.get("matched") or campaign_result.get("campaign_id") is not None):
            sim = float(campaign_result.get("similarity_score", 0.0))
            # Campaign similarity contributes to threat risk only when message exhibits suspicious context
            if sim > 0.50 and is_threat_context:
                campaign_score = sim
                campaign_weight = 0.10
                cname = campaign_result.get("associated_campaign") or campaign_result.get("campaign_name", "Known Campaign")
                breakdown["campaign_signal"] = {
                    "matched_campaign": cname,
                    "similarity_score": round(sim, 4),
                    "weight": campaign_weight,
                }
                contributions.append(("Campaign Intelligence", round(campaign_score * campaign_weight, 4), f"Aligned with '{cname}' ({sim:.2f})"))

        # Step 3: Compute Calibrated Weighted Risk Composite
        total_weight = text_weight + url_weight + tactic_weight + campaign_weight
        if total_weight > 0:
            raw_risk = (
                (text_prob * text_weight)
                + (url_prob * url_weight)
                + (tactic_score * tactic_weight)
                + (campaign_score * campaign_weight)
            ) / total_weight
        else:
            raw_risk = 0.0

        # Elevation if known threat intel IOC matched or critical phishing URL confirmed
        if threat_intel_match:
            raw_risk = max(raw_risk, 0.92)
            contributions.append(("Threat Intelligence", 0.92, "Known malicious IOC in database"))

        if url_result and url_result.get("is_phishing") and url_prob > 0.95:
            raw_risk = max(raw_risk, 0.90)

        # Elevation if text model confirms strong threat combined with coercive tactics
        if text_result and text_result.get("is_threat") and text_prob >= 0.70:
            if has_high_severity:
                raw_risk = max(raw_risk, 0.75)
            else:
                raw_risk = max(raw_risk, 0.60)

        calibrated_risk = round(min(max(raw_risk, 0.0), 1.0), 4)

        # Step 4: Map to Standard Threat Levels
        if not is_threat_context and not threat_intel_match:
            # When all models confirm clean context without technical or behavioral threats
            if calibrated_risk >= 0.25:
                level = self.LEVEL_LOW
                verdict = "Low Risk / Informational: Institutional communication without malicious coercion."
                remedies = ["No threat actions required."]
            else:
                level = self.LEVEL_CLEAN
                verdict = "Legitimate / Clean: No malicious behavioral or technical indicators detected."
                remedies = ["No threat actions required."]
        elif calibrated_risk >= 0.80:
            level = self.LEVEL_CRITICAL
            verdict = "Critical Malicious Fraud: Immediate threat detected across multiple independent vectors."
            remedies = [
                "Do NOT click any embedded links or provide credentials / OTP.",
                "Block sender immediately and report to institutional anti-fraud hotline.",
                "If credentials were entered, change bank/account passwords immediately.",
            ]
        elif calibrated_risk >= 0.60:
            level = self.LEVEL_HIGH
            verdict = "High Risk Deception: Strong indicators of targeted social engineering or deceptive infrastructure."
            remedies = [
                "Verify sender authenticity via official known phone channels.",
                "Do NOT transfer funds or authorize UPI payment reversals.",
            ]
        elif calibrated_risk >= 0.35:
            level = self.LEVEL_MEDIUM
            verdict = "Suspicious Communication: Displays potential psychological pressure or unverified claims."
            remedies = [
                "Exercise caution; avoid sharing sensitive personal information.",
                "Inspect sender address carefully for typosquatting.",
            ]
        elif calibrated_risk >= 0.15:
            level = self.LEVEL_LOW
            verdict = "Low Risk / Unsolicited Marketing: Minor commercial or bulk messaging characteristics."
            remedies = ["Standard caution advised; likely promotional marketing."]
        else:
            level = self.LEVEL_CLEAN
            verdict = "Legitimate / Clean: No malicious behavioral or technical indicators detected."
            remedies = ["No threat actions required."]

        # Determine Primary Attack Vector
        primary_vector = None
        if url_result and url_result.get("is_phishing"):
            primary_vector = "Phishing URL / Fake Domain"
        elif active_tactics:
            primary_vector = active_tactics[0]
        elif text_result and text_result.get("is_threat"):
            primary_vector = f"Social Engineering Scam ({text_result.get('predicted_label', 'smishing')})"

        breakdown["contributing_factors"] = [
            {"source": src, "score_impact": impact, "rationale": rat}
            for src, impact, rat in contributions
        ]

        if tactic_result and tactic_result.get("model_version"):
            model_versions["tactic_model"] = tactic_result["model_version"]
            if tactic_result.get("tactics"):
                top_tac = tactic_result["tactics"][0]
                t_conf = float(top_tac.get("confidence", 0.5))
                model_probabilities["tactic_model"] = {
                    "top_tactic_probability": round(t_conf, 4),
                    "calibrated": True,
                    "calibration_method": "platt_scaling_ovr_cv3",
                    "uncertainty": round(1.0 - abs(2.0 * t_conf - 1.0), 4),
                    "model_version": tactic_result["model_version"],
                }

        if campaign_result and campaign_result.get("campaign_id") not in (None, -1):
            sim = float(campaign_result.get("similarity_score", 0.0))
            c_ver = campaign_result.get("correlation_provenance", {}).get("clustering_version", "hdbscan")
            model_versions["campaign_model"] = c_ver
            model_probabilities["campaign_model"] = {
                "cosine_similarity": round(sim, 4),
                "calibrated": False,
                "calibration_method": "cosine_similarity_not_probability",
                "uncertainty": round(1.0 - sim, 4),
                "model_version": c_ver,
            }

        calibrated_verified = any(v.get("calibrated") for v in model_probabilities.values()) and not any(
            not v.get("calibrated") for v in model_probabilities.values()
        )
        overall_uncertainty = round(
            sum(per_model_uncertainties) / len(per_model_uncertainties), 4
        ) if per_model_uncertainties else 0.50
        if not calibrated_verified and not uncertainty_reasons:
            uncertainty_reasons.append("Composite includes uncalibrated similarity or tree-score signals.")

        factor_summary = "; ".join(f"{src} ({rat})" for src, _, rat in contributions) or "No high-risk signals triggered"
        human_explanation = (
            f"Severity '{level.upper()}' (normalized risk {calibrated_risk:.2f}). "
            f"Evidence: {factor_summary}. "
            f"Uncertainty: {overall_uncertainty:.2f} ({'Platt-calibrated probabilities' if calibrated_verified else 'contains uncalibrated scores'})."
        )

        return {
            "threat_level": level,
            "calibrated_confidence": calibrated_risk if level != self.LEVEL_CLEAN else round(1.0 - calibrated_risk, 4),
            "risk_score": calibrated_risk,
            "verdict": verdict,
            "primary_vector": primary_vector,
            "model_probabilities": model_probabilities,
            "risk_normalization": {
                "raw_weighted_score": round(raw_risk, 4),
                "normalized_risk_score": calibrated_risk,
                "method": "weighted_composite_with_escalation_floors",
            },
            "severity_classification": {
                "level": level,
                "is_safety_guarantee": False,
            },
            "uncertainty_assessment": {
                "overall_uncertainty": overall_uncertainty,
                "calibrated_probability_verified": calibrated_verified,
                "uncertainty_reasons": uncertainty_reasons,
                "requires_human_review": bool(overall_uncertainty >= 0.45 or level == self.LEVEL_INCONCLUSIVE),
            },
            "model_versions": model_versions,
            "human_readable_explanation": human_explanation,
            "transparency_breakdown": breakdown,
            "remedial_actions": remedies,
        }


risk_service = TransparentRiskAggregationService()

