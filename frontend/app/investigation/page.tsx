"use client";

import React, { useState } from "react";
import { PageHeader, AnalysisResultPanel, ErrorState } from "@/components/ui";
import { AnalyzeModeTabs } from "@/components/ui/AnalyzeModeTabs";
import { scanComprehensive, ScanResult } from "@/lib/api";
import {
  Crosshair,
  Sparkles,
  RefreshCw,
  Layers,
  ShieldCheck,
  ShieldAlert,
  ArrowRight,
  Globe,
  Link as LinkIcon,
  Fingerprint,
  Network,
  Cpu,
  Info,
  CheckCircle2,
  AlertTriangle,
  ClipboardPaste,
  Trash2,
  AlertOctagon,
} from "lucide-react";

interface IncidentPreset {
  label: string;
  channel: string;
  sender: string;
  url: string;
  content: string;
  description: string;
}

const INCIDENT_PRESETS: IncidentPreset[] = [
  {
    label: "SBI Banking KYC Suspicion + Direct IP URL",
    channel: "sms",
    sender: "VK-SBIBNK",
    url: "http://192.168.1.50/sbi-kyc/update.php",
    content: "Aapka SBI khata turant band ho jayega. Urgent verify karein: http://192.168.1.50/sbi-kyc/update.php",
    description: "Urgency manipulation combined with direct IP address credential harvesting trap.",
  },
  {
    label: "Work-From-Home Task Fraud + UPI Trap",
    channel: "whatsapp",
    sender: "+91 98402 11928",
    url: "http://secure-workfromhome-portal.xyz/deposit",
    content: "URGENT: Earn 5000 daily part-time job from home! Complete simple YouTube rating tasks. Send UPI deposit 500 to upi@fastpay to start.",
    description: "High-yield investment pretext combined with non-refundable registration fee extortion.",
  },
  {
    label: "India Post Delivery Address Phish",
    channel: "sms",
    sender: "IP-POST",
    url: "http://indiapost-parcel-tracking.xyz/address/update",
    content: "India Post: Your parcel has arrived at our sorting hub but cannot be dispatched due to invalid postal address. Update within 24 hours: http://indiapost-parcel-tracking.xyz/address/update",
    description: "Fake courier alert weaponizing parcel tracking anxiety.",
  },
  {
    label: "Legitimate Corporate Salary Credit",
    channel: "sms",
    sender: "AD-HDFCBK",
    url: "",
    content: "Dear Customer, INR 45,000.00 credited to A/C XX8912 on 24-Nov-2026 by TECH SERVICES LTD. Available Balance INR 78,140.20 - HDFC Bank",
    description: "Genuine corporate banking credit transaction record.",
  },
];

export default function ComprehensiveInvestigationPage() {
  const [content, setContent] = useState(INCIDENT_PRESETS[0].content);
  const [url, setUrl] = useState(INCIDENT_PRESETS[0].url);
  const [channel, setChannel] = useState(INCIDENT_PRESETS[0].channel);
  const [sender, setSender] = useState(INCIDENT_PRESETS[0].sender);

  const [loading, setLoading] = useState(false);
  const [progressStatus, setProgressStatus] = useState<string>("");
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ScanResult | null>(null);

  const executeInvestigate = async (
    customContent?: string,
    customUrl?: string,
    customChannel?: string,
    customSender?: string
  ) => {
    const cTarget = customContent !== undefined ? customContent : content;
    const uTarget = customUrl !== undefined ? customUrl : url;
    const chTarget = customChannel !== undefined ? customChannel : channel;
    const sTarget = customSender !== undefined ? customSender : sender;

    const trimmedContent = cTarget.trim();
    if (!trimmedContent && !uTarget.trim()) {
      setError("Please provide either message text, a target URL, or both for investigation.");
      return;
    }

    setLoading(true);
    setError(null);
    setProgressStatus("Correlating multi-vector telemetry across 4 ML tracks...");

    try {
      setTimeout(() => setProgressStatus("Executing Model 1 (Text Scam) & Model 2 (Zero-Hop URL)..."), 200);
      setTimeout(() => setProgressStatus("Evaluating Model 3 (Tactics) & Model 4 (Campaign Clustering)..."), 450);

      const data = await scanComprehensive({
        content: trimmedContent || uTarget.trim(),
        url: uTarget.trim() || undefined,
        channel: chTarget,
        sender: sTarget.trim() || undefined,
      });

      setResult(data);
    } catch (err: any) {
      setError(err.message || "Failed to execute comprehensive investigation.");
    } finally {
      setLoading(false);
      setProgressStatus("");
    }
  };

  const handleInvestigate = () => executeInvestigate();

  React.useEffect(() => {
    executeInvestigate(
      INCIDENT_PRESETS[0].content,
      INCIDENT_PRESETS[0].url,
      INCIDENT_PRESETS[0].channel,
      INCIDENT_PRESETS[0].sender
    );
  }, []);

  const handleClear = () => {
    setContent("");
    setUrl("");
    setSender("");
    setResult(null);
    setError(null);
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Comprehensive Multi-Modal Forensic Investigation Studio"
        description="Unified cross-correlation across text semantics (Model 1), zero-hop lexical URLs (Model 2), social engineering tactics (Model 3), and campaign clustering (Model 4)."
        badge={{ text: "All 4 ML Engines Fused", variant: "rose" }}
      />

      <AnalyzeModeTabs />

      {/* Security Architecture Principle */}
      <div className="p-4 bg-slate-900 rounded-xl border border-slate-800 text-xs text-slate-300 flex items-start space-x-3">
        <Cpu className="w-5 h-5 text-rose-400 shrink-0 mt-0.5" />
        <div className="leading-relaxed">
          <strong className="text-white block font-sans font-semibold">
            Transparent De-aggregated Scoring Architecture
          </strong>
          TRUSTLENS AI presents distinct, verifiable outputs for each ML engine. The platform never buries model decisions inside an arbitrary black-box score; composite risk is calculated using documented, auditable weighted linear calibration.
        </div>
      </div>

      {/* ThreatQ Advanced Workspace Callout Banner */}
      <div className="p-4 bg-[#1E2631] rounded-xl border border-cyan-500/40 text-xs text-slate-200 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 shadow-xl">
        <div className="flex items-center space-x-3">
          <div className="w-9 h-9 rounded-lg bg-blue-600/20 border border-blue-500/50 flex items-center justify-center shrink-0 text-cyan-400">
            <Network className="w-5 h-5" />
          </div>
          <div>
            <h4 className="font-bold text-white text-sm">
              ThreatQ Advanced Cyber Threat Workspace
            </h4>
            <p className="text-slate-400 text-xs mt-0.5">
              Launch the dark immersive workspace with interactive relationship graph, right-side inspector, and correlation timeline.
            </p>
          </div>
        </div>
        <a
          href="/investigations/INV-2026-KYC-11"
          className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-md font-semibold flex items-center space-x-2 shrink-0 shadow-md shadow-blue-600/30 transition-all border border-blue-400/40"
        >
          <span>Launch ThreatQ Canvas</span>
          <ArrowRight className="w-4 h-4" />
        </a>
      </div>

      {/* Investigation Dossier Input Workbench */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-subtle p-6 space-y-5">
        {/* Preset Selector */}
        <div>
          <span className="text-[11px] font-mono uppercase text-slate-500 font-semibold tracking-wider block mb-2">
            Load Complex Incident Scenarios
          </span>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
            {INCIDENT_PRESETS.map((preset, idx) => (
              <button
                key={idx}
                onClick={() => {
                  setContent(preset.content);
                  setUrl(preset.url);
                  setChannel(preset.channel);
                  setSender(preset.sender);
                  setError(null);
                  executeInvestigate(preset.content, preset.url, preset.channel, preset.sender);
                }}
                className={`p-3 rounded-lg border text-left transition-colors font-mono ${
                  content === preset.content && url === preset.url
                    ? "bg-rose-50 border-rose-400 text-rose-900"
                    : "bg-slate-50 border-slate-200 text-slate-700 hover:bg-slate-100"
                }`}
              >
                <div className="text-xs font-bold">{preset.label}</div>
                <div className="text-[11px] text-slate-500 mt-1 line-clamp-1">{preset.description}</div>
              </button>
            ))}
          </div>
        </div>

        {/* Ingestion Parameters: Channel and Sender */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-1">
          <div>
            <label className="text-xs font-semibold text-slate-700 block mb-1">
              Ingestion Channel / Protocol
            </label>
            <select
              value={channel}
              onChange={(e) => setChannel(e.target.value)}
              className="w-full text-xs font-mono p-2.5 rounded-lg border border-slate-300 bg-white focus:outline-none focus:ring-2 focus:ring-rose-500"
            >
              <option value="sms">SMS Text Gateway</option>
              <option value="whatsapp">WhatsApp / Messaging</option>
              <option value="email">Email Gateway</option>
              <option value="web">Cloned Web Form</option>
              <option value="telegram">Telegram Public Channel</option>
            </select>
          </div>

          <div>
            <label className="text-xs font-semibold text-slate-700 block mb-1">
              Sender Header / IP Origin (Optional)
            </label>
            <input
              type="text"
              value={sender}
              onChange={(e) => setSender(e.target.value)}
              placeholder="e.g. VK-SBIBNK or 192.168.1.50"
              className="w-full text-xs font-mono p-2.5 rounded-lg border border-slate-300 bg-white focus:outline-none focus:ring-2 focus:ring-rose-500"
            />
          </div>
        </div>

        {/* Text Payload Input */}
        <div>
          <label className="text-xs font-semibold text-slate-700 block mb-1">
            Suspicious Communication Body (SMS, WhatsApp, Email text)
          </label>
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            rows={3}
            placeholder="Paste suspicious text payload..."
            className="w-full text-xs font-mono p-3 rounded-lg border border-slate-300 bg-white focus:outline-none focus:ring-2 focus:ring-rose-500 leading-relaxed"
          />
        </div>

        {/* URL Target Input */}
        <div>
          <label className="text-xs font-semibold text-slate-700 block mb-1">
            Embedded / Extracted URL Target (Optional)
          </label>
          <div className="relative">
            <Globe className="w-4 h-4 text-slate-400 absolute left-3.5 top-3.5 pointer-events-none" />
            <input
              type="text"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="e.g. http://192.168.1.50/sbi-kyc/update.php"
              className="w-full text-xs font-mono pl-10 pr-4 py-2.5 rounded-lg border border-slate-300 bg-white focus:outline-none focus:ring-2 focus:ring-rose-500"
            />
          </div>
        </div>

        {/* Action Bar */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-2 border-t border-slate-100">
          <div className="text-[11px] font-mono text-slate-500 flex items-center space-x-2">
            <span className="w-2 h-2 rounded-full bg-rose-500"></span>
            <span>Pipeline: Bi-LSTM Text + XGBoost URL + SVM Tactics + HDBSCAN Density</span>
          </div>

          <div className="flex items-center space-x-2">
            <button
              type="button"
              onClick={handleClear}
              className="px-3 py-2 text-xs font-mono text-slate-500 hover:text-slate-800 hover:bg-slate-100 rounded-lg transition-colors"
            >
              Clear
            </button>
            <button
              onClick={handleInvestigate}
              disabled={loading}
              className="flex items-center space-x-2 px-6 py-2.5 bg-rose-600 hover:bg-rose-700 text-white text-xs font-semibold rounded-lg shadow-sm transition-all disabled:opacity-50"
            >
              {loading ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>{progressStatus || "Correlating Vectors..."}</span>
                </>
              ) : (
                <>
                  <Crosshair className="w-4 h-4" />
                  <span>Launch Comprehensive Forensic Scan</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Error State */}
      {error && <ErrorState message={error} onRetry={handleInvestigate} />}

      {/* Individual Model Results Grid (Requirements: Show individual results from each model) */}
      {result && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2 text-xs font-mono uppercase tracking-wider text-slate-500 font-semibold">
              <Layers className="w-4 h-4 text-rose-500" />
              <span>Independent Machine Learning Sub-Engine Verdicts</span>
            </div>
            <span className="text-xs font-mono text-slate-400">
              Total Incident Processing: <strong>{result.processing_time_ms} ms</strong>
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Card 1: Model 1 Text Scam */}
            <div className="bg-white rounded-xl border border-slate-200 shadow-subtle p-5 flex flex-col justify-between space-y-3">
              <div>
                <div className="flex items-center justify-between pb-2 border-b border-slate-100">
                  <div className="flex items-center space-x-2">
                    <Globe className="w-4 h-4 text-blue-600" />
                    <span className="text-xs font-bold text-slate-900 font-mono">
                      Model 1: Multilingual Scam Classifier
                    </span>
                  </div>
                  <span
                    className={`text-[10px] font-mono px-2 py-0.5 rounded uppercase font-semibold ${
                      result.text_model?.is_threat
                        ? "bg-rose-50 text-rose-700 border border-rose-200"
                        : "bg-emerald-50 text-emerald-700 border border-emerald-200"
                    }`}
                  >
                    {result.text_model ? "Operational" : "Engine Inactive"}
                  </span>
                </div>

                {result.text_model ? (
                  <div className="mt-3 space-y-2 text-xs font-mono">
                    <div className="flex justify-between">
                      <span className="text-slate-500">Predicted Class:</span>
                      <strong className={result.text_model.is_threat ? "text-rose-600" : "text-emerald-600"}>
                        {result.text_model.predicted_label?.toUpperCase()}
                      </strong>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-500">Calibrated Confidence:</span>
                      <strong>{Math.round((result.text_model.confidence || 0) * 100)}%</strong>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-500">Detected Language:</span>
                      <span className="text-slate-800">{result.text_model.detected_language}</span>
                    </div>
                    <div className="p-2.5 bg-slate-50 rounded border border-slate-200 text-[11px] text-slate-600 mt-2">
                      {result.text_model.explanation || "Linguistic indicators analyzed."}
                    </div>
                  </div>
                ) : (
                  <div className="text-xs font-mono text-slate-400 py-4 text-center">
                    No text input provided for Model 1 evaluation.
                  </div>
                )}
              </div>

              <div className="text-[10px] font-mono text-slate-400 pt-2 border-t border-slate-100 flex justify-between">
                <span>Arch: Bi-LSTM + Calibrated Linear</span>
                <span>Latency: {result.text_model?.processing_time_ms ?? 0} ms</span>
              </div>
            </div>

            {/* Card 2: Model 2 Zero-Hop Phishing URL */}
            <div className="bg-white rounded-xl border border-slate-200 shadow-subtle p-5 flex flex-col justify-between space-y-3">
              <div>
                <div className="flex items-center justify-between pb-2 border-b border-slate-100">
                  <div className="flex items-center space-x-2">
                    <LinkIcon className="w-4 h-4 text-cyan-600" />
                    <span className="text-xs font-bold text-slate-900 font-mono">
                      Model 2: Zero-Hop Phishing URL Detector
                    </span>
                  </div>
                  <span
                    className={`text-[10px] font-mono px-2 py-0.5 rounded uppercase font-semibold ${
                      result.url_model?.is_phishing
                        ? "bg-rose-50 text-rose-700 border border-rose-200"
                        : result.url_model
                        ? "bg-emerald-50 text-emerald-700 border border-emerald-200"
                        : "bg-slate-100 text-slate-500"
                    }`}
                  >
                    {result.url_model ? "Confirmed Output" : "No URL Evaluated"}
                  </span>
                </div>

                {result.url_model ? (
                  <div className="mt-3 space-y-2 text-xs font-mono">
                    <div className="flex justify-between">
                      <span className="text-slate-500">Verdict:</span>
                      <strong className={result.url_model.is_phishing ? "text-rose-600" : "text-emerald-600"}>
                        {result.url_model.is_phishing ? "PHISHING URL DETECTED" : "LEGITIMATE URL"}
                      </strong>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-500">Risk Score:</span>
                      <strong>{Math.round((result.url_model.risk_score || 0) * 100)}%</strong>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-500">Shannon Entropy:</span>
                      <span>{result.url_model.features?.url_entropy ? `${Number(result.url_model.features.url_entropy).toFixed(2)} bits` : "N/A"}</span>
                    </div>
                    <div className="p-2.5 bg-slate-50 rounded border border-slate-200 text-[11px] text-slate-600 mt-2">
                      {result.url_model.top_risk_factors?.[0] || "Zero-hop lexical features validated."}
                    </div>
                  </div>
                ) : (
                  <div className="text-xs font-mono text-slate-400 py-4 text-center">
                    No target URL extracted from incident payload.
                  </div>
                )}
              </div>

              <div className="text-[10px] font-mono text-slate-400 pt-2 border-t border-slate-100 flex justify-between">
                <span>Arch: Gradient Boosted Trees (XGBoost)</span>
                <span>Latency: {result.url_model?.processing_time_ms ?? 0} ms</span>
              </div>
            </div>

            {/* Card 3: Model 3 Tactics */}
            <div className="bg-white rounded-xl border border-slate-200 shadow-subtle p-5 flex flex-col justify-between space-y-3">
              <div>
                <div className="flex items-center justify-between pb-2 border-b border-slate-100">
                  <div className="flex items-center space-x-2">
                    <Fingerprint className="w-4 h-4 text-amber-600" />
                    <span className="text-xs font-bold text-slate-900 font-mono">
                      Model 3: Social Engineering Tactics
                    </span>
                  </div>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-amber-50 text-amber-800 border border-amber-200 uppercase font-semibold">
                    {result.tactic_model?.tactic_count ?? 0} Detected
                  </span>
                </div>

                {result.tactic_model?.tactics && result.tactic_model.tactics.length > 0 ? (
                  <div className="mt-3 space-y-2">
                    {result.tactic_model.tactics.map((t: any, i: number) => (
                      <div key={i} className="p-2 rounded bg-slate-50 border border-slate-200 text-xs font-mono">
                        <div className="flex justify-between font-bold text-slate-800">
                          <span>{t.tactic_name || t.tactic_code}</span>
                          <span className="text-amber-700">{Math.round((t.confidence || 1.0) * 100)}%</span>
                        </div>
                        {t.evidence_tokens && t.evidence_tokens.length > 0 && (
                          <div className="text-[10px] text-slate-500 mt-1">
                            Tokens: {t.evidence_tokens.join(", ")}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-xs font-mono text-slate-400 py-4 text-center">
                    No psychological pressure tactics isolated.
                  </div>
                )}
              </div>

              <div className="text-[10px] font-mono text-slate-400 pt-2 border-t border-slate-100 flex justify-between">
                <span>Arch: One-vs-Rest Linear SVM (10 Classes)</span>
                <span>Latency: {result.tactic_model?.processing_time_ms ?? 0} ms</span>
              </div>
            </div>

            {/* Card 4: Model 4 Campaign Clustering */}
            <div className="bg-white rounded-xl border border-slate-200 shadow-subtle p-5 flex flex-col justify-between space-y-3">
              <div>
                <div className="flex items-center justify-between pb-2 border-b border-slate-100">
                  <div className="flex items-center space-x-2">
                    <Network className="w-4 h-4 text-purple-600" />
                    <span className="text-xs font-bold text-slate-900 font-mono">
                      Model 4: Campaign Discovery Engine
                    </span>
                  </div>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-purple-50 text-purple-800 border border-purple-200 uppercase font-semibold">
                    {result.campaign_association?.associated_campaign ? "Cluster Match" : "Isolated Sample"}
                  </span>
                </div>

                {result.campaign_association?.associated_campaign ? (
                  <div className="mt-3 space-y-2 text-xs font-mono">
                    <div className="font-bold text-purple-900">
                      {result.campaign_association.associated_campaign}
                    </div>
                    <div className="flex justify-between text-slate-600">
                      <span>Embedding Proximity:</span>
                      <strong>{((result.campaign_association.similarity_score || 0) * 100).toFixed(1)}%</strong>
                    </div>
                    <div className="flex justify-between text-slate-600">
                      <span>Historical Cluster Size:</span>
                      <span>{result.campaign_association.cluster_size || 0} messages</span>
                    </div>
                    <div className="p-2 bg-amber-50 rounded border border-amber-200 text-[10px] text-amber-800 leading-normal mt-2">
                      <Info className="w-3 h-3 inline mr-1 text-amber-600" />
                      {result.campaign_association.legal_disclaimer}
                    </div>
                  </div>
                ) : (
                  <div className="text-xs font-mono text-slate-400 py-4 text-center">
                    No active campaign cluster linkage identified.
                  </div>
                )}
              </div>

              <div className="text-[10px] font-mono text-slate-400 pt-2 border-t border-slate-100 flex justify-between">
                <span>Arch: MiniLM-L6-v2 + HDBSCAN Density</span>
                <span>Latency: {result.campaign_association?.processing_time_ms ?? 0} ms</span>
              </div>
            </div>
          </div>

          {/* Full Forensic Panel with PhiShark Risk Gauge & Guidance */}
          <AnalysisResultPanel result={result} />
        </div>
      )}
    </div>
  );
}
