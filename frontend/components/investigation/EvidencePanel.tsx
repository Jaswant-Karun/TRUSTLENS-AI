"use client";

import React, { useState } from "react";
import { GraphNode } from "./types";
import {
  Activity,
  Copy,
  Check,
  ChevronDown,
  ChevronRight,
  ShieldAlert,
  AlertTriangle,
  FileText,
  Clock,
} from "lucide-react";
import { getNodeColor } from "./GraphNode";

interface EvidencePanelProps {
  node: GraphNode;
}

export function EvidencePanel({ node }: EvidencePanelProps) {
  const [modelOpen, setModelOpen] = useState(true);
  const [evidenceOpen, setEvidenceOpen] = useState(true);
  const [copied, setCopied] = useState(false);

  const colors = getNodeColor(node.type, node.isCentral);

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="space-y-4 font-sans text-xs">
      {/* 1. Object Identity & Type Card */}
      <div className="bg-[#181E28] p-3.5 rounded-md border border-[#3A4553] space-y-2.5 shadow-md">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-1.5">
            <span
              className="w-2.5 h-2.5 rounded-full"
              style={{ backgroundColor: colors.border }}
            ></span>
            <span className="text-[10px] font-mono uppercase tracking-wider text-cyan-400 font-bold">
              {node.type.replace("_", " ")}
            </span>
          </div>

          {node.severity && (
            <span
              className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase tracking-wider ${
                node.severity === "critical"
                  ? "bg-rose-950/80 text-rose-400 border border-rose-800"
                  : node.severity === "high"
                  ? "bg-amber-950/80 text-amber-400 border border-amber-800"
                  : "bg-slate-800 text-slate-300 border border-slate-700"
              }`}
            >
              {node.severity}
            </span>
          )}
        </div>

        {/* Identifier Display with Instant Copy */}
        <div className="font-mono text-xs text-slate-200 break-all bg-[#12161E] p-2.5 rounded border border-[#2D3748] flex items-center justify-between">
          <span className="select-all">{node.label}</span>
          <button
            onClick={() => handleCopy(node.label)}
            title="Copy Identifier"
            className="p-1 text-slate-400 hover:text-white shrink-0 ml-2"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
          </button>
        </div>

        {node.metadata?.description && (
          <p className="text-[11px] text-slate-300 leading-relaxed font-sans pt-1">
            {node.metadata.description}
          </p>
        )}
      </div>

      {/* 2. Machine Learning Inference & Telemetry */}
      {node.metadata && (node.metadata.modelVersion || node.metadata.riskScore !== undefined) && (
        <div className="space-y-1.5">
          <button
            onClick={() => setModelOpen(!modelOpen)}
            className="flex items-center justify-between w-full font-semibold text-slate-200 uppercase tracking-wider text-[11px] select-none"
          >
            <span className="flex items-center space-x-1.5 text-cyan-400">
              <Activity className="w-3.5 h-3.5" />
              <span>Model Inference & Explainability</span>
            </span>
            {modelOpen ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronRight className="w-3.5 h-3.5" />}
          </button>

          {modelOpen && (
            <div className="bg-[#181E28] p-3 rounded border border-[#3A4553] space-y-2 font-mono text-[11px]">
              {node.metadata.modelVersion && (
                <div className="flex justify-between">
                  <span className="text-slate-400">Model Lineage:</span>
                  <span className="text-white font-medium">{node.metadata.modelVersion}</span>
                </div>
              )}

              {node.metadata.confidence !== undefined && (
                <div className="flex justify-between">
                  <span className="text-slate-400">Model Confidence:</span>
                  <span className="text-cyan-400 font-bold">
                    {(node.metadata.confidence * 100).toFixed(1)}%
                  </span>
                </div>
              )}

              {node.metadata.riskScore !== undefined && (
                <div className="flex justify-between">
                  <span className="text-slate-400">Calculated Risk:</span>
                  <span className="text-rose-400 font-bold">
                    {(node.metadata.riskScore * 100).toFixed(1)}%
                  </span>
                </div>
              )}

              {/* Verified Evidence Tokens / Risk Factors */}
              {node.metadata.evidence && node.metadata.evidence.length > 0 && (
                <div className="pt-2 border-t border-[#2D3748] space-y-1.5 font-sans">
                  <span className="text-slate-400 text-[10px] font-mono uppercase tracking-wider block">
                    Verified Risk Factors:
                  </span>
                  <ul className="space-y-1">
                    {node.metadata.evidence.map((ev, i) => (
                      <li key={i} className="text-[11px] text-slate-300 flex items-start space-x-1.5">
                        <span className="text-amber-400 shrink-0 mt-0.5">•</span>
                        <span>{ev}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
