"use client";

import React, { useState } from "react";
import { GraphNode, GraphEdge, InvestigationData } from "./types";
import {
  ChevronRight,
  ChevronDown,
  X,
  ExternalLink,
  ShieldAlert,
  Clock,
  Tag,
  Link as LinkIcon,
  Layers,
  FileText,
  Activity,
  CheckCircle2,
  AlertTriangle,
  Copy,
  Check,
  ChevronLeft,
} from "lucide-react";

interface ObjectInspectorProps {
  investigation: InvestigationData;
  selectedNode: GraphNode | null;
  selectedEdge: GraphEdge | null;
  onCloseSelection: () => void;
  onSelectNodeById: (id: string) => void;
  isCollapsed: boolean;
  onToggleCollapse: () => void;
}

export function ObjectInspector({
  investigation,
  selectedNode,
  selectedEdge,
  onCloseSelection,
  onSelectNodeById,
  isCollapsed,
  onToggleCollapse,
}: ObjectInspectorProps) {
  // Collapsible section state
  const [descOpen, setDescOpen] = useState(true);
  const [evidenceOpen, setEvidenceOpen] = useState(true);
  const [sourcesOpen, setSourcesOpen] = useState(true);
  const [tagsOpen, setTagsOpen] = useState(true);
  const [attributesOpen, setAttributesOpen] = useState(true);
  const [relationshipsOpen, setRelationshipsOpen] = useState(true);
  const [modelOpen, setModelOpen] = useState(true);

  const [copied, setCopied] = useState(false);

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // Find connected neighbors for the selected node
  const neighborNodes = React.useMemo(() => {
    if (!selectedNode) return [];
    const connectedIds = new Set<string>();
    investigation.edges.forEach((edge) => {
      if (edge.source === selectedNode.id) connectedIds.add(edge.target);
      if (edge.target === selectedNode.id) connectedIds.add(edge.source);
    });
    return investigation.nodes.filter((n) => connectedIds.has(n.id));
  }, [selectedNode, investigation]);

  if (isCollapsed) {
    return (
      <div className="w-10 bg-[#252D38] border-l border-[#3A4553] flex flex-col items-center py-3 select-none z-20">
        <button
          onClick={onToggleCollapse}
          title="Expand Details Panel"
          className="p-1.5 text-slate-400 hover:text-white hover:bg-[#181E28] rounded mb-4"
        >
          <ChevronLeft className="w-4 h-4" />
        </button>
        <span className="[writing-mode:vertical-rl] text-xs font-mono tracking-widest text-slate-400 uppercase">
          {selectedNode ? "Object Details" : "Investigation"}
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
            {selectedNode ? selectedNode.label : investigation.title}
          </h2>
        </div>

        <div className="flex items-center space-x-1.5 shrink-0">
          {selectedNode && (
            <button
              onClick={onCloseSelection}
              title="Return to Investigation Overview"
              className="p-1 text-slate-400 hover:text-white hover:bg-[#181E28] rounded"
            >
              <X className="w-4 h-4" />
            </button>
          )}
          <button
            onClick={onToggleCollapse}
            title="Collapse Panel"
            className="p-1 text-slate-400 hover:text-white hover:bg-[#181E28] rounded"
          >
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* 2. Scrollable Content Body */}
      <div className="flex-1 overflow-y-auto divide-y divide-[#3A4553]/70 font-sans text-xs">
        {/* CASE A: Specific Node Selected */}
        {selectedNode ? (
          <div className="p-4 space-y-4">
            {/* Object Header & Summary Card */}
            <div className="bg-[#181E28] p-3 rounded-md border border-[#3A4553] space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-mono uppercase tracking-wider text-cyan-400 font-semibold">
                  Type: {selectedNode.type.replace("_", " ")}
                </span>
                {selectedNode.severity && (
                  <span
                    className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase tracking-wider ${
                      selectedNode.severity === "critical"
                        ? "bg-rose-950/80 text-rose-400 border border-rose-800"
                        : selectedNode.severity === "high"
                        ? "bg-amber-950/80 text-amber-400 border border-amber-800"
                        : "bg-slate-800 text-slate-300"
                    }`}
                  >
                    {selectedNode.severity}
                  </span>
                )}
              </div>
              <div className="font-mono text-xs text-slate-200 break-all bg-[#12161E] p-2 rounded border border-[#2D3748] flex items-center justify-between">
                <span>{selectedNode.label}</span>
                <button
                  onClick={() => handleCopy(selectedNode.label)}
                  title="Copy Identifier"
                  className="p-1 text-slate-400 hover:text-white"
                >
                  {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                </button>
              </div>
            </div>

            {/* Model Output / ML Classification */}
            {selectedNode.metadata?.modelOutput && (
              <div className="space-y-1.5">
                <button
                  onClick={() => setModelOpen(!modelOpen)}
                  className="flex items-center justify-between w-full font-semibold text-slate-200 uppercase tracking-wider text-[11px]"
                >
                  <span className="flex items-center space-x-1.5 text-cyan-400">
                    <Activity className="w-3.5 h-3.5" />
                    <span>ML Inference & Explainability</span>
                  </span>
                  {modelOpen ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronRight className="w-3.5 h-3.5" />}
                </button>
                {modelOpen && (
                  <div className="bg-[#181E28] p-2.5 rounded border border-[#3A4553] space-y-2 font-mono text-[11px]">
                    <div className="flex justify-between">
                      <span className="text-slate-400">Model Version:</span>
                      <span className="text-white">{selectedNode.metadata.modelVersion || "Production v1.0"}</span>
                    </div>
                    {selectedNode.metadata.riskScore !== undefined && (
                      <div className="flex justify-between">
                        <span className="text-slate-400">Risk Score:</span>
                        <span className="text-rose-400 font-bold">
                          {(selectedNode.metadata.riskScore * 100).toFixed(1)}%
                        </span>
                      </div>
                    )}
                    {/* Top SHAP / Risk Factors */}
                    {selectedNode.metadata.evidence && selectedNode.metadata.evidence.length > 0 && (
                      <div className="pt-1.5 border-t border-[#2D3748] space-y-1">
                        <span className="text-slate-400 text-[10px]">Key Risk Indicators:</span>
                        <ul className="list-disc list-inside text-slate-300 space-y-0.5 text-[10px]">
                          {selectedNode.metadata.evidence.map((ev, i) => (
                            <li key={i}>{ev}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}

            {/* Relationships & Connected Neighbors */}
            <div className="space-y-1.5">
              <button
                onClick={() => setRelationshipsOpen(!relationshipsOpen)}
                className="flex items-center justify-between w-full font-semibold text-slate-200 uppercase tracking-wider text-[11px]"
              >
                <span className="flex items-center space-x-1.5 text-purple-400">
                  <LinkIcon className="w-3.5 h-3.5" />
                  <span>Connected Entities ({neighborNodes.length})</span>
                </span>
                {relationshipsOpen ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronRight className="w-3.5 h-3.5" />}
              </button>
              {relationshipsOpen && (
                <div className="space-y-1 max-h-48 overflow-y-auto">
                  {neighborNodes.map((neighbor) => (
                    <div
                      key={neighbor.id}
                      onClick={() => onSelectNodeById(neighbor.id)}
                      className="p-2 bg-[#181E28] hover:bg-[#1E2631] rounded border border-[#3A4553] flex items-center justify-between cursor-pointer transition-colors"
                    >
                      <div className="flex items-center space-x-2 min-w-0">
                        <span className="w-2 h-2 rounded-full bg-cyan-400 shrink-0"></span>
                        <span className="text-slate-200 truncate">{neighbor.label}</span>
                      </div>
                      <span className="text-[9px] font-mono text-slate-400 uppercase shrink-0">
                        {neighbor.type}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        ) : (
          /* CASE B: Investigation-Level Overview (ThreatQ exact format) */
          <div>
            {/* Top Stat Matrix */}
            <div className="p-4 grid grid-cols-3 gap-2 border-b border-[#3A4553]/70 text-center">
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

            {/* Severity & Visibility */}
            <div className="p-4 grid grid-cols-2 gap-4 border-b border-[#3A4553]/70">
              <div>
                <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider">Severity</span>
                <p className="text-xs font-bold text-rose-400 font-mono mt-0.5">{investigation.severity.toUpperCase()}</p>
              </div>
              <div>
                <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider">Visibility</span>
                <p className="text-xs font-semibold text-slate-200 mt-0.5">{investigation.visibility}</p>
              </div>
            </div>

            {/* Timestamps & Attribution */}
            <div className="p-4 space-y-2 border-b border-[#3A4553]/70 text-xs">
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

            {/* Collapsible: Description */}
            <div className="p-4 border-b border-[#3A4553]/70 space-y-2">
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

            {/* Collapsible: Sources */}
            <div className="p-4 border-b border-[#3A4553]/70 space-y-2">
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

            {/* Collapsible: Tags */}
            <div className="p-4 border-b border-[#3A4553]/70 space-y-2">
              <button
                onClick={() => setTagsOpen(!tagsOpen)}
                className="flex items-center justify-between w-full font-semibold text-slate-200 uppercase tracking-wider text-[11px]"
              >
                <span>Tags</span>
                {tagsOpen ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronRight className="w-3.5 h-3.5" />}
              </button>
              {tagsOpen && (
                <div className="flex flex-wrap gap-1.5">
                  {investigation.tags.map((tag) => (
                    <span
                      key={tag}
                      className="px-2 py-0.5 rounded bg-blue-950/60 border border-blue-800/60 text-blue-300 text-[10px] font-mono"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              )}
            </div>

            {/* Collapsible: Attributes */}
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
        )}
      </div>
    </aside>
  );
}
