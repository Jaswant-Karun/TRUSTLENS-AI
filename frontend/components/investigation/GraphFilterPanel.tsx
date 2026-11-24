"use client";

import React from "react";
import { Filter, X, Check, RotateCcw } from "lucide-react";
import { NodeType } from "./types";

interface FilterOption {
  type: NodeType;
  label: string;
  color: string;
  badgeBg: string;
}

export const GRAPH_FILTER_OPTIONS: FilterOption[] = [
  { type: "message", label: "Messages (SMS/WhatsApp)", color: "bg-sky-500", badgeBg: "border-sky-500/40 text-sky-400" },
  { type: "url", label: "Phishing URLs", color: "bg-amber-500", badgeBg: "border-amber-500/40 text-amber-400" },
  { type: "domain", label: "Domains & FQDNs", color: "bg-emerald-500", badgeBg: "border-emerald-500/40 text-emerald-400" },
  { type: "ip", label: "IP Addresses (C2)", color: "bg-pink-500", badgeBg: "border-pink-500/40 text-pink-400" },
  { type: "scam_category", label: "Scam Categories", color: "bg-red-500", badgeBg: "border-red-500/40 text-red-400" },
  { type: "tactic", label: "Social Engineering Tactics", color: "bg-purple-500", badgeBg: "border-purple-500/40 text-purple-400" },
  { type: "campaign_cluster", label: "Campaign Hubs", color: "bg-orange-500", badgeBg: "border-orange-500/40 text-orange-400" },
  { type: "threat_indicator", label: "Technical IOCs (Phone/UPI)", color: "bg-yellow-500", badgeBg: "border-yellow-500/40 text-yellow-400" },
  { type: "user_report", label: "Community Reports", color: "bg-cyan-500", badgeBg: "border-cyan-500/40 text-cyan-400" },
  { type: "source_reference", label: "Source References (CERT-In)", color: "bg-slate-400", badgeBg: "border-slate-500/40 text-slate-400" },
];

interface GraphFilterPanelProps {
  selectedTypes: Set<NodeType>;
  onToggleType: (type: NodeType) => void;
  onSelectAll: () => void;
  onClearAll: () => void;
  isOpen: boolean;
  onToggleOpen: () => void;
}

export function GraphFilterPanel({
  selectedTypes,
  onToggleType,
  onSelectAll,
  onClearAll,
  isOpen,
  onToggleOpen,
}: GraphFilterPanelProps) {
  return (
    <div className="relative">
      <button
        onClick={onToggleOpen}
        title="Filter Object Types"
        className={`p-1.5 rounded transition-colors flex items-center space-x-1 ${
          isOpen ? "text-cyan-400 bg-[#181E28]" : "text-slate-400 hover:text-white"
        }`}
      >
        <Filter className="w-3.5 h-3.5" />
      </button>

      {isOpen && (
        <div
          className="absolute left-0 mt-2 w-64 bg-[#252D38] border border-[#3A4553] rounded-md shadow-2xl p-3 z-40 text-xs animate-in fade-in zoom-in-95 duration-100"
          onMouseLeave={onToggleOpen}
        >
          <div className="font-semibold text-white mb-2.5 pb-1.5 border-b border-[#3A4553] flex items-center justify-between">
            <span className="flex items-center space-x-1.5">
              <Filter className="w-3.5 h-3.5 text-cyan-400" />
              <span>Object Type Filters</span>
            </span>
            <span className="text-[10px] font-mono text-cyan-400 bg-cyan-950/80 px-1.5 py-0.5 rounded border border-cyan-800/40">
              {selectedTypes.size} / {GRAPH_FILTER_OPTIONS.length} Active
            </span>
          </div>

          <div className="flex items-center justify-between mb-2 text-[10px] font-mono">
            <button
              onClick={onSelectAll}
              className="text-cyan-400 hover:text-cyan-300 font-semibold"
            >
              Select All
            </button>
            <span className="text-slate-500">|</span>
            <button
              onClick={onClearAll}
              className="text-slate-400 hover:text-rose-400 font-semibold"
            >
              Clear All
            </button>
          </div>

          <div className="space-y-1.5 max-h-60 overflow-y-auto pr-1">
            {GRAPH_FILTER_OPTIONS.map((opt) => {
              const isChecked = selectedTypes.has(opt.type);
              return (
                <label
                  key={opt.type}
                  className="flex items-center space-x-2 text-slate-300 hover:text-white cursor-pointer select-none py-1 px-1.5 rounded hover:bg-[#181E28] transition-colors"
                >
                  <input
                    type="checkbox"
                    checked={isChecked}
                    onChange={() => onToggleType(opt.type)}
                    className="rounded border-[#3A4553] text-blue-600 focus:ring-0 bg-[#181E28]"
                  />
                  <span className={`w-2 h-2 rounded-full ${opt.color} shrink-0`}></span>
                  <span className="text-xs truncate">{opt.label}</span>
                </label>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
