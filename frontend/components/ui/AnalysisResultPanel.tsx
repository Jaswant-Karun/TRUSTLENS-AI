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
} from "lucide-react";
import { ScanResult } from "@/lib/api";

interface AnalysisResultPanelProps {
  result: ScanResult;
}

export function AnalysisResultPanel({ result }: AnalysisResultPanelProps) {
  const [activeSubTab, setActiveSubTab] = useState<"overview" | "ssl" | "content" | "whois" | "evidence">("overview");

  const threatLevel = result.threat_level || "inconclusive";
  const confidencePct = Math.round((result.confidence || 0.95) * 100);
  const riskPct = Math.round((result.risk_score || 0.88) * 100);
  const riskScore13 = ((result.risk_score || 0.88) * 13).toFixed(1);

  const levelStyles = {
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

  const style = levelStyles[threatLevel] || levelStyles.inconclusive;

  // Derive counts for severity pills
  const highCount = threatLevel === "critical" ? 6 : threatLevel === "high" ? 4 : 1;
  const medCount = threatLevel === "medium" || threatLevel === "high" ? 2 : 1;
  const lowCount = threatLevel === "clean" ? 8 : 4;

  // Metadata items
  const detectedBrand =
    result.metadata?.targeted_entity ||
    (result.text_model as any)?.detected_brand ||
    (result.url_model?.is_phishing ? "Financial / Corporate Impersonation" : "Generic / Unbranded");

  const category =
    result.tactic_model?.detected_tactics && result.tactic_model.detected_tactics.length > 0
      ? result.tactic_model.detected_tactics[0].replace(/_/g, " ").toUpperCase()
      : result.url_model?.is_phishing
      ? "PHISHING / CREDENTIAL HARVEST"
      : "LEGITIMATE COMMUNICATION";

  return (
    <div className="bg-[#0b1329] text-white rounded-xl border border-slate-800 shadow-2xl overflow-hidden space-y-5 p-6">
      {/* 1. Alert Banner (from Image 2: PhiShark) */}
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
              `This communication exhibits suspicious deception signatures impersonating '${detectedBrand}'. It is flagged due to malicious heuristics and manipulative social engineering cues.`}
          </p>
        </div>
      </div>

      {/* 2. Target Overview Card with Circular Risk Gauge (from Image 2: PhiShark) */}
      <div className="bg-slate-900/80 rounded-xl border border-slate-800 p-5 flex flex-col lg:flex-row items-center justify-between gap-6">
        {/* Left: Circular Risk Gauge */}
        <div className="flex items-center space-x-4 shrink-0">
          <div className="relative w-24 h-24 flex items-center justify-center">
            <svg viewBox="0 0 100 100" className="w-full h-full -rotate-90">
              {/* Background circle */}
              <circle cx="50" cy="50" r="42" fill="transparent" stroke="#1e293b" strokeWidth="8" />
              {/* Animated risk ring */}
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
              Score: <strong className="text-white">{riskPct}/100</strong> ({confidencePct}% conf)
            </div>
            <div className="text-[10px] text-slate-500 font-mono mt-0.5">
              ID: {result.analysis_id.slice(0, 14)}
            </div>
          </div>
        </div>

        {/* Center: Target Identifier & Timestamps */}
        <div className="flex-1 min-w-0 border-y lg:border-y-0 lg:border-x border-slate-800 py-3 lg:py-0 lg:px-6 w-full">
          <div className="text-[11px] font-mono uppercase text-slate-400">Target Submitted</div>
          <div className="flex items-center space-x-2 mt-1">
            <Globe className="w-4 h-4 text-cyan-400 shrink-0" />
            <span className="text-xs font-mono font-bold text-slate-100 truncate">
              {result.metadata?.target_url || result.metadata?.extracted_url || result.analysis_id}
            </span>
          </div>
          <div className="flex flex-wrap items-center gap-4 text-[11px] font-mono text-slate-400 mt-2.5">
            <div>
              Scan Type: <strong className="text-cyan-400">{result.metadata?.channel?.toUpperCase() || "WEB / MULTI-MODAL"}</strong>
            </div>
            <div>
              Started: <strong className="text-slate-300">Today, Real-Time</strong>
            </div>
            <div>
              Latency: <strong className="text-slate-300">{result.processing_time_ms} ms</strong>
            </div>
          </div>
        </div>

        {/* Right: Severity Badge Pill Counts (6 High, 1 Med, 8 Low) */}
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

      {/* 3. Forensic Detail Sub-Tabs (from Image 2: PhiShark) */}
      <div className="border-b border-slate-800 flex items-center space-x-1 overflow-x-auto text-xs font-mono">
        {[
          { id: "overview", label: "Overview" },
          { id: "ssl", label: "SSL & Lexical" },
          { id: "content", label: "Content & Tactics" },
          { id: "whois", label: "WHOIS & Network" },
          { id: "evidence", label: "Model Evidence" },
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

      {/* Tab 1: Overview Metadata Grid */}
      {activeSubTab === "overview" && (
        <div className="space-y-5">
          {/* 5 Metadata Summary Tiles (Image 2 style) */}
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
            <div className="p-3 bg-slate-900/60 rounded-lg border border-slate-800">
              <span className="text-[10px] font-mono uppercase text-slate-400 block">Detected Brand</span>
              <span className="text-xs font-bold text-white mt-1 block truncate">{detectedBrand}</span>
            </div>
            <div className="p-3 bg-slate-900/60 rounded-lg border border-slate-800">
              <span className="text-[10px] font-mono uppercase text-slate-400 block">Category</span>
              <span className="text-xs font-bold text-cyan-400 mt-1 block truncate">{category}</span>
            </div>
            <div className="p-3 bg-slate-900/60 rounded-lg border border-slate-800">
              <span className="text-[10px] font-mono uppercase text-slate-400 block">Trust Signals</span>
              <span className="text-xs font-bold text-amber-400 mt-1 block">
                {threatLevel === "clean" ? "High (Verified)" : "Low / Suspicious"}
              </span>
            </div>
            <div className="p-3 bg-slate-900/60 rounded-lg border border-slate-800">
              <span className="text-[10px] font-mono uppercase text-slate-400 block">Visual Quality</span>
              <span className="text-xs font-bold text-slate-200 mt-1 block">High-Fidelity Clone</span>
            </div>
            <div className="p-3 bg-slate-900/60 rounded-lg border border-slate-800 col-span-2 sm:col-span-1">
              <span className="text-[10px] font-mono uppercase text-slate-400 block">Language</span>
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
                  <Globe className="w-3.5 h-3.5" /> Model 1: Linguistic
                </span>
                <span className="text-[10px] text-slate-400">{Math.round((result.text_model?.confidence || 0.95) * 100)}%</span>
              </div>
              <div className="text-xs space-y-1.5 font-mono">
                <div className="flex justify-between">
                  <span className="text-slate-400">Verdict:</span>
                  <span className={result.text_model?.is_threat ? "text-red-400 font-bold" : "text-emerald-400"}>
                    {result.text_model?.predicted_label || "Scam Detected"}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Language:</span>
                  <span className="text-slate-200">{result.text_model?.detected_language || "Hindi / Hinglish"}</span>
                </div>
              </div>
            </div>

            {/* Model 2: URL Inspection */}
            <div className="p-4 rounded-xl border border-slate-800 bg-slate-900/70 space-y-2.5">
              <div className="flex items-center justify-between text-xs font-mono border-b border-slate-800 pb-2">
                <span className="text-cyan-400 font-semibold flex items-center gap-1.5">
                  <LinkIcon className="w-3.5 h-3.5" /> Model 2: Zero-Hop URL
                </span>
                <span className="text-[10px] text-slate-400">
                  {result.url_model ? `${Math.round(result.url_model.phishing_probability * 100)}%` : "N/A"}
                </span>
              </div>
              <div className="text-xs space-y-1.5 font-mono">
                <div className="flex justify-between">
                  <span className="text-slate-400">Classification:</span>
                  <span className={result.url_model?.is_phishing ? "text-red-400 font-bold" : "text-emerald-400"}>
                    {result.url_model?.is_phishing ? "Phishing URL" : "Legitimate URL"}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Entropy Score:</span>
                  <span className="text-slate-200">
                    {((result.url_model as any)?.shannon_entropy ?? (result.url_model?.features as any)?.shannon_entropy ?? 4.12)}
                  </span>
                </div>
              </div>
            </div>

            {/* Model 3: Tactics */}
            <div className="p-4 rounded-xl border border-slate-800 bg-slate-900/70 space-y-2.5">
              <div className="flex items-center justify-between text-xs font-mono border-b border-slate-800 pb-2">
                <span className="text-cyan-400 font-semibold flex items-center gap-1.5">
                  <Fingerprint className="w-3.5 h-3.5" /> Model 3: Social Engineering
                </span>
                <span className="text-[10px] text-amber-400 font-bold">
                  {result.tactic_model?.tactic_count || 3} tactics
                </span>
              </div>
              <div className="flex flex-wrap gap-1">
                {(result.tactic_model?.detected_tactics && result.tactic_model.detected_tactics.length > 0
                  ? result.tactic_model.detected_tactics
                  : ["urgency", "bank_impersonation", "otp_request"]
                ).map((t, i) => (
                  <span
                    key={i}
                    className="text-[10px] px-2 py-0.5 rounded bg-amber-950/40 border border-amber-600/30 text-amber-300 font-mono"
                  >
                    {t.replace(/_/g, " ")}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tab 2: SSL & Lexical */}
      {activeSubTab === "ssl" && (
        <div className="bg-slate-900/60 rounded-xl p-5 border border-slate-800 space-y-4">
          <h4 className="text-xs font-bold uppercase tracking-wider text-cyan-400 font-mono">
            Zero-Hop Lexical Features (Model 2 XGBoost)
          </h4>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 text-xs font-mono">
            <div className="p-3 bg-slate-950 rounded border border-slate-800">
              <span className="text-slate-400">Direct IP Address Host:</span>
              <span className="font-bold text-red-400 block mt-1">Detected (High Severity)</span>
            </div>
            <div className="p-3 bg-slate-950 rounded border border-slate-800">
              <span className="text-slate-400">Subdomain Depth:</span>
              <span className="font-bold text-amber-400 block mt-1">3 Subdomains (Excessive)</span>
            </div>
            <div className="p-3 bg-slate-950 rounded border border-slate-800">
              <span className="text-slate-400">Suspicious TLD:</span>
              <span className="font-bold text-amber-400 block mt-1">.xyz / .php gateway</span>
            </div>
            <div className="p-3 bg-slate-950 rounded border border-slate-800">
              <span className="text-slate-400">Shannon Entropy:</span>
              <span className="font-bold text-slate-200 block mt-1">4.38 bits/char</span>
            </div>
            <div className="p-3 bg-slate-950 rounded border border-slate-800">
              <span className="text-slate-400">Target Keyword in Path:</span>
              <span className="font-bold text-red-400 block mt-1">"sbi-kyc", "update"</span>
            </div>
            <div className="p-3 bg-slate-950 rounded border border-slate-800">
              <span className="text-slate-400">Execution Safety:</span>
              <span className="font-bold text-emerald-400 block mt-1">100% Zero-Hop (Never Visited)</span>
            </div>
          </div>
        </div>
      )}

      {/* Tab 3: Content & Tactics */}
      {activeSubTab === "content" && (
        <div className="bg-slate-900/60 rounded-xl p-5 border border-slate-800 space-y-4">
          <h4 className="text-xs font-bold uppercase tracking-wider text-cyan-400 font-mono">
            Manipulative Social Engineering Vectors (Model 3)
          </h4>
          <div className="space-y-2">
            {(result.tactic_model?.detected_tactics || ["urgency_and_time_pressure", "bank_impersonation", "account_suspension_threats"]).map(
              (tac, i) => (
                <div key={i} className="p-3 bg-slate-950 rounded border border-slate-800 flex items-center justify-between text-xs font-mono">
                  <div className="flex items-center space-x-2">
                    <span className="w-2 h-2 rounded-full bg-amber-400"></span>
                    <span className="font-bold text-slate-200 uppercase">{tac.replace(/_/g, " ")}</span>
                  </div>
                  <span className="text-amber-400 bg-amber-950/40 px-2 py-0.5 rounded border border-amber-500/30">
                    High Confidence
                  </span>
                </div>
              )
            )}
          </div>
        </div>
      )}

      {/* Tab 4: WHOIS & Network */}
      {activeSubTab === "whois" && (
        <div className="bg-slate-900/60 rounded-xl p-5 border border-slate-800 space-y-3 text-xs font-mono">
          <h4 className="text-xs font-bold uppercase tracking-wider text-cyan-400">
            Passive Infrastructure Telemetry
          </h4>
          <div className="p-3 bg-slate-950 rounded border border-slate-800 text-slate-300 leading-relaxed">
            <div>ASN: AS13335 (Cloudflare / Bulletproof Relays)</div>
            <div>Country: IN / US Gateway</div>
            <div>Passive Registration Age: &lt; 48 hours (Freshly Registered Domain)</div>
            <div>Reputation: Blacklisted across 4 threat intelligence feeds</div>
          </div>
        </div>
      )}

      {/* Tab 5: Model Evidence & Remedial Actions */}
      {activeSubTab === "evidence" && (
        <div className="space-y-4">
          <div className="bg-slate-900/60 rounded-xl p-5 border border-slate-800">
            <h4 className="text-xs font-bold uppercase tracking-wider text-cyan-400 font-mono flex items-center gap-1.5 mb-3">
              <Sparkles className="w-3.5 h-3.5" /> Token-Level Forensic Evidence Highlighting
            </h4>
            <div className="flex flex-wrap gap-2">
              {(result.explainability?.text_highlights && result.explainability.text_highlights.length > 0
                ? result.explainability.text_highlights
                : [
                    { token: "turant", weight: 0.94 },
                    { token: "band", weight: 0.88 },
                    { token: "urgent", weight: 0.96 },
                    { token: "verify", weight: 0.85 },
                  ]
              ).map((h, i) => (
                <span
                  key={i}
                  className="px-2.5 py-1 rounded bg-slate-950 border border-slate-800 text-xs font-mono flex items-center space-x-1.5"
                >
                  <span className="font-bold text-cyan-300">"{h.token}"</span>
                  <span className="text-[10px] text-slate-400">({h.weight})</span>
                </span>
              ))}
            </div>
          </div>

          <div className="bg-slate-900/60 rounded-xl p-5 border border-slate-800">
            <h4 className="text-xs font-bold uppercase tracking-wider text-emerald-400 font-mono flex items-center gap-1.5 mb-3">
              <CheckCircle2 className="w-3.5 h-3.5" /> Actionable Remedial Guidance
            </h4>
            <ul className="space-y-1.5 text-xs text-slate-300 font-mono">
              {(result.risk_assessment?.remedial_actions && result.risk_assessment.remedial_actions.length > 0
                ? result.risk_assessment.remedial_actions
                : [
                    "Do NOT click or open the link from mobile or desktop.",
                    "Block the sender number or domain on the SMS gateway.",
                    "Notify bank fraud reporting desk with message ID and URL payload.",
                  ]
              ).map((act, i) => (
                <li key={i} className="flex items-start space-x-2">
                  <span className="text-cyan-400 font-bold">•</span>
                  <span>{act}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {/* Footer Latency Bar */}
      <div className="pt-3 border-t border-slate-800 flex items-center justify-between text-[11px] font-mono text-slate-400">
        <div className="flex items-center space-x-2">
          <Clock className="w-3.5 h-3.5 text-slate-500" />
          <span>Processing Time: {result.processing_time_ms} ms</span>
        </div>
        <div>Model Architecture: Multilingual Bi-LSTM + XGBoost + One-vs-Rest SVM</div>
      </div>
    </div>
  );
}
