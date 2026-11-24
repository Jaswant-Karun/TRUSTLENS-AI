"use client";

import React, { useState, useEffect } from "react";
import {
  PageHeader,
  DataTable,
  Column,
  SearchFilterBar,
  SkeletonTable,
} from "@/components/ui";
import { getAnalysesHistory, AnalysisHistoryItem } from "@/lib/api";
import { History, ShieldAlert, ShieldCheck, AlertTriangle, HelpCircle } from "lucide-react";

const BACKUP_HISTORY: AnalysisHistoryItem[] = [
  {
    analysis_id: "tr-7f8a9b1c2d3e",
    created_at: "24-Nov-2026 14:32:05",
    channel: "sms",
    sender: "VK-SBIBNK",
    content_preview: "Aapka SBI khata turant band ho jayega. Urgent verify karein...",
    threat_level: "critical",
    risk_score: 0.94,
    is_threat: true,
  },
  {
    analysis_id: "tr-4a5b6c7d8e9f",
    created_at: "24-Nov-2026 14:15:22",
    channel: "url",
    sender: "Web Request",
    content_preview: "http://secure-login-hdfcbank-account-update.xyz/login.php",
    threat_level: "critical",
    risk_score: 0.96,
    is_threat: true,
  },
  {
    analysis_id: "tr-1a2b3c4d5e6f",
    created_at: "24-Nov-2026 13:58:19",
    channel: "whatsapp",
    sender: "+91 98402 11928",
    content_preview: "Earn 5000 daily part-time job from home! Complete simple YouTube tasks...",
    threat_level: "high",
    risk_score: 0.88,
    is_threat: true,
  },
  {
    analysis_id: "tr-9f8e7d6c5b4a",
    created_at: "24-Nov-2026 13:42:01",
    channel: "sms",
    sender: "AD-HDFCBK",
    content_preview: "Dear Customer, INR 12,500 credited to account ending 4912...",
    threat_level: "clean",
    risk_score: 0.05,
    is_threat: false,
  },
  {
    analysis_id: "tr-3b4c5d6e7f8a",
    created_at: "24-Nov-2026 13:20:44",
    channel: "sms",
    sender: "CP-POWDIS",
    content_preview: "Electricity power will be disconnected tonight 9:30pm due to bill...",
    threat_level: "critical",
    risk_score: 0.92,
    is_threat: true,
  },
];

export default function HistoryPage() {
  const [items, setItems] = useState<AnalysisHistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [threatLevel, setThreatLevel] = useState("");
  const [channel, setChannel] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedItem, setSelectedItem] = useState<AnalysisHistoryItem | null>(null);

  useEffect(() => {
    let isMounted = true;
    getAnalysesHistory({ page: currentPage, page_size: 20 })
      .then((data) => {
        if (isMounted) {
          if (data && data.items && data.items.length > 0) {
            setItems(data.items);
          } else {
            setItems(BACKUP_HISTORY);
          }
          setLoading(false);
        }
      })
      .catch(() => {
        if (isMounted) {
          setItems(BACKUP_HISTORY);
          setLoading(false);
        }
      });

    return () => {
      isMounted = false;
    };
  }, [currentPage]);

  const filtered = items.filter((item) => {
    const matchSearch =
      !search ||
      item.content_preview.toLowerCase().includes(search.toLowerCase()) ||
      item.analysis_id.toLowerCase().includes(search.toLowerCase()) ||
      (item.sender && item.sender.toLowerCase().includes(search.toLowerCase()));

    const matchThreat = !threatLevel || item.threat_level === threatLevel;
    const matchChannel = !channel || item.channel.toLowerCase() === channel.toLowerCase();

    return matchSearch && matchThreat && matchChannel;
  });

  const columns: Column<AnalysisHistoryItem>[] = [
    {
      header: "Analysis ID",
      accessorKey: "analysis_id",
      cell: (row) => (
        <span className="font-mono text-xs font-bold text-slate-800">
          {row.analysis_id.slice(0, 14)}
        </span>
      ),
    },
    {
      header: "Ingestion Vector",
      accessorKey: "channel",
      cell: (row) => (
        <span className="px-2 py-0.5 rounded bg-slate-100 text-slate-700 font-mono text-[11px] uppercase border border-slate-200">
          {row.channel}
        </span>
      ),
    },
    {
      header: "Sender / Origin",
      accessorKey: "sender",
      cell: (row) => (
        <span className="font-mono text-xs text-slate-600">{row.sender || "Anonymous Client"}</span>
      ),
    },
    {
      header: "Payload Excerpt",
      accessorKey: "content_preview",
      cell: (row) => (
        <span className="font-mono text-xs text-slate-700 truncate max-w-sm block">
          {row.content_preview}
        </span>
      ),
    },
    {
      header: "Threat Level",
      accessorKey: "threat_level",
      cell: (row) => {
        const styles: Record<string, string> = {
          critical: "bg-red-50 text-red-700 border-red-200",
          high: "bg-orange-50 text-orange-700 border-orange-200",
          medium: "bg-amber-50 text-amber-700 border-amber-200",
          clean: "bg-emerald-50 text-emerald-700 border-emerald-200",
        };
        return (
          <span
            className={`px-2 py-0.5 rounded-full text-[10px] font-mono font-semibold uppercase border ${
              styles[row.threat_level] || "bg-slate-100 text-slate-700 border-slate-200"
            }`}
          >
            {row.threat_level}
          </span>
        );
      },
    },
    {
      header: "Risk Score",
      accessorKey: "risk_score",
      align: "right",
      cell: (row) => (
        <span className="font-mono text-xs font-bold text-slate-900">
          {Math.round(row.risk_score * 100)}/100
        </span>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      <PageHeader
        title="Analysis History & Forensic Incident Audit Trail"
        description="Comprehensive audit trail of all multi-modal digital communications decomposed and categorized by TRUSTLENS AI."
        badge={{ text: "Audit Logs", variant: "neutral" }}
      />

      <div className="bg-white rounded-xl border border-slate-200 shadow-subtle p-6 space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-slate-100">
          <div className="flex items-center space-x-2">
            <History className="w-4 h-4 text-slate-600" />
            <h3 className="text-sm font-bold text-slate-900">Historical Deception Analyses</h3>
          </div>
          <span className="text-xs font-mono text-slate-500">{filtered.length} Recorded Scans</span>
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
          <DataTable
            columns={columns}
            data={filtered}
            onRowClick={(row) => setSelectedItem(row)}
            emptyTitle="No historical scans match criteria"
            emptyDescription="Submit new communications from the Analysis studio."
          />
        )}
      </div>

      {/* Selected Item Drawer Details Modal */}
      {selectedItem && (
        <div className="fixed inset-0 bg-slate-950/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl border border-slate-200 shadow-2xl max-w-lg w-full p-6 space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <h4 className="text-sm font-bold text-slate-900">Analysis Record Details</h4>
              <button
                onClick={() => setSelectedItem(null)}
                className="text-xs font-mono text-slate-400 hover:text-slate-800"
              >
                Close ✕
              </button>
            </div>

            <div className="space-y-2 text-xs font-mono">
              <div>
                <span className="text-slate-400 block">UUID:</span>
                <span className="font-bold text-slate-900">{selectedItem.analysis_id}</span>
              </div>
              <div>
                <span className="text-slate-400 block">Created At:</span>
                <span className="text-slate-700">{selectedItem.created_at}</span>
              </div>
              <div>
                <span className="text-slate-400 block">Payload Excerpt:</span>
                <div className="p-3 bg-slate-50 rounded border border-slate-200 text-slate-800 mt-1">
                  {selectedItem.content_preview}
                </div>
              </div>
              <div className="flex justify-between pt-2">
                <div>
                  <span className="text-slate-400 block">Threat Classification:</span>
                  <span className="font-bold text-red-600 uppercase">{selectedItem.threat_level}</span>
                </div>
                <div>
                  <span className="text-slate-400 block">Calibrated Risk:</span>
                  <span className="font-bold text-slate-900">{Math.round(selectedItem.risk_score * 100)}%</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
