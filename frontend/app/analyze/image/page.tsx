"use client";

import React, { useState } from "react";
import { PageHeader, AnalysisResultPanel, ErrorState } from "@/components/ui";
import { scanImage, ScanResult } from "@/lib/api";
import { Image as ImageIcon, UploadCloud, X, RefreshCw, Sparkles, FileCheck } from "lucide-react";

export default function ImageAnalysisPage() {
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
    if (!selectedFile) {
      setError("Please select a screenshot image to upload.");
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const data: any = await scanImage(selectedFile);
      setResult(data.analysis_result || data);
    } catch (err: any) {
      setError(err.message || "Failed to analyze screenshot.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Screenshot Forensic OCR Analysis"
        description="Extract and evaluate deceptive text, URLs, and social engineering cues from uploaded screenshots using Tesseract OCR + Models 1 & 3."
        badge={{ text: "Vision OCR Active", variant: "purple" }}
      />

      {/* Upload Workbench Card */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-subtle p-6 space-y-5">
        <div>
          <label className="text-xs font-semibold text-slate-700 block mb-2">
            Upload Suspicious Screenshot (SMS, WhatsApp, Banking Login, Telegram)
          </label>

          {!filePreview ? (
            <label className="border-2 border-dashed border-slate-300 hover:border-purple-500 rounded-xl p-8 flex flex-col items-center justify-center cursor-pointer transition-colors bg-slate-50/50 hover:bg-purple-50/30">
              <UploadCloud className="w-10 h-10 text-slate-400 mb-2" />
              <span className="text-xs font-semibold text-slate-700">
                Click to browse or drop screenshot here
              </span>
              <span className="text-[11px] text-slate-400 mt-1 font-mono">
                Supports PNG, JPG, WEBP (Max: 10MB)
              </span>
              <input
                type="file"
                accept="image/*"
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
                    {selectedFile ? (selectedFile.size / 1024).toFixed(1) : 0} KB
                  </div>
                  <div className="flex items-center space-x-1 text-[11px] text-emerald-600 font-medium mt-1">
                    <FileCheck className="w-3.5 h-3.5" />
                    <span>Image validated and ready for OCR</span>
                  </div>
                </div>
              </div>

              <button
                onClick={() => {
                  setSelectedFile(null);
                  setFilePreview(null);
                  setResult(null);
                }}
                className="p-1.5 rounded-lg text-slate-400 hover:text-rose-600 hover:bg-rose-50 transition-colors"
                title="Remove image"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
          )}
        </div>

        {/* Action Bar */}
        <div className="flex items-center justify-between pt-2">
          <div className="text-[11px] font-mono text-slate-400">
            Engine: PyTesseract OCR Engine + Multilingual Scam Classifier
          </div>

          <button
            onClick={handleScan}
            disabled={loading || !selectedFile}
            className="flex items-center space-x-2 px-5 py-2.5 bg-purple-600 hover:bg-purple-700 text-white text-xs font-semibold rounded-lg shadow-sm transition-all disabled:opacity-50"
          >
            {loading ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                <span>Extracting Text & Triage...</span>
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

      {/* Analysis Result Panel */}
      {result && <AnalysisResultPanel result={result} />}
    </div>
  );
}
