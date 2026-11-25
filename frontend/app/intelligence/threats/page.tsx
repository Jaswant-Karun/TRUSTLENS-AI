"use client";

import React, { useState } from "react";
import {
  PageHeader,
  ThreatTrendChart,
  SeverityDistributionChart,
  DataTable,
  Column,
  SearchFilterBar,
} from "@/components/ui";
import { AlertTriangle, Globe, Server, Hash, ShieldAlert, Copy, Check } from "lucide-react";

interface ThreatIndicator {
  type: "domain" | "ip" | "sender_id" | "brand";
  indicator: string;
  threatLevel: "critical" | "high" | "medium";
  associatedCampaign: string;
  firstSeen: string;
  hits: number;
}

const INITIAL_INDICATORS: ThreatIndicator[] = [
  {
    type: "ip",
    indicator: "192.168.1.50",
    threatLevel: "critical",
    associatedCampaign: "Cluster #0: SBI Netbanking Clone",
    firstSeen: "24-Nov-2026",
    hits: 142,
  },
  {
    type: "domain",
    indicator: "secure-login-hdfcbank-account-update.xyz",
    threatLevel: "critical",
    associatedCampaign: "Cluster #2: HDFC KYC Trap",
    firstSeen: "22-Nov-2026",
    hits: 89,
  },
  {
    type: "sender_id",
    indicator: "VK-SBIBNK",
    threatLevel: "high",
    associatedCampaign: "Cluster #0: SBI Netbanking Clone",
    firstSeen: "20-Nov-2026",
    hits: 310,
  },
  {
    type: "brand",
    indicator: "State Bank of India (SBI)",
    threatLevel: "high",
    associatedCampaign: "Clusters #0, #14, #22",
    firstSeen: "15-Nov-2026",
    hits: 840,
  },
  {
    type: "ip",
    indicator: "203.0.113.15",
    threatLevel: "critical",
    associatedCampaign: "Cluster #5: Credential Relay",
    firstSeen: "18-Nov-2026",
    hits: 64,
  },
  {
    type: "domain",
    indicator: "electricity-bill-disconnection-alert.top",
    threatLevel: "high",
    associatedCampaign: "Cluster #8: Utility Threat",
    firstSeen: "23-Nov-2026",
    hits: 51,
  },
  {
    type: "sender_id",
    indicator: "AD-POWDIS",
    threatLevel: "medium",
    associatedCampaign: "Cluster #8: Utility Threat",
    firstSeen: "21-Nov-2026",
    hits: 112,
  },
];

export default function ThreatIntelligencePage() {
  const [search, setSearch] = useState("");
  const [threatLevel, setThreatLevel] = useState("");
  const [copiedText, setCopiedText] = useState<string | null>(null);

  const filtered = INITIAL_INDICATORS.filter((item) => {
    const matchSearch =
      !search ||
      item.indicator.toLowerCase().includes(search.toLowerCase()) ||
      item.associatedCampaign.toLowerCase().includes(search.toLowerCase());
    const matchThreat = !threatLevel || item.threatLevel === threatLevel;
    return matchSearch && matchThreat;
  });

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedText(text);
    setTimeout(() => setCopiedText(null), 2000);
  };

  const columns: Column<ThreatIndicator>[] = [
    {
      header: "Type",
      accessorKey: "type",
      cell: (row) => {
        const icons = {
          domain: <Globe className="w-3.5 h-3.5 text-cyan-600" />,
          ip: <Server className="w-3.5 h-3.5 text-rose-600" />,
          sender_id: <Hash className="w-3.5 h-3.5 text-amber-600" />,
          brand: <ShieldAlert className="w-3.5 h-3.5 text-purple-600" />,
        };
        return (
          <span className="flex items-center space-x-1.5 font-mono text-xs uppercase text-white">
            {icons[row.type]}
            <span>{row.type}</span>
          </span>
        );
      },
    },
    {
      header: "Indicator (IOC)",
      accessorKey: "indicator",
      cell: (row) => (
        <div className="flex items-center space-x-2 font-mono text-xs font-bold text-white">
          <span>{row.indicator}</span>
          <button
            onClick={() => handleCopy(row.indicator)}
            aria-label="Copy indicator"
            className="p-1 text-[#A1A1AA] hover:text-white rounded hover:bg-[#170A12]"
          >
            {copiedText === row.indicator ? (
              <Check className="w-3 h-3 text-[#00D68F]" />
            ) : (
              <Copy className="w-3 h-3" />
            )}
          </button>
        </div>
      ),
    },
    {
      header: "Severity",
      accessorKey: "threatLevel",
      cell: (row) => {
        const styles = {
          critical: "bg-[#FF174F]/15 text-[#FF174F] border-[#FF174F]/50",
          high: "bg-[#FF3D70]/15 text-[#FF3D70] border-[#FF3D70]/40",
          medium: "bg-[#FFB020]/15 text-[#FFB020] border-[#FFB020]/40",
        };
        return (
          <span
            className={`px-2 py-0.5 rounded-full text-[10px] font-mono font-semibold uppercase border ${styles[row.threatLevel]}`}
          >
            {row.threatLevel}
          </span>
        );
      },
    },
    {
      header: "Associated Campaign",
      accessorKey: "associatedCampaign",
      className: "text-xs text-[#A1A1AA] font-medium",
    },
    {
      header: "Observed Hits",
      accessorKey: "hits",
      align: "right",
      className: "font-mono font-bold text-white text-xs",
    },
  ];

  return (
    <div className="space-y-6">
      <PageHeader
        title="Threat Indicators & IOC Intelligence"
        description="Curated indicators of compromise extracted across analyzed deceptive communications, phishing domains, and bulk SMS sender headers."
        badge={{ text: "Active IOC Feed", variant: "rose" }}
      />

      {/* Real-time Threat Distribution & Trend Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ThreatTrendChart />
        <SeverityDistributionChart />
      </div>

      {/* IOC Search & Table Card */}
      <div className="cyber-panel p-6 space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-[#481326]">
          <div className="flex items-center space-x-2">
            <AlertTriangle className="w-4 h-4 text-[#FF174F]" />
            <h3 className="text-sm font-mono font-bold uppercase text-white">
              Extracted Threat Indicators of Compromise
            </h3>
          </div>
          <span className="text-xs font-mono text-[#A1A1AA]">{filtered.length} Indicators Listed</span>
        </div>

        <SearchFilterBar
          search={search}
          onSearchChange={setSearch}
          threatLevel={threatLevel}
          onThreatLevelChange={setThreatLevel}
          onReset={() => {
            setSearch("");
            setThreatLevel("");
          }}
        />

        <DataTable
          columns={columns}
          data={filtered}
          emptyTitle="No threat indicators found"
          emptyDescription="Try clearing your search filters."
        />
      </div>
    </div>
  );
}
