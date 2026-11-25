"use client";

import React, { useCallback, useState } from "react";
import { PageHeader, AnalysisResultPanel, ErrorState } from "@/components/ui";
import { AnalyzeModeTabs } from "@/components/ui/AnalyzeModeTabs";
import { GlowButton } from "@/components/product/GlowButton";
import { scanUrl, ScanResult } from "@/lib/api";
import {
  AlertTriangle,
  ClipboardPaste,
  Link as LinkIcon,
  Lock,
  RefreshCw,
  ShieldCheck,
  Sparkles,
  Trash2,
} from "lucide-react";

interface URLPreset {
  label: string;
  url: string;
  type: string;
}

const URL_PRESETS: URLPreset[] = [
  {
    label: "Direct IP Banking Phish",
    url: "http://192.168.1.50/sbi-kyc/update.php",
    type: "Direct IPv4",
  },
  {
    label: "Typo-Squatted Bank Trap",
    url: "http://secure-login-hdfcbank-account-update.xyz/login.php",
    type: "Suspicious TLD",
  },
  {
    label: "Query Token Harvester",
    url: "http://203.0.113.15/secure-login-portal/auth.php?account_id=98214&kyc=required",
    type: "Credential Trap",
  },
  {
    label: "India Post Parcel Phish",
    url: "http://indiapost-parcel-tracking.xyz/address/update",
    type: "Courier Phish",
  },
  {
    label: "Legitimate Bank Portal",
    url: "https://www.onlinesbi.sbi/portal/index.html",
    type: "Legitimate",
  },
];

export default function UrlAnalysisPage() {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ScanResult | null>(null);

  const executeScan = useCallback(
    async (targetUrl?: string) => {
      const candidate = targetUrl !== undefined ? targetUrl : url;
      const trimmed = candidate.trim();
      if (!trimmed) {
        setError("Please provide a target URL or domain to inspect.");
        return;
      }
      if (trimmed.length < 4 || /\s/.test(trimmed)) {
        setError("Enter a valid URL without spaces (minimum 4 characters).");
        return;
      }

      let normalized = trimmed;
      if (!/^https?:\/\//i.test(normalized)) {
        normalized = `http://${normalized}`;
      }

      try {
        new URL(normalized);
      } catch {
        setError("Malformed URL syntax. Please check the address and try again.");
        return;
      }

      setLoading(true);
      setError(null);
      try {
        const data = await scanUrl(normalized);
        setResult(data);
      } catch (err: any) {
        setError(err?.message || "Failed to inspect URL.");
      } finally {
        setLoading(false);
      }
    },
    [url]
  );

  const handlePaste = async () => {
    try {
      const text = await navigator.clipboard.readText();
      if (text) setUrl(text.trim());
    } catch {
      setError("Clipboard access was blocked by the browser. Paste manually with Ctrl+V.");
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
        title="URL Shield"
        description="Zero-hop offline phishing inspection using 16 lexical & structural features with SHAP explanations. Submitted URLs are treated as untrusted text and never visited."
        badge={{ text: "Model 2: Zero-Hop XGBoost", variant: "green" }}
      />

      <AnalyzeModeTabs />

      {/* Safety & Model Limitations Banners */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="cyber-panel p-4 border-[#00D68F]/40 flex items-start space-x-3 text-xs text-[#A1A1AA]">
          <ShieldCheck className="w-5 h-5 text-[#00D68F] shrink-0 mt-0.5" />
          <div className="leading-relaxed">
            <strong className="block font-mono uppercase text-white mb-0.5">
              Zero-Hop Untrusted Input Policy
            </strong>
            TRUSTLENS AI never visits, resolves, or executes submitted URLs. All
            analysis is performed purely offline on lexical and structural tokens.
          </div>
        </div>

        <div className="cyber-panel p-4 border-[#FFB020]/40 flex items-start space-x-3 text-xs text-[#A1A1AA]">
          <AlertTriangle className="w-5 h-5 text-[#FFB020] shrink-0 mt-0.5" />
          <div className="leading-relaxed">
            <strong className="block font-mono uppercase text-white mb-0.5">
              Model Limitations &amp; Uncertainty
            </strong>
            Lexical inspection cannot verify live TLS certificates, DNS age, or
            compromised legitimate hosts, and may flag long SaaS/CDN paths as
            elevated risk. Treat results as decision support, not absolute proof.
          </div>
        </div>
      </div>

      {/* URL Input Workbench */}
      <div className="cyber-panel p-5 sm:p-6 space-y-5">
        <div>
          <span className="text-[11px] font-mono uppercase text-[#A1A1AA] font-semibold tracking-wider block mb-2.5">
            Sample URLs (Inert Test Strings)
          </span>
          <div className="flex flex-wrap gap-2">
            {URL_PRESETS.map((preset, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => {
                  setUrl(preset.url);
                  setError(null);
                  executeScan(preset.url);
                }}
                className={`text-xs px-3 py-1.5 rounded-lg border font-mono transition-colors flex items-center space-x-2 ${
                  url === preset.url
                    ? "bg-[#FF174F]/15 border-[#FF174F] text-white font-semibold"
                    : "bg-[#050306] border-[#481326] text-[#A1A1AA] hover:border-[#FF174F]/60 hover:text-white"
                }`}
              >
                <span className="text-[10px] px-1.5 py-0.5 rounded bg-[#170A12] border border-[#481326] text-[#FF3D70]">
                  {preset.type}
                </span>
                <span>{preset.label}</span>
              </button>
            ))}
          </div>
        </div>

        <div>
          <div className="flex items-center justify-between mb-1.5">
            <label htmlFor="url-input" className="text-[11px] font-mono uppercase text-[#A1A1AA]">
              Target URL String (Never Auto-Opened)
            </label>
            <div className="flex items-center space-x-3 text-[11px] font-mono text-[#A1A1AA]">
              <button
                type="button"
                onClick={handlePaste}
                className="hover:text-[#FF3D70] flex items-center space-x-1 transition-colors"
              >
                <ClipboardPaste className="w-3.5 h-3.5" />
                <span>Paste</span>
              </button>
              <span>•</span>
              <button
                type="button"
                onClick={handleClear}
                className="hover:text-[#FF174F] flex items-center space-x-1 transition-colors"
              >
                <Trash2 className="w-3.5 h-3.5" />
                <span>Clear</span>
              </button>
            </div>
          </div>

          <div className="relative">
            <LinkIcon className="pointer-events-none absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-[#A1A1AA]" />
            <input
              id="url-input"
              type="text"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  e.preventDefault();
                  executeScan();
                }
              }}
              placeholder="Paste suspicious URL e.g. http://192.168.1.50/sbi-kyc/update.php"
              className="cyber-input pl-10 font-mono"
            />
          </div>
        </div>

        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-3 border-t border-[#481326]/70">
          <div className="text-[11px] font-mono text-[#A1A1AA] flex items-center gap-2">
            <Lock className="w-3.5 h-3.5 text-[#00D68F] shrink-0" />
            <span>Engine: XGBoost 16-Feature Lexical Classifier + SHAP TreeExplainer</span>
          </div>

          <GlowButton
            type="button"
            variant="primary"
            onClick={() => executeScan()}
            disabled={loading}
          >
            {loading ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                <span>INSPECTING URL...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                <span>Inspect URL</span>
              </>
            )}
          </GlowButton>
        </div>
      </div>

      {/* Error State */}
      {error && <ErrorState message={error} onRetry={() => executeScan()} />}

      {/* Real ML Inference Result */}
      {result && <AnalysisResultPanel result={result} />}
    </div>
  );
}
