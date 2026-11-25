"use client";

import React, { useState, useCallback, useMemo, useEffect } from "react";
import {
  InvestigationData,
  GraphNode,
  GraphEdge,
  TimelineEvent,
  NodeType,
  adaptBackendNode,
  adaptBackendEdge,
} from "./types";
import Link from "next/link";
import { LayoutGrid, Network, Search, Shield, History } from "lucide-react";
import { TopNavigation } from "./TopNavigation";
import { ThreatGraph } from "./ThreatGraph";
import { GraphToolbar } from "./GraphToolbar";
import { GraphMinimap } from "./GraphMinimap";
import { GraphLegend } from "./GraphLegend";
import { ObjectInspector } from "./ObjectInspector";
import { InvestigationTimeline } from "./InvestigationTimeline";
import { CreateInvestigationModal } from "./CreateInvestigationModal";
import { getInvestigationObjectRelationships } from "@/lib/api";

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

  // Sync state if prop changes
  useEffect(() => {
    setInvestigation(initialInvestigation);
  }, [initialInvestigation]);

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

  // Live 1-hop expansion state
  const [isExpanding, setIsExpanding] = useState(false);
  const [syncStatusMessage, setSyncStatusMessage] = useState("Live Intelligence Sync Active");

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

  // 1-Hop Relationship Expansion implementation
  const handleExpandNeighbors = useCallback(
    async (nodeId: string) => {
      setIsExpanding(true);
      setSyncStatusMessage(`Expanding 1-hop relationships for ${nodeId}...`);
      try {
        const res = await getInvestigationObjectRelationships(investigation.id, nodeId);
        if (res && res.connected_nodes) {
          const existingNodeIds = new Set(investigation.nodes.map((n) => n.id));
          const parent = investigation.nodes.find((pn) => pn.id === nodeId);

          const newNodes = res.connected_nodes
            .filter((n) => !existingNodeIds.has(n.id))
            .map((n, idx) => {
              const angle = (idx / Math.max(res.connected_nodes.length, 1)) * 2 * Math.PI;
              const adapted = adaptBackendNode(n);
              if (parent) {
                adapted.x = parent.x + Math.cos(angle) * 160;
                adapted.y = parent.y + Math.sin(angle) * 160;
              }
              return adapted;
            });

          const existingEdgeIds = new Set(investigation.edges.map((e) => e.id));
          const newEdges = res.edges
            .filter((e) => !existingEdgeIds.has(e.id))
            .map(adaptBackendEdge);

          if (newNodes.length > 0 || newEdges.length > 0) {
            const updatedInv: InvestigationData = {
              ...investigation,
              objectsCount: investigation.nodes.length + newNodes.length,
              nodes: [...investigation.nodes, ...newNodes],
              edges: [...investigation.edges, ...newEdges],
            };
            setInvestigation(updatedInv);
            if (onUpdateInvestigation) onUpdateInvestigation(updatedInv);
            setSyncStatusMessage(
              `Expanded +${newNodes.length} nodes, +${newEdges.length} edges from MongoDB`
            );
          } else {
            setSyncStatusMessage(`No additional 1-hop entities found for ${nodeId}`);
          }
        }
      } catch (err: any) {
        setSyncStatusMessage(`Expansion error: ${err?.message || "Failed"}`);
      } finally {
        setIsExpanding(false);
        setTimeout(() => setSyncStatusMessage("Live Intelligence Sync Active"), 5000);
      }
    },
    [investigation, onUpdateInvestigation]
  );

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
    <div className="w-screen h-screen flex flex-col bg-[#181E28] text-[#F8FAFC] overflow-hidden font-sans">
      {/* 1. ThreatQ Persistent Top Navigation Bar */}
      <TopNavigation
        onCreateClick={() => setIsCreateModalOpen(true)}
        onSearchClick={() => {
          const input = document.querySelector('input[placeholder="Filter nodes..."]') as HTMLInputElement;
          if (input) input.focus();
        }}
      />

      {/* 2. Main Workspace Body (Left Rail + Graph + Side Inspector) */}
      <div className="flex-1 flex min-h-0 relative overflow-hidden">
        {/* Slim Left SOC Tool Rail */}
        <aside className="hidden sm:flex w-11 bg-[#252D38] border-r border-[#3A4553] flex-col items-center py-3 space-y-3 z-20 shrink-0">
          <Link href="/dashboard" title="SOC Home" className="p-2 rounded-md text-[#94A3B8] hover:text-[#22D3EE] hover:bg-[#202936] transition-colors">
            <LayoutGrid className="w-4 h-4" />
          </Link>
          <Link href="/investigations" title="Investigation Graph Directory" className="p-2 rounded-md text-[#60A5FA] bg-[#202936] border border-[#60A5FA]/40">
            <Network className="w-4 h-4" />
          </Link>
          <Link href="/threat-library" title="Threat Library" className="p-2 rounded-md text-[#94A3B8] hover:text-[#22D3EE] hover:bg-[#202936] transition-colors">
            <Search className="w-4 h-4" />
          </Link>
          <Link href="/analyze/text" title="Analyze New Threat" className="p-2 rounded-md text-[#94A3B8] hover:text-[#22D3EE] hover:bg-[#202936] transition-colors">
            <Shield className="w-4 h-4" />
          </Link>
          <Link href="/history" title="Analysis History" className="p-2 rounded-md text-[#94A3B8] hover:text-[#22D3EE] hover:bg-[#202936] transition-colors">
            <History className="w-4 h-4" />
          </Link>
        </aside>

        {/* Central Graph Canvas Container */}
        <div
          className="flex-1 relative h-full overflow-hidden bg-[#181E28]"
          style={{
            backgroundImage:
              "radial-gradient(circle at 50% 45%, rgba(96, 165, 250, 0.06) 0%, rgba(24, 30, 40, 0) 60%), radial-gradient(rgba(148, 163, 184, 0.08) 1px, transparent 1px)",
            backgroundSize: "100% 100%, 24px 24px",
          }}
        >
          {/* Floating Graph Controls Toolbar */}
          <GraphToolbar
            searchQuery={searchQuery}
            onSearchChange={setSearchQuery}
            onZoomIn={handleZoomIn}
            onZoomOut={handleZoomOut}
            onFitScreen={handleFitScreen}
            onResetLayout={handleResetLayout}
            onRefresh={() => {
              setInvestigation({ ...initialInvestigation });
              setSyncStatusMessage("Refreshed from persisted state");
              setTimeout(() => setSyncStatusMessage("Live Intelligence Sync Active"), 3000);
            }}
            showMinimap={showMinimap}
            onToggleMinimap={() => setShowMinimap(!showMinimap)}
            selectedTypes={selectedTypes}
            onToggleType={handleToggleType}
            onSelectAllTypes={handleSelectAllTypes}
            onClearAllTypes={handleClearAllTypes}
            syncStatus={syncStatusMessage}
            matchesCount={searchMatchesCount}
          />

          {/* Floating Investigation Title Pill (Below Toolbar, Zero Overlap) */}
          <div className="absolute top-14 left-4 z-20 pointer-events-none hidden md:flex flex-col bg-[#202936]/90 backdrop-blur-md border border-[#3A4553] rounded-lg px-3.5 py-2 shadow-xl max-w-md">
            <div className="flex items-center space-x-2">
              <span className="font-mono text-xs font-bold text-[#22D3EE]">{investigation.id}</span>
              <span className="px-1.5 py-0.5 rounded text-[10px] font-mono font-bold uppercase bg-emerald-950/80 text-emerald-300 border border-emerald-700/60">
                {investigation.status}
              </span>
            </div>
            <div className="text-xs font-semibold text-[#F8FAFC] truncate mt-0.5">{investigation.title}</div>
            <div className="text-[10px] text-[#94A3B8] mt-0.5">
              Created: {investigation.created.date} • Updated: {investigation.lastModified.date}
            </div>
          </div>

          {/* Floating Minimap + Live Legend Stack (Left Side Below Title Pill) */}
          <div className="absolute top-32 left-4 z-20 hidden lg:flex flex-col space-y-2.5">
            {showMinimap && (
              <GraphMinimap
                nodes={investigation.nodes}
                viewState={viewState}
                onClose={() => setShowMinimap(false)}
              />
            )}
            <GraphLegend
              nodes={investigation.nodes}
              selectedTypes={selectedTypes}
              onToggleType={handleToggleType}
            />
          </div>

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
            onExpandNeighbors={handleExpandNeighbors}
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
          onExpandNode={handleExpandNeighbors}
          isExpanding={isExpanding}
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
