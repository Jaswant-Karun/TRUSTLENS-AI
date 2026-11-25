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
    <div className="cyber-panel p-4 mb-5 flex flex-col md:flex-row md:items-center justify-between gap-3">
      {/* Search Bar */}
      <div className="relative flex-1 max-w-md">
        <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-[#A1A1AA]" />
        <input
          type="text"
          value={search}
          onChange={(e) => onSearchChange(e.target.value)}
          placeholder={searchPlaceholder}
          className="cyber-input pl-9 pr-8"
        />
        {search && (
          <button
            onClick={() => onSearchChange("")}
            aria-label="Clear search"
            className="absolute right-2.5 top-1/2 -translate-y-1/2 text-[#A1A1AA] hover:text-white p-0.5 rounded"
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
            className="cyber-select"
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
            className="cyber-select"
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
            className="inline-flex items-center space-x-1 px-2.5 py-2 text-xs font-mono text-[#A1A1AA] hover:text-white hover:bg-[#170A12] rounded-lg transition-colors"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Reset</span>
          </button>
        )}
      </div>
    </div>
  );
}
