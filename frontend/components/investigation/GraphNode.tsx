"use client";

import React from "react";
import { GraphNode, NodeType } from "./types";
import {
  ShieldAlert,
  Globe,
  Link as LinkIcon,
  Server,
  Zap,
  Mail,
  FileText,
  AlertTriangle,
  Fingerprint,
  Database,
  UserCheck,
} from "lucide-react";

interface GraphNodeComponentProps {
  node: GraphNode;
  isSelected: boolean;
  isHovered: boolean;
  isConnected: boolean;
  isSearchMatch: boolean;
  opacity: number;
  onMouseDown: (e: React.MouseEvent, node: GraphNode) => void;
  onMouseEnter: () => void;
  onMouseLeave: () => void;
  onContextMenu?: (e: React.MouseEvent, node: GraphNode) => void;
}

export function getNodeColor(type: NodeType, isCentral?: boolean) {
  if (isCentral) {
    return { bg: "#EF4444", border: "#F87171", text: "#FEE2E2", halo: "rgba(239, 68, 68, 0.3)" };
  }
  switch (type) {
    case "message":
      return { bg: "#0284C7", border: "#38BDF8", text: "#E0F2FE", halo: "rgba(56, 189, 248, 0.25)" };
    case "url":
      return { bg: "#D97706", border: "#FBBF24", text: "#FEF3C7", halo: "rgba(251, 191, 36, 0.25)" };
    case "domain":
      return { bg: "#059669", border: "#34D399", text: "#D1FAE5", halo: "rgba(52, 211, 153, 0.25)" };
    case "ip":
      return { bg: "#DB2777", border: "#F472B6", text: "#FCE7F3", halo: "rgba(244, 114, 182, 0.25)" };
    case "scam_category":
      return { bg: "#DC2626", border: "#F87171", text: "#FEE2E2", halo: "rgba(248, 113, 113, 0.25)" };
    case "tactic":
      return { bg: "#7C3AED", border: "#A78BFA", text: "#EDE9FE", halo: "rgba(167, 139, 250, 0.25)" };
    case "campaign_cluster":
      return { bg: "#EA580C", border: "#FB923C", text: "#FFEDD5", halo: "rgba(251, 146, 60, 0.3)" };
    case "user_report":
      return { bg: "#0891B2", border: "#22D3EE", text: "#CFFAFE", halo: "rgba(34, 211, 238, 0.25)" };
    case "threat_indicator":
      return { bg: "#CA8A04", border: "#FACC15", text: "#FEF9C3", halo: "rgba(250, 204, 21, 0.25)" };
    case "source_reference":
    default:
      return { bg: "#475569", border: "#94A3B8", text: "#F1F5F9", halo: "rgba(148, 163, 184, 0.25)" };
  }
}

export function getNodeIcon(type: NodeType) {
  switch (type) {
    case "message":
      return <Mail className="w-4 h-4 text-white" />;
    case "url":
      return <LinkIcon className="w-4 h-4 text-white" />;
    case "domain":
      return <Globe className="w-4 h-4 text-white" />;
    case "ip":
      return <Server className="w-4 h-4 text-white" />;
    case "scam_category":
      return <ShieldAlert className="w-4 h-4 text-white" />;
    case "tactic":
      return <Zap className="w-4 h-4 text-white" />;
    case "campaign_cluster":
      return <AlertTriangle className="w-5 h-5 text-white" />;
    case "user_report":
      return <UserCheck className="w-4 h-4 text-white" />;
    case "threat_indicator":
      return <Fingerprint className="w-4 h-4 text-white" />;
    case "source_reference":
    default:
      return <Database className="w-4 h-4 text-white" />;
  }
}

export function GraphNodeComponent({
  node,
  isSelected,
  isHovered,
  isConnected,
  isSearchMatch,
  opacity,
  onMouseDown,
  onMouseEnter,
  onMouseLeave,
  onContextMenu,
}: GraphNodeComponentProps) {
  const radius = node.isCentral ? 38 : node.radius || 24;
  const colors = getNodeColor(node.type, node.isCentral);

  return (
    <g
      transform={`translate(${node.x}, ${node.y})`}
      onMouseDown={(e) => onMouseDown(e, node)}
      onMouseEnter={onMouseEnter}
      onMouseLeave={onMouseLeave}
      onContextMenu={(e) => {
        if (onContextMenu) {
          e.preventDefault();
          onContextMenu(e, node);
        }
      }}
      className="cursor-pointer transition-opacity duration-150"
      style={{ opacity }}
    >
      {/* Central Node Pulse Halo (ThreatQ GRIZZLY STEPPE effect) */}
      {node.isCentral && (
        <circle
          r={radius + 12}
          fill="none"
          stroke={colors.border}
          strokeWidth="1.5"
          strokeOpacity="0.4"
          className="animate-ping"
        />
      )}

      {/* Selection / Search Match Halo Ring */}
      {(isSelected || isHovered || isSearchMatch) && (
        <circle
          r={radius + 6}
          fill="none"
          stroke={isSelected ? "#38BDF8" : isSearchMatch ? "#FBBF24" : colors.border}
          strokeWidth="2.5"
          strokeDasharray={isSelected ? "4,2" : undefined}
          filter="url(#node-glow)"
        />
      )}

      {/* Main Node Body Circle */}
      <circle
        r={radius}
        fill={colors.bg}
        stroke={isSelected ? "#FFFFFF" : colors.border}
        strokeWidth={isSelected ? 3 : 2}
        className="shadow-xl"
      />

      {/* Centered Node Icon Glyph */}
      <foreignObject
        x={-10}
        y={-10}
        width={20}
        height={20}
        className="pointer-events-none flex items-center justify-center"
      >
        <div className="w-full h-full flex items-center justify-center">
          {getNodeIcon(node.type)}
        </div>
      </foreignObject>

      {/* Numeric Indicator Count Badge (ThreatQ style e.g. 45 or 18) */}
      {node.count !== undefined && (
        <g transform={`translate(${radius * 0.7}, ${-radius * 0.7})`}>
          <circle r="9" fill="#0284C7" stroke="#38BDF8" strokeWidth="1.5" />
          <text
            y="3.5"
            fill="#FFFFFF"
            fontSize="9"
            fontWeight="bold"
            fontFamily="monospace"
            textAnchor="middle"
            className="pointer-events-none select-none"
          >
            {node.count}
          </text>
        </g>
      )}

      {/* Label Text Underneath Node */}
      <text
        y={radius + 14}
        fill={isSelected ? "#38BDF8" : "#E2E8F0"}
        fontSize={node.isCentral ? "12" : "10"}
        fontWeight={node.isCentral ? "bold" : "500"}
        fontFamily="sans-serif"
        textAnchor="middle"
        className="select-none pointer-events-none tracking-wide"
      >
        {node.label.length > 28 ? node.label.substring(0, 26) + "..." : node.label}
      </text>

      {/* Subtype Badge Label */}
      {node.subType && (
        <text
          y={radius + 26}
          fill="#94A3B8"
          fontSize="8"
          fontFamily="monospace"
          textAnchor="middle"
          className="select-none pointer-events-none"
        >
          {node.subType}
        </text>
      )}
    </g>
  );
}
