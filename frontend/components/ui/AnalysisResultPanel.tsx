"use client";

import React from "react";
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
} from "lucide-react";
import { ScanResult } from "@/lib/api";

interface AnalysisResultPanelProps {
  result: ScanResult;
}

export function AnalysisResultPanel({ result }: AnalysisResultPanelProps) {
  const threatLevel = result.threat_level || "inconclusive";
  const confidencePct = Math.round(result.confidence * 100);
  const riskPct = Math.round(result.risk_score * 100);

  const levelStyles = {
    critical: {
      badge: "bg-red-50 text-red-700 border-red-200",
      icon: <ShieldAlert className="w-5 h-5 text-red-600" />,
      label: "Critical Threat Detected",
      bar: "bg-red-600",
    },
    high: {
      badge: "bg-orange-50 text-orange-700 border-orange-200",
      icon: <AlertTriangle className="w-5 h-5 text-orange-600" />,
      label: "High Threat Detected",
      bar: "bg-orange-500",
    },
    medium: {
      badge: "bg-amber-50 text-amber-700 border-amber-200",
      icon: <AlertTriangle className="w-5 h-5 text-amber-600" />,
      label: "Suspicious / Medium Risk",
      bar: "bg-amber-500",
    },
    low: {
      badge: "bg-sky-50 text-sky-700 border-sky-200",
      icon: <ShieldCheck className="w-5 h-5 text-sky-600" />,
      label: "Low Risk / Unlikely Threat",
      bar: "bg-sky-500",
    },
    clean: {
      badge: "bg-emerald-50 text-emerald-700 border-emerald-200",
      icon: <ShieldCheck className="w-5 h-5 text-emerald-600" />,
      label: "Clean / Benign Content",
      bar: "bg-emerald-500",
    },
    inconclusive: {
      badge: "bg-slate-100 text-slate-700 border-slate-200",
      icon: <HelpCircle className="w-5 h-5 text-slate-500" />,
      label: "Inconclusive / Insufficient Evidence",
      bar: "bg-slate-400",
    },
  };

  const style = levelStyles[threatLevel] || levelStyles.inconclusive;

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-card overflow-hidden">
      {/* Primary Verdict Header */}
      <div className="p-6 border-b border-slate-100 flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-50/40">
        <div className="flex items-start space-x-3.5">
          <div className="p-2.5 rounded-xl bg-white border border-slate-200 shadow-subtle shrink-0">
            {style.icon}
          </div>
          <div>
            <div className="flex items-center space-x-2.5">
              <span className={`text-xs font-semibold px-2.5 py-0.5 rounded-full border uppercase tracking-wider font-mono ${style.badge}`}>
                {threatLevel}
              </span>
              <span className="text-xs text-slate-400 font-mono">ID: {result.analysis_id.slice(0, 16)}</span>
            </div>
            <h2 className="text-lg font-bold text-slate-900 mt-1">{style.label}</h2>
            <p className="text-xs text-slate-600 mt-0.5">{result.risk_assessment?.verdict}</p>
          </div>
        </div>

        {/* Quantitative Confidence Gauge */}
        <div className="bg-white p-3.5 rounded-xl border border-slate-200 shadow-subtle flex items-center space-x-5 shrink-0">
          <div>
            <div className="text-[11px] uppercase tracking-wider text-slate-400 font-mono font-medium">Confidence</div>
            <div className="text-xl font-bold text-slate-900 font-mono">{confidencePct}%</div>
          </div>
          <div className="border-l border-slate-200 pl-5">
            <div className="text-[11px] uppercase tracking-wider text-slate-400 font-mono font-medium">Risk Score</div>
            <div className="text-xl font-bold text-slate-900 font-mono">{riskPct}/100</div>
          </div>
        </div>
      </div>

      {/* Grid of Forensic Decompositions */}
      <div className="p-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {/* Model 1: Linguistic Intelligence */}
        <div className="p-4 rounded-xl border border-slate-200/90 bg-white space-y-3">
          <div className="flex items-center space-x-2 text-xs font-semibold uppercase tracking-wider text-slate-500 font-mono border-b border-slate-100 pb-2">
            <Globe className="w-3.5 h-3.5 text-blue-600" />
            <span>Model 1: Linguistic Analysis</span>
          </div>
          <div className="space-y-2 text-xs">
            <div className="flex justify-between items-center">
              <span className="text-slate-500">Detected Language:</span>
              <span className="font-semibold text-slate-900">
                {result.text_model?.detected_language || "N/A"}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-slate-500">Classification:</span>
              <span
                className={`font-semibold uppercase font-mono ${
                  result.text_model?.is_threat ? "text-red-600" : "text-emerald-600"
                }`}
              >
                {result.text_model?.predicted_label || "Clean"}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-slate-500">Model Confidence:</span>
              <span className="font-mono text-slate-700">
                {result.text_model?.confidence ? `${Math.round(result.text_model.confidence * 100)}%` : "—"}
              </span>
            </div>
          </div>
        </div>

        {/* Model 2: URL Inspection */}
        <div className="p-4 rounded-xl border border-slate-200/90 bg-white space-y-3">
          <div className="flex items-center space-x-2 text-xs font-semibold uppercase tracking-wider text-slate-500 font-mono border-b border-slate-100 pb-2">
            <LinkIcon className="w-3.5 h-3.5 text-cyan-600" />
            <span>Model 2: URL Lexical Inspection</span>
          </div>
          {result.url_model ? (
            <div className="space-y-2 text-xs">
              <div className="flex justify-between items-center">
                <span className="text-slate-500">Phishing Probability:</span>
                <span className="font-mono font-bold text-slate-900">
                  {Math.round(result.url_model.phishing_probability * 100)}%
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-slate-500">Classification:</span>
                <span className={`font-semibold uppercase font-mono ${result.url_model.is_phishing ? "text-red-600" : "text-emerald-600"}`}>
                  {result.url_model.is_phishing ? "Phishing URL" : "Legitimate URL"}
                </span>
              </div>
              {result.url_model.top_risk_factors && result.url_model.top_risk_factors.length > 0 && (
                <div className="pt-1">
                  <span className="text-[11px] text-slate-400 block mb-1">Risk Factors:</span>
                  <div className="flex flex-wrap gap-1">
                    {result.url_model.top_risk_factors.map((factor, idx) => (
                      <span key={idx} className="text-[10px] px-2 py-0.5 rounded bg-slate-100 text-slate-700 border border-slate-200">
                        {factor}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="text-xs text-slate-400 py-4 text-center">No standalone URL evaluated</div>
          )}
        </div>

        {/* Model 3: Scam Tactics */}
        <div className="p-4 rounded-xl border border-slate-200/90 bg-white space-y-3">
          <div className="flex items-center space-x-2 text-xs font-semibold uppercase tracking-wider text-slate-500 font-mono border-b border-slate-100 pb-2">
            <Fingerprint className="w-3.5 h-3.5 text-amber-600" />
            <span>Model 3: Social Engineering</span>
          </div>
          <div className="space-y-2 text-xs">
            <div className="flex justify-between items-center">
              <span className="text-slate-500">Tactics Detected:</span>
              <span className="font-bold text-slate-900">{result.tactic_model?.tactic_count || 0}</span>
            </div>
            {result.tactic_model?.detected_tactics && result.tactic_model.detected_tactics.length > 0 ? (
              <div className="flex flex-wrap gap-1 pt-1">
                {result.tactic_model.detected_tactics.map((tac, idx) => (
                  <span
                    key={idx}
                    className="text-[10px] px-2 py-0.5 rounded bg-amber-50 text-amber-800 border border-amber-200 font-medium"
                  >
                    {tac.replace(/_/g, " ")}
                  </span>
                ))}
              </div>
            ) : (
              <span className="text-xs text-slate-400">Zero manipulative tactics triggered.</span>
            )}
          </div>
        </div>
      </div>

      {/* Forensic Explainability & Remedial Actions */}
      <div className="p-6 border-t border-slate-100 bg-slate-50/30 grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Token Highlights / Explainability */}
        <div>
          <h4 className="text-xs font-semibold text-slate-800 uppercase tracking-wider font-mono flex items-center space-x-1.5 mb-2.5">
            <Sparkles className="w-3.5 h-3.5 text-blue-600" />
            <span>Forensic Evidence Highlighting</span>
          </h4>
          {result.explainability?.text_highlights && result.explainability.text_highlights.length > 0 ? (
            <div className="flex flex-wrap gap-1.5">
              {result.explainability.text_highlights.map((item, idx) => (
                <span
                  key={idx}
                  className="px-2.5 py-1 rounded-md bg-white border border-slate-200 text-xs font-mono text-slate-800 shadow-subtle flex items-center space-x-1.5"
                >
                  <span className="font-bold text-blue-600">"{item.token}"</span>
                  <span className="text-[10px] text-slate-400 font-medium">(w: {item.weight})</span>
                </span>
              ))}
            </div>
          ) : (
            <p className="text-xs text-slate-500 leading-relaxed">
              No strong deceptive lexical keywords were isolated. Communication patterns fall within normal benign distributions.
            </p>
          )}
        </div>

        {/* Actionable Remedial Guidance */}
        <div>
          <h4 className="text-xs font-semibold text-slate-800 uppercase tracking-wider font-mono flex items-center space-x-1.5 mb-2.5">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
            <span>Recommended Security Action</span>
          </h4>
          {result.risk_assessment?.remedial_actions && result.risk_assessment.remedial_actions.length > 0 ? (
            <ul className="space-y-1.5 text-xs text-slate-700">
              {result.risk_assessment.remedial_actions.map((action, idx) => (
                <li key={idx} className="flex items-start space-x-2">
                  <span className="text-blue-600 font-bold shrink-0">•</span>
                  <span>{action}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-xs text-slate-500 leading-relaxed">
              Standard operational vigilance recommended. No emergency intervention needed.
            </p>
          )}
        </div>
      </div>

      {/* Footer Info */}
      <div className="px-6 py-2.5 bg-slate-100/70 border-t border-slate-200/80 flex items-center justify-between text-[11px] font-mono text-slate-500">
        <div className="flex items-center space-x-1.5">
          <Clock className="w-3 h-3 text-slate-400" />
          <span>Inference Latency: {result.processing_time_ms} ms</span>
        </div>
        <div>Engine: Multi-Vector Threat Model Fusion v1.0.0</div>
      </div>
    </div>
  );
}
