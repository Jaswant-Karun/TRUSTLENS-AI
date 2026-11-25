"use client";

import React, { useMemo } from "react";
import { GraphNode, NodeType } from "./types";
import { getNodeColor, getNodeIcon } from "./GraphNode";

interface GraphLegendProps {
  nodes: GraphNode[];
  selectedTypes: Set<NodeType>;
  onToggleType: (type: NodeType) => void;
}

const NODE_TYPE_LABELS: Record<NodeType, string> = {
  campaign_cluster: "Campaign",
  message: "Message",
  url: "URL",
  domain: "Domain",
  ip: "IP Address",
  tactic: "Tactic",
  threat_indicator: "Indicator",
  user_report: "Report",
  scam_category: "Category",
  source_reference: "Source",
};

export function GraphLegend({ nodes, selectedTypes, onToggleType }: GraphLegendProps) {
  const typeCounts = useMemo(() => {
    const counts: Partial<Record<NodeType, number>> = {};
    for (const n of nodes) {
      counts[n.type] = (counts[n.type] || 0) + 1;
    }
    return Object.entries(counts) as [NodeType, number][];
  }, [nodes]);

  if (typeCounts.length === 0) return null;

  return (
    <div className="bg-[#202936]/90 backdrop-blur-md border border-[#3A4553] rounded-lg p-3 w-52 shadow-2xl select-none">
      <div className="text-[10px] font-mono font-semibold uppercase tracking-wider text-slate-400 mb-2 flex items-center justify-between">
        <span>Legend</span>
        <span className="text-cyan-400">{nodes.length} nodes</span>
      </div>
      <div className="space-y-1">
        {typeCounts.map(([type, count]) => {
          const colors = getNodeColor(type);
          const active = selectedTypes.has(type);
          return (
            <button
              key={type}
              onClick={() => onToggleType(type)}
              className={`w-full flex items-center justify-between px-1.5 py-1 rounded text-[11px] transition-colors ${
                active
                  ? "text-slate-200 hover:bg-[#1E293B]/60"
                  : "text-slate-500 opacity-50 hover:opacity-80"
              }`}
              title={`Toggle ${NODE_TYPE_LABELS[type] || type}`}
            >
              <span className="flex items-center space-x-2">
                <span
                  className="w-4 h-4 rounded-full flex items-center justify-center shrink-0"
                  style={{ backgroundColor: colors.bg, border: `1px solid ${colors.border}` }}
                >
                  <span className="scale-[0.65] flex items-center justify-center">{getNodeIcon(type)}</span>
                </span>
                <span className="truncate">{NODE_TYPE_LABELS[type] || type}</span>
              </span>
              <span className="font-mono text-[10px] text-slate-400">{count}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
