"use client";

import React, { useState, useRef, useEffect, useCallback, useMemo } from "react";
import { GraphNode, GraphEdge, NodeType } from "./types";
import { GraphNodeComponent } from "./GraphNode";
import { GraphEdgeComponent } from "./GraphEdge";
import { NodeContextMenu } from "./NodeContextMenu";

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
  onExpandNeighbors?: (nodeId: string) => void;
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
  onExpandNeighbors,
}: ThreatGraphProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  // Local mutable positions for drag & force layout simulation
  const [nodes, setNodes] = useState<GraphNode[]>(initialNodes);
  const [viewTransform, setViewTransform] = useState({ x: 550, y: 340, zoom: 0.95 });
  const [isPanning, setIsPanning] = useState(false);
  const [panStart, setPanStart] = useState({ x: 0, y: 0 });
  const [draggedNodeId, setDraggedNodeId] = useState<string | null>(null);
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });
  const [hoveredNodeId, setHoveredNodeId] = useState<string | null>(null);

  // Right-click context menu state
  const [contextMenu, setContextMenu] = useState<{
    node: GraphNode;
    x: number;
    y: number;
  } | null>(null);

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

  // Pan interactions
  const handleMouseDown = (e: React.MouseEvent) => {
    if (e.button === 2) return; // Right-click handled separately
    if (e.target === containerRef.current || (e.target as HTMLElement).tagName === "svg") {
      setIsPanning(true);
      setPanStart({ x: e.clientX - viewTransform.x, y: e.clientY - viewTransform.y });
      onSelectNode(null);
      onSelectEdge(null);
      setContextMenu(null);
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
    if (e.button === 2) return; // Right-click handled by context menu
    e.stopPropagation();
    setDraggedNodeId(node.id);
    const rect = containerRef.current?.getBoundingClientRect();
    if (!rect) return;
    const mouseCanvasX = (e.clientX - rect.left - viewTransform.x) / viewTransform.zoom;
    const mouseCanvasY = (e.clientY - rect.top - viewTransform.y) / viewTransform.zoom;
    setDragOffset({ x: mouseCanvasX - node.x, y: mouseCanvasY - node.y });
    onSelectNode(node);
    setContextMenu(null);
  };

  // Node context menu handler
  const handleNodeContextMenu = (e: React.MouseEvent, node: GraphNode) => {
    e.preventDefault();
    e.stopPropagation();
    setContextMenu({
      node,
      x: e.clientX,
      y: e.clientY,
    });
  };

  // Context menu actions
  const handleCopyIdentifier = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  const handleInspectDetails = (node: GraphNode) => {
    onSelectNode(node);
  };

  const handleExpandNeighbors = (nodeId: string) => {
    if (onExpandNeighbors) {
      onExpandNeighbors(nodeId);
    } else {
      const targetNode = nodes.find((n) => n.id === nodeId);
      if (targetNode) {
        onSelectNode(targetNode);
      }
    }
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
          {/* Edges rendered via modular GraphEdgeComponent */}
          {visibleEdges.map((edge) => {
            const src = nodeMap.get(edge.source);
            const tgt = nodeMap.get(edge.target);
            if (!src || !tgt) return null;

            const isSelected = selectedEdgeId === edge.id;
            const isConnectedToFocus = activeFocusId ? connectedEdgeIds.has(edge.id) : true;

            return (
              <GraphEdgeComponent
                key={edge.id}
                edge={edge}
                sourceNode={src}
                targetNode={tgt}
                isSelected={isSelected}
                activeFocusId={activeFocusId}
                isConnectedToFocus={isConnectedToFocus}
                onClick={(e, clickedEdge) => {
                  e.stopPropagation();
                  onSelectEdge(clickedEdge);
                }}
              />
            );
          })}

          {/* Nodes rendered via modular GraphNodeComponent */}
          {visibleNodes.map((node) => {
            const isSelected = selectedNodeId === node.id;
            const isHovered = hoveredNodeId === node.id;
            const isConnected = activeFocusId ? connectedNodeIds.has(node.id) : true;
            const isSearchMatch = Boolean(
              searchQuery && node.label.toLowerCase().includes(searchQuery.toLowerCase())
            );
            const opacity = activeFocusId ? (isConnected ? 1 : 0.25) : 1;

            return (
              <GraphNodeComponent
                key={node.id}
                node={node}
                isSelected={isSelected}
                isHovered={isHovered}
                isConnected={isConnected}
                isSearchMatch={isSearchMatch}
                opacity={opacity}
                onMouseDown={handleNodeMouseDown}
                onMouseEnter={() => setHoveredNodeId(node.id)}
                onMouseLeave={() => setHoveredNodeId(null)}
                onContextMenu={handleNodeContextMenu}
              />
            );
          })}
        </g>
      </svg>

      {/* Floating Right-Click Context Menu */}
      {contextMenu && (
        <NodeContextMenu
          node={contextMenu.node}
          position={{ x: contextMenu.x, y: contextMenu.y }}
          onClose={() => setContextMenu(null)}
          onInspectDetails={handleInspectDetails}
          onCopyIdentifier={handleCopyIdentifier}
          onExpandNeighbors={handleExpandNeighbors}
        />
      )}
    </div>
  );
}
