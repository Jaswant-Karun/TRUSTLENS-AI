"use client";

import React, { useState, useRef, useEffect, useCallback, useMemo } from "react";
import { GraphNode, GraphEdge, NodeType } from "./types";
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
  Check,
} from "lucide-react";

interface ThreatGraphProps {
  nodes: GraphNode[];
  edges: GraphEdge[];
  selectedNodeId: string | null;
  selectedEdgeId: string | null;
  onSelectNode: (node: GraphNode | null) => void;
  onSelectEdge: (edge: GraphEdge | null) => void;
  searchQuery?: string;
  typeFilter?: Set<NodeType>;
  zoomLevel?: number;
  onZoomChange?: (zoom: number) => void;
  onViewChange?: (view: { x: number; y: number; zoom: number; bounds: { minX: number; maxX: number; minY: number; maxY: number } }) => void;
}

export function ThreatGraph({
  nodes: initialNodes,
  edges,
  selectedNodeId,
  selectedEdgeId,
  onSelectNode,
  onSelectEdge,
  searchQuery = "",
  typeFilter,
  zoomLevel: externalZoom,
  onZoomChange,
  onViewChange,
}: ThreatGraphProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  // Local mutable positions for drag & force simulation
  const [nodes, setNodes] = useState<GraphNode[]>(initialNodes);
  const [viewTransform, setViewTransform] = useState({ x: 550, y: 340, zoom: 0.95 });
  const [isPanning, setIsPanning] = useState(false);
  const [panStart, setPanStart] = useState({ x: 0, y: 0 });
  const [draggedNodeId, setDraggedNodeId] = useState<string | null>(null);
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });
  const [hoveredNodeId, setHoveredNodeId] = useState<string | null>(null);

  // Automatically center graph on mount based on viewport dimensions
  useEffect(() => {
    if (containerRef.current) {
      const rect = containerRef.current.getBoundingClientRect();
      if (rect.width > 100 && rect.height > 100) {
        setViewTransform({
          x: rect.width / 2,
          y: rect.height / 2 + 25,
          zoom: 0.9,
        });
      }
    }
  }, []);

  // Sync external zoom if provided
  useEffect(() => {
    if (externalZoom && externalZoom !== viewTransform.zoom) {
      setViewTransform((prev) => ({ ...prev, zoom: externalZoom }));
    }
  }, [externalZoom]);

  // Sync initial nodes when prop changes
  useEffect(() => {
    setNodes(initialNodes);
  }, [initialNodes]);

  // Compute connected node & edge IDs for the selected or hovered node
  const activeFocusId = hoveredNodeId || selectedNodeId;
  const connectedNodeIds = useMemo(() => {
    if (!activeFocusId) return new Set<string>();
    const ids = new Set<string>([activeFocusId]);
    edges.forEach((edge) => {
      if (edge.source === activeFocusId) ids.add(edge.target);
      if (edge.target === activeFocusId) ids.add(edge.source);
    });
    return ids;
  }, [activeFocusId, edges]);

  const connectedEdgeIds = useMemo(() => {
    if (!activeFocusId) return new Set<string>();
    const ids = new Set<string>();
    edges.forEach((edge) => {
      if (edge.source === activeFocusId || edge.target === activeFocusId) {
        ids.add(edge.id);
      }
    });
    return ids;
  }, [activeFocusId, edges]);

  // Calculate bounding box for minimap and fit-to-screen
  const bounds = useMemo(() => {
    if (nodes.length === 0) return { minX: -500, maxX: 500, minY: -500, maxY: 500 };
    let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
    nodes.forEach((n) => {
      if (n.x < minX) minX = n.x;
      if (n.x > maxX) maxX = n.x;
      if (n.y < minY) minY = n.y;
      if (n.y > maxY) maxY = n.y;
    });
    return {
      minX: minX - 100,
      maxX: maxX + 100,
      minY: minY - 100,
      maxY: maxY + 100,
    };
  }, [nodes]);

  // Notify parent of view and bounds updates (for minimap)
  useEffect(() => {
    if (onViewChange) {
      onViewChange({
        x: viewTransform.x,
        y: viewTransform.y,
        zoom: viewTransform.zoom,
        bounds,
      });
    }
  }, [viewTransform, bounds, onViewChange]);

  // Node styles and colors based on 10 object types
  const getNodeColor = (type: NodeType, isCentral?: boolean) => {
    if (isCentral) return { bg: "#EF4444", border: "#F87171", text: "#FEE2E2", halo: "rgba(239, 68, 68, 0.3)" };
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
  };

  const getNodeIcon = (type: NodeType) => {
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
  };

  // Mouse pan handlers
  const handleMouseDown = (e: React.MouseEvent) => {
    // If clicking background, start pan
    if (e.target === containerRef.current || (e.target as HTMLElement).tagName === "svg") {
      setIsPanning(true);
      setPanStart({ x: e.clientX - viewTransform.x, y: e.clientY - viewTransform.y });
    }
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (isPanning) {
      setViewTransform((prev) => ({
        ...prev,
        x: e.clientX - panStart.x,
        y: e.clientY - panStart.y,
      }));
    } else if (draggedNodeId) {
      // Drag selected node
      const rect = containerRef.current?.getBoundingClientRect();
      if (!rect) return;
      const mouseCanvasX = (e.clientX - rect.left - viewTransform.x) / viewTransform.zoom;
      const mouseCanvasY = (e.clientY - rect.top - viewTransform.y) / viewTransform.zoom;

      setNodes((prevNodes) =>
        prevNodes.map((n) =>
          n.id === draggedNodeId
            ? { ...n, x: mouseCanvasX - dragOffset.x, y: mouseCanvasY - dragOffset.y }
            : n
        )
      );
    }
  };

  const handleMouseUp = () => {
    setIsPanning(false);
    setDraggedNodeId(null);
  };

  // Mouse wheel zoom
  const handleWheel = (e: React.WheelEvent) => {
    e.preventDefault();
    const zoomFactor = e.deltaY < 0 ? 1.1 : 0.9;
    const newZoom = Math.min(Math.max(viewTransform.zoom * zoomFactor, 0.25), 3.0);

    const rect = containerRef.current?.getBoundingClientRect();
    if (!rect) return;
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;

    // Zoom centered on cursor
    const newX = mouseX - (mouseX - viewTransform.x) * (newZoom / viewTransform.zoom);
    const newY = mouseY - (mouseY - viewTransform.y) * (newZoom / viewTransform.zoom);

    setViewTransform({ x: newX, y: newY, zoom: newZoom });
    if (onZoomChange) onZoomChange(newZoom);
  };

  // Node drag start
  const handleNodeMouseDown = (e: React.MouseEvent, node: GraphNode) => {
    e.stopPropagation();
    setDraggedNodeId(node.id);
    const rect = containerRef.current?.getBoundingClientRect();
    if (!rect) return;
    const mouseCanvasX = (e.clientX - rect.left - viewTransform.x) / viewTransform.zoom;
    const mouseCanvasY = (e.clientY - rect.top - viewTransform.y) / viewTransform.zoom;
    setDragOffset({ x: mouseCanvasX - node.x, y: mouseCanvasY - node.y });
    onSelectNode(node);
  };

  // Filtered nodes based on typeFilter and searchQuery
  const visibleNodes = useMemo(() => {
    return nodes.filter((node) => {
      if (typeFilter && !typeFilter.has(node.type)) return false;
      return true;
    });
  }, [nodes, typeFilter]);

  const visibleNodeIds = useMemo(() => new Set(visibleNodes.map((n) => n.id)), [visibleNodes]);

  const visibleEdges = useMemo(() => {
    return edges.filter(
      (e) => visibleNodeIds.has(e.source) && visibleNodeIds.has(e.target)
    );
  }, [edges, visibleNodeIds]);

  // Lookup map for fast coordinate access
  const nodeMap = useMemo(() => {
    const map = new Map<string, GraphNode>();
    nodes.forEach((n) => map.set(n.id, n));
    return map;
  }, [nodes]);

  return (
    <div
      ref={containerRef}
      onMouseDown={handleMouseDown}
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
      onWheel={handleWheel}
      className="w-full h-full relative overflow-hidden bg-[#181E28] cursor-grab active:cursor-grabbing select-none"
    >
      {/* Background Dot Grid (Cyber Security Aesthetics) */}
      <svg className="absolute inset-0 w-full h-full pointer-events-none opacity-20">
        <defs>
          <pattern id="threatq-grid" width="32" height="32" patternUnits="userSpaceOnUse">
            <circle cx="2" cy="2" r="1" fill="#475569" />
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#threatq-grid)" />
      </svg>

      {/* Main Interactive SVG Canvas */}
      <svg className="w-full h-full block">
        <defs>
          <filter id="node-glow" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur in="SourceGraphic" stdDeviation="6" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        <g transform={`translate(${viewTransform.x}, ${viewTransform.y}) scale(${viewTransform.zoom})`}>
          {/* Edges */}
          {visibleEdges.map((edge) => {
            const src = nodeMap.get(edge.source);
            const tgt = nodeMap.get(edge.target);
            if (!src || !tgt) return null;

            const isSelected = selectedEdgeId === edge.id;
            const isConnectedToFocus = activeFocusId ? connectedEdgeIds.has(edge.id) : true;
            const strokeOpacity = activeFocusId ? (isConnectedToFocus ? 0.9 : 0.15) : 0.45;
            const strokeColor = isSelected
              ? "#38BDF8"
              : isConnectedToFocus && activeFocusId
              ? "#60A5FA"
              : "#4B5563";
            const strokeWidth = isSelected ? 2.5 : isConnectedToFocus && activeFocusId ? 2 : 1.2;

            return (
              <g
                key={edge.id}
                onClick={(e) => {
                  e.stopPropagation();
                  onSelectEdge(edge);
                }}
                className="cursor-pointer"
              >
                <line
                  x1={src.x}
                  y1={src.y}
                  x2={tgt.x}
                  y2={tgt.y}
                  stroke={strokeColor}
                  strokeWidth={strokeWidth}
                  strokeOpacity={strokeOpacity}
                  strokeDasharray={edge.isDashed ? "4,4" : undefined}
                />
                {/* Edge Label on Hover/Select */}
                {edge.label && (isSelected || (activeFocusId && isConnectedToFocus)) && (
                  <text
                    x={(src.x + tgt.x) / 2}
                    y={(src.y + tgt.y) / 2 - 4}
                    fill="#94A3B8"
                    fontSize="9"
                    fontFamily="monospace"
                    textAnchor="middle"
                    className="select-none pointer-events-none bg-slate-900"
                  >
                    {edge.label}
                  </text>
                )}
              </g>
            );
          })}

          {/* Nodes */}
          {visibleNodes.map((node) => {
            const isSelected = selectedNodeId === node.id;
            const isHovered = hoveredNodeId === node.id;
            const isConnected = activeFocusId ? connectedNodeIds.has(node.id) : true;
            const isSearchMatch =
              searchQuery && node.label.toLowerCase().includes(searchQuery.toLowerCase());
            const opacity = activeFocusId ? (isConnected ? 1 : 0.25) : 1;

            const radius = node.isCentral ? 38 : node.radius || 24;
            const colors = getNodeColor(node.type, node.isCentral);

            return (
              <g
                key={node.id}
                transform={`translate(${node.x}, ${node.y})`}
                onMouseDown={(e) => handleNodeMouseDown(e, node)}
                onMouseEnter={() => setHoveredNodeId(node.id)}
                onMouseLeave={() => setHoveredNodeId(null)}
                className="cursor-pointer transition-opacity duration-150"
                style={{ opacity }}
              >
                {/* Central Node Pulse Halo */}
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

                {/* Selection Halo Ring */}
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

                {/* Outer Node Circle */}
                <circle
                  r={radius}
                  fill={colors.bg}
                  stroke={isSelected ? "#FFFFFF" : colors.border}
                  strokeWidth={isSelected ? 3 : 2}
                  className="shadow-xl"
                />

                {/* Inner Icon / Glyph */}
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

                {/* Count Badge (e.g. 45 indicators or 18 events) */}
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

                {/* Label Underneath Node */}
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

                {/* Subtype tag if available */}
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
          })}
        </g>
      </svg>
    </div>
  );
}
