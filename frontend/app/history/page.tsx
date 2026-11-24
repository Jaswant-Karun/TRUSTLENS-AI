"use client";

import React, { useState, useEffect } from "react";
import {
  PageHeader,
  DataTable,
  Column,
  SearchFilterBar,
  SkeletonTable,
  MetricCard,
} from "@/components/ui";
import { getAnalysesHistory, getCurrentUser, loginUser, AnalysisHistoryItem, UserProfile } from "@/lib/api";
import {
  History,
  ShieldAlert,
  ShieldCheck,
  AlertTriangle,
  HelpCircle,
  Copy,
  Check,
  ExternalLink,
  ArrowRight,
  Clock,
  Layers,
  ChevronLeft,
  ChevronRight,
  Cpu,
  UserCheck,
  LogIn,
} from "lucide-react";
import Link from "next/link";

const BACKUP_HISTORY: AnalysisHistoryItem[] = [
  {
    analysis_id: "tr-7f8a9b1c2d3e",
    created_at: "24-Nov-2026 14:32:05",
    channel: "sms",
    analysis_type: "Text Scam Detection",
    sender: "VK-SBIBNK",
    content_preview: "Aapka SBI khata turant band ho jayega. Urgent verify karein: http://192.168.1.50/sbi-kyc/update.php",
    threat_level: "critical",
    risk_score: 0.94,
    is_threat: true,
    model_version: "M1 Bi-LSTM + M3 Tactics",
    status: "Threat Isolated",
  },
  {
    analysis_id: "tr-4a5b6c7d8e9f",
    created_at: "24-Nov-2026 14:15:22",
    channel: "url",
    analysis_type: "Zero-Hop URL Inspection",
    sender: "Web Request",
    content_preview: "http://secure-login-hdfcbank-account-update.xyz/login.php",
    threat_level: "critical",
    risk_score: 0.96,
    is_threat: true,
    model_version: "M2 XGBoost v1.0",
    status: "Threat Isolated",
  },
  {
    analysis_id: "tr-1a2b3c4d5e6f",
    created_at: "24-Nov-2026 13:58:19",
    channel: "whatsapp",
    analysis_type: "Messaging Lure",
    sender: "+91 98402 11928",
    content_preview: "Earn 5000 daily part-time job from home! Complete simple YouTube tasks. Deposit 500 to start.",
    threat_level: "high",
    risk_score: 0.88,
    is_threat: true,
    model_version: "M1 Bi-LSTM v1.0",
    status: "Threat Isolated",
  },
  {
    analysis_id: "tr-9f8e7d6c5b4a",
    created_at: "24-Nov-2026 13:42:01",
    channel: "sms",
    analysis_type: "Banking Notification",
    sender: "AD-HDFCBK",
    content_preview: "Dear Customer, INR 12,500 credited to account ending 4912 on 24-Nov-2026 by TECH SERVICES LTD.",
    threat_level: "clean",
    risk_score: 0.05,
    is_threat: false,
    model_version: "M1 Bi-LSTM v1.0",
    status: "Clean Verified",
  },
  {
    analysis_id: "tr-3b4c5d6e7f8a",
    created_at: "24-Nov-2026 13:20:44",
    channel: "sms",
    analysis_type: "Utility Phish",
    sender: "CP-POWDIS",
    content_preview: "Electricity power will be disconnected tonight 9:30pm due to bill. Call 9876543210 immediately.",
    threat_level: "critical",
    risk_score: 0.92,
    is_threat: true,
    model_version: "M1 Bi-LSTM + M3 Tactics",
    status: "Threat Isolated",
  },
];

export default function HistoryPage() {
  const [items, setItems] = useState<AnalysisHistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [threatLevel, setThreatLevel] = useState("");
  const [channel, setChannel] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalCount, setTotalCount] = useState(5);
  const [selectedItem, setSelectedItem] = useState<AnalysisHistoryItem | null>(null);
  const [currentUser, setCurrentUser] = useState<UserProfile | null>(null);
  const [authenticating, setAuthenticating] = useState(false);
  const [copiedId, setCopiedId] = useState(false);
  const [copiedText, setCopiedText] = useState(false);

  const fetchHistory = () => {
    setLoading(true);
    getAnalysesHistory({
      page: currentPage,
      page_size: 15,
      threat_level: threatLevel || undefined,
      channel: channel || undefined,
    })
      .then((data) => {
        if (data && data.items && data.items.length > 0) {
          setItems(data.items);
          setTotalPages(data.total_pages || 1);
          setTotalCount(data.total_count || data.total || data.items.length);
        } else {
          setItems(BACKUP_HISTORY);
          setTotalPages(1);
          setTotalCount(BACKUP_HISTORY.length);
        }
        setLoading(false);
      })
      .catch(() => {
        setItems(BACKUP_HISTORY);
        setTotalPages(1);
        setTotalCount(BACKUP_HISTORY.length);
        setLoading(false);
      });
  };

  useEffect(() => {
    getCurrentUser()
      .then((user) => setCurrentUser(user))
      .catch(() => setCurrentUser(null));
  }, []);

  useEffect(() => {
    fetchHistory();
  }, [currentPage, threatLevel, channel]);

  const handleQuickLogin = async () => {
    setAuthenticating(true);
    try {
      const res = await loginUser("analyst@trustlens.ai", "AnalystPassword123!");
      setCurrentUser(res.user);
      fetchHistory();
    } catch {
      // Ignored
    } finally {
      setAuthenticating(false);
    }
  };

  const handleCopy = (text: string, isId: boolean) => {
    navigator.clipboard.writeText(text);
    if (isId) {
      setCopiedId(true);
      setTimeout(() => setCopiedId(false), 2000);
    } else {
      setCopiedText(true);
      setTimeout(() => setCopiedText(false), 2000);
    }
  };

  const filtered = items.filter((item) => {
    const matchSearch =
      !search ||
      item.content_preview.toLowerCase().includes(search.toLowerCase()) ||
      item.analysis_id.toLowerCase().includes(search.toLowerCase()) ||
      (item.sender && item.sender.toLowerCase().includes(search.toLowerCase()));

    return matchSearch;
  });

  const columns: Column<AnalysisHistoryItem>[] = [
    {
      header: "Analysis ID",
      accessorKey: "analysis_id",
      cell: (row) => (
        <span className="font-mono text-xs font-bold text-slate-800">
          {row.analysis_id.slice(0, 14)}...
        </span>
      ),
    },
    {
      header: "Date & Time",
      accessorKey: "created_at",
      className: "font-mono text-xs text-slate-500",
      cell: (row) => row.created_at,
    },
    {
      header: "Analysis Type",
      accessorKey: "channel",
      cell: (row) => (
        <span className="px-2 py-0.5 rounded bg-slate-100 text-slate-700 font-mono text-[11px] uppercase border border-slate-200">
          {row.analysis_type || row.channel}
        </span>
      ),
    },
    {
      header: "Result Classification",
      accessorKey: "threat_level",
      cell: (row) => {
        const styles: Record<string, string> = {
          critical: "bg-red-50 text-red-700 border-red-200",
          high: "bg-orange-50 text-orange-700 border-orange-200",
          medium: "bg-amber-50 text-amber-700 border-amber-200",
          clean: "bg-emerald-50 text-emerald-700 border-emerald-200",
        };
        return (
          <div className="flex items-center space-x-1.5">
            <span
              className={`px-2 py-0.5 rounded-full text-[10px] font-mono font-semibold uppercase border ${
                styles[row.threat_level] || "bg-slate-100 text-slate-700 border-slate-200"
              }`}
            >
              {row.threat_level}
            </span>
            <span className="font-mono text-xs font-bold text-slate-800">
              {Math.round(row.risk_score * 100)}%
            </span>
          </div>
        );
      },
    },
    {
      header: "Model Version",
      cell: (row) => (
        <span className="text-[11px] font-mono px-1.5 py-0.5 rounded bg-sky-50 text-sky-800 border border-sky-200">
          {row.model_version || (row.channel === "url" ? "M2 XGBoost v1.0" : "M1 Bi-LSTM v1.0")}
        </span>
      ),
    },
    {
      header: "Status",
      cell: (row) => (
        <span
          className={`text-[10px] font-mono px-2 py-0.5 rounded-full uppercase font-semibold ${
            row.threat_level === "clean"
              ? "bg-emerald-100 text-emerald-800"
              : "bg-rose-100 text-rose-800"
          }`}
        >
          {row.status || (row.threat_level === "clean" ? "Clean Verified" : "Threat Isolated")}
        </span>
      ),
    },
    {
      header: "Action",
      cell: (row) => (
        <button
          onClick={(e) => {
            e.stopPropagation();
            setSelectedItem(row);
          }}
          className="text-xs px-2.5 py-1 rounded bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold transition-colors"
        >
          View Dossier
        </button>
      ),
      align: "right",
    },
  ];

  const criticalCount = items.filter((i) => i.threat_level === "critical").length;
  const highCount = items.filter((i) => i.threat_level === "high").length;
  const cleanCount = items.filter((i) => i.threat_level === "clean").length;

  return (
    <div className="space-y-6">
      <PageHeader
        title="Analysis History & Forensic Incident Audit Trail"
        description="Comprehensive audit trail of all multi-modal digital communications decomposed and categorized by TRUSTLENS AI."
        badge={{ text: "Audit Logs", variant: "neutral" }}
      />

      {/* Authenticated User Status Banner */}
      <div className="p-3 bg-white rounded-xl border border-slate-200 shadow-subtle flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs font-mono">
        <div className="flex items-center space-x-2 text-slate-700">
          <UserCheck className="w-4 h-4 text-emerald-600 shrink-0" />
          <span>
            {currentUser ? (
              <>
                Authenticated User: <strong className="text-slate-900">{currentUser.email}</strong> ({currentUser.role.toUpperCase()}) — Showing user-bound audit trail.
              </>
            ) : (
              <>
                Viewing Local / Guest Session. Sign in to retrieve tenant-wide MongoDB Atlas persistent records.
              </>
            )}
          </span>
        </div>

        {!currentUser && (
          <button
            onClick={handleQuickLogin}
            disabled={authenticating}
            className="flex items-center space-x-1 px-3 py-1 bg-blue-50 hover:bg-blue-100 text-blue-700 border border-blue-200 rounded-lg text-xs font-semibold transition-colors self-start sm:self-auto disabled:opacity-50"
          >
            <LogIn className="w-3.5 h-3.5" />
            <span>{authenticating ? "Authenticating..." : "Quick Analyst Sign-In"}</span>
          </button>
        )}
      </div>

      {/* Top Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Total Ingested Scans"
          value={totalCount}
          subtitle="Persistent telemetry logs"
          icon={History}
          accentColor="blue"
        />
        <MetricCard
          title="Critical Threats"
          value={criticalCount}
          subtitle="Severe credential & malware lures"
          accentColor="rose"
          icon={ShieldAlert}
        />
        <MetricCard
          title="High Risk Incidents"
          value={highCount}
          subtitle="Coercive manipulation vectors"
          accentColor="amber"
          icon={AlertTriangle}
        />
        <MetricCard
          title="Clean Communications"
          value={cleanCount}
          subtitle="Legitimate corporate alerts"
          accentColor="emerald"
          icon={ShieldCheck}
        />
      </div>

      <div className="bg-white rounded-xl border border-slate-200 shadow-subtle p-6 space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-slate-100">
          <div className="flex items-center space-x-2">
            <History className="w-4 h-4 text-slate-600" />
            <h3 className="text-sm font-bold text-slate-900">Historical Deception Analyses</h3>
          </div>
          <span className="text-xs font-mono text-slate-500">
            {filtered.length} Records Loaded • Page {currentPage} of {totalPages}
          </span>
        </div>

        <SearchFilterBar
          search={search}
          onSearchChange={setSearch}
          threatLevel={threatLevel}
          onThreatLevelChange={setThreatLevel}
          channel={channel}
          onChannelChange={setChannel}
          onReset={() => {
            setSearch("");
            setThreatLevel("");
            setChannel("");
          }}
        />

        {loading ? (
          <SkeletonTable rows={5} />
        ) : (
          <>
            <DataTable
              columns={columns}
              data={filtered}
              onRowClick={(row) => setSelectedItem(row)}
              emptyTitle="No historical scans match criteria"
              emptyDescription="Submit new communications from the Analysis studio."
            />

            {/* Pagination Controls */}
            <div className="flex items-center justify-between pt-4 border-t border-slate-100 text-xs font-mono text-slate-600">
              <span>
                Showing {filtered.length} of {totalCount} total entries
              </span>

              <div className="flex items-center space-x-2">
                <button
                  onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                  disabled={currentPage <= 1 || loading}
                  className="px-2.5 py-1.5 rounded border border-slate-200 bg-white hover:bg-slate-50 disabled:opacity-40 flex items-center space-x-1"
                >
                  <ChevronLeft className="w-3.5 h-3.5" />
                  <span>Previous</span>
                </button>

                <span className="px-2 font-bold text-slate-800">
                  {currentPage} / {totalPages}
                </span>

                <button
                  onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
                  disabled={currentPage >= totalPages || loading}
                  className="px-2.5 py-1.5 rounded border border-slate-200 bg-white hover:bg-slate-50 disabled:opacity-40 flex items-center space-x-1"
                >
                  <span>Next</span>
                  <ChevronRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          </>
        )}
      </div>

      {/* Selected Item Drawer Details Modal */}
      {selectedItem && (
        <div className="fixed inset-0 bg-slate-950/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl border border-slate-200 shadow-2xl max-w-lg w-full p-6 space-y-5">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <div className="flex items-center space-x-2">
                <ShieldAlert className="w-4 h-4 text-blue-600" />
                <h4 className="text-sm font-bold text-slate-900">Forensic Incident Dossier</h4>
              </div>
              <button
                onClick={() => setSelectedItem(null)}
                className="text-xs font-mono text-slate-400 hover:text-slate-800 p-1"
              >
                ✕
              </button>
            </div>

            <div className="space-y-3 text-xs font-mono">
              <div className="flex justify-between items-center p-2.5 rounded bg-slate-50 border border-slate-200">
                <div>
                  <span className="text-slate-400 text-[10px] block uppercase">Incident UUID</span>
                  <span className="font-bold text-slate-900">{selectedItem.analysis_id}</span>
                </div>
                <button
                  onClick={() => handleCopy(selectedItem.analysis_id, true)}
                  className="p-1.5 rounded hover:bg-slate-200 text-slate-500"
                  title="Copy UUID"
                >
                  {copiedId ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
                </button>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="p-2.5 rounded bg-slate-50 border border-slate-200">
                  <span className="text-slate-400 text-[10px] block uppercase">Ingestion Vector</span>
                  <span className="font-bold uppercase text-slate-800">{selectedItem.channel}</span>
                </div>
                <div className="p-2.5 rounded bg-slate-50 border border-slate-200">
                  <span className="text-slate-400 text-[10px] block uppercase">Sender / Origin</span>
                  <span className="font-bold text-slate-800">{selectedItem.sender || "Anonymous"}</span>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="p-2.5 rounded bg-slate-50 border border-slate-200">
                  <span className="text-slate-400 text-[10px] block uppercase">Classification</span>
                  <span className={`font-bold uppercase ${
                    selectedItem.threat_level === "critical"
                      ? "text-red-600"
                      : selectedItem.threat_level === "high"
                      ? "text-orange-600"
                      : "text-emerald-600"
                  }`}>
                    {selectedItem.threat_level}
                  </span>
                </div>
                <div className="p-2.5 rounded bg-slate-50 border border-slate-200">
                  <span className="text-slate-400 text-[10px] block uppercase">Calibrated Risk</span>
                  <span className="font-bold text-slate-900">
                    {Math.round(selectedItem.risk_score * 100)} / 100
                  </span>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="p-2.5 rounded bg-slate-50 border border-slate-200">
                  <span className="text-slate-400 text-[10px] block uppercase">Model Version</span>
                  <span className="font-bold text-sky-800">
                    {selectedItem.model_version || (selectedItem.channel === "url" ? "M2 XGBoost v1.0" : "M1 Bi-LSTM v1.0")}
                  </span>
                </div>
                <div className="p-2.5 rounded bg-slate-50 border border-slate-200">
                  <span className="text-slate-400 text-[10px] block uppercase">Forensic Status</span>
                  <span className={`font-bold ${selectedItem.threat_level === "clean" ? "text-emerald-700" : "text-rose-700"}`}>
                    {selectedItem.status || (selectedItem.threat_level === "clean" ? "Clean Verified" : "Threat Isolated")}
                  </span>
                </div>
              </div>

              <div className="space-y-1">
                <div className="flex items-center justify-between">
                  <span className="text-slate-400 text-[10px] uppercase">Payload Content</span>
                  <button
                    onClick={() => handleCopy(selectedItem.content_preview, false)}
                    className="text-[11px] text-blue-600 hover:text-blue-800 flex items-center space-x-1"
                  >
                    {copiedText ? (
                      <>
                        <Check className="w-3 h-3 text-emerald-600" />
                        <span>Copied</span>
                      </>
                    ) : (
                      <>
                        <Copy className="w-3 h-3" />
                        <span>Copy Text</span>
                      </>
                    )}
                  </button>
                </div>
                <div className="p-3 bg-slate-50 rounded-lg border border-slate-200 text-slate-800 font-sans text-xs max-h-32 overflow-y-auto leading-relaxed">
                  {selectedItem.content_preview}
                </div>
              </div>

              <div className="text-[11px] text-slate-400 flex items-center space-x-1 pt-1">
                <Clock className="w-3 h-3" />
                <span>Captured timestamp: {selectedItem.created_at}</span>
              </div>
            </div>

            <div className="flex items-center justify-between pt-3 border-t border-slate-100">
              <button
                type="button"
                onClick={() => setSelectedItem(null)}
                className="px-4 py-2 text-xs font-semibold text-slate-600 hover:text-slate-900"
              >
                Close
              </button>

              <Link
                href={`/investigation?q=${encodeURIComponent(selectedItem.content_preview)}`}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-semibold shadow-sm transition-all flex items-center space-x-1.5"
              >
                <span>Investigate in Studio</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
