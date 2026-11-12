"use client";

import React, { useState, useMemo } from "react";
import { ListFilter, ShieldAlert, ShieldCheck, AlertTriangle } from "lucide-react";
import { DataTable, Column } from "./ui/DataTable";
import { SearchFilterBar } from "./ui/SearchFilterBar";

interface Incident {
  time: string;
  channel: string;
  sender: string;
  preview: string;
  classification: string;
  severity: "critical" | "high" | "medium" | "clean";
  action: string;
}

const INITIAL_INCIDENTS: Incident[] = [
  {
    time: "22:14:02",
    channel: "SMS",
    sender: "VK-SBIBNK",
    preview: "Aapka SBI khata turant band ho jayega. Urgent verify karein...",
    classification: "Smishing / Banking",
    severity: "critical",
    action: "Blocked",
  },
  {
    time: "22:11:45",
    channel: "URL",
    sender: "Web Request",
    preview: "http://203.0.113.15/secure-login-portal/auth.php",
    classification: "Credential Phishing",
    severity: "critical",
    action: "Blocked",
  },
  {
    time: "22:08:19",
    channel: "WhatsApp",
    sender: "+91 98402 11928",
    preview: "Earn 5000 daily part-time job from home! Complete simple YouTube tasks...",
    classification: "Fake Employment Scam",
    severity: "high",
    action: "Flagged",
  },
  {
    time: "22:04:33",
    channel: "Email",
    sender: "billing@hdfc-updates-kyc.top",
    preview: "Notice: Your KYC renewal period has lapsed. Re-enter credentials...",
    classification: "Phishing Lure",
    severity: "high",
    action: "Quarantined",
  },
  {
    time: "21:58:12",
    channel: "SMS",
    sender: "AD-HDFCBK",
    preview: "Your a/c XXX1234 is credited with INR 5,000.00 on 12-Nov-2026. Avail Bal: INR 45,210.50.",
    classification: "Legitimate Transaction",
    severity: "clean",
    action: "Allowed",
  },
  {
    time: "21:42:09",
    channel: "SMS",
    sender: "CP-POWDIS",
    preview: "Dear customer your electricity power will be disconnected tonight 9:30pm...",
    classification: "Extortion / Utility Threat",
    severity: "critical",
    action: "Blocked",
  },
];

export default function IncidentFeed({ id }: { id?: string }) {
  const [search, setSearch] = useState("");
  const [threatLevel, setThreatLevel] = useState("");
  const [channel, setChannel] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 5;

  const filteredData = useMemo(() => {
    return INITIAL_INCIDENTS.filter((item) => {
      const matchSearch =
        !search ||
        item.preview.toLowerCase().includes(search.toLowerCase()) ||
        item.sender.toLowerCase().includes(search.toLowerCase()) ||
        item.classification.toLowerCase().includes(search.toLowerCase());

      const matchThreat = !threatLevel || item.severity === threatLevel;
      const matchChannel = !channel || item.channel.toLowerCase() === channel.toLowerCase();

      return matchSearch && matchThreat && matchChannel;
    });
  }, [search, threatLevel, channel]);

  const totalPages = Math.ceil(filteredData.length / pageSize) || 1;
  const paginatedData = filteredData.slice((currentPage - 1) * pageSize, currentPage * pageSize);

  const columns: Column<Incident>[] = [
    {
      header: "Timestamp",
      accessorKey: "time",
      className: "font-mono text-slate-500",
    },
    {
      header: "Vector",
      accessorKey: "channel",
      cell: (row) => (
        <span className="font-semibold px-2 py-0.5 rounded bg-slate-100 text-slate-700 font-mono text-[11px] border border-slate-200">
          {row.channel}
        </span>
      ),
    },
    {
      header: "Sender / Source",
      accessorKey: "sender",
      className: "font-mono font-medium text-slate-800",
    },
    {
      header: "Payload Excerpt",
      accessorKey: "preview",
      cell: (row) => (
        <span className="text-slate-600 truncate max-w-xs block font-mono text-xs">
          {row.preview}
        </span>
      ),
    },
    {
      header: "Classification",
      accessorKey: "classification",
      className: "font-medium text-slate-900",
    },
    {
      header: "Severity",
      accessorKey: "severity",
      cell: (row) => {
        const severityMap = {
          critical: "bg-red-50 text-red-700 border-red-200",
          high: "bg-orange-50 text-orange-700 border-orange-200",
          medium: "bg-amber-50 text-amber-700 border-amber-200",
          clean: "bg-emerald-50 text-emerald-700 border-emerald-200",
        };
        return (
          <span
            className={`px-2 py-0.5 rounded-full text-[10px] font-mono font-semibold uppercase border ${
              severityMap[row.severity] || "bg-slate-100 text-slate-700 border-slate-200"
            }`}
          >
            {row.severity}
          </span>
        );
      },
    },
    {
      header: "Action",
      accessorKey: "action",
      align: "right",
      cell: (row) => (
        <span className="font-mono text-[11px] font-semibold text-slate-700">
          {row.action}
        </span>
      ),
    },
  ];

  return (
    <div id={id} className="mb-6">
      <div className="flex items-center justify-between mb-3">
        <div>
          <h2 className="text-base font-bold text-slate-900 flex items-center space-x-2">
            <ListFilter className="w-4 h-4 text-slate-500" />
            <span>Recent Incident Telemetry & Threat Ingestion Log</span>
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Audit trail of multi-channel digital communications decomposed and categorized by TRUSTLENS AI.
          </p>
        </div>
      </div>

      <SearchFilterBar
        search={search}
        onSearchChange={(v) => {
          setSearch(v);
          setCurrentPage(1);
        }}
        threatLevel={threatLevel}
        onThreatLevelChange={(v) => {
          setThreatLevel(v);
          setCurrentPage(1);
        }}
        channel={channel}
        onChannelChange={(v) => {
          setChannel(v);
          setCurrentPage(1);
        }}
        onReset={() => {
          setSearch("");
          setThreatLevel("");
          setChannel("");
          setCurrentPage(1);
        }}
      />

      <DataTable
        columns={columns}
        data={paginatedData}
        emptyTitle="No matching incidents"
        emptyDescription="Try adjusting your search terms or filter selections."
        pagination={{
          currentPage,
          totalPages,
          totalItems: filteredData.length,
          onPageChange: (p) => setCurrentPage(p),
        }}
      />
    </div>
  );
}
