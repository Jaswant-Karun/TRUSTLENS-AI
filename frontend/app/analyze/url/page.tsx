"use client";

import React, { useState } from "react";
import { PageHeader, AnalysisResultPanel, ErrorState } from "@/components/ui";
import { scanUrl, ScanResult } from "@/lib/api";
import { Globe, Sparkles, RefreshCw, Link as LinkIcon, ShieldAlert } from "lucide-react";

const URL_PRESETS = [
  {
    label: "Direct IP Banking Phish",
    url: "http://192.168.1.50/sbi-kyc/update.php",
    type: "Malicious IP",
  },
  {
    label: "Typo-Squatted HDFC Portal",
    url: "http://secure-login-hdfcbank-account-update.xyz/login.php",
    type: "Typo-squat",
  },
  {
    label: "Complex Query Token Harvester",
    url: "http://203.0.113.15/secure-login-portal/auth.php?account_id=98214&kyc=required",
    type: "Credential Trap",
  },
  {
    label: "Legitimate Corporate Domain",
    url: "https://www.onlinesbi.sbi/portal/index.html",
    type: "Legitimate",
  },
];

export default function UrlAnalysisPage() {
  const [url, setUrl] = useState(URL_PRESETS[1].url);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ScanResult | null>(null);

  const handleScan = async () => {
    if (!url.trim()) {
      setError("Please provide a URL to inspect.");
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const data = await scanUrl(url);
      setResult(data);
    } catch (err: any) {
      setError(err.message || "Failed to inspect URL.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Zero-Hop Offline Phishing URL Inspection"
        description="Safe, lexical URL decomposition without web crawler visits or code execution using Model 2 (XGBoost)."
        badge={{ text: "Model 2 Active (ROC-AUC 1.000)", variant: "green" }}
      />

      {/* Input Workbench Card */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-subtle p-6 space-y-5">
        {/* Preset Selector */}
        <div>
          <span className="text-[11px] font-mono uppercase text-slate-400 font-semibold block mb-2">
            Preset URL Test Targets
          </span>
          <div className="flex flex-wrap gap-2">
            {URL_PRESETS.map((preset, idx) => (
              <button
                key={idx}
                onClick={() => {
                  setUrl(preset.url);
                  setError(null);
                }}
                className={`text-xs px-3 py-1.5 rounded-lg border font-mono transition-colors ${
                  url === preset.url
                    ? "bg-cyan-50 border-cyan-400 text-cyan-800 font-semibold"
                    : "bg-slate-50 border-slate-200 text-slate-600 hover:bg-slate-100"
                }`}
              >
                {preset.label}
              </button>
            ))}
          </div>
        </div>

        {/* URL Target Input */}
        <div>
          <label className="text-xs font-semibold text-slate-700 block mb-1">
            Suspicious Target URL or Domain
          </label>
          <div className="relative">
            <Globe className="w-4 h-4 text-slate-400 absolute left-3.5 top-3.5 pointer-events-none" />
            <input
              type="text"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="e.g. http://secure-login-portal.xyz/verify.php"
              className="w-full text-xs font-mono pl-10 pr-4 py-3 rounded-lg border border-slate-300 bg-white focus:outline-none focus:ring-2 focus:ring-cyan-500"
            />
          </div>
        </div>

        {/* Feature Preview Badges */}
        <div className="p-3 bg-slate-50 rounded-lg border border-slate-200 flex flex-wrap items-center gap-3 text-[11px] font-mono text-slate-600">
          <span className="font-semibold text-slate-800">Lexical Features Extracted:</span>
          <span>• Shannon Entropy</span>
          <span>• Direct IP Flag</span>
          <span>• Subdomain Depth</span>
          <span>• Suspicious TLD</span>
          <span>• Keyword Traps</span>
          <span className="text-emerald-600 font-bold ml-auto">✓ 100% Zero-Hop Safe</span>
        </div>

        {/* Action Bar */}
        <div className="flex items-center justify-between pt-2">
          <div className="text-[11px] font-mono text-slate-400">
            Engine: High-Throughput Lexical XGBoost Classifier
          </div>

          <button
            onClick={handleScan}
            disabled={loading}
            className="flex items-center space-x-2 px-5 py-2.5 bg-cyan-600 hover:bg-cyan-700 text-white text-xs font-semibold rounded-lg shadow-sm transition-all disabled:opacity-50"
          >
            {loading ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                <span>Extracting Features...</span>
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
