"use client";

import React from "react";
import { GraphNode, GraphEdge, InvestigationData } from "./types";
import {
  ChevronRight,
  ChevronLeft,
  X,
  ShieldAlert,
  Link as LinkIcon,
} from "lucide-react";
import { InvestigationHeader } from "./InvestigationHeader";
import { RelationshipInspector } from "./RelationshipInspector";
import { EvidencePanel } from "./EvidencePanel";

interface ObjectInspectorProps {
  investigation: InvestigationData;
  selectedNode: GraphNode | null;
  selectedEdge: GraphEdge | null;
  onCloseSelection: () => void;
  onSelectNodeById: (id: string) => void;
  isCollapsed: boolean;
  onToggleCollapse: () => void;
  onExpandNode?: (id: string) => void;
  isExpanding?: boolean;
}

export function ObjectInspector({
  investigation,
  selectedNode,
  selectedEdge,
  onCloseSelection,
  onSelectNodeById,
  isCollapsed,
  onToggleCollapse,
  onExpandNode,
  isExpanding,
}: ObjectInspectorProps) {
  // Collapsed Sidebar View (ThreatQ right rail)
  if (isCollapsed) {
    return (
      <div className="w-10 bg-[#252D38] border-l border-[#3A4553] flex flex-col items-center py-3 select-none z-20">
        <button
          onClick={onToggleCollapse}
          title="Expand Details Panel"
          className="p-1.5 text-slate-400 hover:text-white hover:bg-[#181E28] rounded mb-4 transition-colors"
        >
          <ChevronLeft className="w-4 h-4" />
        </button>
        <span className="[writing-mode:vertical-rl] text-xs font-mono tracking-widest text-slate-400 uppercase">
          {selectedNode ? "Object Details" : selectedEdge ? "Relationship" : "Investigation"}
        </span>
      </div>
    );
  }

  return (
    <aside className="w-80 md:w-96 bg-[#252D38] border-l border-[#3A4553] flex flex-col h-full text-slate-200 select-none z-20 overflow-hidden shadow-2xl">
      {/* 1. Header Bar */}
      <div className="p-4 border-b border-[#3A4553] flex items-center justify-between bg-[#202731]">
        <div className="flex items-center space-x-2 min-w-0">
          <div className="w-6 h-6 rounded bg-rose-500/20 border border-rose-500/40 flex items-center justify-center shrink-0">
            <ShieldAlert className="w-3.5 h-3.5 text-rose-400" />
          </div>
          <h2 className="text-sm font-semibold text-white truncate font-sans">
            {selectedNode
              ? selectedNode.label
              : selectedEdge
              ? `Relationship: ${selectedEdge.label || selectedEdge.relationship || "Connected"}`
              : investigation.title}
          </h2>
        </div>

        <div className="flex items-center space-x-1.5 shrink-0">
          {(selectedNode || selectedEdge) && (
            <button
              onClick={onCloseSelection}
              title="Return to Investigation Overview"
              className="p-1 text-slate-400 hover:text-white hover:bg-[#181E28] rounded transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          )}
          <button
            onClick={onToggleCollapse}
            title="Collapse Panel"
            className="p-1 text-slate-400 hover:text-white hover:bg-[#181E28] rounded transition-colors"
          >
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* 2. Scrollable Inspector Content */}
      <div className="flex-1 overflow-y-auto divide-y divide-[#3A4553]/70 font-sans text-xs">
        {/* CASE A: Node is selected -> Compose EvidencePanel & RelationshipInspector */}
        {selectedNode ? (
          <div className="p-4 space-y-5">
            <EvidencePanel node={selectedNode} />

            <div className="pt-3 border-t border-[#3A4553]/70">
              <RelationshipInspector
                selectedNode={selectedNode}
                allNodes={investigation.nodes}
                edges={investigation.edges}
                onSelectNodeById={onSelectNodeById}
                onExpandNode={onExpandNode}
                isExpanding={isExpanding}
              />
            </div>
          </div>
        ) : selectedEdge ? (
          /* CASE B: Edge is selected -> Show relationship details */
          <div className="p-4 space-y-4 font-sans text-xs">
            <div className="bg-[#181E28] p-3.5 rounded-md border border-[#3A4553] space-y-2">
              <div className="flex items-center space-x-1.5 text-cyan-400 font-mono text-[11px] font-semibold">
                <LinkIcon className="w-3.5 h-3.5" />
                <span>RELATIONSHIP LINK</span>
              </div>
              <div className="font-mono text-xs text-white bg-[#12161E] p-2 rounded border border-[#2D3748]">
                {selectedEdge.label || selectedEdge.relationship || "Associated with"}
              </div>
            </div>

            <div className="space-y-2 font-mono text-xs">
              <div className="p-2.5 bg-[#181E28] rounded border border-[#3A4553]">
                <span className="text-[10px] text-slate-400 block uppercase">Source Node</span>
                <span className="text-white break-all font-semibold">{selectedEdge.source}</span>
              </div>
              <div className="p-2.5 bg-[#181E28] rounded border border-[#3A4553]">
                <span className="text-[10px] text-slate-400 block uppercase">Target Node</span>
                <span className="text-white break-all font-semibold">{selectedEdge.target}</span>
              </div>
              {selectedEdge.weight !== undefined && (
                <div className="p-2.5 bg-[#181E28] rounded border border-[#3A4553] flex justify-between">
                  <span className="text-[10px] text-slate-400 uppercase">Weight / Confidence</span>
                  <span className="text-cyan-400 font-bold">{(selectedEdge.weight * 100).toFixed(0)}%</span>
                </div>
              )}
            </div>
          </div>
        ) : (
          /* CASE C: No selection -> Compose InvestigationHeader */
          <InvestigationHeader investigation={investigation} />
        )}
      </div>
    </aside>
  );
}
