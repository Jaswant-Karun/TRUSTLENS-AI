"use client";

import React, { useState } from "react";
import {
  generateIntelligenceReport,
  exportInvestigationJson,
  exportInvestigationStix,
  IntelligenceReportResponse,
} from "@/lib/api";
import { FileText, Download, AlertCircle, CheckCircle2, RefreshCw } from "lucide-react";

const REPORT_TYPES = [
  { id: "comprehensive_investigation", label: "Comprehensive Investigation", defaultTarget: "INV-2026-0011", placeholder: "INV-2026-0011" },
  { id: "campaign_similarity", label: "Campaign Similarity Cluster", defaultTarget: "11", placeholder: "Cluster ID (e.g. 11)" },
  { id: "model_evaluation", label: "Model Evaluation Summary", defaultTarget: "", placeholder: "Optional (leave blank)" },
  { id: "message_analysis", label: "Individual Message Analysis", defaultTarget: "", placeholder: "Analysis UUID" },
  { id: "url_analysis", label: "URL Analysis", defaultTarget: "", placeholder: "Analysis UUID" },
];

export function IntelligenceReportPanel() {
  const [reportType, setReportType] = useState("comprehensive_investigation");
  const [targetId, setTargetId] = useState("INV-2026-0011");
  const [report, setReport] = useState<IntelligenceReportResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const selectedMeta = REPORT_TYPES.find((r) => r.id === reportType) || REPORT_TYPES[0];

  const handleGenerate = async () => {
    setLoading(true);
    setErrorMsg(null);
    try {
      const res = await generateIntelligenceReport(
        reportType,
        targetId.trim() || undefined
      );
      setReport(res);
    } catch (err: any) {
      setErrorMsg(err?.message || "Failed to generate intelligence report.");
      setReport(null);
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async (format: "json" | "stix") => {
    setErrorMsg(null);
    try {
      const exportType =
        reportType === "campaign_similarity"
          ? "campaign"
          : reportType === "comprehensive_investigation"
          ? "investigation"
          : "analysis";
      const id = targetId.trim() || "INV-2026-0011";
      const payload =
        format === "stix"
          ? await exportInvestigationStix(exportType, id)
          : await exportInvestigationJson(exportType, id);

      const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `trustlens-${exportType}-${id}.${format === "stix" ? "stix.json" : "json"}`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err: any) {
      setErrorMsg(err?.message || `Failed to export ${format.toUpperCase()}.`);
    }
  };

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm space-y-5 mt-8">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-3 border-b border-slate-200 pb-4">
        <div>
          <h2 className="text-base font-bold text-slate-900 flex items-center space-x-2">
            <FileText className="w-4 h-4 text-blue-600" />
            <span>Investigation Report Generator & STIX 2.1 / JSON Exports</span>
          </h2>
          <p className="text-xs text-slate-500 mt-1">
            Generate auditable intelligence dossiers with model versions, evidence provenance, review status, and explicit limitations.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-3 items-end">
        <div>
          <label className="block text-[11px] font-semibold text-slate-600 mb-1">Report Type</label>
          <select
            aria-label="Report Type"
            value={reportType}
            onChange={(e) => {
              const next = e.target.value;
              setReportType(next);
              const meta = REPORT_TYPES.find((r) => r.id === next);
              setTargetId(meta?.defaultTarget || "");
              setReport(null);
              setErrorMsg(null);
            }}
            className="w-full px-3 py-2 text-xs border border-slate-300 rounded-lg bg-white text-slate-800"
          >
            {REPORT_TYPES.map((rt) => (
              <option key={rt.id} value={rt.id}>
                {rt.label}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-[11px] font-semibold text-slate-600 mb-1">Target Identifier</label>
          <input
            type="text"
            value={targetId}
            onChange={(e) => setTargetId(e.target.value)}
            placeholder={selectedMeta.placeholder}
            disabled={reportType === "model_evaluation"}
            className="w-full px-3 py-2 text-xs border border-slate-300 rounded-lg bg-white text-slate-800 disabled:bg-slate-100"
          />
        </div>

        <button
          onClick={handleGenerate}
          disabled={loading}
          className="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold inline-flex items-center justify-center space-x-1.5 disabled:opacity-60"
        >
          {loading ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <FileText className="w-3.5 h-3.5" />}
          <span>Generate Report</span>
        </button>

        <div className="flex space-x-2">
          <button
            onClick={() => handleExport("json")}
            disabled={reportType === "model_evaluation"}
            className="flex-1 px-3 py-2 rounded-lg border border-slate-300 hover:bg-slate-50 text-slate-700 text-xs font-semibold inline-flex items-center justify-center space-x-1 disabled:opacity-40"
          >
            <Download className="w-3.5 h-3.5" />
            <span>JSON</span>
          </button>
          <button
            onClick={() => handleExport("stix")}
            disabled={reportType === "model_evaluation"}
            className="flex-1 px-3 py-2 rounded-lg border border-emerald-300 bg-emerald-50 hover:bg-emerald-100 text-emerald-800 text-xs font-semibold inline-flex items-center justify-center space-x-1 disabled:opacity-40"
          >
            <Download className="w-3.5 h-3.5" />
            <span>STIX 2.1</span>
          </button>
        </div>
      </div>

      {errorMsg && (
        <div className="p-3 rounded-lg bg-rose-50 border border-rose-200 text-xs text-rose-700 flex items-center space-x-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}

      {report && (
        <div className="border border-slate-200 rounded-lg p-4 bg-slate-50 space-y-3 text-xs">
          <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-200 pb-2">
            <div className="font-bold text-slate-900">
              {report.report_id} • {report.investigation_id}
            </div>
            <div className="flex items-center space-x-2">
              <span className="px-2 py-0.5 rounded bg-blue-100 text-blue-800 font-semibold">
                {report.review_status}
              </span>
              <span className="text-slate-500 font-mono">{report.generated_at}</span>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div className="bg-white p-3 rounded border border-slate-200">
              <div className="text-[10px] font-bold uppercase text-slate-500 mb-1">Sources & Model Versions</div>
              <div className="text-slate-700 space-y-1">
                <div>Sources: {report.sources.join(", ")}</div>
                <div className="font-mono text-[11px]">
                  Models: {JSON.stringify(report.model_versions)}
                </div>
              </div>
            </div>
            <div className="bg-white p-3 rounded border border-slate-200">
              <div className="text-[10px] font-bold uppercase text-slate-500 mb-1">Predictions</div>
              <pre className="text-[11px] font-mono text-slate-700 whitespace-pre-wrap">
                {JSON.stringify(report.predictions, null, 2)}
              </pre>
            </div>
          </div>

          <div className="bg-amber-50 border border-amber-200 p-3 rounded text-amber-900 space-y-1">
            <div className="text-[10px] font-bold uppercase">Documented Limitations</div>
            {report.limitations.map((lim, idx) => (
              <div key={idx}>• {lim}</div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
