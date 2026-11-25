"use client";

import React, { useEffect, useState } from "react";
import { ShieldAlert, Globe2, Cpu, Scale, Lock, Mail, AlertTriangle, CheckCircle2 } from "lucide-react";
import { apiFetch } from "@/lib/api";

export default function MethodologyPage() {
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    apiFetch<any>("/privacy/transparency").then(setData).catch(() => null);
  }, []);

  const evaluatedLangs = data?.supported_languages?.evaluated || ["English", "Hindi", "Hinglish"];
  const unsupportedLangs = data?.supported_languages?.unsupported_unverified || ["Tamil", "Bengali"];

  return (
    <div className="max-w-5xl mx-auto px-4 py-8 space-y-6">
      <div className="space-y-2">
        <h1 className="text-2xl font-bold text-white flex items-center gap-2">
          <Scale className="w-6 h-6 text-cyan-400" />
          Transparent AI Methodology &amp; Trust Framework
        </h1>
        <p className="text-sm text-slate-400">
          How TRUSTLENS AI models work, where they are limited, how user data is protected, and why human review remains mandatory.
        </p>
      </div>

      {/* Clear User-Facing Disclaimer */}
      <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-200 text-xs space-y-1">
        <div className="font-bold uppercase tracking-wider flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 text-amber-400" />
          Decision-Support Disclaimer (Not Universal Fraud Detection)
        </div>
        <p>
          TRUSTLENS AI provides statistical risk profiling and similarity intelligence. It does <strong>not</strong> guarantee universal fraud detection or 100% accuracy, and automated outputs do not constitute legal proof of criminal origin.
        </p>
      </div>

      {/* Supported & Unsupported Languages */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="p-5 rounded-xl bg-slate-900/90 border border-slate-800 space-y-2">
          <h2 className="text-sm font-bold text-slate-100 flex items-center gap-2">
            <Globe2 className="w-4 h-4 text-emerald-400" />
            Evaluated Languages
          </h2>
          <div className="flex flex-wrap gap-2">
            {evaluatedLangs.map((l: string) => (
              <span key={l} className="px-2.5 py-1 rounded text-xs font-mono bg-emerald-500/15 text-emerald-300 border border-emerald-500/30">
                {l}
              </span>
            ))}
          </div>
          <p className="text-xs text-slate-400 mt-2">
            Unsupported / Unverified (0 samples):{" "}
            <span className="text-amber-300 font-mono">{unsupportedLangs.join(", ")}</span>
          </p>
        </div>

        <div className="p-5 rounded-xl bg-slate-900/90 border border-slate-800 space-y-2">
          <h2 className="text-sm font-bold text-slate-100 flex items-center gap-2">
            <Lock className="w-4 h-4 text-cyan-400" />
            Data Handling &amp; User Rights
          </h2>
          <ul className="text-xs text-slate-300 space-y-1 list-disc pl-4">
            <li>PII (phones, emails, OTPs, UPIs, PAN, Aadhaar) masked prior to persistence.</li>
            <li>90-day retention for analyses &amp; unverified reports; 365-day security audit logs.</li>
            <li>Self-service data export (<code>/auth/export-data</code>), deletion (<code>/auth/account</code>), and consent (<code>/privacy/consent</code>).</li>
          </ul>
        </div>
      </div>

      {/* Model Limitations & Uncertainty */}
      <div className="p-5 rounded-xl bg-slate-900/90 border border-slate-800 space-y-3">
        <h2 className="text-sm font-bold text-slate-100 flex items-center gap-2">
          <Cpu className="w-4 h-4 text-cyan-400" />
          Model Limitations &amp; Prediction Uncertainty
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs text-slate-300">
          <div className="p-3 rounded-lg bg-slate-950 border border-slate-800">
            <div className="font-semibold text-slate-100">Model 1 — Multilingual Text (v2.1)</div>
            <p className="text-slate-400 mt-1">Word+Char TF-IDF + Platt-calibrated LinearSVC. Evaluated on English, Hindi, Hinglish; Tamil/Bengali unverified.</p>
          </div>
          <div className="p-3 rounded-lg bg-slate-950 border border-slate-800">
            <div className="font-semibold text-slate-100">Model 2 — Zero-Hop URL (v2.2)</div>
            <p className="text-slate-400 mt-1">Offline XGBoost + brand/homograph/typosquatting signals. Never visits target URLs; uncalibrated tree score.</p>
          </div>
          <div className="p-3 rounded-lg bg-slate-950 border border-slate-800">
            <div className="font-semibold text-slate-100">Model 3 — Fraud Tactics (v2.3)</div>
            <p className="text-slate-400 mt-1">Platt-calibrated OvR LinearSVC across 9 tactics. <code>fake_investment</code> is Blocked (0 verified labels).</p>
          </div>
          <div className="p-3 rounded-lg bg-slate-950 border border-slate-800">
            <div className="font-semibold text-slate-100">Model 4 — Campaign Clustering (v2.4)</div>
            <p className="text-slate-400 mt-1">Multilingual MiniLM-L12-v2 + HDBSCAN. Similarity alone is never proof of shared criminal origin.</p>
          </div>
        </div>
      </div>

      {/* Human Review & Security Contact */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="p-5 rounded-xl bg-slate-900/90 border border-slate-800 space-y-2">
          <h2 className="text-sm font-bold text-slate-100 flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            Moderation &amp; Human Review
          </h2>
          <p className="text-xs text-slate-300">
            Community reports follow <code>pending → reviewed → rejected / confirmed</code>. Only analyst-confirmed reports or human-verified feedback can influence threat intelligence or training pools.
          </p>
        </div>
        <div className="p-5 rounded-xl bg-slate-900/90 border border-slate-800 space-y-2">
          <h2 className="text-sm font-bold text-slate-100 flex items-center gap-2">
            <Mail className="w-4 h-4 text-cyan-400" />
            Security Contact
          </h2>
          <p className="text-xs text-slate-300">
            Report security issues responsibly to <span className="font-mono text-cyan-300">security@trustlens.ai</span>.
          </p>
        </div>
      </div>
    </div>
  );
}
