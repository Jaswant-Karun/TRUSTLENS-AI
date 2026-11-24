"use client";

import React, { useState, useCallback, useMemo } from "react";
import { InvestigationData, GraphNode, GraphEdge, TimelineEvent, NodeType } from "./types";
import { TopNavigation } from "./TopNavigation";
import { ThreatGraph } from "./ThreatGraph";
import { GraphToolbar } from "./GraphToolbar";
import { GraphMinimap } from "./GraphMinimap";
import { ObjectInspector } from "./ObjectInspector";
import { InvestigationTimeline } from "./InvestigationTimeline";
import { CreateInvestigationModal } from "./CreateInvestigationModal";

interface InvestigationWorkspaceProps {
  investigation: InvestigationData;
  onUpdateInvestigation?: (updated: InvestigationData) => void;
}

const ALL_NODE_TYPES: NodeType[] = [
  "message",
  "url",
  "domain",
  "ip",
  "scam_category",
  "tactic",
  "campaign_cluster",
  "user_report",
  "threat_indicator",
  "source_reference",
];

export function InvestigationWorkspace({
  investigation: initialInvestigation,
  onUpdateInvestigation,
}: InvestigationWorkspaceProps) {
  const [investigation, setInvestigation] = useState<InvestigationData>(initialInvestigation);
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [selectedEdge, setSelectedEdge] = useState<GraphEdge | null>(null);
  const [selectedEvent, setSelectedEvent] = useState<TimelineEvent | null>(null);

  // Graph viewport & tools state
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedTypes, setSelectedTypes] = useState<Set<NodeType>>(
    new Set<NodeType>(ALL_NODE_TYPES)
  );
  const [showMinimap, setShowMinimap] = useState(true);
  const [zoomLevel, setZoomLevel] = useState(1.0);
  const [viewState, setViewState] = useState({
    x: 0,
    y: 0,
    zoom: 1.0,
    bounds: { minX: -600, maxX: 600, minY: -400, maxY: 400 },
  });

  // Panel collapse states
  const [isInspectorCollapsed, setIsInspectorCollapsed] = useState(false);
  const [isTimelineCollapsed, setIsTimelineCollapsed] = useState(false);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);

  // Search match count calculation
  const searchMatchesCount = useMemo(() => {
    if (!searchQuery.trim()) return undefined;
    return investigation.nodes.filter((n) =>
      n.label.toLowerCase().includes(searchQuery.toLowerCase())
    ).length;
  }, [searchQuery, investigation.nodes]);

  // Handle node selection
  const handleSelectNode = useCallback((node: GraphNode | null) => {
    setSelectedNode(node);
    if (node) {
      setSelectedEdge(null);
      setIsInspectorCollapsed(false); // Auto-expand inspector when object is clicked
    }
  }, []);

  // Handle edge selection
  const handleSelectEdge = useCallback((edge: GraphEdge | null) => {
    setSelectedEdge(edge);
    if (edge) {
      setSelectedNode(null);
    }
  }, []);

  // Handle timeline event selection -> jump to related node
  const handleSelectEvent = useCallback(
    (event: TimelineEvent | null) => {
      setSelectedEvent(event);
      if (event && event.relatedNodeIds && event.relatedNodeIds.length > 0) {
        const targetNode = investigation.nodes.find((n) => n.id === event.relatedNodeIds![0]);
        if (targetNode) {
          setSelectedNode(targetNode);
          setIsInspectorCollapsed(false);
        }
      }
    },
    [investigation.nodes]
  );

  // Filter object types
  const handleToggleType = useCallback((type: NodeType) => {
    setSelectedTypes((prev) => {
      const next = new Set(prev);
      if (next.has(type)) {
        next.delete(type);
      } else {
        next.add(type);
      }
      return next;
    });
  }, []);

  const handleSelectAllTypes = useCallback(() => {
    setSelectedTypes(new Set<NodeType>(ALL_NODE_TYPES));
  }, []);

  const handleClearAllTypes = useCallback(() => {
    setSelectedTypes(new Set<NodeType>());
  }, []);

  // Zoom controls
  const handleZoomIn = () => setZoomLevel((z) => Math.min(z * 1.2, 3.0));
  const handleZoomOut = () => setZoomLevel((z) => Math.max(z * 0.8, 0.25));
  const handleFitScreen = () => {
    setZoomLevel(0.95);
    setViewState((prev) => ({ ...prev, x: 550, y: 340, zoom: 0.95 }));
  };
  const handleResetLayout = () => {
    setInvestigation({ ...initialInvestigation });
    setZoomLevel(0.95);
    setSelectedNode(null);
    setSelectedEdge(null);
    setSelectedEvent(null);
  };

  // Create new investigation modal handler
  const handleCreateSubmit = (data: any) => {
    const newInv: InvestigationData = {
      ...investigation,
      id: `INV-${Date.now().toString().slice(-4)}`,
      title: data.title,
      description: data.description || "Active security incident initialized by analyst.",
      severity: data.severity,
      tags: data.tags,
      created: {
        date: "Just now",
        author: "Senior Analyst (RS)",
        relative: "Seconds ago",
      },
      lastModified: {
        date: "Just now",
        author: "Senior Analyst (RS)",
        relative: "Seconds ago",
      },
    };
    setInvestigation(newInv);
    if (onUpdateInvestigation) onUpdateInvestigation(newInv);
  };

  return (
    <div className="w-screen h-screen flex flex-col bg-[#171C25] text-slate-100 overflow-hidden font-sans">
      {/* 1. ThreatQ Persistent Top Navigation Bar */}
      <TopNavigation
        onCreateClick={() => setIsCreateModalOpen(true)}
        onSearchClick={() => {
          const input = document.querySelector('input[placeholder="Filter nodes..."]') as HTMLInputElement;
          if (input) input.focus();
        }}
      />

      {/* 2. Main Workspace Body (Graph + Side Inspector) */}
      <div className="flex-1 flex min-h-0 relative overflow-hidden">
        {/* Central Graph Canvas Container */}
        <div className="flex-1 relative h-full overflow-hidden bg-[#181E28]">
          {/* Floating Graph Controls Toolbar (Top Left) */}
          <GraphToolbar
            searchQuery={searchQuery}
            onSearchChange={setSearchQuery}
            onZoomIn={handleZoomIn}
            onZoomOut={handleZoomOut}
            onFitScreen={handleFitScreen}
            onResetLayout={handleResetLayout}
            showMinimap={showMinimap}
            onToggleMinimap={() => setShowMinimap(!showMinimap)}
            selectedTypes={selectedTypes}
            onToggleType={handleToggleType}
            onSelectAllTypes={handleSelectAllTypes}
            onClearAllTypes={handleClearAllTypes}
            syncStatus="Live Intelligence Sync Active"
            matchesCount={searchMatchesCount}
          />

          {/* Floating Minimap Bird's-Eye (Top Left underneath toolbar) */}
          {showMinimap && (
            <GraphMinimap
              nodes={investigation.nodes}
              viewState={viewState}
              onClose={() => setShowMinimap(false)}
            />
          )}

          {/* Interactive Threat Graph Engine */}
          <ThreatGraph
            nodes={investigation.nodes}
            edges={investigation.edges}
            selectedNodeId={selectedNode?.id || null}
            selectedEdgeId={selectedEdge?.id || null}
            onSelectNode={handleSelectNode}
            onSelectEdge={handleSelectEdge}
            searchQuery={searchQuery}
            typeFilter={selectedTypes}
            zoomLevel={zoomLevel}
            onZoomChange={setZoomLevel}
            onViewChange={setViewState}
          />
        </div>

        {/* 3. Persistent Right-Side Object Inspector Panel */}
        <ObjectInspector
          investigation={investigation}
          selectedNode={selectedNode}
          selectedEdge={selectedEdge}
          onCloseSelection={() => setSelectedNode(null)}
          onSelectNodeById={(id) => {
            const found = investigation.nodes.find((n) => n.id === id);
            if (found) setSelectedNode(found);
          }}
          isCollapsed={isInspectorCollapsed}
          onToggleCollapse={() => setIsInspectorCollapsed(!isInspectorCollapsed)}
        />
      </div>

      {/* 4. Persistent Bottom Investigation Timeline */}
      <InvestigationTimeline
        events={investigation.timeline}
        selectedEventId={selectedEvent?.id || null}
        onSelectEvent={handleSelectEvent}
        isCollapsed={isTimelineCollapsed}
        onToggleCollapse={() => setIsTimelineCollapsed(!isTimelineCollapsed)}
      />

      {/* 5. Create Investigation Modal */}
      <CreateInvestigationModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        onSubmit={handleCreateSubmit}
      />
    </div>
  );
}
