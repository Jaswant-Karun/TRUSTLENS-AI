"use client";

import React, { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  Column,
  ConfirmDialog,
  DataTable,
  EmptyState,
  ErrorState,
  PageHeader,
  SearchFilterBar,
  useToast,
} from "@/components/ui";
import {
  AnalysisHistoryItem,
  deleteAnalysis,
  getAnalysesHistory,
  getAnalysisDetail,
  getStoredToken,
} from "@/lib/api";
import { Eye, Trash2, X } from "lucide-react";

export default function HistoryPage() {
  const router = useRouter();
  const { success, error: showError } = useToast();

  const [items, setItems] = useState<AnalysisHistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalCount, setTotalCount] = useState(0);

  const [search, setSearch] = useState("");
  const [threatLevel, setThreatLevel] = useState("");
  const [channel, setChannel] = useState("");
  const [sortBy, setSortBy] = useState("created_at");
  const [sortOrder, setSortOrder] = useState("desc");

  const [selectedDetail, setSelectedDetail] = useState<any | null>(null);
  const [deleteTargetId, setDeleteTargetId] = useState<string | null>(null);

  const fetchHistory = useCallback(async () => {
    if (!getStoredToken()) {
      setLoading(false);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const res = await getAnalysesHistory({
        page,
        page_size: 15,
        threat_level: threatLevel || undefined,
        channel: channel || undefined,
        search: search.trim() || undefined,
        sort_by: sortBy,
        sort_order: sortOrder,
      });
      setItems(res.items || []);
      setTotalPages(res.total_pages || 1);
      setTotalCount(res.total_count || 0);
    } catch (err: any) {
      setError(err?.message || "Failed to load persistent analysis history.");
    } finally {
      setLoading(false);
    }
  }, [page, threatLevel, channel, search, sortBy, sortOrder]);

  useEffect(() => {
    fetchHistory();
  }, [fetchHistory]);

  const handleInspect = async (analysisId: string) => {
    try {
      const detail = await getAnalysisDetail(analysisId);
      setSelectedDetail(detail);
    } catch (err: any) {
      showError("Load Failed", err?.message || "Could not load analysis detail.");
    }
  };

  const handleConfirmDelete = async () => {
    if (!deleteTargetId) return;
    const target = deleteTargetId;
    setDeleteTargetId(null);
    try {
      await deleteAnalysis(target);
      success("Deleted", `Analysis ${target} removed.`);
      if (selectedDetail?.analysis_id === target) setSelectedDetail(null);
      fetchHistory();
    } catch (err: any) {
      showError("Delete Failed", err?.message || "Not authorized to delete this record.");
    }
  };

  const columns: Column<AnalysisHistoryItem>[] = [
    {
      header: "Timestamp",
      accessorKey: "created_at",
      cell: (row) => (
        <span className="font-mono text-[11px] text-[#A1A1AA]">
          {row.created_at ? new Date(row.created_at).toLocaleString() : "—"}
        </span>
      ),
    },
    {
      header: "Type",
      accessorKey: "analysis_type",
      cell: (row) => (
        <span className="font-mono text-xs uppercase text-white">
          {row.analysis_type || row.channel || "scan"}
        </span>
      ),
    },
    {
      header: "Threat Level",
      accessorKey: "threat_level",
      cell: (row) => {
        const lvl = (row.threat_level || "inconclusive").toLowerCase();
        const badgeCls =
          lvl === "critical" || lvl === "high"
            ? "bg-[#FF174F]/15 text-[#FF174F] border-[#FF174F]/50"
            : lvl === "medium"
            ? "bg-[#FFB020]/15 text-[#FFB020] border-[#FFB020]/50"
            : "bg-[#00D68F]/15 text-[#00D68F] border-[#00D68F]/40";
        return (
          <span className={`px-2 py-0.5 rounded-full text-[10px] font-mono uppercase border ${badgeCls}`}>
            {lvl}
          </span>
        );
      },
    },
    {
      header: "Risk Score",
      accessorKey: "risk_score",
      align: "right",
      cell: (row) => (
        <span className="font-mono text-xs font-bold text-white">
          {typeof row.risk_score === "number" ? `${Math.round(row.risk_score * 100)}%` : "—"}
        </span>
      ),
    },
    {
      header: "Actions",
      align: "right",
      cell: (row) => (
        <div className="inline-flex items-center gap-1.5">
          <button
            type="button"
            onClick={(e) => {
              e.stopPropagation();
              handleInspect(row.analysis_id);
            }}
            aria-label={`Inspect ${row.analysis_id}`}
            className="p-1.5 rounded border border-[#481326] bg-[#050306] text-[#A1A1AA] hover:border-[#FF174F] hover:text-white transition-colors"
          >
            <Eye className="w-3.5 h-3.5" />
          </button>
          <button
            type="button"
            onClick={(e) => {
              e.stopPropagation();
              setDeleteTargetId(row.analysis_id);
            }}
            aria-label={`Delete ${row.analysis_id}`}
            className="p-1.5 rounded border border-[#481326] bg-[#050306] text-[#A1A1AA] hover:border-[#FF174F] hover:text-[#FF174F] transition-colors"
          >
            <Trash2 className="w-3.5 h-3.5" />
          </button>
        </div>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      <PageHeader
        title="Analysis History"
        description="Persistent MongoDB record of your submitted message, URL, and screenshot analyses."
        badge={{ text: `${totalCount} Stored Records`, variant: "rose" }}
      />

      <SearchFilterBar
        search={search}
        onSearchChange={(val) => {
          setPage(1);
          setSearch(val);
        }}
        searchPlaceholder="Search by analysis ID, type, or threat level..."
        threatLevel={threatLevel}
        onThreatLevelChange={(val) => {
          setPage(1);
          setThreatLevel(val);
        }}
        channel={channel}
        onChannelChange={(val) => {
          setPage(1);
          setChannel(val);
        }}
        extraFilters={
          <select
            aria-label="Sort history"
            value={`${sortBy}:${sortOrder}`}
            onChange={(e) => {
              const [sb, so] = e.target.value.split(":");
              setPage(1);
              setSortBy(sb);
              setSortOrder(so);
            }}
            className="cyber-select"
          >
            <option value="created_at:desc">Newest First</option>
            <option value="created_at:asc">Oldest First</option>
            <option value="risk_score:desc">Highest Risk</option>
            <option value="risk_score:asc">Lowest Risk</option>
          </select>
        }
        onReset={() => {
          setPage(1);
          setSearch("");
          setThreatLevel("");
          setChannel("");
          setSortBy("created_at");
          setSortOrder("desc");
        }}
      />

      {error && <ErrorState message={error} onRetry={fetchHistory} />}

      {!loading && !error && items.length === 0 ? (
        <EmptyState
          title="No Saved Analyses Yet"
          description="Submit a suspicious message, URL, or screenshot to record real ML analysis results here."
          actionLabel="Open Message Scanner"
          onAction={() => router.push("/analyze/text")}
        />
      ) : (
        <DataTable
          columns={columns}
          data={items}
          loading={loading}
          onRowClick={(row) => handleInspect(row.analysis_id)}
          pagination={{
            currentPage: page,
            totalPages,
            totalItems: totalCount,
            onPageChange: (p) => setPage(p),
          }}
        />
      )}

      {/* Analysis Detail Modal */}
      {selectedDetail && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-[#050306]/85 backdrop-blur-sm p-4">
          <div className="cyber-modal w-full max-w-2xl max-h-[85vh] overflow-y-auto p-6 space-y-4">
            <div className="flex items-center justify-between border-b border-[#481326] pb-3">
              <div>
                <h3 className="font-mono text-sm font-bold uppercase text-white">
                  Analysis Detail — {selectedDetail.analysis_id}
                </h3>
                <p className="text-[11px] font-mono text-[#A1A1AA]">
                  {selectedDetail.created_at
                    ? new Date(selectedDetail.created_at).toLocaleString()
                    : "Timestamp unavailable"}
                </p>
              </div>
              <button
                type="button"
                aria-label="Close detail"
                onClick={() => setSelectedDetail(null)}
                className="text-[#A1A1AA] hover:text-white p-1"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 text-xs font-mono">
              <div className="p-3 rounded bg-[#050306] border border-[#481326]">
                <span className="text-[#A1A1AA] block text-[10px] uppercase">Threat Level</span>
                <span className="text-white font-bold uppercase">{selectedDetail.threat_level}</span>
              </div>
              <div className="p-3 rounded bg-[#050306] border border-[#481326]">
                <span className="text-[#A1A1AA] block text-[10px] uppercase">Risk Score</span>
                <span className="text-[#FF3D70] font-bold">
                  {typeof selectedDetail.risk_score === "number"
                    ? `${Math.round(selectedDetail.risk_score * 100)}%`
                    : "—"}
                </span>
              </div>
              <div className="p-3 rounded bg-[#050306] border border-[#481326]">
                <span className="text-[#A1A1AA] block text-[10px] uppercase">Type</span>
                <span className="text-white">{selectedDetail.analysis_type}</span>
              </div>
            </div>

            {selectedDetail.risk_assessment && (
              <div className="p-4 rounded-lg bg-[#050306] border border-[#481326] space-y-2 text-xs">
                <div className="font-mono text-[10px] uppercase text-[#FF3D70] font-bold">
                  Risk Assessment &amp; Model Evidence
                </div>
                <p className="text-[#A1A1AA]">{selectedDetail.risk_assessment.verdict}</p>
              </div>
            )}

            <pre className="p-3 rounded-lg bg-[#050306] border border-[#481326] text-[11px] font-mono text-[#A1A1AA] overflow-x-auto max-h-60">
              {JSON.stringify(selectedDetail.model_results || selectedDetail.input_payload || {}, null, 2)}
            </pre>
          </div>
        </div>
      )}

      <ConfirmDialog
        isOpen={Boolean(deleteTargetId)}
        title="Delete Analysis Record"
        message={`Permanently delete analysis ${deleteTargetId}? This action cannot be undone.`}
        confirmText="Delete Record"
        variant="danger"
        onConfirm={handleConfirmDelete}
        onCancel={() => setDeleteTargetId(null)}
      />
    </div>
  );
}
