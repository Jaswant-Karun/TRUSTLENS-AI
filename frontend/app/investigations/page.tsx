"use client";

import React, { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import {
  ShieldAlert,
  Search,
  Plus,
  ArrowRight,
  Clock,
  Layers,
  Activity,
  User,
  Tag,
  AlertTriangle,
  RotateCcw,
} from "lucide-react";
import { TopNavigation } from "@/components/investigation/TopNavigation";
import { CreateInvestigationModal } from "@/components/investigation/CreateInvestigationModal";
import {
  getInvestigations,
  createInvestigation,
  InvestigationSummaryItem,
} from "@/lib/api";

export default function InvestigationsDirectoryPage() {
  const [search, setSearch] = useState("");
  const [severityFilter, setSeverityFilter] = useState("all");
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [investigations, setInvestigations] = useState<InvestigationSummaryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch real investigations from FastAPI backend
  const loadInvestigations = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getInvestigations();
      setInvestigations(data || []);
    } catch (err: any) {
      setError(err?.message || "Failed to load investigations from backend.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadInvestigations();
  }, [loadInvestigations]);

  // Handle creating new real investigation
  const handleCreateSubmit = async (payload: any) => {
    try {
      const created = await createInvestigation({
        title: payload.title,
        description: payload.description,
        severity: payload.severity,
        tags: payload.tags,
      });
      setIsCreateOpen(false);
      setInvestigations((prev) => [created, ...prev]);
    } catch (err: any) {
      alert(`Failed to create investigation: ${err?.message}`);
    }
  };

  const filtered = investigations.filter((inv) => {
    if (severityFilter !== "all" && inv.severity !== severityFilter) return false;
    if (
      search &&
      !inv.title.toLowerCase().includes(search.toLowerCase()) &&
      !(inv.description || "").toLowerCase().includes(search.toLowerCase())
    ) {
      return false;
    }
    return true;
  });

  return (
    <div className="min-h-screen bg-[#171C25] text-slate-100 flex flex-col font-sans select-none">
      {/* 1. ThreatQ Top Navigation Bar */}
      <TopNavigation onCreateClick={() => setIsCreateOpen(true)} />

      {/* 2. Main Content Area */}
      <main className="flex-1 p-6 md:p-8 max-w-7xl w-full mx-auto space-y-6">
        {/* Header Strip */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-[#3A4553]">
          <div>
            <div className="flex items-center space-x-2">
              <span className="w-2.5 h-2.5 rounded-full bg-cyan-400 animate-pulse"></span>
              <span className="text-xs font-mono uppercase tracking-widest text-cyan-400 font-bold">
                Threat Intelligence Operations
              </span>
            </div>
            <h1 className="text-2xl font-bold text-white tracking-tight mt-1">
              Active Investigations Directory
            </h1>
            <p className="text-xs text-slate-400 mt-1">
              Live threat dossiers synchronized with MongoDB Atlas, Model 4 HDBSCAN clusters, and verified IOC feeds.
            </p>
          </div>

          <div className="flex items-center space-x-3">
            <button
              onClick={() => setIsCreateOpen(true)}
              className="flex items-center space-x-2 px-3.5 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded text-xs font-semibold shadow-lg shadow-blue-900/30 transition-colors"
            >
              <Plus className="w-4 h-4" />
              <span>New Dossier</span>
            </button>
          </div>
        </div>

        {/* Search & Filter Toolbar */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-3 bg-[#252D38] p-3 rounded-md border border-[#3A4553]">
          <div className="relative w-full sm:w-80">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search dossiers, IOCs, campaign entities..."
              className="w-full bg-[#181E28] border border-[#3A4553] rounded pl-9 pr-3 py-1.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500"
            />
          </div>

          <div className="flex items-center space-x-2 w-full sm:w-auto">
            <span className="text-xs text-slate-400 font-mono">Severity:</span>
            {["all", "critical", "high", "medium", "low"].map((sev) => (
              <button
                key={sev}
                onClick={() => setSeverityFilter(sev)}
                className={`px-2.5 py-1 rounded text-xs font-mono uppercase transition-colors ${
                  severityFilter === sev
                    ? "bg-cyan-500 text-slate-950 font-bold"
                    : "bg-[#181E28] text-slate-400 hover:text-white border border-[#3A4553]"
                }`}
              >
                {sev}
              </button>
            ))}
            <button
              onClick={loadInvestigations}
              title="Refresh Investigations"
              className="p-1.5 bg-[#181E28] hover:bg-[#202731] border border-[#3A4553] rounded text-slate-300 hover:text-white transition-colors ml-2"
            >
              <RotateCcw className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>

        {/* Loading State */}
        {loading && (
          <div className="flex flex-col items-center justify-center py-20 space-y-3">
            <div className="w-8 h-8 rounded-full border-2 border-cyan-400 border-t-transparent animate-spin"></div>
            <p className="text-xs font-mono text-slate-400">Loading active investigations from MongoDB...</p>
          </div>
        )}

        {/* Error State */}
        {error && !loading && (
          <div className="bg-rose-950/40 border border-rose-800/80 rounded-md p-6 text-center space-y-3">
            <AlertTriangle className="w-6 h-6 text-rose-400 mx-auto" />
            <p className="text-sm font-semibold text-rose-300">{error}</p>
            <button
              onClick={loadInvestigations}
              className="px-4 py-1.5 bg-rose-600 hover:bg-rose-500 text-white rounded text-xs font-semibold"
            >
              Retry Connection
            </button>
          </div>
        )}

        {/* Investigations Grid */}
        {!loading && !error && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {filtered.map((inv) => (
              <Link
                key={inv.id}
                href={`/investigations/${inv.id}`}
                className="group block bg-[#252D38] border border-[#3A4553] hover:border-cyan-500/60 rounded-md p-5 transition-all shadow-xl hover:shadow-cyan-950/20 relative overflow-hidden"
              >
                {/* Top Strip */}
                <div className="flex items-center justify-between mb-3">
                  <span className="font-mono text-xs font-bold text-cyan-400 group-hover:text-cyan-300">
                    {inv.id}
                  </span>
                  <span
                    className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase tracking-wider ${
                      inv.severity === "critical"
                        ? "bg-rose-950/80 text-rose-400 border border-rose-800"
                        : inv.severity === "high"
                        ? "bg-amber-950/80 text-amber-400 border border-amber-800"
                        : "bg-slate-800 text-slate-300 border border-slate-700"
                    }`}
                  >
                    {inv.severity || "medium"}
                  </span>
                </div>

                {/* Title & Description */}
                <h3 className="text-sm font-semibold text-white group-hover:text-cyan-300 transition-colors line-clamp-1 mb-1.5">
                  {inv.title}
                </h3>
                <p className="text-xs text-slate-300 line-clamp-2 leading-relaxed mb-4">
                  {inv.description || "Active cyber threat investigation dossier."}
                </p>

                {/* Tags */}
                <div className="flex flex-wrap gap-1 mb-4">
                  {(inv.tags || []).slice(0, 3).map((tag) => (
                    <span
                      key={tag}
                      className="px-1.5 py-0.5 bg-[#181E28] border border-[#3A4553] text-[10px] font-mono text-slate-400 rounded"
                    >
                      #{tag}
                    </span>
                  ))}
                  {(inv.tags || []).length > 3 && (
                    <span className="px-1 py-0.5 text-[10px] font-mono text-slate-500">
                      +{inv.tags.length - 3}
                    </span>
                  )}
                </div>

                {/* Metrics Matrix (Objects | Tasks) */}
                <div className="pt-3 border-t border-[#3A4553] flex items-center justify-between text-xs text-slate-400 font-mono">
                  <div className="flex items-center space-x-3">
                    <span className="flex items-center space-x-1">
                      <Layers className="w-3.5 h-3.5 text-slate-500" />
                      <strong className="text-white">{inv.objects_count || 0}</strong> objs
                    </span>
                    <span className="flex items-center space-x-1">
                      <Activity className="w-3.5 h-3.5 text-slate-500" />
                      <strong className="text-white">{inv.tasks_count || 0}</strong> tasks
                    </span>
                  </div>

                  <span className="flex items-center text-cyan-400 group-hover:translate-x-1 transition-transform">
                    <span className="text-[11px] font-sans mr-1 font-semibold">Inspect</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </span>
                </div>
              </Link>
            ))}

            {filtered.length === 0 && (
              <div className="col-span-full py-16 text-center text-slate-500 text-xs font-mono">
                No matching investigations found for current filter.
              </div>
            )}
          </div>
        )}
      </main>

      {/* Create Modal */}
      <CreateInvestigationModal
        isOpen={isCreateOpen}
        onClose={() => setIsCreateOpen(false)}
        onSubmit={handleCreateSubmit}
      />
    </div>
  );
}
