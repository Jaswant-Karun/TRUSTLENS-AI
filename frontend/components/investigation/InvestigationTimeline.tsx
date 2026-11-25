"use client";

import React, { useMemo, useRef } from "react";
import { TimelineEvent } from "./types";
import {
  ChevronUp,
  ChevronDown,
  Clock,
  RefreshCw,
} from "lucide-react";

interface InvestigationTimelineProps {
  events: TimelineEvent[];
  selectedEventId: string | null;
  onSelectEvent: (event: TimelineEvent | null) => void;
  isCollapsed: boolean;
  onToggleCollapse: () => void;
  onRefresh?: () => void;
  loading?: boolean;
  error?: string | null;
}

export function InvestigationTimeline({
  events,
  selectedEventId,
  onSelectEvent,
  isCollapsed,
  onToggleCollapse,
  onRefresh,
  loading = false,
  error = null,
}: InvestigationTimelineProps) {
  const scrollRef = useRef<HTMLDivElement>(null);

  const taskEvents = events.filter((e) => e.track === "tasks");
  const situationEvents = events.filter((e) => e.track === "situation");
  const indicatorEvents = events.filter((e) => e.track === "indicators");

  const dates = useMemo(() => {
    const validDates = events
      .map((e) => new Date(e.timestamp))
      .filter((d) => !isNaN(d.getTime()))
      .sort((a, b) => a.getTime() - b.getTime());
    if (validDates.length === 0) return [];
    const labels = validDates.map((d) =>
      d.toLocaleDateString("en-US", { month: "short", day: "numeric" }).toUpperCase()
    );
    return Array.from(new Set(labels)).slice(0, 8);
  }, [events]);

  if (isCollapsed) {
    return (
      <div className="h-7 bg-[#0F172A] border-t border-[#1E293B] flex items-center justify-between px-4 select-none z-20 text-slate-400 text-xs">
        <div className="flex items-center space-x-2">
          <Clock className="w-3.5 h-3.5 text-cyan-400" />
          <span className="font-mono text-[11px] uppercase tracking-wider text-slate-300">
            Investigation Timeline ({events.length} Events)
          </span>
        </div>
        <button
          onClick={onToggleCollapse}
          title="Expand Investigation Timeline"
          className="flex items-center space-x-1 text-slate-400 hover:text-white"
        >
          <span className="text-[10px] uppercase font-mono">Expand</span>
          <ChevronUp className="w-3.5 h-3.5" />
        </button>
      </div>
    );
  }

  return (
    <div className="h-44 bg-[#1E2631] border-t border-[#3A4553] flex flex-col select-none z-20 shadow-2xl relative">
      {/* 1. Timeline Header Strip */}
      <div className="h-7 bg-[#1A202A] border-b border-[#3A4553] flex items-center justify-between px-4 text-xs font-mono">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2 text-cyan-400 font-semibold">
            <Clock className="w-3.5 h-3.5" />
            <span className="text-[11px] uppercase tracking-wider">Correlation Timeline</span>
          </div>
          <span className="text-slate-500">|</span>
          <div className="flex items-center space-x-3 text-[10px] text-slate-400">
            <span className="flex items-center space-x-1">
              <span className="w-2 h-2 rounded bg-blue-500"></span>
              <span>Tasks & Mitigation</span>
            </span>
            <span className="flex items-center space-x-1">
              <span className="w-2 h-2 rounded bg-cyan-600"></span>
              <span>Situation & Pretexts</span>
            </span>
            <span className="flex items-center space-x-1">
              <span className="w-2 h-2 rounded bg-rose-600"></span>
              <span>Detections & Indicators</span>
            </span>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          {onRefresh && (
            <button
              onClick={onRefresh}
              title="Refresh Timeline"
              className="flex items-center space-x-1 text-slate-400 hover:text-cyan-300"
            >
              <RefreshCw className={`w-3 h-3 ${loading ? "animate-spin" : ""}`} />
              <span className="text-[10px] uppercase font-mono">Refresh</span>
            </button>
          )}
          <button
            onClick={onToggleCollapse}
            title="Collapse Timeline"
            className="flex items-center space-x-1 text-slate-400 hover:text-white"
          >
            <span className="text-[10px] uppercase font-mono">Minimize</span>
            <ChevronDown className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* 2. Horizontal Multi-Track Container */}
      <div className="flex-1 flex overflow-hidden">
        {/* Track Label Sidebar */}
        <div className="w-28 bg-[#181E28] border-r border-[#3A4553] flex flex-col justify-around py-1.5 px-3 text-[9px] font-mono uppercase tracking-wider text-slate-400 shrink-0">
          <div className="text-blue-400 font-bold">Tasks</div>
          <div className="text-cyan-400 font-bold">Situation</div>
          <div className="text-rose-400 font-bold">Selected / IOC</div>
        </div>

        {/* Scrollable Event Tracks & Time Grid */}
        <div
          ref={scrollRef}
          className="flex-1 overflow-x-auto relative flex flex-col justify-between py-2 px-4 cursor-ew-resize"
        >
          {error ? (
            <div className="flex-1 flex items-center justify-center text-xs font-mono text-rose-400">
              {error}
            </div>
          ) : events.length === 0 ? (
            <div className="flex-1 flex items-center justify-center text-xs font-mono text-slate-500 italic">
              No persisted timeline events recorded for this investigation yet.
            </div>
          ) : (
            <>
          {/* Vertical Time Grid Guide Lines */}
          <div className="absolute inset-0 flex justify-between pointer-events-none px-6">
            {dates.map((d) => (
              <div key={d} className="h-full border-r border-[#3A4553]/30 flex flex-col justify-end"></div>
            ))}
          </div>

          {/* Track 1: TASKS */}
          <div className="relative h-6 flex items-center space-x-6 z-10 pl-2">
            {taskEvents.map((ev) => {
              const isSelected = selectedEventId === ev.id;
              return (
                <button
                  key={ev.id}
                  onClick={() => onSelectEvent(isSelected ? null : ev)}
                  className={`h-5 px-2.5 rounded text-[10px] font-mono flex items-center space-x-1.5 transition-all shadow-md shrink-0 ${
                    isSelected
                      ? "bg-blue-600 text-white ring-2 ring-cyan-400 scale-105"
                      : "bg-blue-900/80 hover:bg-blue-800 text-blue-200 border border-blue-700/60"
                  }`}
                >
                  <span className="truncate max-w-[180px]">{ev.title}</span>
                </button>
              );
            })}
          </div>

          {/* Track 2: SITUATION */}
          <div className="relative h-6 flex items-center space-x-5 z-10 pl-8">
            {situationEvents.map((ev) => {
              const isSelected = selectedEventId === ev.id;
              return (
                <button
                  key={ev.id}
                  onClick={() => onSelectEvent(isSelected ? null : ev)}
                  className={`h-5 px-2.5 rounded text-[10px] font-mono flex items-center space-x-1.5 transition-all shadow-md shrink-0 ${
                    isSelected
                      ? "bg-cyan-600 text-white ring-2 ring-cyan-300 scale-105"
                      : "bg-[#1E3A4C] hover:bg-[#254A62] text-cyan-200 border border-cyan-800/80"
                  }`}
                >
                  <span className="truncate max-w-[200px]">{ev.title}</span>
                </button>
              );
            })}
          </div>

          {/* Track 3: THREAT INDICATORS */}
          <div className="relative h-6 flex items-center space-x-4 z-10 pl-4">
            {indicatorEvents.map((ev) => {
              const isSelected = selectedEventId === ev.id;
              return (
                <button
                  key={ev.id}
                  onClick={() => onSelectEvent(isSelected ? null : ev)}
                  className={`h-5 px-2.5 rounded text-[10px] font-mono flex items-center space-x-1.5 transition-all shadow-md shrink-0 ${
                    isSelected
                      ? "bg-rose-600 text-white ring-2 ring-rose-400 scale-105"
                      : ev.severity === "critical"
                      ? "bg-rose-950/90 hover:bg-rose-900 text-rose-300 border border-rose-800"
                      : "bg-amber-950/90 hover:bg-amber-900 text-amber-300 border border-amber-800"
                  }`}
                >
                  <span className="truncate max-w-[180px]">{ev.title}</span>
                </button>
              );
            })}
          </div>

          {/* Date Axis Bar at bottom */}
          <div className="h-4 border-t border-[#3A4553] flex justify-between items-center text-[9px] font-mono text-slate-400 pt-1 px-2 z-10">
            {dates.map((d) => (
              <span key={d} className="select-none">
                {d}
              </span>
            ))}
          </div>
          </>
          )}
        </div>
      </div>
    </div>
  );
}
