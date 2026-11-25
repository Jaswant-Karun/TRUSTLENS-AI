"use client";

import React, { useState } from "react";
import { PageHeader, AnalysisResultPanel, ErrorState } from "@/components/ui";
import { AnalyzeModeTabs } from "@/components/ui/AnalyzeModeTabs";
import { scanImage, ImageAnalysisResponse, ScanResult } from "@/lib/api";
import {
  Image as ImageIcon,
  UploadCloud,
  X,
  RefreshCw,
  Sparkles,
  FileCheck,
  AlertTriangle,
  ShieldCheck,
  ShieldAlert,
  Copy,
  Check,
  FileText,
  HelpCircle,
  Clock,
} from "lucide-react";

export default function ImageAnalysisPage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [filePreview, setFilePreview] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [ocrResponse, setOcrResponse] = useState<ImageAnalysisResponse | null>(null);
  const [copiedText, setCopiedText] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];

      // File validation: Size
      if (file.size > 10 * 1024 * 1024) {
        setError("Uploaded image exceeds the maximum allowable limit of 10 MB.");
        return;
      }
      if (file.size === 0) {
        setError("Selected image file is empty (0 bytes).");
        return;
      }

      // File validation: Type
      const allowedTypes = ["image/jpeg", "image/png", "image/webp"];
      if (!allowedTypes.includes(file.type)) {
        setError(`Unsupported file format '${file.type}'. Allowed formats: JPEG, PNG, WEBP.`);
        return;
      }

      setSelectedFile(file);
      setError(null);
      setOcrResponse(null);

      const reader = new FileReader();
      reader.onload = (ev) => setFilePreview(ev.target?.result as string);
      reader.readAsDataURL(file);
    }
  };

  const handleScan = async () => {
    if (!selectedFile) {
      setError("Please select a screenshot image to upload.");
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const data = await scanImage(selectedFile);
      setOcrResponse(data);
    } catch (err: any) {
      setError(err.message || "Failed to analyze screenshot.");
    } finally {
      setLoading(false);
    }
  };

  const handleCopyText = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedText(true);
    setTimeout(() => setCopiedText(false), 2000);
  };

  const handleClear = () => {
    setSelectedFile(null);
    setFilePreview(null);
    setOcrResponse(null);
    setError(null);
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Screenshot Forensic OCR & Visual Threat Triage"
        description="Extract and evaluate deceptive text, embedded URLs, and manipulative cues from uploaded screenshots using Tesseract OCR + Models 1 & 3."
        badge={{ text: "Vision OCR Active", variant: "purple" }}
      />

      <AnalyzeModeTabs />

      {/* Safety Notice Banner */}
      <div className="p-3.5 bg-slate-900 rounded-xl border border-slate-800 flex items-start space-x-3 text-xs text-slate-300">
        <ShieldCheck className="w-5 h-5 text-purple-400 shrink-0 mt-0.5" />
        <div className="leading-relaxed font-mono">
          <strong className="text-white block font-sans font-semibold">Forensic Isolation Guarantee</strong>
          Uploaded screenshots are parsed purely into digital text using local OCR. Embedded links, scripts, or active binaries are <strong>never executed</strong>.
        </div>
      </div>

      {/* Upload Workbench Card */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-subtle p-6 space-y-5">
        <div>
          <label className="text-xs font-semibold text-slate-700 block mb-2">
            Upload Suspicious Communication Screenshot (SMS, WhatsApp, Banking Login, Telegram)
          </label>

          {!filePreview ? (
            <label className="border-2 border-dashed border-slate-300 hover:border-purple-500 rounded-xl p-8 flex flex-col items-center justify-center cursor-pointer transition-colors bg-slate-50/50 hover:bg-purple-50/30">
              <UploadCloud className="w-10 h-10 text-slate-400 mb-2" />
              <span className="text-xs font-semibold text-slate-700">
                Click to browse or drag & drop screenshot here
              </span>
              <span className="text-[11px] text-slate-400 mt-1 font-mono">
                Supports PNG, JPG, JPEG, WEBP (Max Limit: 10MB)
              </span>
              <input
                type="file"
                accept="image/jpeg,image/png,image/webp"
                onChange={handleFileChange}
                className="hidden"
              />
            </label>
          ) : (
            <div className="relative border border-slate-200 rounded-xl p-4 bg-slate-50 flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <img
                  src={filePreview}
                  alt="Screenshot preview"
                  className="w-20 h-20 object-cover rounded-lg border border-slate-200 shadow-sm"
                />
                <div>
                  <div className="text-xs font-bold text-slate-900 font-mono">
                    {selectedFile?.name}
                  </div>
                  <div className="text-[11px] text-slate-500 font-mono mt-0.5">
                    {selectedFile ? (selectedFile.size / 1024).toFixed(1) : 0} KB • {selectedFile?.type}
                  </div>
                  <div className="flex items-center space-x-1 text-[11px] text-emerald-600 font-medium mt-1">
                    <FileCheck className="w-3.5 h-3.5" />
                    <span>Image validated and ready for OCR extraction</span>
                  </div>
                </div>
              </div>

              <button
                onClick={handleClear}
                className="p-1.5 rounded-lg text-slate-400 hover:text-rose-600 hover:bg-rose-50 transition-colors"
                title="Remove image"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
          )}
        </div>

        {/* Action Bar */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-2 border-t border-slate-100">
          <div className="text-[11px] font-mono text-slate-500 flex items-center space-x-2">
            <span className="w-2 h-2 rounded-full bg-purple-500"></span>
            <span>Pipeline: PyTesseract OCR Engine + Multilingual Scam Classifier</span>
          </div>

          <button
            onClick={handleScan}
            disabled={loading || !selectedFile}
            className="flex items-center justify-center space-x-2 px-6 py-2.5 bg-purple-600 hover:bg-purple-700 text-white text-xs font-semibold rounded-lg shadow-sm transition-all disabled:opacity-50"
          >
            {loading ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                <span>Extracting Text & Triaging Models...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                <span>Execute Vision OCR Scan</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Error State */}
      {error && <ErrorState message={error} onRetry={handleScan} />}

      {/* OCR Text Extraction Card */}
      {ocrResponse && (
        <div className="bg-white rounded-xl border border-slate-200 shadow-subtle p-6 space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100">
            <div className="flex items-center space-x-2">
              <FileText className="w-4 h-4 text-purple-600" />
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-800 font-mono">
                OCR Text Extraction Output
              </h3>
            </div>
            <div className="flex items-center space-x-3 text-xs font-mono">
              <span className="px-2 py-0.5 rounded bg-purple-50 text-purple-700 font-semibold border border-purple-200">
                Confidence: {Math.round(ocrResponse.ocr_confidence * 100)}%
              </span>
              <span className="text-slate-400">
                Status: <strong>{ocrResponse.analysis_status}</strong>
              </span>
              <span className="text-slate-400">
                Latency: <strong>{ocrResponse.processing_time_ms} ms</strong>
              </span>
            </div>
          </div>

          {ocrResponse.extracted_text ? (
            <div className="relative">
              <div className="p-4 bg-slate-900 rounded-xl text-slate-100 font-mono text-xs leading-relaxed max-h-48 overflow-y-auto whitespace-pre-wrap border border-slate-800">
                {ocrResponse.extracted_text}
              </div>
              <button
                onClick={() => handleCopyText(ocrResponse.extracted_text)}
                className="absolute right-3 top-3 px-2 py-1 bg-slate-800 hover:bg-slate-700 text-slate-300 text-[10px] font-mono rounded flex items-center space-x-1 border border-slate-700 transition-colors"
                title="Copy extracted text"
              >
                {copiedText ? (
                  <>
                    <Check className="w-3 h-3 text-emerald-400" />
                    <span className="text-emerald-400">Copied</span>
                  </>
                ) : (
                  <>
                    <Copy className="w-3 h-3" />
                    <span>Copy</span>
                  </>
                )}
              </button>
            </div>
          ) : (
            <div className="p-5 bg-slate-50 rounded-xl border border-slate-200 text-xs font-mono text-slate-500 flex items-center space-x-3">
              <HelpCircle className="w-5 h-5 text-slate-400 shrink-0" />
              <div>
                <strong className="text-slate-700 block">No Readable Text Extracted</strong>
                The uploaded image contains insufficient alphanumeric signals or low visual contrast. The platform recorded an <code>insufficient-evidence</code> triage without fabricating synthetic threat results.
              </div>
            </div>
          )}
        </div>
      )}

      {/* Downstream Scam Analysis Result (if text was extracted) */}
      {ocrResponse?.analysis_result && (
        <AnalysisResultPanel result={ocrResponse.analysis_result} />
      )}
    </div>
  );
}
