"use client";

import React, { useEffect, useRef } from "react";
import { GraphNode } from "./types";
import {
  Info,
  Copy,
  Check,
  Pin,
  EyeOff,
  Share2,
  ExternalLink,
  ShieldAlert,
} from "lucide-react";

interface NodeContextMenuProps {
  node: GraphNode;
  position: { x: number; y: number };
  onClose: () => void;
  onInspectDetails: (node: GraphNode) => void;
  onCopyIdentifier: (text: string) => void;
  onPinNode?: (nodeId: string) => void;
  onExpandNeighbors?: (nodeId: string) => void;
  onHideNode?: (nodeId: string) => void;
}

export function NodeContextMenu({
  node,
  position,
  onClose,
  onInspectDetails,
  onCopyIdentifier,
  onPinNode,
  onExpandNeighbors,
  onHideNode,
}: NodeContextMenuProps) {
  const menuRef = useRef<HTMLDivElement>(null);

  // Close on outside click
  useEffect(() => {
    const handleOutsideClick = (e: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        onClose();
      }
    };
    window.addEventListener("mousedown", handleOutsideClick);
    return () => window.removeEventListener("mousedown", handleOutsideClick);
  }, [onClose]);

  return (
    <div
      ref={menuRef}
      style={{ top: position.y, left: position.x }}
      className="fixed z-50 w-52 bg-[#252D38]/95 backdrop-blur-md border border-[#3A4553] rounded-md shadow-2xl py-1.5 text-xs text-slate-200 select-none animate-in fade-in zoom-in-95 duration-100"
    >
      <div className="px-3 py-1.5 border-b border-[#3A4553] flex items-center justify-between">
        <span className="font-mono text-[10px] text-cyan-400 uppercase tracking-wider font-semibold truncate max-w-[140px]">
          {node.label}
        </span>
        <span className="text-[9px] font-mono text-slate-400 uppercase">{node.type}</span>
      </div>

      <div className="py-1">
        <button
          onClick={() => {
            onInspectDetails(node);
            onClose();
          }}
          className="w-full px-3 py-1.5 text-left flex items-center space-x-2 hover:bg-[#181E28] hover:text-cyan-400 transition-colors"
        >
          <Info className="w-3.5 h-3.5 text-cyan-400" />
          <span>Inspect Object Details</span>
        </button>

        <button
          onClick={() => {
            onCopyIdentifier(node.label);
            onClose();
          }}
          className="w-full px-3 py-1.5 text-left flex items-center space-x-2 hover:bg-[#181E28] hover:text-white transition-colors"
        >
          <Copy className="w-3.5 h-3.5 text-slate-400" />
          <span>Copy Identifier</span>
        </button>

        {onExpandNeighbors && (
          <button
            onClick={() => {
              onExpandNeighbors(node.id);
              onClose();
            }}
            className="w-full px-3 py-1.5 text-left flex items-center space-x-2 hover:bg-[#181E28] hover:text-purple-400 transition-colors"
          >
            <Share2 className="w-3.5 h-3.5 text-purple-400" />
            <span>Expand Connected Objects</span>
          </button>
        )}

        {onPinNode && (
          <button
            onClick={() => {
              onPinNode(node.id);
              onClose();
            }}
            className="w-full px-3 py-1.5 text-left flex items-center space-x-2 hover:bg-[#181E28] hover:text-amber-400 transition-colors"
          >
            <Pin className="w-3.5 h-3.5 text-amber-400" />
            <span>Pin Position on Canvas</span>
          </button>
        )}

        {onHideNode && (
          <button
            onClick={() => {
              onHideNode(node.id);
              onClose();
            }}
            className="w-full px-3 py-1.5 text-left flex items-center space-x-2 hover:bg-rose-950/40 text-rose-300 transition-colors border-t border-[#3A4553]/60 mt-1 pt-1.5"
          >
            <EyeOff className="w-3.5 h-3.5 text-rose-400" />
            <span>Hide from View</span>
          </button>
        )}
      </div>
    </div>
  );
}
