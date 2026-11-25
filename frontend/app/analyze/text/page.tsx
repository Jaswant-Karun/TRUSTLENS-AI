"use client";

import React, { useCallback, useState } from "react";
import { PageHeader, AnalysisResultPanel, ErrorState } from "@/components/ui";
import { AnalyzeModeTabs } from "@/components/ui/AnalyzeModeTabs";
import { GlowButton } from "@/components/product/GlowButton";
import { scanText, ScanResult } from "@/lib/api";
import {
  ClipboardPaste,
  Globe,
  RefreshCw,
  Sparkles,
  Trash2,
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
    content:
      "Aapka SBI khata turant band ho jayega. Urgent verify karein: http://192.168.1.50/sbi-kyc/update.php",
  },
  {
    category: "SMS",
    label: "Electricity Bill Cutoff (Hindi)",
    channel: "sms",
    sender: "BZ-POWIND",
    language: "Hindi",
    content:
      "प्रिय ग्राहक, आपका बिजली कनेक्शन आज रात 9:30 बजे काट दिया जाएगा क्योंकि पिछला बिल अपडेट नहीं हुआ है। तुरंत 9876543210 पर संपर्क करें।",
  },
  {
    category: "SMS",
    label: "India Post Address Incomplete",
    channel: "sms",
    sender: "IP-POST",
    language: "English",
    content:
      "India Post: Your package could not be delivered due to incomplete street address. Please update within 12 hours: http://indiapost-parcel-tracking.xyz/address",
  },
  {
    category: "WhatsApp",
    label: "YouTube Video Rating Task Scam",
    channel: "whatsapp",
    sender: "+91 98402 11928",
    language: "English",
    content:
      "Hello! We offer flexible work from home job. Like and subscribe to 3 YouTube videos and earn Rs 1500 immediately. Telegram contact: @hr_recruit_99",
  },
  {
    category: "Job Offer",
    label: "Part-Time Reviewer Fee Scam",
    channel: "whatsapp",
    sender: "+91 87654 09876",
    language: "English",
    content:
      "URGENT HIRING: Part-time online marketing assistant needed. Daily payout Rs 3000 to Rs 8000. Send UPI deposit Rs 500 registration fee to upi@jobportal to start.",
  },
  {
    category: "Email",
    label: "CEO Wire Transfer Impersonation",
    channel: "email",
    sender: "ceo-office@company-corp.cc",
    language: "English",
    content:
      "Urgent: I am currently in an executive meeting and cannot take calls. Please immediately process a confidential wire transfer of $24,500 to vendor account #889124 before close of business.",
  },
  {
    category: "Legitimate",
    label: "Legitimate Bank Alert",
    channel: "sms",
    sender: "AD-HDFCBK",
    language: "English",
    content:
      "Dear Customer, INR 14,250.00 deposited to your A/C ending XX3401 on 24-Nov-2026 via NEFT from ACME TECH CORP. Total Available Balance: INR 68,910.40 - HDFC Bank",
  },
];

export default function TextAnalysisPage() {
  const [content, setContent] = useState("");
  const [channel, setChannel] = useState("sms");
  const [sender, setSender] = useState("");
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

  const executeScan = useCallback(
    async (customText?: string, customChannel?: string, customSender?: string) => {
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
      setProgressStep("Detecting script & tokenizing message...");

      const t1 = setTimeout(
        () => setProgressStep("Running Calibrated LinearSVC Scam Classifier (Model 1)..."),
        180
      );
      const t2 = setTimeout(
        () => setProgressStep("Evaluating Social Engineering Tactics (Model 3)..."),
        400
      );

      try {
        const data = await scanText({
          text: trimmed,
          channel: channelTarget,
          sender: senderTarget.trim() || undefined,
        });
        setResult(data);
      } catch (err: any) {
        setError(err?.message || "Failed to analyze text message.");
      } finally {
        clearTimeout(t1);
        clearTimeout(t2);
        setLoading(false);
        setProgressStep("");
      }
    },
    [content, channel, sender]
  );

  const handlePaste = async () => {
    try {
      const text = await navigator.clipboard.readText();
      if (text) setContent(text);
    } catch {
      setError("Clipboard access was blocked by the browser. Paste manually with Ctrl+V.");
    }
  };

  const handleClear = () => {
    setContent("");
    setSender("");
    setResult(null);
    setError(null);
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Message Intelligence"
        description="Multilingual fraud classification, language detection, tactic attribution, and calibrated risk scoring across English, Hindi (Devanagari), and Hinglish."
        badge={{ text: "Models 1 & 3 Live", variant: "rose" }}
      />

      <AnalyzeModeTabs />

      {/* Input Workbench Card */}
      <div className="cyber-panel p-5 sm:p-6 space-y-5">
        {/* Sample Presets */}
        <div>
          <div className="flex flex-wrap items-center justify-between gap-2 mb-2.5">
            <span className="text-[11px] font-mono uppercase text-[#A1A1AA] font-semibold tracking-wider">
              Sample Messages (Optional)
            </span>
            <div className="flex flex-wrap items-center gap-1 text-xs">
              {["All", "SMS", "WhatsApp", "Job Offer", "Email", "Legitimate"].map((cat) => (
                <button
                  key={cat}
                  type="button"
                  onClick={() => setSelectedCategory(cat)}
                  className={`px-2.5 py-1 rounded text-[11px] font-mono transition-colors ${
                    selectedCategory === cat
                      ? "bg-[#FF174F] text-white font-semibold"
                      : "text-[#A1A1AA] hover:text-white hover:bg-[#170A12]"
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
                type="button"
                onClick={() => {
                  setContent(preset.content);
                  setChannel(preset.channel);
                  setSender(preset.sender);
                  setError(null);
                  executeScan(preset.content, preset.channel, preset.sender);
                }}
                className={`text-xs px-3 py-1.5 rounded-lg border font-mono transition-colors text-left flex items-center space-x-2 ${
                  content === preset.content
                    ? "bg-[#FF174F]/15 border-[#FF174F] text-white font-semibold"
                    : "bg-[#050306] border-[#481326] text-[#A1A1AA] hover:border-[#FF174F]/60 hover:text-white"
                }`}
              >
                <span className="text-[10px] px-1.5 py-0.5 rounded bg-[#170A12] border border-[#481326] text-[#FF3D70]">
                  {preset.category}
                </span>
                <span>{preset.label}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Channel, Sender & Script Hint */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-1">
          <div>
            <label htmlFor="msg-channel" className="text-[11px] font-mono uppercase text-[#A1A1AA] block mb-1.5">
              Communication Channel
            </label>
            <select
              id="msg-channel"
              value={channel}
              onChange={(e) => setChannel(e.target.value)}
              className="cyber-select w-full font-mono"
            >
              <option value="sms">SMS Text Gateway</option>
              <option value="whatsapp">WhatsApp / Messaging</option>
              <option value="email">Email Gateway</option>
              <option value="job_offer">Job Offer Portal</option>
              <option value="telegram">Telegram Channel</option>
            </select>
          </div>

          <div>
            <label htmlFor="msg-sender" className="text-[11px] font-mono uppercase text-[#A1A1AA] block mb-1.5">
              Sender Identifier (Optional)
            </label>
            <input
              id="msg-sender"
              type="text"
              value={sender}
              onChange={(e) => setSender(e.target.value)}
              placeholder="e.g. VK-SBIBNK or +91..."
              className="cyber-input font-mono"
            />
          </div>

          <div>
            <label htmlFor="msg-lang" className="text-[11px] font-mono uppercase text-[#A1A1AA] block mb-1.5">
              Language Target
            </label>
            <select
              id="msg-lang"
              value={selectedLanguage}
              onChange={(e) => setSelectedLanguage(e.target.value)}
              className="cyber-select w-full font-mono"
            >
              <option value="auto">Auto-Detect (Recommended)</option>
              <option value="english">English</option>
              <option value="hindi">Hindi (Devanagari)</option>
              <option value="hinglish">Hinglish (Romanized)</option>
            </select>
          </div>
        </div>

        {/* Message Body */}
        <div>
          <div className="flex items-center justify-between mb-1.5">
            <label htmlFor="msg-content" className="text-[11px] font-mono uppercase text-[#A1A1AA]">
              Suspicious Message Content
            </label>
            <div className="flex items-center space-x-3 text-[11px] font-mono text-[#A1A1AA]">
              <span>{content.length} chars</span>
              <span>•</span>
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

          <textarea
            id="msg-content"
            value={content}
            onChange={(e) => setContent(e.target.value)}
            rows={5}
            placeholder="Paste suspicious SMS, WhatsApp message, email body, or job offer here..."
            className="cyber-input font-mono leading-relaxed"
          />
        </div>

        {/* Action & Engine Bar */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-3 border-t border-[#481326]/70">
          <div className="text-[11px] font-mono text-[#A1A1AA] flex items-center gap-2">
            <Globe className="w-3.5 h-3.5 text-[#FF3D70] shrink-0" />
            <span>
              Engine: Word+Char TF-IDF Calibrated LinearSVC (Model 1) + 9-Tactic OvR Classifier (Model 3)
            </span>
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
                <span>{progressStep || "ANALYZING..."}</span>
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                <span>Analyze Message</span>
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
