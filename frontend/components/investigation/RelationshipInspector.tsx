"use client";

import React, { useState } from "react";
import { GraphNode, GraphEdge } from "./types";
import { Link as LinkIcon, ChevronDown, ChevronRight, ArrowRight } from "lucide-react";
import { getNodeColor } from "./GraphNode";

interface RelationshipInspectorProps {
  selectedNode: GraphNode;
  allNodes: GraphNode[];
  edges: GraphEdge[];
  onSelectNodeById: (id: string) => void;
}

export function RelationshipInspector({
  selectedNode,
  allNodes,
  edges,
  onSelectNodeById,
}: RelationshipInspectorProps) {
  const [isOpen, setIsOpen] = useState(true);

  // Find all edges connected to selectedNode
  const connectedEdges = edges.filter(
    (e) => e.source === selectedNode.id || e.target === selectedNode.id
  );

  const nodeMap = React.useMemo(() => {
    const map = new Map<string, GraphNode>();
    allNodes.forEach((n) => map.set(n.id, n));
    return map;
  }, [allNodes]);

  return (
    <div className="space-y-2">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center justify-between w-full font-semibold text-slate-200 uppercase tracking-wider text-[11px] select-none"
      >
        <span className="flex items-center space-x-1.5 text-purple-400">
          <LinkIcon className="w-3.5 h-3.5" />
          <span>Connected Entities ({connectedEdges.length})</span>
        </span>
        {isOpen ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronRight className="w-3.5 h-3.5" />}
      </button>

      {isOpen && (
        <div className="space-y-1.5 max-h-56 overflow-y-auto pr-1">
          {connectedEdges.length === 0 ? (
            <p className="text-[11px] text-slate-400 italic">No connected entities.</p>
          ) : (
            connectedEdges.map((edge) => {
              const isSource = edge.source === selectedNode.id;
              const neighborId = isSource ? edge.target : edge.source;
              const neighbor = nodeMap.get(neighborId);
              if (!neighbor) return null;

              const colors = getNodeColor(neighbor.type, neighbor.isCentral);

              return (
                <div
                  key={edge.id}
                  onClick={() => onSelectNodeById(neighbor.id)}
                  className="p-2.5 bg-[#181E28] hover:bg-[#1E2631] rounded border border-[#3A4553] hover:border-purple-500/50 flex items-center justify-between cursor-pointer transition-all group shadow-sm"
                >
                  <div className="flex items-center space-x-2 min-w-0">
                    <span
                      className="w-2.5 h-2.5 rounded-full shrink-0"
                      style={{ backgroundColor: colors.border }}
                    ></span>
                    <div className="min-w-0">
                      <div className="text-slate-200 group-hover:text-cyan-300 font-medium truncate text-xs">
                        {neighbor.label}
                      </div>
                      <div className="text-[10px] font-mono text-purple-400 flex items-center space-x-1">
                        <span>{edge.label || edge.relationship}</span>
                        <span className="text-slate-500">•</span>
                        <span className="text-slate-400 uppercase">{neighbor.type}</span>
                      </div>
                    </div>
                  </div>

                  <ArrowRight className="w-3.5 h-3.5 text-slate-500 group-hover:text-cyan-400 shrink-0 group-hover:translate-x-0.5 transition-transform" />
                </div>
              );
            })
          )}
        </div>
      )}
    </div>
  );
}
