"use client";

import React, { useState, useEffect } from "react";
import { PageHeader, AnalysisResultPanel, ErrorState } from "@/components/ui";
import { AnalyzeModeTabs } from "@/components/ui/AnalyzeModeTabs";
import { scanUrl, ScanResult } from "@/lib/api";
import {
  Globe,
  Sparkles,
  RefreshCw,
  Link as LinkIcon,
  ShieldAlert,
  ShieldCheck,
  AlertTriangle,
  Lock,
  ClipboardPaste,
  Trash2,
  Info,
  CheckCircle2,
  ExternalLink,
} from "lucide-react";

interface URLPreset {
  label: string;
  url: string;
  type: string;
  severity: "critical" | "high" | "clean";
}

const URL_PRESETS: URLPreset[] = [
  {
    label: "Direct IP Banking Phish (SBI Clone)",
    url: "http://192.168.1.50/sbi-kyc/update.php",
    type: "Malicious Direct IPv4",
    severity: "critical",
  },
  {
    label: "Typo-Squatted HDFC Account Trap",
    url: "http://secure-login-hdfcbank-account-update.xyz/login.php",
    type: "Suspicious TLD & Typo-squat",
    severity: "critical",
  },
  {
    label: "Complex Query Token Harvester",
    url: "http://203.0.113.15/secure-login-portal/auth.php?account_id=98214&kyc=required",
    type: "Credential Extraction Trap",
    severity: "critical",
  },
  {
    label: "India Post Parcel Phish",
    url: "http://indiapost-parcel-tracking.xyz/address/update",
    type: "Courier Impersonation",
    severity: "high",
  },
  {
    label: "Legitimate State Bank Portal",
    url: "https://www.onlinesbi.sbi/portal/index.html",
    type: "Verified Corporate Banking",
    severity: "clean",
  },
];

export default function UrlAnalysisPage() {
  const [url, setUrl] = useState(URL_PRESETS[0].url);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ScanResult | null>(null);

  const executeScan = async (targetUrl?: string) => {
    const candidate = targetUrl || url;
    const trimmed = candidate.trim();
    if (!trimmed) {
      setError("Please provide a target URL or domain to inspect.");
      return;
    }

    if (trimmed.length < 4) {
      setError("URL string is too short to extract lexical features.");
      return;
    }

    // Ensure scheme is present for parsing
    let normalized = trimmed;
    if (!normalized.startsWith("http://") && !normalized.startsWith("https://")) {
      normalized = "http://" + normalized;
    }

    setLoading(true);
    setError(null);
    try {
      const data = await scanUrl(normalized);
      setResult(data);
    } catch (err: any) {
      setError(err.message || "Failed to inspect URL.");
    } finally {
      setLoading(false);
    }
  };

  const handleScan = () => executeScan();

  // Initial scan on mount
  useEffect(() => {
    executeScan(URL_PRESETS[0].url);
  }, []);

  const handlePaste = async () => {
    try {
      const text = await navigator.clipboard.readText();
      if (text) setUrl(text.trim());
    } catch {
      // Clipboard access denied
    }
  };

  const handleClear = () => {
    setUrl("");
    setResult(null);
    setError(null);
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Zero-Hop Offline Phishing URL Inspection"
        description="Safe, lexical URL decomposition without web crawler visits, DNS lookups, or script execution using Model 2 (XGBoost)."
        badge={{ text: "Model 2 Active (ROC-AUC 1.000)", variant: "green" }}
      />

      <AnalyzeModeTabs />

      {/* Mandatory Security Alerts */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Banner 1: Zero-Hop Rule */}
        <div className="p-3.5 bg-emerald-50 rounded-xl border border-emerald-200 flex items-start space-x-3 text-xs text-emerald-800">
          <ShieldCheck className="w-5 h-5 text-emerald-600 shrink-0 mt-0.5" />
          <div className="leading-relaxed">
            <strong className="block font-semibold">100% Zero-Hop Lexical Inspection</strong>
            TRUSTLENS AI decomposes URLs purely through offline structural and entropy analysis. Target servers are <strong>never visited, pinged, or resolved</strong>.
          </div>
        </div>

        {/* Banner 2: Fallback Caution Rule */}
        <div className="p-3.5 bg-amber-50 rounded-xl border border-amber-200 flex items-start space-x-3 text-xs text-amber-800">
          <AlertTriangle className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
          <div className="leading-relaxed">
            <strong className="block font-semibold">Heuristic Verification Rule</strong>
            Never classify a newly submitted URL as safe solely because it has no prior threat-intelligence record or public blocklist match.
          </div>
        </div>
      </div>

      {/* Input Workbench Card */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-subtle p-6 space-y-5">
        {/* Preset Selector */}
        <div>
          <span className="text-[11px] font-mono uppercase text-slate-500 font-semibold tracking-wider block mb-2">
            Preset URL Test Benchmarks
          </span>
          <div className="flex flex-wrap gap-2">
            {URL_PRESETS.map((preset, idx) => (
              <button
                key={idx}
                onClick={() => {
                  setUrl(preset.url);
                  setError(null);
                  executeScan(preset.url);
                }}
                className={`text-xs px-3 py-1.5 rounded-lg border font-mono transition-colors text-left flex items-center space-x-2 ${
                  url === preset.url
                    ? "bg-cyan-50 border-cyan-400 text-cyan-800 font-semibold"
                    : "bg-slate-50 border-slate-200 text-slate-600 hover:bg-slate-100"
                }`}
              >
                <span
                  className={`text-[9px] px-1.5 py-0.2 rounded font-semibold uppercase ${
                    preset.severity === "critical"
                      ? "bg-rose-100 text-rose-700"
                      : preset.severity === "high"
                      ? "bg-amber-100 text-amber-700"
                      : "bg-emerald-100 text-emerald-700"
                  }`}
                >
                  {preset.type}
                </span>
                <span>{preset.label}</span>
              </button>
            ))}
          </div>
        </div>

        {/* URL Target Input */}
        <div>
          <div className="flex items-center justify-between mb-1.5">
            <label className="text-xs font-semibold text-slate-700">
              Suspicious Target URL or Domain String
            </label>
            <div className="flex items-center space-x-3 text-[11px] font-mono text-slate-400">
              <button
                type="button"
                onClick={handlePaste}
                className="hover:text-cyan-600 flex items-center space-x-1 transition-colors"
                title="Paste from clipboard"
              >
                <ClipboardPaste className="w-3.5 h-3.5" />
                <span>Paste</span>
              </button>
              <span>•</span>
              <button
                type="button"
                onClick={handleClear}
                className="hover:text-rose-600 flex items-center space-x-1 transition-colors"
                title="Clear input"
              >
                <Trash2 className="w-3.5 h-3.5" />
                <span>Clear</span>
              </button>
            </div>
          </div>

          <div className="relative">
            <Globe className="w-4 h-4 text-slate-400 absolute left-3.5 top-3.5 pointer-events-none" />
            <input
              type="text"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="e.g. http://192.168.1.50/sbi-kyc/update.php"
              className="w-full text-xs font-mono pl-10 pr-4 py-3 rounded-lg border border-slate-300 bg-white focus:outline-none focus:ring-2 focus:ring-cyan-500 shadow-inner"
            />
          </div>
        </div>

        {/* Feature Preview Badges */}
        <div className="p-3 bg-slate-50 rounded-lg border border-slate-200 flex flex-wrap items-center gap-3 text-[11px] font-mono text-slate-600">
          <span className="font-semibold text-slate-800">Model 2 Structural Extraction:</span>
          <span>• Shannon Entropy</span>
          <span>• Direct IPv4 / IPv6</span>
          <span>• Subdomain Depth</span>
          <span>• Script Extension Flag</span>
          <span>• Numeric Character Ratio</span>
          <span className="text-emerald-600 font-bold ml-auto">✓ High-Throughput Offline</span>
        </div>

        {/* Action Bar */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-2 border-t border-slate-100">
          <div className="text-[11px] font-mono text-slate-500 flex items-center space-x-2">
            <span className="w-2 h-2 rounded-full bg-cyan-500"></span>
            <span>Classifier: XGBoost (29 Extracted Features + TreeSHAP Explainer)</span>
          </div>

          <button
            onClick={handleScan}
            disabled={loading}
            className="flex items-center justify-center space-x-2 px-6 py-2.5 bg-cyan-600 hover:bg-cyan-700 text-white text-xs font-semibold rounded-lg shadow-sm transition-all disabled:opacity-50"
          >
            {loading ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                <span>Decomposing Lexical Features...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                <span>Execute Zero-Hop URL Scan</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Error State */}
      {error && <ErrorState message={error} onRetry={handleScan} />}

      {/* Analysis Result Panel */}
      {result && <AnalysisResultPanel result={result} />}
    </div>
  );
}
