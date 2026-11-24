"use client";

import React, { useState } from "react";
import { PageHeader, AnalysisResultPanel, ErrorState } from "@/components/ui";
import { scanText, ScanResult } from "@/lib/api";
import {
  MessageSquare,
  Sparkles,
  RefreshCw,
  Send,
  CheckCircle2,
  Globe,
  AlertTriangle,
  Fingerprint,
  ShieldCheck,
  ShieldAlert,
  ClipboardPaste,
  Trash2,
  Layers,
  ArrowRight,
  Info,
} from "lucide-react";

interface PresetLure {
  category: "SMS" | "WhatsApp" | "Email" | "Job Offer" | "Legitimate";
  label: string;
  channel: string;
  sender: string;
  language: string;
  content: string;
}

const PRESET_LURES: PresetLure[] = [
  {
    category: "SMS",
    label: "Hinglish SBI KYC Threat",
    channel: "sms",
    sender: "VK-SBIBNK",
    language: "Hinglish",
    content: "Aapka SBI khata turant band ho jayega. Urgent verify karein: http://192.168.1.50/sbi-kyc/update.php",
  },
  {
    category: "SMS",
    label: "Electricity Bill Cutoff (Hindi)",
    channel: "sms",
    sender: "BZ-POWIND",
    language: "Hindi",
    content: "प्रिय ग्राहक, आपका बिजली कनेक्शन आज रात 9:30 बजे काट दिया जाएगा क्योंकि पिछला बिल अपडेट नहीं हुआ है। तुरंत 9876543210 पर संपर्क करें।",
  },
  {
    category: "SMS",
    label: "India Post Address Incomplete",
    channel: "sms",
    sender: "IP-POST",
    language: "English",
    content: "India Post: Your package could not be delivered due to incomplete street address. Please update within 12 hours: http://indiapost-parcel-tracking.xyz/address",
  },
  {
    category: "WhatsApp",
    label: "YouTube Video Rating Task Scam",
    channel: "whatsapp",
    sender: "+91 98402 11928",
    language: "English",
    content: "Hello! We offer flexible work from home job. Like and subscribe to 3 YouTube videos and earn Rs 1500 immediately. Telegram contact: @hr_recruit_99",
  },
  {
    category: "Job Offer",
    label: "Part-Time Amazon Reviewer",
    channel: "whatsapp",
    sender: "+91 87654 09876",
    language: "English",
    content: "URGENT HIRING: Part-time online marketing assistant needed for Amazon product reviews. Daily payout Rs 3000 to Rs 8000. Send UPI deposit Rs 500 registration fee to upi@jobportal to start.",
  },
  {
    category: "Email",
    label: "CEO Wire Transfer Impersonation",
    channel: "email",
    sender: "ceo-office@company-corp.cc",
    language: "English",
    content: "Urgent: I am currently in an executive meeting and cannot take calls. Please immediately process a confidential wire transfer of $24,500 to vendor account #889124 before close of business.",
  },
  {
    category: "Legitimate",
    label: "Legitimate Bank Transaction Alert",
    channel: "sms",
    sender: "AD-HDFCBK",
    language: "English",
    content: "Dear Customer, INR 14,250.00 deposited to your A/C ending XX3401 on 24-Nov-2026 via NEFT from ACME TECH CORP. Total Available Balance: INR 68,910.40 - HDFC Bank",
  },
];

export default function TextAnalysisPage() {
  const [content, setContent] = useState(PRESET_LURES[0].content);
  const [channel, setChannel] = useState(PRESET_LURES[0].channel);
  const [sender, setSender] = useState(PRESET_LURES[0].sender);
  const [selectedLanguage, setSelectedLanguage] = useState<string>("auto");
  const [selectedCategory, setSelectedCategory] = useState<string>("All");

  const [loading, setLoading] = useState(false);
  const [progressStep, setProgressStep] = useState<string>("");
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ScanResult | null>(null);

  const filteredPresets =
    selectedCategory === "All"
      ? PRESET_LURES
      : PRESET_LURES.filter((p) => p.category === selectedCategory);

  const executeScan = async (customText?: string, customChannel?: string, customSender?: string) => {
    const textTarget = customText !== undefined ? customText : content;
    const channelTarget = customChannel !== undefined ? customChannel : channel;
    const senderTarget = customSender !== undefined ? customSender : sender;

    const trimmed = textTarget.trim();
    if (!trimmed) {
      setError("Please provide a suspicious communication text to analyze.");
      return;
    }
    if (trimmed.length < 2) {
      setError("Message text must contain at least 2 characters.");
      return;
    }

    setLoading(true);
    setError(null);
    setProgressStep("Initializing Linguistic & Semantic NLP Pipeline...");

    try {
      setTimeout(() => setProgressStep("Extracting Lexical Signals & Calibrating Model 1..."), 150);
      setTimeout(() => setProgressStep("Scanning 10 Social Engineering Tactics with Model 3..."), 350);

      const data = await scanText({
        text: trimmed,
        channel: channelTarget,
        sender: senderTarget.trim() || undefined,
      });

      setResult(data);
    } catch (err: any) {
      setError(err.message || "Failed to analyze text message.");
    } finally {
      setLoading(false);
      setProgressStep("");
    }
  };

  const handleScan = () => executeScan();

  React.useEffect(() => {
    executeScan(PRESET_LURES[0].content, PRESET_LURES[0].channel, PRESET_LURES[0].sender);
  }, []);

  const handlePaste = async () => {
    try {
      const text = await navigator.clipboard.readText();
      if (text) setContent(text);
    } catch {
      // Clipboard access denied
    }
  };

  const handleClear = () => {
    setContent("");
    setResult(null);
    setError(null);
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Multilingual Text Scam & Social Engineering Analysis"
        description="Linguistic decomposition of SMS, WhatsApp, Email, and Job Offer lures across English, Hindi (Devanagari), and romanized Hinglish."
        badge={{ text: "Models 1 & 3 Active", variant: "blue" }}
      />

      {/* Input Workbench Card */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-subtle p-6 space-y-5">
        {/* Category Filter for Presets */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <span className="text-[11px] font-mono uppercase text-slate-500 font-semibold tracking-wider">
              Benchmark Lure Presets
            </span>
            <div className="flex items-center space-x-1 text-xs">
              {["All", "SMS", "WhatsApp", "Job Offer", "Email", "Legitimate"].map((cat) => (
                <button
                  key={cat}
                  onClick={() => setSelectedCategory(cat)}
                  className={`px-2 py-0.5 rounded text-[11px] font-mono transition-colors ${
                    selectedCategory === cat
                      ? "bg-slate-900 text-white font-semibold"
                      : "text-slate-500 hover:text-slate-800 hover:bg-slate-100"
                  }`}
                >
                  {cat}
                </button>
              ))}
            </div>
          </div>

          <div className="flex flex-wrap gap-2">
            {filteredPresets.map((preset, idx) => (
              <button
                key={idx}
                onClick={() => {
                  setContent(preset.content);
                  setChannel(preset.channel);
                  setSender(preset.sender);
                  setError(null);
                  executeScan(preset.content, preset.channel, preset.sender);
                }}
                className={`text-xs px-3 py-1.5 rounded-lg border font-mono transition-colors text-left flex items-center space-x-2 ${
                  content === preset.content
                    ? "bg-blue-50 border-blue-400 text-blue-700 font-semibold"
                    : "bg-slate-50 border-slate-200 text-slate-600 hover:bg-slate-100"
                }`}
              >
                <span className="text-[10px] px-1.5 py-0.2 rounded bg-slate-200 text-slate-700">
                  {preset.category}
                </span>
                <span>{preset.label}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Ingestion Parameters: Channel, Sender, Language Mode */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-1">
          <div>
            <label className="text-xs font-semibold text-slate-700 block mb-1">
              Communication Channel
            </label>
            <select
              value={channel}
              onChange={(e) => setChannel(e.target.value)}
              className="w-full text-xs font-mono p-2.5 rounded-lg border border-slate-300 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="sms">SMS Text Gateway</option>
              <option value="whatsapp">WhatsApp / Messaging</option>
              <option value="email">Email Gateway</option>
              <option value="job_offer">Job Offer Portal</option>
              <option value="telegram">Telegram Channel</option>
            </select>
          </div>

          <div>
            <label className="text-xs font-semibold text-slate-700 block mb-1">
              Sender Identifier / Header (Optional)
            </label>
            <input
              type="text"
              value={sender}
              onChange={(e) => setSender(e.target.value)}
              placeholder="e.g. VK-SBIBNK or +91 98402 11928"
              className="w-full text-xs font-mono p-2.5 rounded-lg border border-slate-300 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="text-xs font-semibold text-slate-700 block mb-1">
              Language Target / Script Hint
            </label>
            <select
              value={selectedLanguage}
              onChange={(e) => setSelectedLanguage(e.target.value)}
              className="w-full text-xs font-mono p-2.5 rounded-lg border border-slate-300 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="auto">Auto-Detect Script (Recommended)</option>
              <option value="hinglish">Hinglish (Romanized Hindi-English)</option>
              <option value="hindi">Hindi (Devanagari Script)</option>
              <option value="english">Standard English</option>
            </select>
          </div>
        </div>

        {/* Text Payload Input */}
        <div>
          <div className="flex items-center justify-between mb-1.5">
            <label className="text-xs font-semibold text-slate-700">
              Suspicious Message Content Body
            </label>
            <div className="flex items-center space-x-3 text-[11px] font-mono text-slate-400">
              <span>{content.length} characters</span>
              <span>•</span>
              <button
                type="button"
                onClick={handlePaste}
                className="hover:text-blue-600 flex items-center space-x-1 transition-colors"
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

          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            rows={4}
            placeholder="Paste suspicious SMS, WhatsApp message, email body, or job offer description here..."
            className="w-full text-xs font-mono p-3 rounded-lg border border-slate-300 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 leading-relaxed"
          />
        </div>

        {/* Scan Action Bar */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-2 border-t border-slate-100">
          <div className="text-[11px] font-mono text-slate-500 flex items-center space-x-2">
            <span className="w-2 h-2 rounded-full bg-blue-500"></span>
            <span>Engine: Multilingual Bi-LSTM (Model 1) + 10-Tactic SVM (Model 3)</span>
          </div>

          <button
            onClick={handleScan}
            disabled={loading}
            className="flex items-center justify-center space-x-2 px-6 py-2.5 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold rounded-lg shadow-sm transition-all disabled:opacity-50"
          >
            {loading ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                <span>{progressStep || "Analyzing Communication..."}</span>
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                <span>Execute Deep Text Scan</span>
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
