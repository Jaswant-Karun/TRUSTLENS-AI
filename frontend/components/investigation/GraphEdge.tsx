"use client";

import React from "react";
import { GraphEdge, GraphNode } from "./types";

interface GraphEdgeComponentProps {
  edge: GraphEdge;
  sourceNode: GraphNode | undefined;
  targetNode: GraphNode | undefined;
  isSelected: boolean;
  activeFocusId: string | null;
  isConnectedToFocus: boolean;
  onClick: (e: React.MouseEvent, edge: GraphEdge) => void;
}

export function GraphEdgeComponent({
  edge,
  sourceNode,
  targetNode,
  isSelected,
  activeFocusId,
  isConnectedToFocus,
  onClick,
}: GraphEdgeComponentProps) {
  if (!sourceNode || !targetNode) return null;

  const strokeOpacity = activeFocusId ? (isConnectedToFocus ? 0.9 : 0.15) : 0.45;
  const strokeColor = isSelected
    ? "#38BDF8"
    : isConnectedToFocus && activeFocusId
    ? "#60A5FA"
    : "#4B5563";
  const strokeWidth = isSelected ? 2.5 : isConnectedToFocus && activeFocusId ? 2 : 1.2;

  const midX = (sourceNode.x + targetNode.x) / 2;
  const midY = (sourceNode.y + targetNode.y) / 2;

  return (
    <g onClick={(e) => onClick(e, edge)} className="cursor-pointer">
      {/* Visual Edge Line */}
      <line
        x1={sourceNode.x}
        y1={sourceNode.y}
        x2={targetNode.x}
        y2={targetNode.y}
        stroke={strokeColor}
        strokeWidth={strokeWidth}
        strokeOpacity={strokeOpacity}
        strokeDasharray={edge.isDashed ? "4,4" : undefined}
      />

      {/* Relationship Label on Hover/Select */}
      {edge.label && (isSelected || (activeFocusId && isConnectedToFocus)) && (
        <g transform={`translate(${midX}, ${midY - 4})`} className="pointer-events-none select-none">
          <rect
            x={-(edge.label.length * 2.8 + 4)}
            y="-8"
            width={edge.label.length * 5.6 + 8}
            height="14"
            fill="#1E2631"
            stroke="#3A4553"
            strokeWidth="0.8"
            rx="3"
            opacity="0.9"
          />
          <text
            y="2"
            fill="#94A3B8"
            fontSize="9"
            fontFamily="monospace"
            textAnchor="middle"
          >
            {edge.label}
          </text>
        </g>
      )}
    </g>
  );
}
