"use client";

import React, { useState } from "react";
import {
  RotateCcw,
  RotateCw,
  Plus,
  Minus,
  Maximize2,
  Map as MapIcon,
} from "lucide-react";
import { NodeType } from "./types";
import { InvestigationSearch } from "./InvestigationSearch";
import { GraphFilterPanel, GRAPH_FILTER_OPTIONS } from "./GraphFilterPanel";

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
  onSelectAllTypes?: () => void;
  onClearAllTypes?: () => void;
  syncStatus?: string;
  matchesCount?: number;
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
  onSelectAllTypes,
  onClearAllTypes,
  syncStatus = "All changes saved",
  matchesCount,
}: GraphToolbarProps) {
  const [filterOpen, setFilterOpen] = useState(false);

  const handleSelectAll = () => {
    if (onSelectAllTypes) {
      onSelectAllTypes();
    } else {
      GRAPH_FILTER_OPTIONS.forEach((opt) => {
        if (!selectedTypes.has(opt.type)) onToggleType(opt.type);
      });
    }
  };

  const handleClearAll = () => {
    if (onClearAllTypes) {
      onClearAllTypes();
    } else {
      selectedTypes.forEach((type) => onToggleType(type));
    }
  };

  return (
    <div className="absolute top-4 left-4 z-30 flex items-center space-x-2 select-none">
      {/* 1. Modular Search Input with Keyboard Shortcut '/' and Match Counter */}
      <InvestigationSearch
        value={searchQuery}
        onChange={onSearchChange}
        matchesCount={matchesCount}
        placeholder="Filter nodes..."
      />

      {/* 2. Undo / Redo & Layout Reset */}
      <div className="flex items-center bg-[#252D38]/90 backdrop-blur-md border border-[#3A4553] rounded-md h-8 px-1 shadow-xl">
        <button
          onClick={onResetLayout}
          title="Reset Layout & Positions"
          className="p-1.5 text-slate-400 hover:text-white hover:bg-[#181E28] rounded transition-colors"
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

      {/* 3. Zoom & Viewport Controls */}
      <div className="flex items-center bg-[#252D38]/90 backdrop-blur-md border border-[#3A4553] rounded-md h-8 px-1 shadow-xl space-x-0.5">
        <button
          onClick={onZoomIn}
          title="Zoom In"
          className="p-1.5 text-slate-400 hover:text-white hover:bg-[#181E28] rounded transition-colors"
        >
          <Plus className="w-3.5 h-3.5" />
        </button>
        <button
          onClick={onZoomOut}
          title="Zoom Out"
          className="p-1.5 text-slate-400 hover:text-white hover:bg-[#181E28] rounded transition-colors"
        >
          <Minus className="w-3.5 h-3.5" />
        </button>
        <button
          onClick={onFitScreen}
          title="Fit to Screen"
          className="p-1.5 text-slate-400 hover:text-white hover:bg-[#181E28] rounded transition-colors"
        >
          <Maximize2 className="w-3.5 h-3.5" />
        </button>
      </div>

      {/* 4. Minimap Toggle & Modular Filter Panel */}
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

        {/* Modular GraphFilterPanel */}
        <GraphFilterPanel
          selectedTypes={selectedTypes}
          onToggleType={onToggleType}
          onSelectAll={handleSelectAll}
          onClearAll={handleClearAll}
          isOpen={filterOpen}
          onToggleOpen={() => setFilterOpen(!filterOpen)}
        />
      </div>

      {/* 5. ThreatQ Sync Status Badge */}
      <div className="hidden lg:flex items-center space-x-1.5 px-2.5 py-1 bg-[#252D38]/80 backdrop-blur-md border border-[#3A4553] rounded-md text-[11px] text-slate-300 font-mono shadow-xl">
        <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
        <span>{syncStatus}</span>
      </div>
    </div>
  );
}
