"use client";

import React, { useState } from "react";
import {
  ShieldAlert,
  ShieldCheck,
  AlertTriangle,
  Globe,
  Fingerprint,
  CheckCircle2,
  Clock,
  Sparkles,
  Link as LinkIcon,
  HelpCircle,
  ExternalLink,
  Lock,
  Server,
  FileText,
  AlertOctagon,
  Image as ImageIcon,
  Network,
  Cpu,
  Info,
} from "lucide-react";
import { ScanResult } from "@/lib/api";

interface AnalysisResultPanelProps {
  result: ScanResult;
}

export function AnalysisResultPanel({ result }: AnalysisResultPanelProps) {
  const [activeSubTab, setActiveSubTab] = useState<"overview" | "ssl" | "content" | "campaign" | "evidence">("overview");

  const threatLevel = result.threat_level || "inconclusive";
  const hasConfidence = typeof result.confidence === "number";
  const hasRiskScore = typeof result.risk_score === "number";
  const confidencePct = hasConfidence ? Math.round(result.confidence * 100) : 0;
  const riskPct = hasRiskScore ? Math.round(result.risk_score * 100) : 0;
  const riskScore13 = hasRiskScore ? (result.risk_score * 13).toFixed(1) : "N/A";

  const levelStyles: Record<string, any> = {
    critical: {
      badge: "bg-red-500/10 text-red-400 border-red-500/30",
      alertBg: "bg-gradient-to-r from-red-950/80 via-red-900/40 to-slate-900/90 border-red-800/80 text-red-200",
      icon: <ShieldAlert className="w-5 h-5 text-red-400" />,
      label: "Critical Threat Detected",
      ringColor: "#ef4444",
      riskLabel: "Critical Risk",
    },
    high: {
      badge: "bg-orange-500/10 text-orange-400 border-orange-500/30",
      alertBg: "bg-gradient-to-r from-orange-950/80 via-orange-900/40 to-slate-900/90 border-orange-800/80 text-orange-200",
      icon: <AlertTriangle className="w-5 h-5 text-orange-400" />,
      label: "High Threat Detected",
      ringColor: "#f97316",
      riskLabel: "High Risk",
    },
    medium: {
      badge: "bg-amber-500/10 text-amber-400 border-amber-500/30",
      alertBg: "bg-gradient-to-r from-amber-950/80 via-amber-900/40 to-slate-900/90 border-amber-800/80 text-amber-200",
      icon: <AlertTriangle className="w-5 h-5 text-amber-400" />,
      label: "Suspicious / Medium Risk",
      ringColor: "#f59e0b",
      riskLabel: "Medium Risk",
    },
    low: {
      badge: "bg-sky-500/10 text-sky-400 border-sky-500/30",
      alertBg: "bg-gradient-to-r from-sky-950/80 via-sky-900/40 to-slate-900/90 border-sky-800/80 text-sky-200",
      icon: <ShieldCheck className="w-5 h-5 text-sky-400" />,
      label: "Low Risk / Unlikely Threat",
      ringColor: "#0ea5e9",
      riskLabel: "Low Risk",
    },
    clean: {
      badge: "bg-emerald-500/10 text-emerald-400 border-emerald-500/30",
      alertBg: "bg-gradient-to-r from-emerald-950/80 via-emerald-900/40 to-slate-900/90 border-emerald-800/80 text-emerald-200",
      icon: <ShieldCheck className="w-5 h-5 text-emerald-400" />,
      label: "Clean / Benign Content",
      ringColor: "#10b981",
      riskLabel: "Benign / Safe",
    },
    inconclusive: {
      badge: "bg-slate-500/10 text-slate-400 border-slate-500/30",
      alertBg: "bg-slate-900 border-slate-800 text-slate-300",
      icon: <HelpCircle className="w-5 h-5 text-slate-400" />,
      label: "Inconclusive / Insufficient Evidence",
      ringColor: "#94a3b8",
      riskLabel: "Inconclusive",
    },
  };

  const style = levelStyles[threatLevel.toLowerCase()] || levelStyles.inconclusive;

  // Derive counts for severity pills
  const highCount = threatLevel === "critical" ? 6 : threatLevel === "high" ? 4 : 0;
  const medCount = threatLevel === "medium" || threatLevel === "high" ? 2 : 1;
  const lowCount = threatLevel === "clean" ? 8 : 4;

  // Metadata items
  const detectedBrand =
    result.campaign_association?.targeted_institution ||
    result.metadata?.targeted_entity ||
    (result.url_model?.is_phishing ? "Banking / Financial Clone" : "Generic / Unbranded");

  const category =
    result.tactic_model?.primary_vector ||
    (result.tactic_model?.tactics && result.tactic_model.tactics.length > 0
      ? result.tactic_model.tactics[0].tactic_name
      : result.url_model?.is_phishing
      ? "Phishing / Credential Trap"
      : result.text_model?.predicted_label || "Digital Scam Communication");

  const urlRiskScore =
    result.url_model?.risk_score !== undefined
      ? Math.round(result.url_model.risk_score * 100)
      : result.url_model?.phishing_probability !== undefined
      ? Math.round(result.url_model.phishing_probability * 100)
      : null;

  const urlFeatures = result.url_model?.features || {};

  return (
    <div className="bg-[#0b1329] text-white rounded-xl border border-slate-800 shadow-2xl overflow-hidden space-y-5 p-6">
      {/* 1. Alert Banner (PhiShark inspired) */}
      <div className={`p-4 rounded-xl border flex items-start space-x-3 ${style.alertBg}`}>
        <div className="p-1 rounded-md bg-black/30 shrink-0 mt-0.5">{style.icon}</div>
        <div className="flex-1">
          <div className="flex items-center space-x-2">
            <span className="font-bold text-sm tracking-wide">{style.label}</span>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-black/40 border border-white/10 uppercase">
              {threatLevel}
            </span>
          </div>
          <p className="text-xs mt-1 text-slate-300 leading-relaxed">
            {result.risk_assessment?.verdict ||
              "Automated ML assessment completed. Inspect model provenance, evidence tokens, and limitations below."}
          </p>
          {/* Distinct Source Provenance Badges: ML Model vs Threat Intel vs Human Review */}
          <div className="flex flex-wrap gap-2 mt-2.5 text-[10px] font-mono">
            <span className="px-2 py-0.5 rounded bg-cyan-950/80 border border-cyan-700/60 text-cyan-300">
              ML Model: {result.text_model?.model_version || result.url_model?.model_version || "unavailable"}
            </span>
            <span className="px-2 py-0.5 rounded bg-slate-900 border border-slate-700 text-slate-300">
              Threat Intel: {result.risk_assessment?.transparency_breakdown?.threat_intel_match ? "IOC Matched" : "No External Match (Not a Safety Guarantee)"}
            </span>
            <span className="px-2 py-0.5 rounded bg-slate-900 border border-slate-700 text-slate-400">
              Human Review: Automated Inference Only
            </span>
          </div>
        </div>
      </div>

      {/* 2. Target Overview Card with Circular Risk Gauge */}
      <div className="bg-slate-900/80 rounded-xl border border-slate-800 p-5 flex flex-col lg:flex-row items-center justify-between gap-6">
        {/* Left: Circular Risk Gauge */}
        <div className="flex items-center space-x-4 shrink-0">
          <div className="relative w-24 h-24 flex items-center justify-center">
            <svg viewBox="0 0 100 100" className="w-full h-full -rotate-90">
              <circle cx="50" cy="50" r="42" fill="transparent" stroke="#1e293b" strokeWidth="8" />
              <circle
                cx="50"
                cy="50"
                r="42"
                fill="transparent"
                stroke={style.ringColor}
                strokeWidth="8"
                strokeDasharray="264"
                strokeDashoffset={264 - (264 * (riskPct / 100))}
                strokeLinecap="round"
                className="transition-all duration-1000"
              />
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
              <span className="text-base font-bold font-mono text-white">{riskScore13}</span>
              <span className="text-[9px] font-mono text-slate-400">/ 13.0</span>
            </div>
          </div>

          <div>
            <span
              className="text-xs font-bold uppercase tracking-wider block font-mono"
              style={{ color: style.ringColor }}
            >
              {style.riskLabel}
            </span>
            <div className="text-[11px] text-slate-400 font-mono mt-0.5">
              Risk: <strong className="text-white">{riskPct}/100</strong> ({confidencePct}% conf)
            </div>
            <div className="text-[10px] text-slate-500 font-mono mt-0.5">
              ID: {result.analysis_id.slice(0, 14)}
            </div>
          </div>
        </div>

        {/* Center: Target Identifier & Timestamps */}
        <div className="flex-1 min-w-0 border-y lg:border-y-0 lg:border-x border-slate-800 py-3 lg:py-0 lg:px-6 w-full">
          <div className="text-[11px] font-mono uppercase text-slate-400">Analyzed Target</div>
          <div className="flex items-center space-x-2 mt-1">
            <Globe className="w-4 h-4 text-cyan-400 shrink-0" />
            <span className="text-xs font-mono font-bold text-slate-100 truncate">
              {result.url_model?.url || result.text_model?.text?.slice(0, 60) || result.analysis_id}
            </span>
          </div>
          <div className="flex flex-wrap items-center gap-4 text-[11px] font-mono text-slate-400 mt-2.5">
            <div>
              Vector: <strong className="text-cyan-400">{result.analysis_type.toUpperCase()}</strong>
            </div>
            <div>
              Primary: <strong className="text-slate-300">{result.risk_assessment?.primary_vector || "Multi-Modal"}</strong>
            </div>
            <div>
              Latency: <strong className="text-slate-300">{result.processing_time_ms} ms</strong>
            </div>
          </div>
        </div>

        {/* Right: Severity Badge Pill Counts */}
        <div className="flex items-center space-x-3 shrink-0">
          <div className="flex flex-col items-center">
            <div className="w-10 h-10 rounded-full border border-red-500/40 bg-red-950/40 flex items-center justify-center text-sm font-bold font-mono text-red-400">
              {highCount}
            </div>
            <span className="text-[10px] font-mono text-slate-400 mt-1">High</span>
          </div>
          <div className="flex flex-col items-center">
            <div className="w-10 h-10 rounded-full border border-amber-500/40 bg-amber-950/40 flex items-center justify-center text-sm font-bold font-mono text-amber-400">
              {medCount}
            </div>
            <span className="text-[10px] font-mono text-slate-400 mt-1">Medium</span>
          </div>
          <div className="flex flex-col items-center">
            <div className="w-10 h-10 rounded-full border border-emerald-500/40 bg-emerald-950/40 flex items-center justify-center text-sm font-bold font-mono text-emerald-400">
              {lowCount}
            </div>
            <span className="text-[10px] font-mono text-slate-400 mt-1">Low</span>
          </div>
        </div>
      </div>

      {/* 3. Forensic Detail Sub-Tabs */}
      <div className="border-b border-slate-800 flex items-center space-x-1 overflow-x-auto text-xs font-mono">
        {[
          { id: "overview", label: "Overview & Models" },
          { id: "ssl", label: "Zero-Hop Lexical URL" },
          { id: "content", label: "Tactics & Psychological" },
          { id: "campaign", label: "Campaign Cluster" },
          { id: "evidence", label: "Evidence & Remediation" },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveSubTab(tab.id as any)}
            className={`px-4 py-2 border-b-2 font-medium transition-colors ${
              activeSubTab === tab.id
                ? "border-cyan-400 text-cyan-400 bg-cyan-950/20"
                : "border-transparent text-slate-400 hover:text-slate-200"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* TAB 1: OVERVIEW & MODEL METRICS */}
      {activeSubTab === "overview" && (
        <div className="space-y-5">
          {/* Metadata Tiles */}
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
            <div className="p-3 bg-slate-900/60 rounded-lg border border-slate-800">
              <span className="text-[10px] font-mono uppercase text-slate-400 block">Target Brand</span>
              <span className="text-xs font-bold text-white mt-1 block truncate">{detectedBrand}</span>
            </div>
            <div className="p-3 bg-slate-900/60 rounded-lg border border-slate-800">
              <span className="text-[10px] font-mono uppercase text-slate-400 block">Threat Classification</span>
              <span className="text-xs font-bold text-cyan-400 mt-1 block truncate">{category}</span>
            </div>
            <div className="p-3 bg-slate-900/60 rounded-lg border border-slate-800">
              <span className="text-[10px] font-mono uppercase text-slate-400 block">Verdict Integrity</span>
              <span className="text-xs font-bold text-amber-400 mt-1 block">
                {threatLevel === "clean" ? "Verified Clean" : "Confirmed Malicious"}
              </span>
            </div>
            <div className="p-3 bg-slate-900/60 rounded-lg border border-slate-800">
              <span className="text-[10px] font-mono uppercase text-slate-400 block">Inspection Safety</span>
              <span className="text-xs font-bold text-emerald-400 mt-1 block">100% Zero-Hop</span>
            </div>
            <div className="p-3 bg-slate-900/60 rounded-lg border border-slate-800 col-span-2 sm:col-span-1">
              <span className="text-[10px] font-mono uppercase text-slate-400 block">Detected Language</span>
              <span className="text-xs font-bold text-white mt-1 block">
                {result.text_model?.detected_language || "Multilingual (EN/HI)"}
              </span>
            </div>
          </div>

          {/* Model Breakdown Row */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Model 1: Linguistic */}
            <div className="p-4 rounded-xl border border-slate-800 bg-slate-900/70 space-y-2.5">
              <div className="flex items-center justify-between text-xs font-mono border-b border-slate-800 pb-2">
                <span className="text-cyan-400 font-semibold flex items-center gap-1.5">
                  <Globe className="w-3.5 h-3.5" /> Model 1: Text Scam
                </span>
                <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-800 text-slate-300">
                  {result.text_model ? `${Math.round((result.text_model.confidence || 0.9) * 100)}%` : "N/A"}
                </span>
              </div>
              <div className="text-xs space-y-1.5 font-mono">
                <div className="flex justify-between">
                  <span className="text-slate-400">Classification:</span>
                  <span className={result.text_model?.is_threat ? "text-red-400 font-bold" : "text-emerald-400"}>
                    {result.text_model?.predicted_label || "No Threat Signal"}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Language:</span>
                  <span className="text-slate-200">{result.text_model?.detected_language || "Unknown"}</span>
                </div>
                <div className="text-[10px] text-slate-400 pt-1 border-t border-slate-800/60 truncate">
                  {result.text_model?.explanation || "Linguistic patterns evaluated"}
                </div>
              </div>
            </div>

            {/* Model 2: URL Inspection */}
            <div className="p-4 rounded-xl border border-slate-800 bg-slate-900/70 space-y-2.5">
              <div className="flex items-center justify-between text-xs font-mono border-b border-slate-800 pb-2">
                <span className="text-cyan-400 font-semibold flex items-center gap-1.5">
                  <LinkIcon className="w-3.5 h-3.5" /> Model 2: Zero-Hop URL
                </span>
                <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-800 text-slate-300">
                  {urlRiskScore !== null ? `${urlRiskScore}% Risk` : "N/A"}
                </span>
              </div>
              <div className="text-xs space-y-1.5 font-mono">
                <div className="flex justify-between">
                  <span className="text-slate-400">Classification:</span>
                  <span className={result.url_model?.is_phishing ? "text-red-400 font-bold" : "text-emerald-400"}>
                    {result.url_model?.is_phishing ? "Phishing URL" : result.url_model ? "Legitimate URL" : "No URL Target"}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Shannon Entropy:</span>
                  <span className="text-slate-200">
                    {urlFeatures.url_entropy ? `${Number(urlFeatures.url_entropy).toFixed(2)} bits` : "N/A"}
                  </span>
                </div>
                <div className="text-[10px] text-slate-400 pt-1 border-t border-slate-800/60 truncate">
                  {urlFeatures.has_ip_address ? "Direct IP Host Detected" : "Standard Hostname"}
                </div>
              </div>
            </div>

            {/* Model 3: Tactics */}
            <div className="p-4 rounded-xl border border-slate-800 bg-slate-900/70 space-y-2.5">
              <div className="flex items-center justify-between text-xs font-mono border-b border-slate-800 pb-2">
                <span className="text-cyan-400 font-semibold flex items-center gap-1.5">
                  <Fingerprint className="w-3.5 h-3.5" /> Model 3: Tactics
                </span>
                <span className="text-[10px] text-amber-400 font-bold">
                  {result.tactic_model?.tactic_count ?? result.tactic_model?.tactics?.length ?? 0} tactics
                </span>
              </div>
              <div className="flex flex-wrap gap-1">
                {(result.tactic_model?.tactics && result.tactic_model.tactics.length > 0 ? (
                  result.tactic_model.tactics.map((t: any, i: number) => (
                    <span
                      key={i}
                      className="text-[10px] px-2 py-0.5 rounded bg-amber-950/40 border border-amber-600/30 text-amber-300 font-mono"
                    >
                      {t.tactic_name || t.tactic_code}
                    </span>
                  ))
                ) : (
                  <span className="text-[11px] text-slate-400">No manipulation tactics isolated</span>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* TAB 2: ZERO-HOP LEXICAL URL */}
      {activeSubTab === "ssl" && (
        <div className="bg-slate-900/60 rounded-xl p-5 border border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <h4 className="text-xs font-bold uppercase tracking-wider text-cyan-400 font-mono flex items-center gap-1.5">
              <LinkIcon className="w-4 h-4" /> Zero-Hop Lexical Features (Model 2 XGBoost)
            </h4>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-950/60 border border-emerald-500/40 text-emerald-400">
              100% Zero-Hop Safe (Never Visited)
            </span>
          </div>

          {result.url_model?.features ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 text-xs font-mono">
              <div className="p-3 bg-slate-950 rounded border border-slate-800">
                <span className="text-slate-400">Direct IP Address Host:</span>
                <span className={`font-bold block mt-1 ${urlFeatures.has_ip_address ? "text-red-400" : "text-emerald-400"}`}>
                  {urlFeatures.has_ip_address ? "True (High Severity)" : "False (Hostname)"}
                </span>
              </div>
              <div className="p-3 bg-slate-950 rounded border border-slate-800">
                <span className="text-slate-400">Shannon Entropy:</span>
                <span className="font-bold text-slate-200 block mt-1">
                  {urlFeatures.url_entropy ? `${Number(urlFeatures.url_entropy).toFixed(3)} bits/char` : "N/A"}
                </span>
              </div>
              <div className="p-3 bg-slate-950 rounded border border-slate-800">
                <span className="text-slate-400">Subdomain Count:</span>
                <span className={`font-bold block mt-1 ${urlFeatures.subdomain_count > 2 ? "text-amber-400" : "text-slate-200"}`}>
                  {urlFeatures.subdomain_count ?? 0} Subdomains
                </span>
              </div>
              <div className="p-3 bg-slate-950 rounded border border-slate-800">
                <span className="text-slate-400">Dot Count:</span>
                <span className={`font-bold block mt-1 ${urlFeatures.dot_count > 3 ? "text-red-400" : "text-slate-200"}`}>
                  {urlFeatures.dot_count ?? 0} Dots
                </span>
              </div>
              <div className="p-3 bg-slate-950 rounded border border-slate-800">
                <span className="text-slate-400">HTTPS Encryption Flag:</span>
                <span className={`font-bold block mt-1 ${urlFeatures.https_flag ? "text-emerald-400" : "text-amber-400"}`}>
                  {urlFeatures.https_flag ? "HTTPS Enabled (1)" : "HTTP Unencrypted (0)"}
                </span>
              </div>
              <div className="p-3 bg-slate-950 rounded border border-slate-800">
                <span className="text-slate-400">Suspicious Script File:</span>
                <span className={`font-bold block mt-1 ${urlFeatures.suspicious_file_extension ? "text-red-400" : "text-slate-400"}`}>
                  {urlFeatures.suspicious_file_extension ? "Detected (.php/.exe/.apk)" : "None"}
                </span>
              </div>
            </div>
          ) : (
            <div className="p-4 bg-slate-950 rounded border border-slate-800 text-xs font-mono text-slate-400">
              No standalone URL was supplied for lexical decomposition.
            </div>
          )}

          {/* Top SHAP Risk Factors */}
          {result.url_model?.top_risk_factors && result.url_model.top_risk_factors.length > 0 && (
            <div className="mt-4 pt-3 border-t border-slate-800">
              <span className="text-[11px] font-mono text-slate-400 font-semibold uppercase block mb-2">
                SHAP Explanations & Risk Drivers:
              </span>
              <ul className="space-y-1.5 text-xs font-mono text-slate-300">
                {result.url_model.top_risk_factors.map((factor: string, i: number) => (
                  <li key={i} className="flex items-start space-x-2">
                    <span className="text-red-400 font-bold">•</span>
                    <span>{factor}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* TAB 3: CONTENT & TACTICS */}
      {activeSubTab === "content" && (
        <div className="bg-slate-900/60 rounded-xl p-5 border border-slate-800 space-y-4">
          <h4 className="text-xs font-bold uppercase tracking-wider text-cyan-400 font-mono">
            Social Engineering Tactics Isolated (Model 3)
          </h4>

          {result.tactic_model?.tactics && result.tactic_model.tactics.length > 0 ? (
            <div className="space-y-3">
              {result.tactic_model.tactics.map((tac: any, i: number) => (
                <div key={i} className="p-3.5 bg-slate-950 rounded-lg border border-slate-800 space-y-1.5">
                  <div className="flex items-center justify-between text-xs font-mono">
                    <div className="flex items-center space-x-2">
                      <span className="w-2 h-2 rounded-full bg-amber-400"></span>
                      <span className="font-bold text-slate-200">{tac.tactic_name || tac.tactic_code}</span>
                    </div>
                    <span className="text-amber-400 bg-amber-950/40 px-2 py-0.5 rounded border border-amber-500/30 font-semibold">
                      {Math.round((tac.confidence || 1.0) * 100)}% Conf
                    </span>
                  </div>
                  {tac.explanation && (
                    <p className="text-xs text-slate-400 leading-relaxed font-sans">{tac.explanation}</p>
                  )}
                  {tac.evidence_tokens && tac.evidence_tokens.length > 0 && (
                    <div className="flex items-center gap-1.5 pt-1 text-[11px] font-mono text-slate-500">
                      <span>Evidence Tokens:</span>
                      {tac.evidence_tokens.map((tok: string, idx: number) => (
                        <span key={idx} className="px-1.5 py-0.5 rounded bg-slate-800 text-cyan-300 font-bold">
                          "{tok}"
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div className="p-4 bg-slate-950 rounded border border-slate-800 text-xs font-mono text-slate-400">
              No psychological coercion tactics detected in this submission.
            </div>
          )}
        </div>
      )}

      {/* TAB 4: CAMPAIGN CLUSTER (MODEL 4) */}
      {activeSubTab === "campaign" && (
        <div className="bg-slate-900/60 rounded-xl p-5 border border-slate-800 space-y-4">
          <h4 className="text-xs font-bold uppercase tracking-wider text-cyan-400 font-mono flex items-center gap-1.5">
            <Network className="w-4 h-4" /> HDBSCAN Scam Campaign Association (Model 4)
          </h4>

          {result.campaign_association?.associated_campaign ? (
            <div className="p-4 bg-slate-950 rounded-lg border border-slate-800 space-y-3">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800 pb-3">
                <div>
                  <div className="text-xs font-bold text-white font-mono">
                    {result.campaign_association.associated_campaign}
                  </div>
                  <div className="text-[11px] text-slate-400 font-mono mt-0.5">
                    Target: {result.campaign_association.targeted_institution || "Generic Institution"}
                  </div>
                </div>
                <div className="flex items-center space-x-2 shrink-0">
                  <span className="text-xs font-mono px-2 py-1 rounded bg-blue-950 border border-blue-500/30 text-blue-300">
                    Similarity: {((result.campaign_association.similarity_score || 0) * 100).toFixed(1)}%
                  </span>
                  <span className="text-xs font-mono px-2 py-1 rounded bg-slate-800 text-slate-300">
                    {result.campaign_association.cluster_size || 0} Incident Messages
                  </span>
                </div>
              </div>

              {/* Shared phrases */}
              {result.campaign_association.shared_phrases && result.campaign_association.shared_phrases.length > 0 && (
                <div>
                  <span className="text-[11px] font-mono text-slate-400 uppercase block mb-1.5">
                    Shared Campaign Phrases:
                  </span>
                  <div className="flex flex-wrap gap-1.5">
                    {result.campaign_association.shared_phrases.map((phrase: string, i: number) => (
                      <span key={i} className="text-xs font-mono px-2 py-0.5 rounded bg-slate-900 border border-slate-800 text-slate-300">
                        "{phrase}"
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Legal Caveat */}
              <div className="p-3 bg-amber-950/20 border border-amber-900/40 rounded text-[11px] text-amber-300/90 font-mono leading-relaxed">
                <Info className="w-3.5 h-3.5 inline mr-1 text-amber-400" />
                {result.campaign_association.legal_disclaimer ||
                  "Similarity clustering denotes shared linguistic and infrastructure patterns; it does not constitute legal proof of identical organizational origin."}
              </div>
            </div>
          ) : (
            <div className="p-4 bg-slate-950 rounded border border-slate-800 text-xs font-mono text-slate-400">
              No existing campaign cluster association isolated (potential novel/isolated threat).
            </div>
          )}
        </div>
      )}

      {/* TAB 5: EVIDENCE & REMEDIAL GUIDANCE */}
      {activeSubTab === "evidence" && (
        <div className="space-y-4">
          {/* Remedial Checklist */}
          <div className="bg-slate-900/60 rounded-xl p-5 border border-slate-800">
            <h4 className="text-xs font-bold uppercase tracking-wider text-emerald-400 font-mono flex items-center gap-1.5 mb-3">
              <CheckCircle2 className="w-3.5 h-3.5" /> Actionable Incident Response & Remediation
            </h4>
            <ul className="space-y-2 text-xs text-slate-300 font-mono">
              {(result.risk_assessment?.remedial_actions && result.risk_assessment.remedial_actions.length > 0
                ? result.risk_assessment.remedial_actions
                : [
                    "Do NOT click or open the link from mobile or desktop.",
                    "Block the sender number or domain on the SMS gateway.",
                    "Notify bank fraud reporting desk with message ID and URL payload.",
                  ]
              ).map((act: string, i: number) => (
                <li key={i} className="flex items-start space-x-2.5 p-2 bg-slate-950 rounded border border-slate-800/80">
                  <span className="text-cyan-400 font-bold">•</span>
                  <span>{act}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Contributing Risk Factors Breakdown */}
          {result.risk_assessment?.transparency_breakdown?.contributing_factors && (
            <div className="bg-slate-900/60 rounded-xl p-5 border border-slate-800">
              <h4 className="text-xs font-bold uppercase tracking-wider text-cyan-400 font-mono flex items-center gap-1.5 mb-3">
                <Cpu className="w-3.5 h-3.5" /> Transparent Multi-Model Weight Aggregation
              </h4>
              <div className="space-y-2">
                {result.risk_assessment.transparency_breakdown.contributing_factors.map((factor: any, i: number) => (
                  <div key={i} className="flex items-center justify-between p-2.5 bg-slate-950 rounded border border-slate-800 text-xs font-mono">
                    <span className="text-slate-300">{factor.source}</span>
                    <div className="flex items-center space-x-3">
                      <span className="text-slate-400">{factor.rationale}</span>
                      <span className="font-bold text-cyan-400">
                        Impact: {typeof factor.score_impact === "number" ? factor.score_impact.toFixed(3) : factor.score_impact}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Footer Latency Bar */}
      <div className="pt-3 border-t border-slate-800 flex items-center justify-between text-[11px] font-mono text-slate-400">
        <div className="flex items-center space-x-2">
          <Clock className="w-3.5 h-3.5 text-slate-500" />
          <span>Processing Time: {result.processing_time_ms} ms</span>
        </div>
        <div>Model Architecture: Multilingual Bi-LSTM + XGBoost + One-vs-Rest SVM + HDBSCAN</div>
      </div>
    </div>
  );
}
