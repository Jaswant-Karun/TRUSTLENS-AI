"use client";

import React from "react";
import { Search, X, RotateCcw } from "lucide-react";

interface SearchFilterBarProps {
  search: string;
  onSearchChange: (value: string) => void;
  searchPlaceholder?: string;
  threatLevel?: string;
  onThreatLevelChange?: (value: string) => void;
  channel?: string;
  onChannelChange?: (value: string) => void;
  onReset?: () => void;
  extraFilters?: React.ReactNode;
}

export function SearchFilterBar({
  search,
  onSearchChange,
  searchPlaceholder = "Search incidents, URLs, senders...",
  threatLevel = "",
  onThreatLevelChange,
  channel = "",
  onChannelChange,
  onReset,
  extraFilters,
}: SearchFilterBarProps) {
  const hasActiveFilters = Boolean(search || threatLevel || channel);

  return (
    <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-subtle mb-5 flex flex-col md:flex-row md:items-center justify-between gap-3">
      {/* Search Bar */}
      <div className="relative flex-1 max-w-md">
        <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
        <input
          type="text"
          value={search}
          onChange={(e) => onSearchChange(e.target.value)}
          placeholder={searchPlaceholder}
          className="w-full pl-9 pr-8 py-2 bg-slate-50 border border-slate-200 rounded-lg text-xs font-medium text-slate-800 placeholder-slate-400 focus:bg-white focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500/30 transition-all"
        />
        {search && (
          <button
            onClick={() => onSearchChange("")}
            className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 p-0.5 rounded"
          >
            <X className="w-3.5 h-3.5" />
          </button>
        )}
      </div>

      {/* Filter Dropdowns */}
      <div className="flex flex-wrap items-center gap-2.5">
        {onThreatLevelChange && (
          <select
            value={threatLevel}
            onChange={(e) => onThreatLevelChange(e.target.value)}
            className="px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-xs font-medium text-slate-700 focus:bg-white focus:outline-none focus:border-blue-500 transition-colors"
          >
            <option value="">All Threat Levels</option>
            <option value="critical">Critical Risk</option>
            <option value="high">High Risk</option>
            <option value="medium">Medium Risk</option>
            <option value="clean">Clean / Safe</option>
          </select>
        )}

        {onChannelChange && (
          <select
            value={channel}
            onChange={(e) => onChannelChange(e.target.value)}
            className="px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-xs font-medium text-slate-700 focus:bg-white focus:outline-none focus:border-blue-500 transition-colors"
          >
            <option value="">All Vectors / Channels</option>
            <option value="sms">SMS</option>
            <option value="whatsapp">WhatsApp</option>
            <option value="email">Email</option>
            <option value="url">URL</option>
            <option value="screenshot">Screenshot (OCR)</option>
          </select>
        )}

        {extraFilters}

        {hasActiveFilters && onReset && (
          <button
            onClick={onReset}
            className="inline-flex items-center space-x-1 px-2.5 py-2 text-xs font-medium text-slate-500 hover:text-slate-800 hover:bg-slate-100 rounded-lg transition-colors"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Reset</span>
          </button>
        )}
      </div>
    </div>
  );
}

