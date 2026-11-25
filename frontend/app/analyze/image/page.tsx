"use client";

import React, { useState } from "react";
import Image from "next/image";
import { PageHeader, AnalysisResultPanel, ErrorState } from "@/components/ui";
import { AnalyzeModeTabs } from "@/components/ui/AnalyzeModeTabs";
import { GlowButton } from "@/components/product/GlowButton";
import { scanImage, ImageAnalysisResponse } from "@/lib/api";
import {
  AlertTriangle,
  Check,
  Copy,
  FileCheck,
  FileText,
  HelpCircle,
  RefreshCw,
  ShieldCheck,
  Sparkles,
  UploadCloud,
  X,
} from "lucide-react";

async function hasValidImageSignature(file: File): Promise<boolean> {
  const buf = new Uint8Array(await file.slice(0, 12).arrayBuffer());
  if (buf.length < 4) return false;
  const isPng = buf[0] === 0x89 && buf[1] === 0x50 && buf[2] === 0x4e && buf[3] === 0x47;
  const isJpeg = buf[0] === 0xff && buf[1] === 0xd8 && buf[2] === 0xff;
  const isWebp =
    buf.length >= 12 &&
    buf[0] === 0x52 &&
    buf[1] === 0x49 &&
    buf[2] === 0x46 &&
    buf[3] === 0x46 &&
    buf[8] === 0x57 &&
    buf[9] === 0x45 &&
    buf[10] === 0x42 &&
    buf[11] === 0x50;
  return isPng || isJpeg || isWebp;
}

export default function ImageAnalysisPage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [filePreview, setFilePreview] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [ocrResponse, setOcrResponse] = useState<ImageAnalysisResponse | null>(null);
  const [copiedText, setCopiedText] = useState(false);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (file.size > 10 * 1024 * 1024) {
      setError("Uploaded image exceeds the maximum allowable limit of 10 MB.");
      return;
    }
    if (file.size === 0) {
      setError("Selected image file is empty (0 bytes).");
      return;
    }

    const allowedTypes = ["image/jpeg", "image/png", "image/webp"];
    if (!allowedTypes.includes(file.type)) {
      setError(`Unsupported file format '${file.type}'. Allowed formats: JPEG, PNG, WEBP.`);
      return;
    }

    const validSig = await hasValidImageSignature(file);
    if (!validSig) {
      setError("Invalid image file signature. Only genuine PNG, JPEG, or WEBP headers are accepted.");
      return;
    }

    setSelectedFile(file);
    setError(null);
    setOcrResponse(null);

    const reader = new FileReader();
    reader.onload = (ev) => setFilePreview(ev.target?.result as string);
    reader.readAsDataURL(file);
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
      setError(err?.message || "Failed to analyze screenshot.");
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
        title="Screenshot Intelligence"
        description="Extracts readable text from validated PNG, JPEG, and WEBP screenshots via local OCR, then evaluates fraud signals using Models 1 & 3."
        badge={{ text: "OCR + Text ML Active", variant: "rose" }}
      />

      <AnalyzeModeTabs />

      {/* Safety & Honest Capability Scope */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="cyber-panel p-4 border-[#00D68F]/40 flex items-start space-x-3 text-xs text-[#A1A1AA]">
          <ShieldCheck className="w-5 h-5 text-[#00D68F] shrink-0 mt-0.5" />
          <div className="leading-relaxed">
            <strong className="text-white block font-mono uppercase mb-0.5">
              Validated File &amp; OCR Isolation
            </strong>
            Files are restricted to 10 MB, verified by MIME type and binary magic
            headers, and parsed into text without executing embedded links or scripts.
          </div>
        </div>

        <div className="cyber-panel p-4 border-[#FFB020]/40 flex items-start space-x-3 text-xs text-[#A1A1AA]">
          <AlertTriangle className="w-5 h-5 text-[#FFB020] shrink-0 mt-0.5" />
          <div className="leading-relaxed">
            <strong className="text-white block font-mono uppercase mb-0.5">
              OCR-Based Scope (No Pixel/Deepfake Vision)
            </strong>
            Fraud classification runs strictly on OCR-extracted text. Low-contrast
            or text-free images return <code>insufficient-evidence</code> rather
            than guessing.
          </div>
        </div>
      </div>

      {/* Upload Workbench */}
      <div className="cyber-panel p-5 sm:p-6 space-y-5">
        <div>
          <label className="text-[11px] font-mono uppercase text-[#A1A1AA] block mb-2.5">
            Upload Communication Screenshot (PNG, JPG, WEBP — Max 10 MB)
          </label>

          {!filePreview ? (
            <label className="border-2 border-dashed border-[#481326] hover:border-[#FF174F] rounded-xl p-8 flex flex-col items-center justify-center cursor-pointer transition-colors bg-[#050306]/70">
              <UploadCloud className="w-10 h-10 text-[#FF3D70] mb-2" />
              <span className="text-xs font-mono font-semibold text-white">
                Click to select screenshot for OCR inspection
              </span>
              <span className="text-[11px] text-[#A1A1AA] mt-1 font-mono">
                PNG, JPG, JPEG, WEBP (Magic-byte &amp; PIL verified, max 10 MB)
              </span>
              <input
                type="file"
                accept="image/jpeg,image/png,image/webp"
                onChange={handleFileChange}
                className="hidden"
              />
            </label>
          ) : (
            <div className="relative border border-[#481326] rounded-xl p-4 bg-[#050306]/80 flex items-center justify-between gap-4">
              <div className="flex items-center space-x-4 min-w-0">
                <Image
                  src={filePreview}
                  alt="Screenshot preview"
                  width={80}
                  height={80}
                  unoptimized
                  className="w-20 h-20 object-cover rounded-lg border border-[#481326] shrink-0"
                />
                <div className="min-w-0">
                  <div className="text-xs font-bold text-white font-mono truncate">
                    {selectedFile?.name}
                  </div>
                  <div className="text-[11px] text-[#A1A1AA] font-mono mt-0.5">
                    {selectedFile ? (selectedFile.size / 1024).toFixed(1) : 0} KB •{" "}
                    {selectedFile?.type}
                  </div>
                  <div className="flex items-center space-x-1 text-[11px] text-[#00D68F] font-mono mt-1">
                    <FileCheck className="w-3.5 h-3.5" />
                    <span>File signature validated — ready for OCR</span>
                  </div>
                </div>
              </div>

              <button
                type="button"
                onClick={handleClear}
                aria-label="Remove image"
                className="p-1.5 rounded-lg text-[#A1A1AA] hover:text-[#FF174F] hover:bg-[#170A12] transition-colors shrink-0"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
          )}
        </div>

        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-3 border-t border-[#481326]/70">
          <div className="text-[11px] font-mono text-[#A1A1AA] flex items-center space-x-2">
            <span className="w-2 h-2 rounded-full bg-[#FF174F]" />
            <span>Pipeline: Tesseract OCR + Multilingual Text &amp; Tactic Models</span>
          </div>

          <GlowButton
            type="button"
            variant="primary"
            onClick={handleScan}
            disabled={loading || !selectedFile}
          >
            {loading ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                <span>EXTRACTING &amp; ANALYZING...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                <span>Analyze Screenshot</span>
              </>
            )}
          </GlowButton>
        </div>
      </div>

      {/* Error State */}
      {error && <ErrorState message={error} onRetry={handleScan} />}

      {/* OCR Output Card */}
      {ocrResponse && (
        <div className="cyber-panel p-5 sm:p-6 space-y-4">
          <div className="flex flex-wrap items-center justify-between gap-2 pb-3 border-b border-[#481326]">
            <div className="flex items-center space-x-2">
              <FileText className="w-4 h-4 text-[#FF3D70]" />
              <h3 className="text-xs font-bold uppercase tracking-wider text-white font-mono">
                OCR Text Extraction Output
              </h3>
            </div>
            <div className="flex flex-wrap items-center gap-3 text-xs font-mono">
              <span className="px-2 py-0.5 rounded bg-[#FF174F]/15 text-[#FF3D70] font-semibold border border-[#481326]">
                Confidence: {Math.round(ocrResponse.ocr_confidence * 100)}%
              </span>
              <span className="text-[#A1A1AA]">
                Status: <strong className="text-white">{ocrResponse.analysis_status}</strong>
              </span>
              <span className="text-[#A1A1AA]">
                Latency: <strong className="text-white">{ocrResponse.processing_time_ms} ms</strong>
              </span>
            </div>
          </div>

          {ocrResponse.extracted_text ? (
            <div className="relative">
              <div className="p-4 bg-[#050306] rounded-xl text-white font-mono text-xs leading-relaxed max-h-48 overflow-y-auto whitespace-pre-wrap border border-[#481326]">
                {ocrResponse.extracted_text}
              </div>
              <button
                type="button"
                onClick={() => handleCopyText(ocrResponse.extracted_text)}
                aria-label="Copy extracted text"
                className="absolute right-3 top-3 px-2 py-1 bg-[#170A12] hover:border-[#FF174F] text-[#A1A1AA] hover:text-white text-[10px] font-mono rounded flex items-center space-x-1 border border-[#481326] transition-colors"
              >
                {copiedText ? (
                  <>
                    <Check className="w-3 h-3 text-[#00D68F]" />
                    <span className="text-[#00D68F]">Copied</span>
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
            <div className="p-5 bg-[#050306]/80 rounded-xl border border-[#481326] text-xs font-mono text-[#A1A1AA] flex items-center space-x-3">
              <HelpCircle className="w-5 h-5 text-[#FFB020] shrink-0" />
              <div>
                <strong className="text-white block">No Readable Text Extracted</strong>
                The uploaded image contains insufficient alphanumeric signals or low
                visual contrast. Recorded as <code>insufficient-evidence</code>{" "}
                without fabricating threat scores.
              </div>
            </div>
          )}
        </div>
      )}

      {ocrResponse?.analysis_result && (
        <AnalysisResultPanel result={ocrResponse.analysis_result} />
      )}
    </div>
  );
}
