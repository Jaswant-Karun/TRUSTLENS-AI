"use client";

import React, { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import { TopNavigation } from "@/components/investigation/TopNavigation";
import {
  queryThreatLibrary,
  ThreatLibraryItem,
  exportInvestigationJson,
  exportInvestigationStix,
} from "@/lib/api";
import {
  Search,
  Filter,
  ArrowUpDown,
  ChevronLeft,
  ChevronRight,
  X,
  ShieldCheck,
  Cpu,
  Globe,
  AlertTriangle,
  MessageSquare,
  Link2,
  Zap,
  Activity,
  Users,
  Download,
  ArrowRight,
  RefreshCw,
} from "lucide-react";

const ENTITY_TABS = [
  { id: "all", label: "All Records" },
  { id: "suspicious_message", label: "Messages" },
  { id: "url", label: "URLs" },
  { id: "domain", label: "Domains" },
  { id: "indicator", label: "Indicators" },
  { id: "tactic", label: "Tactics" },
  { id: "similarity_cluster", label: "Clusters" },
  { id: "community_report", label: "Reports" },
];

const SEVERITY_BADGE: Record<string, string> = {
  critical: "bg-rose-950/90 text-rose-300 border-rose-700/70",
  high: "bg-orange-950/90 text-orange-300 border-orange-700/70",
  medium: "bg-amber-950/90 text-amber-300 border-amber-700/70",
  low: "bg-sky-950/90 text-sky-300 border-sky-700/70",
  clean: "bg-emerald-950/90 text-emerald-300 border-emerald-700/70",
  inconclusive: "bg-slate-800 text-slate-300 border-slate-600",
};

const VERIFICATION_BADGE: Record<string, string> = {
  verified: "bg-emerald-950/80 text-emerald-300 border-emerald-700/60",
  automated_inference: "bg-indigo-950/80 text-indigo-300 border-indigo-700/60",
  under_review: "bg-amber-950/80 text-amber-300 border-amber-700/60",
  unverified: "bg-slate-800 text-slate-400 border-slate-600",
};

export default function ThreatLibraryPage() {
  const [items, setItems] = useState<ThreatLibraryItem[]>([]);
  const [total, setTotal] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [facets, setFacets] = useState<Record<string, number>>({});
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const [search, setSearch] = useState("");
  const [entityType, setEntityType] = useState("all");
  const [severity, setSeverity] = useState("all");
  const [verificationStatus, setVerificationStatus] = useState("all");
  const [provenance, setProvenance] = useState("all");
  const [sortBy, setSortBy] = useState("created_at");
  const [sortOrder, setSortOrder] = useState<"desc" | "asc">("desc");
  const [page, setPage] = useState(1);

  const [selectedItem, setSelectedItem] = useState<ThreatLibraryItem | null>(null);
  const [exportStatus, setExportStatus] = useState<string | null>(null);

  const fetchLibrary = useCallback(async () => {
    setLoading(true);
    setErrorMsg(null);
    try {
      const res = await queryThreatLibrary({
        search: search || undefined,
        entity_type: entityType,
        severity,
        verification_status: verificationStatus,
        provenance,
        sort_by: sortBy,
        sort_order: sortOrder,
        page,
        page_size: 15,
      });
      setItems(res.items || []);
      setTotal(res.total || 0);
      setTotalPages(res.total_pages || 1);
      setFacets(res.facets?.entity_types || {});
    } catch (err: any) {
      setErrorMsg(err?.message || "Failed to load Threat Library records.");
    } finally {
      setLoading(false);
    }
  }, [search, entityType, severity, verificationStatus, provenance, sortBy, sortOrder, page]);

  useEffect(() => {
    fetchLibrary();
  }, [fetchLibrary]);

  const handleDownloadExport = async (format: "json" | "stix", item: ThreatLibraryItem) => {
    setExportStatus(`Exporting ${format.toUpperCase()}...`);
    try {
      const targetType =
        item.entity_type === "similarity_cluster"
          ? "campaign"
          : item.metadata?.analysis_id
          ? "analysis"
          : null;
      const targetId =
        item.entity_type === "similarity_cluster"
          ? item.raw_id
          : item.metadata?.analysis_id || item.raw_id;

      if (!targetType) {
        setExportStatus("Direct STIX/JSON export is supported for Analyses, Investigations, and Campaigns.");
        return;
      }

      const data =
        format === "stix"
          ? await exportInvestigationStix(targetType, targetId)
          : await exportInvestigationJson(targetType, targetId);

      const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `trustlens-${targetType}-${targetId}.${format === "stix" ? "stix.json" : "json"}`;
      a.click();
      URL.revokeObjectURL(url);
      setExportStatus(`Downloaded ${format.toUpperCase()} export.`);
    } catch (err: any) {
      setExportStatus(err?.message || "Export failed (check authentication for private analysis records).");
    }
  };

  return (
    <div className="min-h-screen bg-[#171C25] text-slate-100 flex flex-col font-sans">
      <TopNavigation />

      <main className="flex-1 p-6 md:p-8 max-w-7xl w-full mx-auto space-y-6">
        {/* Header + Quick Sub-Workspace Links */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 pb-4 border-b border-[#3A4553]">
          <div>
            <h1 className="text-xl font-bold text-white tracking-wide">
              Threat Intelligence Library
            </h1>
            <p className="text-xs text-slate-400 mt-1">
              Searchable repository over actual stored messages, URLs, domains, indicators, tactics, similarity clusters, and community reports.
            </p>
          </div>
          <div className="flex flex-wrap gap-2 text-xs">
            <Link
              href="/intelligence/tactics"
              className="px-3 py-1.5 rounded bg-[#252D38] border border-[#3A4553] hover:border-purple-500/60 text-purple-300 inline-flex items-center space-x-1"
            >
              <Zap className="w-3.5 h-3.5" />
              <span>10-Tactic Matrix</span>
            </Link>
            <Link
              href="/intelligence/campaigns"
              className="px-3 py-1.5 rounded bg-[#252D38] border border-[#3A4553] hover:border-orange-500/60 text-orange-300 inline-flex items-center space-x-1"
            >
              <Activity className="w-3.5 h-3.5" />
              <span>Campaign Dossiers</span>
            </Link>
            <Link
              href="/intelligence/threats"
              className="px-3 py-1.5 rounded bg-[#252D38] border border-[#3A4553] hover:border-rose-500/60 text-rose-300 inline-flex items-center space-x-1"
            >
              <AlertTriangle className="w-3.5 h-3.5" />
              <span>IOC Feed</span>
            </Link>
          </div>
        </div>

        {/* Entity Type Filter Tabs */}
        <div className="flex flex-wrap gap-2">
          {ENTITY_TABS.map((tab) => {
            const count =
              tab.id === "all"
                ? Object.values(facets).reduce((a, b) => a + b, 0)
                : facets[tab.id] || 0;
            const active = entityType === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => {
                  setEntityType(tab.id);
                  setPage(1);
                }}
                className={`px-3 py-1.5 rounded-md text-xs font-medium border transition-colors ${
                  active
                    ? "bg-blue-600/20 border-blue-500 text-blue-300"
                    : "bg-[#252D38] border-[#3A4553] text-slate-300 hover:border-slate-500"
                }`}
              >
                {tab.label} <span className="ml-1 text-[10px] opacity-75">({count})</span>
              </button>
            );
          })}
        </div>

        {/* Search, Filter, and Sort Controls */}
        <div className="bg-[#252D38] border border-[#3A4553] rounded-lg p-4 grid grid-cols-1 md:grid-cols-6 gap-3">
          <div className="md:col-span-2 relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
            <input
              type="text"
              value={search}
              onChange={(e) => {
                setSearch(e.target.value);
                setPage(1);
              }}
              placeholder="Search messages, URLs, domains, IOCs, clusters..."
              className="w-full pl-9 pr-3 py-2 text-xs bg-[#171C25] border border-[#3A4553] rounded text-slate-100 placeholder-slate-500 focus:outline-none focus:border-blue-500"
            />
          </div>

          <select
            aria-label="Filter by severity"
            value={severity}
            onChange={(e) => {
              setSeverity(e.target.value);
              setPage(1);
            }}
            className="px-2.5 py-2 text-xs bg-[#171C25] border border-[#3A4553] rounded text-slate-200"
          >
            <option value="all">Severity: All</option>
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
            <option value="clean">Clean</option>
            <option value="inconclusive">Inconclusive</option>
          </select>

          <select
            aria-label="Filter by verification status"
            value={verificationStatus}
            onChange={(e) => {
              setVerificationStatus(e.target.value);
              setPage(1);
            }}
            className="px-2.5 py-2 text-xs bg-[#171C25] border border-[#3A4553] rounded text-slate-200"
          >
            <option value="all">Verification: All</option>
            <option value="verified">Verified</option>
            <option value="automated_inference">Automated Inference</option>
            <option value="under_review">Under Review</option>
            <option value="unverified">Unverified</option>
          </select>

          <select
            aria-label="Filter by provenance"
            value={provenance}
            onChange={(e) => {
              setProvenance(e.target.value);
              setPage(1);
            }}
            className="px-2.5 py-2 text-xs bg-[#171C25] border border-[#3A4553] rounded text-slate-200"
          >
            <option value="all">Provenance: All</option>
            <option value="ml_model">ML Model</option>
            <option value="threat_intel">Threat Intel</option>
            <option value="human_review">Human Review</option>
            <option value="unsupervised_clustering">Clustering (HDBSCAN)</option>
          </select>

          <div className="flex space-x-2">
            <select
              aria-label="Sort field"
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="flex-1 px-2 py-2 text-xs bg-[#171C25] border border-[#3A4553] rounded text-slate-200"
            >
              <option value="created_at">Sort: Date</option>
              <option value="severity">Sort: Severity</option>
              <option value="confidence">Sort: Confidence</option>
              <option value="label">Sort: Label</option>
            </select>
            <button
              onClick={() => setSortOrder((prev) => (prev === "desc" ? "asc" : "desc"))}
              className="px-2.5 py-2 bg-[#171C25] border border-[#3A4553] rounded text-slate-300 hover:text-white"
              title={`Order: ${sortOrder.toUpperCase()}`}
            >
              <ArrowUpDown className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>

        {/* Results Table */}
        <div className="bg-[#252D38] border border-[#3A4553] rounded-lg overflow-hidden shadow-xl">
          {loading ? (
            <div className="p-12 text-center text-xs text-slate-400 flex flex-col items-center space-y-2">
              <RefreshCw className="w-5 h-5 animate-spin text-blue-400" />
              <span>Querying Threat Library records...</span>
            </div>
          ) : errorMsg ? (
            <div className="p-8 text-center text-xs text-rose-300 space-y-2">
              <p>{errorMsg}</p>
              <button
                onClick={fetchLibrary}
                className="px-3 py-1.5 bg-rose-900/50 border border-rose-700 rounded text-rose-200"
              >
                Retry
              </button>
            </div>
          ) : items.length === 0 ? (
            <div className="p-12 text-center text-xs text-slate-400">
              No stored threat records match the current search and filter criteria.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse text-xs">
                <thead>
                  <tr className="bg-[#1B212C] border-b border-[#3A4553] text-slate-400 uppercase tracking-wider text-[10px]">
                    <th className="py-3 px-4">Type</th>
                    <th className="py-3 px-4">Record / Indicator</th>
                    <th className="py-3 px-4">Severity</th>
                    <th className="py-3 px-4">Provenance</th>
                    <th className="py-3 px-4">Verification</th>
                    <th className="py-3 px-4">Confidence</th>
                    <th className="py-3 px-4 text-right">Details</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#3A4553]/60">
                  {items.map((item) => (
                    <tr
                      key={item.item_id}
                      onClick={() => {
                        setSelectedItem(item);
                        setExportStatus(null);
                      }}
                      className="hover:bg-[#2E3846] cursor-pointer transition-colors"
                    >
                      <td className="py-3 px-4 font-mono text-[11px] text-slate-300 whitespace-nowrap">
                        {item.entity_type}
                      </td>
                      <td className="py-3 px-4 max-w-md">
                        <div className="font-semibold text-white truncate">{item.label}</div>
                        <div className="text-[11px] text-slate-400 truncate mt-0.5">{item.summary}</div>
                      </td>
                      <td className="py-3 px-4 whitespace-nowrap">
                        <span
                          className={`px-2 py-0.5 rounded border text-[10px] uppercase font-semibold ${
                            SEVERITY_BADGE[item.severity] || SEVERITY_BADGE.inconclusive
                          }`}
                        >
                          {item.severity}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-[11px] text-slate-300 whitespace-nowrap">
                        <div>{item.provenance}</div>
                        <div className="text-[10px] text-slate-500 truncate max-w-[160px]">
                          {item.source_name}
                        </div>
                      </td>
                      <td className="py-3 px-4 whitespace-nowrap">
                        <span
                          className={`px-2 py-0.5 rounded border text-[10px] font-medium ${
                            VERIFICATION_BADGE[item.verification_status] || VERIFICATION_BADGE.unverified
                          }`}
                        >
                          {item.verification_status}
                        </span>
                      </td>
                      <td className="py-3 px-4 font-mono text-slate-200 whitespace-nowrap">
                        {item.confidence !== null && item.confidence !== undefined
                          ? `${(item.confidence * 100).toFixed(1)}%`
                          : "N/A"}
                      </td>
                      <td className="py-3 px-4 text-right whitespace-nowrap">
                        <span className="text-blue-400 hover:text-blue-300 inline-flex items-center space-x-1">
                          <span>Inspect</span>
                          <ArrowRight className="w-3 h-3" />
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* Pagination Footer */}
          <div className="px-4 py-3 bg-[#1B212C] border-t border-[#3A4553] flex items-center justify-between text-xs text-slate-400">
            <span>
              Showing page <strong className="text-white">{page}</strong> of{" "}
              <strong className="text-white">{totalPages}</strong> ({total} matching records)
            </span>
            <div className="flex space-x-2">
              <button
                disabled={page <= 1}
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                className="px-2.5 py-1 rounded bg-[#252D38] border border-[#3A4553] disabled:opacity-40 hover:border-slate-500 inline-flex items-center space-x-1"
              >
                <ChevronLeft className="w-3.5 h-3.5" />
                <span>Prev</span>
              </button>
              <button
                disabled={page >= totalPages}
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                className="px-2.5 py-1 rounded bg-[#252D38] border border-[#3A4553] disabled:opacity-40 hover:border-slate-500 inline-flex items-center space-x-1"
              >
                <span>Next</span>
                <ChevronRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        </div>
      </main>

      {/* Detail View Modal */}
      {selectedItem && (
        <div className="fixed inset-0 z-50 bg-black/70 flex items-center justify-center p-4">
          <div className="bg-[#252D38] border border-[#3A4553] rounded-lg max-w-2xl w-full max-h-[85vh] flex flex-col shadow-2xl">
            <div className="px-5 py-4 border-b border-[#3A4553] flex items-center justify-between">
              <div>
                <span className="text-[10px] uppercase font-mono text-blue-400">
                  {selectedItem.entity_type} • {selectedItem.item_id}
                </span>
                <h2 className="text-sm font-bold text-white mt-0.5 break-all">{selectedItem.label}</h2>
              </div>
              <button
                onClick={() => setSelectedItem(null)}
                className="p-1 text-slate-400 hover:text-white rounded"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="p-5 overflow-y-auto space-y-4 text-xs">
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                <div className="bg-[#171C25] p-2.5 rounded border border-[#3A4553]">
                  <div className="text-[10px] text-slate-400">Severity</div>
                  <div className="font-semibold text-white uppercase mt-0.5">{selectedItem.severity}</div>
                </div>
                <div className="bg-[#171C25] p-2.5 rounded border border-[#3A4553]">
                  <div className="text-[10px] text-slate-400">Verification</div>
                  <div className="font-semibold text-white mt-0.5">{selectedItem.verification_status}</div>
                </div>
                <div className="bg-[#171C25] p-2.5 rounded border border-[#3A4553]">
                  <div className="text-[10px] text-slate-400">Provenance</div>
                  <div className="font-semibold text-white mt-0.5">{selectedItem.provenance}</div>
                </div>
                <div className="bg-[#171C25] p-2.5 rounded border border-[#3A4553]">
                  <div className="text-[10px] text-slate-400">Confidence</div>
                  <div className="font-semibold text-white font-mono mt-0.5">
                    {selectedItem.confidence !== null ? `${(selectedItem.confidence * 100).toFixed(1)}%` : "N/A"}
                  </div>
                </div>
              </div>

              <div className="bg-[#171C25] p-3 rounded border border-[#3A4553]">
                <div className="text-[10px] text-slate-400 uppercase mb-1">Source & Summary</div>
                <p className="text-slate-200">{selectedItem.source_name}</p>
                <p className="text-slate-400 mt-1">{selectedItem.summary}</p>
              </div>

              <div className="bg-[#171C25] p-3 rounded border border-[#3A4553]">
                <div className="text-[10px] text-slate-400 uppercase mb-1">Stored Record Metadata</div>
                <pre className="text-[11px] font-mono text-slate-300 whitespace-pre-wrap overflow-x-auto max-h-60">
                  {JSON.stringify(selectedItem.metadata, null, 2)}
                </pre>
              </div>

              {exportStatus && (
                <div className="text-[11px] text-blue-300 bg-blue-950/50 border border-blue-800/60 px-3 py-2 rounded">
                  {exportStatus}
                </div>
              )}
            </div>

            <div className="px-5 py-3 border-t border-[#3A4553] bg-[#1B212C] flex items-center justify-between">
              <div className="flex space-x-2">
                <button
                  onClick={() => handleDownloadExport("json", selectedItem)}
                  className="px-3 py-1.5 rounded bg-[#252D38] border border-[#3A4553] hover:border-blue-500 text-xs text-slate-200 inline-flex items-center space-x-1.5"
                >
                  <Download className="w-3.5 h-3.5" />
                  <span>Export JSON</span>
                </button>
                <button
                  onClick={() => handleDownloadExport("stix", selectedItem)}
                  className="px-3 py-1.5 rounded bg-[#252D38] border border-[#3A4553] hover:border-emerald-500 text-xs text-emerald-300 inline-flex items-center space-x-1.5"
                >
                  <Download className="w-3.5 h-3.5" />
                  <span>Export STIX 2.1</span>
                </button>
              </div>
              <button
                onClick={() => setSelectedItem(null)}
                className="px-4 py-1.5 rounded bg-blue-600 hover:bg-blue-500 text-xs font-semibold text-white"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
