"use client";

import React, { useState } from "react";
import {
  Search,
  RotateCcw,
  RotateCw,
  Plus,
  Minus,
  Maximize2,
  Minimize2,
  RefreshCw,
  Map as MapIcon,
  Filter,
  Layers,
  X,
} from "lucide-react";
import { NodeType } from "./types";

interface GraphToolbarProps {
  searchQuery: string;
  onSearchChange: (q: string) => void;
  onZoomIn: () => void;
  onZoomOut: () => void;
  onFitScreen: () => void;
  onResetLayout: () => void;
  showMinimap: boolean;
  onToggleMinimap: () => void;
  selectedTypes: Set<NodeType>;
  onToggleType: (type: NodeType) => void;
  syncStatus?: string;
}

export function GraphToolbar({
  searchQuery,
  onSearchChange,
  onZoomIn,
  onZoomOut,
  onFitScreen,
  onResetLayout,
  showMinimap,
  onToggleMinimap,
  selectedTypes,
  onToggleType,
  syncStatus = "All changes saved",
}: GraphToolbarProps) {
  const [filterOpen, setFilterOpen] = useState(false);

  const filterOptions: { type: NodeType; label: string; color: string }[] = [
    { type: "message", label: "Messages", color: "bg-sky-500" },
    { type: "url", label: "Phishing URLs", color: "bg-amber-500" },
    { type: "domain", label: "Domains", color: "bg-emerald-500" },
    { type: "ip", label: "IP Addresses", color: "bg-pink-500" },
    { type: "tactic", label: "Tactics", color: "bg-purple-500" },
    { type: "campaign_cluster", label: "Campaigns", color: "bg-orange-500" },
    { type: "threat_indicator", label: "IOC Indicators", color: "bg-yellow-500" },
    { type: "user_report", label: "Community Reports", color: "bg-cyan-500" },
  ];

  return (
    <div className="absolute top-4 left-4 z-30 flex items-center space-x-2 select-none">
      {/* Search Input */}
      <div className="relative flex items-center bg-[#252D38]/90 backdrop-blur-md border border-[#3A4553] rounded-md h-8 px-2 shadow-xl">
        <Search className="w-3.5 h-3.5 text-slate-400 mr-2" />
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => onSearchChange(e.target.value)}
          placeholder="Filter nodes..."
          className="bg-transparent text-xs text-slate-200 placeholder-slate-400 focus:outline-none w-28 md:w-36 font-sans"
        />
        {searchQuery && (
          <button onClick={() => onSearchChange("")} className="text-slate-400 hover:text-white">
            <X className="w-3 h-3" />
          </button>
        )}
      </div>

      {/* Undo / Redo */}
      <div className="flex items-center bg-[#252D38]/90 backdrop-blur-md border border-[#3A4553] rounded-md h-8 px-1 shadow-xl">
        <button
          onClick={onResetLayout}
          title="Reset Layout"
          className="p-1.5 text-slate-400 hover:text-white hover:bg-[#181E28] rounded"
        >
          <RotateCcw className="w-3.5 h-3.5" />
        </button>
        <button
          disabled
          title="Redo (Clean state)"
          className="p-1.5 text-slate-600 rounded cursor-not-allowed"
        >
          <RotateCw className="w-3.5 h-3.5" />
        </button>
      </div>

      {/* Zoom & Screen Controls */}
      <div className="flex items-center bg-[#252D38]/90 backdrop-blur-md border border-[#3A4553] rounded-md h-8 px-1 shadow-xl space-x-0.5">
        <button
          onClick={onZoomIn}
          title="Zoom In"
          className="p-1.5 text-slate-400 hover:text-white hover:bg-[#181E28] rounded"
        >
          <Plus className="w-3.5 h-3.5" />
        </button>
        <button
          onClick={onZoomOut}
          title="Zoom Out"
          className="p-1.5 text-slate-400 hover:text-white hover:bg-[#181E28] rounded"
        >
          <Minus className="w-3.5 h-3.5" />
        </button>
        <button
          onClick={onFitScreen}
          title="Fit to Screen"
          className="p-1.5 text-slate-400 hover:text-white hover:bg-[#181E28] rounded"
        >
          <Maximize2 className="w-3.5 h-3.5" />
        </button>
      </div>

      {/* Minimap & Filter Toggles */}
      <div className="flex items-center bg-[#252D38]/90 backdrop-blur-md border border-[#3A4553] rounded-md h-8 px-1 shadow-xl space-x-0.5">
        <button
          onClick={onToggleMinimap}
          title="Toggle Bird's-Eye Minimap"
          className={`p-1.5 rounded transition-colors ${
            showMinimap ? "text-cyan-400 bg-[#181E28]" : "text-slate-400 hover:text-white"
          }`}
        >
          <MapIcon className="w-3.5 h-3.5" />
        </button>

        <div className="relative">
          <button
            onClick={() => setFilterOpen(!filterOpen)}
            title="Filter Object Types"
            className={`p-1.5 rounded transition-colors ${
              filterOpen ? "text-cyan-400 bg-[#181E28]" : "text-slate-400 hover:text-white"
            }`}
          >
            <Filter className="w-3.5 h-3.5" />
          </button>

          {/* Filter Popover */}
          {filterOpen && (
            <div
              className="absolute left-0 mt-2 w-52 bg-[#252D38] border border-[#3A4553] rounded-md shadow-2xl p-2.5 z-40 text-xs"
              onMouseLeave={() => setFilterOpen(false)}
            >
              <div className="font-semibold text-white mb-2 pb-1 border-b border-[#3A4553] flex items-center justify-between">
                <span>Object Type Filter</span>
                <span className="text-[10px] text-slate-400">{selectedTypes.size} Active</span>
              </div>
              <div className="space-y-1.5">
                {filterOptions.map((opt) => {
                  const isChecked = selectedTypes.has(opt.type);
                  return (
                    <label
                      key={opt.type}
                      className="flex items-center space-x-2 text-slate-300 hover:text-white cursor-pointer select-none py-0.5"
                    >
                      <input
                        type="checkbox"
                        checked={isChecked}
                        onChange={() => onToggleType(opt.type)}
                        className="rounded border-[#3A4553] text-blue-600 focus:ring-0 bg-[#181E28]"
                      />
                      <span className={`w-2 h-2 rounded-full ${opt.color}`}></span>
                      <span>{opt.label}</span>
                    </label>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Sync Status Badge (ThreatQ style) */}
      <div className="hidden lg:flex items-center space-x-1.5 px-2.5 py-1 bg-[#252D38]/80 backdrop-blur-md border border-[#3A4553] rounded-md text-[11px] text-slate-300 font-mono shadow-xl">
        <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
        <span>{syncStatus}</span>
      </div>
    </div>
  );
}
