"use client";

import React, { useState } from "react";
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
  CheckCircle2,
  AlertTriangle,
  Compass,
} from "lucide-react";
import { TopNavigation } from "@/components/investigation/TopNavigation";
import { CreateInvestigationModal } from "@/components/investigation/CreateInvestigationModal";

interface InvestigationSummary {
  id: string;
  title: string;
  description: string;
  severity: "critical" | "high" | "medium" | "low";
  status: "Active" | "Closed" | "Under Review";
  objectsCount: number;
  tasksCount: number;
  author: string;
  updatedAt: string;
  targetEntity: string;
  tags: string[];
}

export default function InvestigationsDirectoryPage() {
  const [search, setSearch] = useState("");
  const [severityFilter, setSeverityFilter] = useState("all");
  const [isCreateOpen, setIsCreateOpen] = useState(false);

  const [investigations, setInvestigations] = useState<InvestigationSummary[]>([
    {
      id: "INV-2026-KYC-11",
      title: "Analysis of Banking KYC Smishing Syndicate #11",
      description:
        "Multilingual SMS campaign targeting State Bank of India account holders with urgent account suspension alerts and credential harvesters.",
      severity: "critical",
      status: "Active",
      objectsCount: 139,
      tasksCount: 3,
      author: "Senior Analyst (RS)",
      updatedAt: "10 mins ago",
      targetEntity: "State Bank of India (SBI)",
      tags: ["sbi_kyc", "smishing", "m1_bilstm", "m2_xgboost"],
    },
    {
      id: "INV-2026-POWER-13",
      title: "Operation State Electricity Board Disconnection Fraud",
      description:
        "Widespread extortion pretexts threatening immediate 9:30 PM power cutoff over bogus unpaid utility invoices.",
      severity: "high",
      status: "Active",
      objectsCount: 84,
      tasksCount: 2,
      author: "SOC Lead (TK)",
      updatedAt: "45 mins ago",
      targetEntity: "State Electricity Boards (BSES, UPPCL)",
      tags: ["utility_fraud", "urgency", "phone_iocs"],
    },
    {
      id: "INV-2026-JOB-24",
      title: "Part-Time Telegram Video Liking Syndicate",
      description:
        "Recruitment scam promising daily ₹5,000 earnings for rating videos, escalating into high-value crypto deposit demands.",
      severity: "critical",
      status: "Active",
      objectsCount: 192,
      tasksCount: 4,
      author: "Analyst (RS)",
      updatedAt: "2 hours ago",
      targetEntity: "Social / Video Portals",
      tags: ["job_fraud", "telegram", "crypto_extraction"],
    },
    {
      id: "INV-2026-COURIER-07",
      title: "Customs Parcel & Illegal Narcotics Impersonation",
      description:
        "Automated IVR calls alleging seized courier parcels containing passports and contraband; spoofing Mumbai Police DCP.",
      severity: "high",
      status: "Under Review",
      objectsCount: 67,
      tasksCount: 1,
      author: "Security Officer (AK)",
      updatedAt: "4 hours ago",
      targetEntity: "FedEx / Mumbai Police Spoof",
      tags: ["ivr_vishing", "authority_spoofing"],
    },
  ]);

  const filtered = investigations.filter((inv) => {
    if (severityFilter !== "all" && inv.severity !== severityFilter) return false;
    if (
      search &&
      !inv.title.toLowerCase().includes(search.toLowerCase()) &&
      !inv.targetEntity.toLowerCase().includes(search.toLowerCase())
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
              <h1 className="text-xl font-bold text-white tracking-wide font-sans">
                Active Cyber Threat Investigations
              </h1>
            </div>
            <p className="text-xs text-slate-400 mt-1">
              ThreatQ-inspired investigation workspace directory. Select an incident to launch the interactive relationship graph and timeline correlation.
            </p>
          </div>

          <div className="flex items-center space-x-3">
            <button
              onClick={() => setIsCreateOpen(true)}
              className="h-9 px-4 bg-blue-600 hover:bg-blue-500 text-white rounded text-xs font-semibold flex items-center space-x-2 shadow-lg shadow-blue-600/30 transition-all border border-blue-400/40"
            >
              <Plus className="w-4 h-4" />
              <span>Create Investigation</span>
            </button>
          </div>
        </div>

        {/* Search & Filter Toolbar */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-3 bg-[#252D38] p-3 rounded-lg border border-[#3A4553]">
          <div className="relative w-full sm:w-80">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search by title, target, or tag..."
              className="w-full bg-[#181E28] border border-[#3A4553] rounded pl-9 pr-3 py-1.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-400"
            />
          </div>

          <div className="flex items-center space-x-2 w-full sm:w-auto">
            <span className="text-[11px] font-mono text-slate-400 uppercase">Severity:</span>
            <select
              value={severityFilter}
              onChange={(e) => setSeverityFilter(e.target.value)}
              className="bg-[#181E28] border border-[#3A4553] rounded px-3 py-1.5 text-xs text-slate-200 focus:outline-none"
            >
              <option value="all">All Severities</option>
              <option value="critical">Critical Threats</option>
              <option value="high">High Risk</option>
              <option value="medium">Medium</option>
            </select>
          </div>
        </div>

        {/* Investigation Dossier Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {filtered.map((inv) => (
            <div
              key={inv.id}
              className="bg-[#252D38] hover:bg-[#202731] border border-[#3A4553] hover:border-cyan-500/50 rounded-lg p-5 flex flex-col justify-between transition-all group shadow-xl"
            >
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-mono font-bold text-cyan-400 bg-cyan-950/80 px-2 py-0.5 rounded border border-cyan-800/40">
                    {inv.id}
                  </span>
                  <span
                    className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase tracking-wider ${
                      inv.severity === "critical"
                        ? "bg-rose-950/80 text-rose-400 border border-rose-800"
                        : inv.severity === "high"
                        ? "bg-amber-950/80 text-amber-400 border border-amber-800"
                        : "bg-slate-800 text-slate-300"
                    }`}
                  >
                    {inv.severity}
                  </span>
                </div>

                <div>
                  <h3 className="text-sm font-bold text-white group-hover:text-cyan-300 transition-colors">
                    {inv.title}
                  </h3>
                  <p className="text-xs text-slate-300 mt-1 line-clamp-2 leading-relaxed">
                    {inv.description}
                  </p>
                </div>

                <div className="grid grid-cols-3 gap-2 py-2 border-y border-[#3A4553]/60 text-center font-mono">
                  <div>
                    <span className="text-[9px] text-slate-400 uppercase">Target</span>
                    <p className="text-[11px] text-white truncate font-medium">{inv.targetEntity}</p>
                  </div>
                  <div>
                    <span className="text-[9px] text-slate-400 uppercase">Objects</span>
                    <p className="text-[11px] text-cyan-400 font-bold">{inv.objectsCount}</p>
                  </div>
                  <div>
                    <span className="text-[9px] text-slate-400 uppercase">Updated</span>
                    <p className="text-[11px] text-slate-300">{inv.updatedAt}</p>
                  </div>
                </div>

                <div className="flex flex-wrap gap-1.5">
                  {inv.tags.map((t) => (
                    <span
                      key={t}
                      className="px-2 py-0.5 rounded bg-[#181E28] border border-[#3A4553] text-[9px] font-mono text-slate-400"
                    >
                      #{t}
                    </span>
                  ))}
                </div>
              </div>

              {/* Action Button */}
              <div className="mt-4 pt-3 border-t border-[#3A4553]/60 flex items-center justify-between">
                <span className="text-[10px] font-mono text-slate-400">
                  Lead: {inv.author}
                </span>
                <Link
                  href={`/investigations/${inv.id}`}
                  className="px-3 py-1.5 bg-blue-600/90 hover:bg-blue-600 text-white rounded text-xs font-semibold flex items-center space-x-1.5 shadow-md shadow-blue-600/20 group-hover:shadow-blue-600/40 transition-all border border-blue-400/30"
                >
                  <span>Launch Workspace</span>
                  <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 transition-transform" />
                </Link>
              </div>
            </div>
          ))}
        </div>
      </main>

      {/* Create Modal */}
      <CreateInvestigationModal
        isOpen={isCreateOpen}
        onClose={() => setIsCreateOpen(false)}
        onSubmit={(data) => {
          const newDossier: InvestigationSummary = {
            id: `INV-2026-${Date.now().toString().slice(-4)}`,
            title: data.title,
            description: data.description,
            severity: data.severity,
            status: "Active",
            objectsCount: 12,
            tasksCount: 1,
            author: "Senior Analyst (RS)",
            updatedAt: "Just now",
            targetEntity: data.targetEntity,
            tags: data.tags,
          };
          setInvestigations([newDossier, ...investigations]);
        }}
      />
    </div>
  );
}
