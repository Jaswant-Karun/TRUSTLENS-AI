"use client";

import React, { useState } from "react";
import { PageHeader, AnalysisResultPanel, ErrorState } from "@/components/ui";
import { scanText, ScanResult } from "@/lib/api";
import { MessageSquare, Sparkles, RefreshCw, Send, CheckCircle2 } from "lucide-react";

const TEXT_PRESETS = [
  {
    label: "Hinglish SBI KYC Scam",
    content: "Aapka SBI khata turant band ho jayega. Urgent verify karein: http://192.168.1.50/sbi-kyc/update.php",
    channel: "sms",
  },
  {
    label: "Fake Work-From-Home Scam",
    content: "URGENT: Earn 5000 daily part-time job from home! Complete simple YouTube rating tasks. Send UPI deposit 500 to start.",
    channel: "whatsapp",
  },
  {
    label: "Electricity Bill Threat (Hindi)",
    content: "प्रिय ग्राहक, आपका बिजली कनेक्शन आज रात काट दिया जाएगा क्योंकि बिल बकाया है। तुरंत इस नंबर पर संपर्क करें।",
    channel: "sms",
  },
  {
    label: "Legitimate Bank Notification",
    content: "Dear Customer, your A/C ending 4912 has been credited with INR 12,500.00 on 24-Nov-2026. Avail Bal: INR 52,190.50 - HDFC Bank",
    channel: "sms",
  },
];

export default function TextAnalysisPage() {
  const [content, setContent] = useState(TEXT_PRESETS[0].content);
  const [channel, setChannel] = useState("sms");
  const [sender, setSender] = useState("VK-SBIBNK");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ScanResult | null>(null);

  const handleScan = async () => {
    if (!content.trim()) {
      setError("Please provide a text message to analyze.");
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const data = await scanText({ content, channel, sender });
      setResult(data);
    } catch (err: any) {
      setError(err.message || "Failed to analyze text message.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Multilingual Text Scam Analysis"
        description="Deconstruct suspicious communications across English, Hindi (Devanagari), and romanized Hinglish using Models 1 & 3."
        badge={{ text: "Models 1 & 3 Active", variant: "blue" }}
      />

      {/* Input Workbench Card */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-subtle p-6 space-y-5">
        {/* Preset Selector */}
        <div>
          <span className="text-[11px] font-mono uppercase text-slate-400 font-semibold block mb-2">
            Preset Test Lures
          </span>
          <div className="flex flex-wrap gap-2">
            {TEXT_PRESETS.map((preset, idx) => (
              <button
                key={idx}
                onClick={() => {
                  setContent(preset.content);
                  setChannel(preset.channel);
                  setError(null);
                }}
                className={`text-xs px-3 py-1.5 rounded-lg border font-mono transition-colors ${
                  content === preset.content
                    ? "bg-blue-50 border-blue-400 text-blue-700 font-semibold"
                    : "bg-slate-50 border-slate-200 text-slate-600 hover:bg-slate-100"
                }`}
              >
                {preset.label}
              </button>
            ))}
          </div>
        </div>

        {/* Input Parameters: Channel & Sender */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
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
              <option value="email">Email Phishing</option>
              <option value="telegram">Telegram Channel</option>
            </select>
          </div>

          <div>
            <label className="text-xs font-semibold text-slate-700 block mb-1">
              Sender Header / Identifier (Optional)
            </label>
            <input
              type="text"
              value={sender}
              onChange={(e) => setSender(e.target.value)}
              placeholder="e.g. VK-SBIBNK or +91 98402 11928"
              className="w-full text-xs font-mono p-2.5 rounded-lg border border-slate-300 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        {/* Text Payload Input */}
        <div>
          <label className="text-xs font-semibold text-slate-700 block mb-1">
            Suspicious Message Text Body
          </label>
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            rows={4}
            placeholder="Paste suspicious SMS, WhatsApp, or email content here..."
            className="w-full text-xs font-mono p-3 rounded-lg border border-slate-300 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        {/* Scan Action Bar */}
        <div className="flex items-center justify-between pt-2">
          <div className="text-[11px] font-mono text-slate-400">
            Engine: Multilingual Bi-LSTM + One-vs-Rest SVM (10 Tactics)
          </div>

          <button
            onClick={handleScan}
            disabled={loading}
            className="flex items-center space-x-2 px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold rounded-lg shadow-sm transition-all disabled:opacity-50"
          >
            {loading ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                <span>Analyzing Lure...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                <span>Execute Text Scan</span>
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
