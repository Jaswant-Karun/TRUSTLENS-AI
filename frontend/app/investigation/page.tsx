"use client";

import React, { useState } from "react";
import { PageHeader, AnalysisResultPanel, ErrorState } from "@/components/ui";
import { scanComprehensive, ScanResult } from "@/lib/api";
import { Crosshair, Sparkles, RefreshCw, Layers, ShieldCheck, ArrowRight } from "lucide-react";

export default function ComprehensiveInvestigationPage() {
  const [content, setContent] = useState(
    "Aapka SBI khata turant band ho jayega. Urgent verify karein: http://192.168.1.50/sbi-kyc/update.php"
  );
  const [url, setUrl] = useState("http://192.168.1.50/sbi-kyc/update.php");
  const [channel, setChannel] = useState("sms");
  const [sender, setSender] = useState("VK-SBIBNK");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ScanResult | null>(null);

  const handleInvestigate = async () => {
    if (!content.trim()) {
      setError("Please provide communication content for multi-modal analysis.");
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const data = await scanComprehensive({
        content,
        url: url.trim() || undefined,
        channel,
        sender: sender.trim() || undefined,
      });
      setResult(data);
    } catch (err: any) {
      setError(err.message || "Failed to execute comprehensive investigation.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Comprehensive Multi-Modal Forensic Investigation Studio"
        description="Simultaneous cross-correlation across text semantics, zero-hop URL lexical analysis, social engineering tactics, and campaign clustering."
        badge={{ text: "All 4 Models Fused", variant: "rose" }}
      />

      {/* Investigation Dossier Input Workbench */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-subtle p-6 space-y-5">
        <div className="flex items-center space-x-2 pb-3 border-b border-slate-100 text-xs font-mono text-slate-500">
          <Layers className="w-4 h-4 text-rose-500" />
          <span className="font-semibold text-slate-800 uppercase tracking-wider">Multi-Vector Incident Telemetry</span>
        </div>

        {/* Channel and Sender Row */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="text-xs font-semibold text-slate-700 block mb-1">
              Ingestion Vector
            </label>
            <select
              value={channel}
              onChange={(e) => setChannel(e.target.value)}
              className="w-full text-xs font-mono p-2.5 rounded-lg border border-slate-300 bg-white focus:outline-none focus:ring-2 focus:ring-rose-500"
            >
              <option value="sms">SMS Text Gateway</option>
              <option value="whatsapp">WhatsApp / Instant Messaging</option>
              <option value="email">Email Phishing Gateway</option>
              <option value="web">Web Portal / Cloned Form</option>
            </select>
          </div>

          <div>
            <label className="text-xs font-semibold text-slate-700 block mb-1">
              Sender Header / IP Origin
            </label>
            <input
              type="text"
              value={sender}
              onChange={(e) => setSender(e.target.value)}
              placeholder="e.g. VK-SBIBNK or 203.0.113.15"
              className="w-full text-xs font-mono p-2.5 rounded-lg border border-slate-300 bg-white focus:outline-none focus:ring-2 focus:ring-rose-500"
            />
          </div>
        </div>

        {/* Content Body Input */}
        <div>
          <label className="text-xs font-semibold text-slate-700 block mb-1">
            Communication Body (SMS, WhatsApp, Email text)
          </label>
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            rows={3}
            placeholder="Paste suspicious text payload..."
            className="w-full text-xs font-mono p-3 rounded-lg border border-slate-300 bg-white focus:outline-none focus:ring-2 focus:ring-rose-500"
          />
        </div>

        {/* Associated URL Input */}
        <div>
          <label className="text-xs font-semibold text-slate-700 block mb-1">
            Contained / Extracted URL (Optional)
          </label>
          <input
            type="text"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="e.g. http://192.168.1.50/sbi-kyc/update.php"
            className="w-full text-xs font-mono p-2.5 rounded-lg border border-slate-300 bg-white focus:outline-none focus:ring-2 focus:ring-rose-500"
          />
        </div>

        {/* Action Bar */}
        <div className="flex items-center justify-between pt-2">
          <div className="text-[11px] font-mono text-slate-400">
            Pipeline: Multilingual NLP + XGBoost URL + SVM Tactics + HDBSCAN Density
          </div>

          <button
            onClick={handleInvestigate}
            disabled={loading}
            className="flex items-center space-x-2 px-6 py-2.5 bg-rose-600 hover:bg-rose-700 text-white text-xs font-semibold rounded-lg shadow-sm transition-all disabled:opacity-50"
          >
            {loading ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                <span>Correlating Vectors...</span>
              </>
            ) : (
              <>
                <Crosshair className="w-4 h-4" />
                <span>Launch Full Investigation</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Error State */}
      {error && <ErrorState message={error} onRetry={handleInvestigate} />}

      {/* Analysis Result Panel */}
      {result && <AnalysisResultPanel result={result} />}
    </div>
  );
}
