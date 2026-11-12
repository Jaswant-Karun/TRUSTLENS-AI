"use client";

import React, { useState } from "react";
import {
  Search,
  MessageSquare,
  Globe,
  Image as ImageIcon,
  UploadCloud,
  FileCheck,
  X,
  Sparkles,
  RefreshCw,
  AlertCircle,
} from "lucide-react";
import { scanComprehensive, scanUrl, scanImage, ScanResult } from "@/lib/api";
import { AnalysisResultPanel } from "./ui/AnalysisResultPanel";
import { ErrorState } from "./ui/ErrorState";

interface ScanWorkbenchProps {
  onResult?: (res: ScanResult) => void;
  id?: string;
}

const PRESETS = [
  {
    label: "Hinglish SBI KYC Scam",
    type: "text",
    content: "Aapka SBI khata turant band ho jayega. Urgent verify karein: http://192.168.1.50/sbi-kyc/update.php",
  },
  {
    label: "Fake Work-From-Home Scam",
    type: "text",
    content: "URGENT: Earn 5000 daily part-time job from home! Complete simple YouTube rating tasks. Send UPI deposit 500 to start.",
  },
  {
    label: "Phishing Banking URL (IP-based)",
    type: "url",
    content: "http://203.0.113.15/secure-login-portal/auth.php?account_id=98214&kyc=required",
  },
  {
    label: "Electricity Bill Threat (Hindi)",
    type: "text",
    content: "प्रिय ग्राहक, आपका बिजली कनेक्शन आज रात काट दिया जाएगा क्योंकि बिल बकाया है। तुरंत इस नंबर पर संपर्क करें।",
  },
];

export default function ScanWorkbench({ onResult, id }: ScanWorkbenchProps) {
  const [activeTab, setActiveTab] = useState<"text" | "url" | "ocr">("text");
  const [textContent, setTextContent] = useState(PRESETS[0].content);
  const [urlContent, setUrlContent] = useState("http://secure-login-hdfcbank-account-update.xyz/login.php");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [filePreview, setFilePreview] = useState<string | null>(null);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ScanResult | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      if (file.size > 10 * 1024 * 1024) {
        setError("File exceeds maximum allowed size of 10MB");
        return;
      }
      setSelectedFile(file);
      setError(null);
      const reader = new FileReader();
      reader.onload = (ev) => setFilePreview(ev.target?.result as string);
      reader.readAsDataURL(file);
    }
  };

  const handleScan = async () => {
    setLoading(true);
    setError(null);

    try {
      let scanData: ScanResult;

      if (activeTab === "text") {
        if (!textContent.trim()) {
          setError("Please provide a text message to analyze.");
          setLoading(false);
          return;
        }
        scanData = await scanComprehensive({ content: textContent, channel: "sms" });
      } else if (activeTab === "url") {
        if (!urlContent.trim()) {
          setError("Please provide a URL to analyze.");
          setLoading(false);
          return;
        }
        scanData = await scanUrl(urlContent);
      } else {
        if (!selectedFile) {
          setError("Please select a screenshot image to upload.");
          setLoading(false);
          return;
        }
        const ocrRes = await scanImage(selectedFile);
        if (ocrRes.analysis_result) {
          scanData = ocrRes.analysis_result;
        } else {
          throw new Error("No readable text found in image evidence (insufficient evidence).");
        }
      }

      setResult(scanData);
      if (onResult) onResult(scanData);
    } catch (err: any) {
      setError(err?.message || "Analysis request failed. Please check backend connectivity.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div id={id} className="bg-white rounded-xl border border-slate-200 shadow-subtle p-6 mb-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between pb-4 mb-4 border-b border-slate-100 gap-3">
        <div>
          <h2 className="text-base font-bold text-slate-900 flex items-center space-x-2">
            <Sparkles className="w-4 h-4 text-blue-600" />
            <span>Multi-Modal Threat Investigation Workbench</span>
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Offline lexical inspection & multilingual deception decomposition (Models 1, 2, 3 & 4).
          </p>
        </div>

        {/* Quick Presets */}
        <div className="hidden sm:flex items-center space-x-1.5 text-xs">
          <span className="text-slate-400 font-mono text-[11px] mr-1">Presets:</span>
          {PRESETS.map((p, i) => (
            <button
              key={i}
              onClick={() => {
                if (p.type === "url") {
                  setActiveTab("url");
                  setUrlContent(p.content);
                } else {
                  setActiveTab("text");
                  setTextContent(p.content);
                }
              }}
              className="px-2 py-1 rounded bg-slate-50 hover:bg-slate-100 border border-slate-200 text-slate-700 font-medium text-[11px] transition-colors"
            >
              {p.label}
            </button>
          ))}
        </div>
      </div>

      {/* Tabs Row */}
      <div className="flex items-center space-x-1 border-b border-slate-200 mb-4">
        <button
          onClick={() => setActiveTab("text")}
          className={`flex items-center space-x-2 px-4 py-2 text-xs font-semibold border-b-2 transition-all ${
            activeTab === "text"
              ? "border-blue-600 text-blue-600"
              : "border-transparent text-slate-500 hover:text-slate-800"
          }`}
        >
          <MessageSquare className="w-3.5 h-3.5" />
          <span>Multilingual Message</span>
        </button>

        <button
          onClick={() => setActiveTab("url")}
          className={`flex items-center space-x-2 px-4 py-2 text-xs font-semibold border-b-2 transition-all ${
            activeTab === "url"
              ? "border-blue-600 text-blue-600"
              : "border-transparent text-slate-500 hover:text-slate-800"
          }`}
        >
          <Globe className="w-3.5 h-3.5" />
          <span>Phishing URL (Zero-Hop)</span>
        </button>

        <button
          onClick={() => setActiveTab("ocr")}
          className={`flex items-center space-x-2 px-4 py-2 text-xs font-semibold border-b-2 transition-all ${
            activeTab === "ocr"
              ? "border-blue-600 text-blue-600"
              : "border-transparent text-slate-500 hover:text-slate-800"
          }`}
        >
          <ImageIcon className="w-3.5 h-3.5" />
          <span>Screenshot OCR Evidence</span>
        </button>
      </div>

      {/* Input Area Depending on Active Tab */}
      <div className="mb-4">
        {activeTab === "text" && (
          <div>
            <textarea
              rows={3}
              value={textContent}
              onChange={(e) => setTextContent(e.target.value)}
              placeholder="Paste suspicious SMS, WhatsApp message forward, KYC alert, or job offer here..."
              className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-lg text-slate-900 placeholder-slate-400 text-xs font-mono focus:bg-white focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500/20 transition-all"
            />
            <div className="flex justify-between items-center text-[11px] text-slate-400 font-mono mt-1.5">
              <span>Supports: English, Hindi (Devanagari), Hinglish (Latin).</span>
              <span>Model 1 + Model 3</span>
            </div>
          </div>
        )}

        {activeTab === "url" && (
          <div>
            <input
              type="text"
              value={urlContent}
              onChange={(e) => setUrlContent(e.target.value)}
              placeholder="Enter suspicious link or domain (e.g. http://secure-kyc-update.xyz/login.php)..."
              className="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-lg text-slate-900 placeholder-slate-400 text-xs font-mono focus:bg-white focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500/20 transition-all"
            />
            <div className="flex justify-between items-center text-[11px] text-slate-400 font-mono mt-1.5">
              <span>Evaluates 17 lexical & entropy features without connecting to remote target.</span>
              <span>Model 2 (XGBoost)</span>
            </div>
          </div>
        )}

        {activeTab === "ocr" && (
          <div>
            <div className="border-2 border-dashed border-slate-200 hover:border-blue-400 rounded-xl p-6 text-center bg-slate-50/50 hover:bg-slate-50 transition-colors cursor-pointer relative">
              <input
                type="file"
                accept="image/png,image/jpeg,image/webp"
                onChange={handleFileChange}
                className="absolute inset-0 opacity-0 cursor-pointer"
              />
              <div className="flex flex-col items-center justify-center space-y-2">
                <div className="p-3 bg-blue-50 text-blue-600 rounded-full">
                  <UploadCloud className="w-6 h-6" />
                </div>
                <div className="text-xs font-semibold text-slate-800">
                  {selectedFile ? selectedFile.name : "Click or drag screenshot here"}
                </div>
                <p className="text-[11px] text-slate-400">
                  PNG, JPEG, WebP up to 10MB. Text will be extracted via Tesseract OCR engine.
                </p>
              </div>
            </div>

            {filePreview && (
              <div className="mt-3 flex items-center justify-between p-2.5 bg-slate-100 rounded-lg text-xs">
                <div className="flex items-center space-x-2 text-slate-700">
                  <FileCheck className="w-4 h-4 text-emerald-600" />
                  <span className="font-medium truncate max-w-xs">{selectedFile?.name}</span>
                  <span className="text-slate-400 font-mono">({Math.round((selectedFile?.size || 0) / 1024)} KB)</span>
                </div>
                <button
                  onClick={() => {
                    setSelectedFile(null);
                    setFilePreview(null);
                  }}
                  className="text-slate-400 hover:text-slate-600 p-1"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Action Row */}
      <div className="flex items-center justify-between pt-2">
        <span className="text-[11px] font-mono text-slate-400">
          Status: Offline zero-execution inspection active
        </span>

        <button
          onClick={handleScan}
          disabled={loading}
          className="flex items-center space-x-2 px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-semibold text-xs rounded-lg shadow-sm transition-all disabled:opacity-50"
        >
          {loading ? (
            <>
              <RefreshCw className="w-3.5 h-3.5 animate-spin" />
              <span>Analyzing Deception...</span>
            </>
          ) : (
            <>
              <Search className="w-3.5 h-3.5" />
              <span>Run Threat Intelligence Scan</span>
            </>
          )}
        </button>
      </div>

      {/* Error Display */}
      {error && (
        <div className="mt-4">
          <ErrorState message={error} onRetry={handleScan} compact />
        </div>
      )}

      {/* Verified Forensic Analysis Result */}
      {result && (
        <div className="mt-6 pt-6 border-t border-slate-100">
          <AnalysisResultPanel result={result} />
        </div>
      )}
    </div>
  );
}
