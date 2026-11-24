"use client";

import React, { useState } from "react";
import { InvestigationData } from "./types";
import { ChevronDown, ChevronRight, ShieldAlert, Tag, Database, Layers } from "lucide-react";

interface InvestigationHeaderProps {
  investigation: InvestigationData;
}

export function InvestigationHeader({ investigation }: InvestigationHeaderProps) {
  const [descOpen, setDescOpen] = useState(true);
  const [sourcesOpen, setSourcesOpen] = useState(true);
  const [tagsOpen, setTagsOpen] = useState(true);
  const [attributesOpen, setAttributesOpen] = useState(true);

  return (
    <div className="font-sans text-xs divide-y divide-[#3A4553]/70">
      {/* 1. Top Stat Matrix (ThreatQ exact format: OBJECTS | TASKS | COMMENTS) */}
      <div className="p-4 grid grid-cols-3 gap-2 text-center bg-[#202731]">
        <div>
          <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider">Objects</span>
          <p className="text-base font-bold text-white font-mono mt-0.5">{investigation.objectsCount}</p>
        </div>
        <div>
          <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider">Tasks</span>
          <p className="text-base font-bold text-white font-mono mt-0.5">{investigation.tasksCount}</p>
        </div>
        <div>
          <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider">Comments</span>
          <p className="text-base font-bold text-white font-mono mt-0.5">{investigation.commentsCount}</p>
        </div>
      </div>

      {/* 2. Severity & Visibility */}
      <div className="p-4 grid grid-cols-2 gap-4">
        <div>
          <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider">Severity</span>
          <p className="text-xs font-bold text-rose-400 font-mono mt-0.5">{investigation.severity.toUpperCase()}</p>
        </div>
        <div>
          <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider">Visibility</span>
          <p className="text-xs font-semibold text-slate-200 mt-0.5">{investigation.visibility}</p>
        </div>
      </div>

      {/* 3. Timestamps & Authors */}
      <div className="p-4 space-y-2 text-xs">
        <div>
          <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider">Created</span>
          <p className="text-slate-300 font-mono text-[11px] mt-0.5">
            {investigation.created.date} by {investigation.created.author}
          </p>
        </div>
        <div>
          <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider">Last Modified</span>
          <p className="text-slate-300 font-mono text-[11px] mt-0.5">
            {investigation.lastModified.date} by {investigation.lastModified.author}
          </p>
        </div>
      </div>

      {/* 4. Collapsible: Description */}
      <div className="p-4 space-y-2">
        <button
          onClick={() => setDescOpen(!descOpen)}
          className="flex items-center justify-between w-full font-semibold text-slate-200 uppercase tracking-wider text-[11px]"
        >
          <span>Description</span>
          {descOpen ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronRight className="w-3.5 h-3.5" />}
        </button>
        {descOpen && (
          <p className="text-xs text-slate-300 leading-relaxed font-sans">
            {investigation.description}
          </p>
        )}
      </div>

      {/* 5. Collapsible: Sources */}
      <div className="p-4 space-y-2">
        <button
          onClick={() => setSourcesOpen(!sourcesOpen)}
          className="flex items-center justify-between w-full font-semibold text-slate-200 uppercase tracking-wider text-[11px]"
        >
          <span>Sources ({investigation.sources.length})</span>
          {sourcesOpen ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronRight className="w-3.5 h-3.5" />}
        </button>
        {sourcesOpen && (
          <p className="text-xs text-cyan-400 font-mono">
            {investigation.sources.join(", ")}
          </p>
        )}
      </div>

      {/* 6. Collapsible: Tags */}
      <div className="p-4 space-y-2">
        <button
          onClick={() => setTagsOpen(!tagsOpen)}
          className="flex items-center justify-between w-full font-semibold text-slate-200 uppercase tracking-wider text-[11px]"
        >
          <span>Tags ({investigation.tags.length})</span>
          {tagsOpen ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronRight className="w-3.5 h-3.5" />}
        </button>
        {tagsOpen && (
          <div className="flex flex-wrap gap-1.5">
            {investigation.tags.map((tag) => (
              <span
                key={tag}
                className="px-2 py-0.5 rounded bg-blue-950/60 border border-blue-800/60 text-blue-300 text-[10px] font-mono"
              >
                #{tag}
              </span>
            ))}
          </div>
        )}
      </div>

      {/* 7. Collapsible: Attributes */}
      <div className="p-4 space-y-2">
        <button
          onClick={() => setAttributesOpen(!attributesOpen)}
          className="flex items-center justify-between w-full font-semibold text-slate-200 uppercase tracking-wider text-[11px]"
        >
          <span>Attributes ({Object.keys(investigation.attributes).length})</span>
          {attributesOpen ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronRight className="w-3.5 h-3.5" />}
        </button>
        {attributesOpen && (
          <div className="bg-[#181E28] rounded border border-[#3A4553] divide-y divide-[#2D3748]">
            {Object.entries(investigation.attributes).map(([k, v]) => (
              <div key={k} className="p-2 flex justify-between font-mono text-[11px]">
                <span className="text-slate-400">{k}:</span>
                <span className="text-white font-medium">{v}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
