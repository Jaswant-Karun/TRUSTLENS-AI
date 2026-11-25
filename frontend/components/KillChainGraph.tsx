"use client";

import React, { useEffect, useState } from "react";
import {
  Network,
  ShieldAlert,
  ShieldCheck,
  AlertCircle,
  ExternalLink,
  ChevronRight,
  Info,
  Layers,
  ArrowRight,
  Maximize2,
  ZoomIn,
  ZoomOut,
  RotateCcw,
  CheckSquare,
  Square,
  X,
  Search,
  Copy,
  Check,
  Globe,
  Phone,
  Hash,
  Filter,
} from "lucide-react";
import { getCampaigns, getCampaignDetail, CampaignSummary, CampaignDetail } from "@/lib/api";
import { SkeletonCard } from "./ui/LoadingStates";

interface KillChainGraphProps {
  id?: string;
}

interface GraphNode {
  id: string;
  name: string;
  type: "technique" | "group" | "software" | "filetype";
  x: number;
  y: number;
  r: number;
  metrics: { total: number; delivered: number; blocked: number };
  deliveryRate: number;
}

export default function KillChainGraph({ id }: KillChainGraphProps) {
  const [campaigns, setCampaigns] = useState<CampaignSummary[]>([]);
  const [selectedCampaign, setSelectedCampaign] = useState<CampaignSummary | null>(null);
  const [campaignDetail, setCampaignDetail] = useState<any | null>(null);
  const [loadingDetail, setLoadingDetail] = useState(false);
  const [loading, setLoading] = useState(true);

  // Search & Filter state for Campaign Clusters
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [copiedExemplar, setCopiedExemplar] = useState(false);
  const [copiedIoc, setCopiedIoc] = useState<string | null>(null);

  // Graph state (from Image 3: Threat Intelligence Relationships)
  const [zoomLevel, setZoomLevel] = useState(129);
  const [activeFilters, setActiveFilters] = useState({
    technique: true,
    group: true,
    software: true,
    filetype: true,
  });

  // Nodes for the radial constellation graph
  const nodes: GraphNode[] = [
    { id: "hub", name: "Containers / Cluster Hub", type: "software", x: 250, y: 175, r: 24, metrics: { total: 47, delivered: 32, blocked: 15 }, deliveryRate: 68 },
    { id: "n1", name: "Scripting (PowerShell)", type: "technique", x: 190, y: 185, r: 16, metrics: { total: 14, delivered: 8, blocked: 6 }, deliveryRate: 57 },
    { id: "n2", name: "ZIP Archive Payload", type: "filetype", x: 260, y: 250, r: 19, metrics: { total: 28, delivered: 19, blocked: 9 }, deliveryRate: 67 },
    { id: "n3", name: "TGZ Compressed Lure", type: "filetype", x: 330, y: 195, r: 11, metrics: { total: 9, delivered: 5, blocked: 4 }, deliveryRate: 55 },
    { id: "n4", name: "BZ2 Packed Trojan", type: "filetype", x: 310, y: 235, r: 8, metrics: { total: 5, delivered: 2, blocked: 3 }, deliveryRate: 40 },
    { id: "n5", name: "RAR Obfuscation", type: "filetype", x: 265, y: 95, r: 13, metrics: { total: 12, delivered: 7, blocked: 5 }, deliveryRate: 58 },
    { id: "n6", name: "SQUASHFS Dropper", type: "filetype", x: 160, y: 135, r: 10, metrics: { total: 7, delivered: 3, blocked: 4 }, deliveryRate: 42 },
    { id: "n7", name: "LZMA Compressed", type: "filetype", x: 150, y: 175, r: 9, metrics: { total: 6, delivered: 4, blocked: 2 }, deliveryRate: 66 },
    { id: "n8", name: "WIM Image", type: "filetype", x: 150, y: 215, r: 8, metrics: { total: 4, delivered: 2, blocked: 2 }, deliveryRate: 50 },
    { id: "n9", name: "GZ Lure Container", type: "filetype", x: 165, y: 250, r: 9, metrics: { total: 8, delivered: 5, blocked: 3 }, deliveryRate: 62 },
    { id: "n10", name: "CPIO Archive", type: "filetype", x: 195, y: 275, r: 8, metrics: { total: 5, delivered: 3, blocked: 2 }, deliveryRate: 60 },
    { id: "n11", name: "TAR Package", type: "filetype", x: 220, y: 290, r: 7, metrics: { total: 3, delivered: 1, blocked: 2 }, deliveryRate: 33 },
    { id: "n12", name: "7Z High Compression", type: "filetype", x: 238, y: 285, r: 9, metrics: { total: 11, delivered: 7, blocked: 4 }, deliveryRate: 63 },
    { id: "n13", name: "ROO Dropper", type: "filetype", x: 235, y: 90, r: 8, metrics: { total: 4, delivered: 2, blocked: 2 }, deliveryRate: 50 },
    { id: "n14", name: "FAT FS Mount", type: "filetype", x: 315, y: 140, r: 9, metrics: { total: 6, delivered: 3, blocked: 3 }, deliveryRate: 50 },
    { id: "n15", name: "SWM Segmented", type: "filetype", x: 195, y: 105, r: 8, metrics: { total: 5, delivered: 2, blocked: 3 }, deliveryRate: 40 },
  ];

  const [selectedNode, setSelectedNode] = useState<GraphNode>(nodes[1]); // Default to Scripting

  useEffect(() => {
    let isMounted = true;
    getCampaigns(12)
      .then((data) => {
        if (isMounted) {
          setCampaigns(data);
          if (data && data.length > 0) {
            setSelectedCampaign(data[0]);
          }
          setLoading(false);
        }
      })
      .catch(() => {
        if (isMounted) setLoading(false);
      });
    return () => {
      isMounted = false;
    };
  }, []);

  useEffect(() => {
    if (selectedCampaign) {
      const id = selectedCampaign.cluster_id ?? selectedCampaign.campaign_id;
      if (id !== undefined) {
        setLoadingDetail(true);
        getCampaignDetail(id)
          .then((res) => {
            setCampaignDetail(res);
            setLoadingDetail(false);
          })
          .catch(() => {
            setLoadingDetail(false);
          });
      }
    }
  }, [selectedCampaign]);

  const handleCopyText = (text: string, isExemplar: boolean) => {
    navigator.clipboard.writeText(text);
    if (isExemplar) {
      setCopiedExemplar(true);
      setTimeout(() => setCopiedExemplar(false), 2000);
    } else {
      setCopiedIoc(text);
      setTimeout(() => setCopiedIoc(null), 2000);
    }
  };

  const filteredCampaigns = campaigns.filter((camp) => {
    const campId = String(camp.cluster_id ?? camp.campaign_id ?? "");
    const targetName = (camp.targeted_entity ?? camp.target_brand ?? "").toLowerCase();
    const campName = (camp.campaign_name ?? "").toLowerCase();
    const q = searchQuery.toLowerCase();
    const matchQuery = !q || campId.includes(q) || targetName.includes(q) || campName.includes(q);
    const matchStatus = statusFilter === "all" || (camp.status || "active").toLowerCase() === statusFilter.toLowerCase();
    return matchQuery && matchStatus;
  });

  if (loading) {
    return <SkeletonCard />;
  }

  const toggleFilter = (key: keyof typeof activeFilters) => {
    setActiveFilters((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  const visibleNodes = nodes.filter((n) => {
    if (n.id === "hub") return true;
    return activeFilters[n.type];
  });

  return (
    <div id={id} className="space-y-6">
      {/* 1. Threat Intelligence Relationships Graph (from Image 3) */}
      <div className="bg-[#0b1329] text-white rounded-xl border border-slate-800 shadow-2xl p-5 overflow-hidden">
        {/* Header and Filter Legend */}
        <div className="flex flex-col lg:flex-row lg:items-center justify-between pb-4 border-b border-slate-800 gap-4">
          <div>
            <h2 className="text-base font-bold text-white flex items-center gap-2">
              <Network className="w-4 h-4 text-cyan-400" />
              Threat Intelligence Relationships
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Node size indicates frequency. Connections show shared attributes between payloads. Highlighting delivered payloads.
            </p>
          </div>

          {/* Interactive Checkbox Filters & Controls */}
          <div className="flex flex-wrap items-center gap-3 text-xs font-mono">
            {/* Filter checkboxes */}
            <button
              onClick={() => toggleFilter("technique")}
              className={`flex items-center space-x-1.5 px-2 py-1 rounded border transition-colors ${
                activeFilters.technique
                  ? "bg-purple-950/40 border-purple-500/40 text-purple-300"
                  : "bg-slate-900 border-slate-800 text-slate-500 line-through"
              }`}
            >
              <span className="w-2 h-2 rounded-full bg-purple-500"></span>
              <span>Attack Techniques</span>
            </button>

            <button
              onClick={() => toggleFilter("group")}
              className={`flex items-center space-x-1.5 px-2 py-1 rounded border transition-colors ${
                activeFilters.group
                  ? "bg-rose-950/40 border-rose-500/40 text-rose-300"
                  : "bg-slate-900 border-slate-800 text-slate-500 line-through"
              }`}
            >
              <span className="w-2 h-2 rounded-full bg-rose-500"></span>
              <span>Threat Groups</span>
            </button>

            <button
              onClick={() => toggleFilter("software")}
              className={`flex items-center space-x-1.5 px-2 py-1 rounded border transition-colors ${
                activeFilters.software
                  ? "bg-amber-950/40 border-amber-500/40 text-amber-300"
                  : "bg-slate-900 border-slate-800 text-slate-500 line-through"
              }`}
            >
              <span className="w-2 h-2 rounded-full bg-amber-500"></span>
              <span>Software</span>
            </button>

            <button
              onClick={() => toggleFilter("filetype")}
              className={`flex items-center space-x-1.5 px-2 py-1 rounded border transition-colors ${
                activeFilters.filetype
                  ? "bg-cyan-950/40 border-cyan-500/40 text-cyan-300"
                  : "bg-slate-900 border-slate-800 text-slate-500 line-through"
              }`}
            >
              <span className="w-2 h-2 rounded-full bg-cyan-400"></span>
              <span>File Types</span>
            </button>
          </div>
        </div>

        {/* Graph Canvas & Docked Node Details Card */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 my-4 items-center">
          {/* Constellation Network SVG (2 cols) */}
          <div className="lg:col-span-2 relative h-[360px] bg-slate-950/60 rounded-xl border border-slate-900 flex items-center justify-center overflow-hidden">
            {/* Top Right Zoom Controls (Image 3) */}
            <div className="absolute top-3 right-3 flex items-center space-x-1 bg-slate-900/90 border border-slate-800 rounded-lg p-1 text-slate-400 text-xs font-mono z-10">
              <button
                onClick={() => setZoomLevel(100)}
                className="p-1 hover:text-white hover:bg-slate-800 rounded"
                title="Fit to Screen"
              >
                <Maximize2 className="w-3.5 h-3.5" />
              </button>
              <button
                onClick={() => setZoomLevel((z) => Math.min(z + 10, 180))}
                className="p-1 hover:text-white hover:bg-slate-800 rounded"
                title="Zoom In"
              >
                <ZoomIn className="w-3.5 h-3.5" />
              </button>
              <span className="px-1.5 font-bold text-cyan-400">{zoomLevel}%</span>
              <button
                onClick={() => setZoomLevel((z) => Math.max(z - 10, 70))}
                className="p-1 hover:text-white hover:bg-slate-800 rounded"
                title="Zoom Out"
              >
                <ZoomOut className="w-3.5 h-3.5" />
              </button>
              <button
                onClick={() => setZoomLevel(129)}
                className="p-1 hover:text-white hover:bg-slate-800 rounded"
                title="Reset"
              >
                <RotateCcw className="w-3.5 h-3.5" />
              </button>
            </div>

            {/* SVG Radial Graph */}
            <svg
              viewBox="100 50 300 270"
              className="w-full h-full transition-transform duration-300"
              style={{ transform: `scale(${zoomLevel / 129})` }}
            >
              {/* Lines from hub to visible nodes */}
              {visibleNodes.map((n) => {
                if (n.id === "hub") return null;
                const isSelected = selectedNode?.id === n.id;
                return (
                  <line
                    key={n.id}
                    x1={nodes[0].x}
                    y1={nodes[0].y}
                    x2={n.x}
                    y2={n.y}
                    stroke={isSelected ? "#38bdf8" : "#334155"}
                    strokeWidth={isSelected ? "2" : "1"}
                    strokeOpacity={isSelected ? "0.9" : "0.5"}
                  />
                );
              })}

              {/* Central Hub Node */}
              <circle
                cx={nodes[0].x}
                cy={nodes[0].y}
                r={nodes[0].r}
                fill="#4338ca"
                stroke="#6366f1"
                strokeWidth="2.5"
                className="cursor-pointer hover:opacity-90"
                onClick={() => setSelectedNode(nodes[0])}
              />
              <text
                x={nodes[0].x}
                y={nodes[0].y + 3}
                textAnchor="middle"
                fill="#ffffff"
                fontSize="8"
                fontFamily="sans-serif"
                fontWeight="bold"
                pointerEvents="none"
              >
                Containers
              </text>

              {/* Satellite Orbiting Nodes */}
              {visibleNodes.map((n) => {
                if (n.id === "hub") return null;
                const isSelected = selectedNode?.id === n.id;
                const nodeColor =
                  n.type === "technique"
                    ? "#6366f1"
                    : n.type === "group"
                    ? "#f43f5e"
                    : n.type === "software"
                    ? "#f59e0b"
                    : "#14b8a6";

                return (
                  <g
                    key={n.id}
                    className="cursor-pointer transition-transform hover:scale-125"
                    onClick={() => setSelectedNode(n)}
                  >
                    <circle
                      cx={n.x}
                      cy={n.y}
                      r={n.r}
                      fill={nodeColor}
                      stroke={isSelected ? "#ffffff" : nodeColor}
                      strokeWidth={isSelected ? "2.5" : "1"}
                      opacity={isSelected ? "1" : "0.85"}
                    />
                    <text
                      x={n.x}
                      y={n.y + 16}
                      textAnchor="middle"
                      fill="#94a3b8"
                      fontSize="6.5"
                      fontFamily="monospace"
                      fontWeight="bold"
                      pointerEvents="none"
                    >
                      {n.name.split(" ")[0]}
                    </text>
                  </g>
                );
              })}
            </svg>
          </div>

          {/* Right: Docked Node Details Card (from Image 3) */}
          <div className="bg-slate-900/90 rounded-xl border border-slate-800 p-5 flex flex-col justify-between h-[360px]">
            <div>
              <div className="flex items-center justify-between pb-3 border-b border-slate-800 mb-4">
                <span className="text-xs font-bold text-slate-100">Node Details</span>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-800 uppercase">
                  {selectedNode.type}
                </span>
              </div>

              <div className="space-y-4 font-mono">
                <div>
                  <span className="text-[10px] text-slate-400 uppercase block">Name</span>
                  <div className="text-sm font-bold text-white mt-0.5">{selectedNode.name}</div>
                </div>

                <div>
                  <span className="text-[10px] text-slate-400 uppercase block">Type</span>
                  <div className="flex items-center space-x-1.5 mt-0.5 text-xs text-slate-300">
                    <span
                      className="w-2 h-2 rounded-full"
                      style={{
                        backgroundColor:
                          selectedNode.type === "technique"
                            ? "#6366f1"
                            : selectedNode.type === "filetype"
                            ? "#14b8a6"
                            : "#f59e0b",
                      }}
                    ></span>
                    <span className="capitalize">{selectedNode.type}</span>
                  </div>
                </div>

                {/* Metrics Breakdown (Total, Delivered, Blocked) */}
                <div>
                  <span className="text-[10px] text-slate-400 uppercase block mb-1">Metrics</span>
                  <div className="grid grid-cols-3 gap-2 text-center bg-slate-950 p-2.5 rounded-lg border border-slate-800">
                    <div>
                      <span className="text-base font-bold text-white block">{selectedNode.metrics.total}</span>
                      <span className="text-[9px] text-slate-400 block">Total</span>
                    </div>
                    <div>
                      <span className="text-base font-bold text-cyan-400 block">{selectedNode.metrics.delivered}</span>
                      <span className="text-[9px] text-slate-400 block">Delivered</span>
                    </div>
                    <div>
                      <span className="text-base font-bold text-rose-400 block">{selectedNode.metrics.blocked}</span>
                      <span className="text-[9px] text-slate-400 block">Blocked</span>
                    </div>
                  </div>
                </div>

                {/* Delivery Rate Bar (from Image 3) */}
                <div>
                  <div className="flex justify-between items-center text-xs mb-1">
                    <span className="text-slate-400">Delivery Rate:</span>
                    <span className="text-cyan-400 font-bold">{selectedNode.deliveryRate}% delivered</span>
                  </div>
                  <div className="w-full h-2 rounded-full bg-slate-800 overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-teal-500 to-cyan-400 rounded-full transition-all duration-500"
                      style={{ width: `${selectedNode.deliveryRate}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            </div>

            <div className="text-[10px] font-mono text-slate-500 pt-3 border-t border-slate-800 text-center">
              ● Click any constellation node to inspect its telemetry
            </div>
          </div>
        </div>
      </div>

      {/* 2. Coordinated Campaign Clusters & Attack Lifecycle Pipeline */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-subtle p-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between pb-4 mb-5 border-b border-slate-100 gap-3">
          <div>
            <div className="flex items-center space-x-2">
              <Network className="w-4 h-4 text-sky-600" />
              <h3 className="text-base font-bold text-slate-900">Campaign Clusters & Attack Lifecycle Pipeline</h3>
              <span className="text-xs px-2 py-0.5 rounded-full bg-sky-50 text-sky-700 font-mono font-medium border border-sky-200">
                HDBSCAN Model 4
              </span>
            </div>
            <p className="text-xs text-slate-500 mt-0.5">
              Correlated scam campaigns grouped by sentence transformer embeddings and shared domain footprints.
            </p>
          </div>

          <div className="text-xs font-mono text-slate-500 bg-slate-50 px-2.5 py-1 rounded border border-slate-200">
            {campaigns.length} Discovered Active Clusters
          </div>
        </div>

        {/* Grid: Left Cluster Selector, Right Kill-Chain Lifecycle */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left: Discovered Campaign Clusters List with Search & Filters */}
          <div className="space-y-3">
            {/* Search & Filter Controls */}
            <div className="space-y-2">
              <div className="relative">
                <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-2.5" />
                <input
                  type="text"
                  placeholder="Filter by ID, entity (e.g. SBI, Paytm)..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full text-xs font-mono pl-8 pr-3 py-1.5 rounded-lg border border-slate-300 bg-white focus:outline-none focus:ring-1 focus:ring-sky-500"
                />
              </div>

              <div className="flex items-center space-x-2">
                <select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  className="text-[11px] font-mono px-2 py-1 rounded border border-slate-300 bg-white flex-1"
                >
                  <option value="all">All Statuses</option>
                  <option value="active">Active Only</option>
                  <option value="mitigated">Mitigated</option>
                </select>
                <span className="text-[11px] font-mono text-slate-400">
                  {filteredCampaigns.length} shown
                </span>
              </div>
            </div>

            <div className="space-y-2 max-h-[460px] overflow-y-auto pr-1">
              {filteredCampaigns.length === 0 ? (
                <div className="p-4 bg-slate-50 rounded-lg text-xs text-slate-500 text-center">
                  No clusters match criteria.
                </div>
              ) : (
                filteredCampaigns.map((camp) => {
                  const campId = camp.cluster_id ?? camp.campaign_id ?? 0;
                  const targetName = camp.targeted_entity ?? camp.target_brand ?? "Financial Institution";
                  const tacticsName = Array.isArray(camp.primary_tactics)
                    ? camp.primary_tactics.join(", ")
                    : camp.primary_tactic || "Phishing Lure";
                  const isSelected = (selectedCampaign?.cluster_id ?? selectedCampaign?.campaign_id) === campId;

                  return (
                    <button
                      key={campId}
                      onClick={() => setSelectedCampaign(camp)}
                      className={`w-full text-left p-3 rounded-lg border transition-all flex flex-col justify-between ${
                        isSelected
                          ? "border-sky-500 bg-sky-50/70 shadow-sm"
                          : "border-slate-200 hover:border-slate-300 bg-white"
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-bold text-slate-900 truncate max-w-[170px]">
                          Cluster #{campId}: {targetName}
                        </span>
                        <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-100 text-slate-600 border border-slate-200 shrink-0">
                          Cohesion: {Math.round(camp.cohesion_score * 100)}%
                        </span>
                      </div>
                      <div className="flex items-center justify-between text-[11px] text-slate-500 mt-2 font-mono">
                        <span className="truncate max-w-[140px]">{tacticsName}</span>
                        <span className="font-semibold text-slate-700 shrink-0">{camp.cluster_size} msgs</span>
                      </div>
                    </button>
                  );
                })
              )}
            </div>
          </div>

          {/* Right: Comprehensive Campaign Dossier & Forensic Breakdown */}
          <div className="lg:col-span-2 bg-slate-50/70 border border-slate-200 rounded-xl p-5 flex flex-col justify-between space-y-4">
            <div className="space-y-4">
              {/* Dossier Header */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-3 border-b border-slate-200 gap-2">
                <div>
                  <span className="text-[11px] font-mono uppercase text-slate-400 font-medium">
                    Cluster Dossier #{selectedCampaign?.cluster_id ?? selectedCampaign?.campaign_id ?? 0}
                  </span>
                  <h4 className="text-sm font-bold text-slate-900">
                    {selectedCampaign
                      ? `Cluster #${selectedCampaign.cluster_id ?? selectedCampaign.campaign_id} — ${
                          selectedCampaign.targeted_entity ?? selectedCampaign.target_brand ?? "Target"
                        }`
                      : "Campaign Dossier"}
                  </h4>
                </div>

                <div className="flex items-center space-x-2">
                  <span className="text-xs px-2 py-0.5 rounded-full bg-sky-100 text-sky-800 border border-sky-300 font-mono font-medium">
                    Cohesion: {Math.round((selectedCampaign?.cohesion_score || 0.8) * 100)}%
                  </span>
                  <span className="text-xs px-2.5 py-0.5 rounded-full bg-amber-50 text-amber-700 border border-amber-200 font-mono font-medium">
                    Status: {(selectedCampaign?.status || "ACTIVE").toUpperCase()}
                  </span>
                </div>
              </div>

              {/* Exemplar Message Card */}
              <div className="p-3.5 bg-white rounded-lg border border-slate-200 shadow-subtle space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-[11px] font-mono uppercase text-slate-500 font-semibold flex items-center gap-1.5">
                    <AlertCircle className="w-3.5 h-3.5 text-sky-600" />
                    Observed Exemplar Communication
                  </span>
                  {campaignDetail?.exemplar_message && (
                    <button
                      onClick={() => handleCopyText(campaignDetail.exemplar_message, true)}
                      className="text-[11px] font-mono text-sky-600 hover:text-sky-800 flex items-center space-x-1"
                    >
                      {copiedExemplar ? (
                        <>
                          <Check className="w-3 h-3 text-emerald-600" />
                          <span>Copied</span>
                        </>
                      ) : (
                        <>
                          <Copy className="w-3 h-3" />
                          <span>Copy Exemplar</span>
                        </>
                      )}
                    </button>
                  )}
                </div>

                <div className="p-2.5 bg-slate-50 rounded border border-slate-200 text-xs font-mono text-slate-800 leading-relaxed">
                  {loadingDetail ? (
                    <span className="text-slate-400 italic">Fetching exemplar from dossier...</span>
                  ) : campaignDetail?.exemplar_message ? (
                    campaignDetail.exemplar_message
                  ) : (
                    "URGENT: Security alert regarding your account. Immediate verification required via secure gateway."
                  )}
                </div>
              </div>

              {/* Shared Phrases & Technical Indicators Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {/* Shared Recurring Phrases */}
                <div className="p-3 bg-white rounded-lg border border-slate-200 shadow-subtle space-y-2">
                  <span className="text-[11px] font-mono uppercase text-slate-500 font-semibold block">
                    Shared Recurring Phrases
                  </span>
                  <div className="flex flex-wrap gap-1.5">
                    {campaignDetail?.shared_phrases && campaignDetail.shared_phrases.length > 0 ? (
                      campaignDetail.shared_phrases.map((phrase: string, idx: number) => (
                        <span
                          key={idx}
                          className="px-2 py-0.5 rounded bg-slate-100 text-slate-700 border border-slate-200 text-[11px] font-mono"
                        >
                          &ldquo;{phrase}&rdquo;
                        </span>
                      ))
                    ) : (
                      <span className="text-xs text-slate-400 font-mono italic">
                        Semantic embedding proximity without strict verbatim n-grams
                      </span>
                    )}
                  </div>
                </div>

                {/* Shared Technical Indicators (IOCs) */}
                <div className="p-3 bg-white rounded-lg border border-slate-200 shadow-subtle space-y-2">
                  <span className="text-[11px] font-mono uppercase text-slate-500 font-semibold block">
                    Associated Technical Indicators
                  </span>
                  <div className="space-y-1 max-h-24 overflow-y-auto">
                    {campaignDetail?.shared_iocs?.sample_phones && campaignDetail.shared_iocs.sample_phones.length > 0 ? (
                      campaignDetail.shared_iocs.sample_phones.slice(0, 4).map((phone: string, i: number) => (
                        <div key={i} className="flex items-center justify-between text-xs font-mono text-slate-700 bg-slate-50 px-2 py-0.5 rounded border border-slate-100">
                          <span className="flex items-center gap-1">
                            <Phone className="w-3 h-3 text-amber-600" /> {phone}
                          </span>
                          <button
                            onClick={() => handleCopyText(phone, false)}
                            className="text-slate-400 hover:text-slate-700"
                            title="Copy Phone"
                          >
                            {copiedIoc === phone ? <Check className="w-3 h-3 text-emerald-600" /> : <Copy className="w-3 h-3" />}
                          </button>
                        </div>
                      ))
                    ) : (
                      <span className="text-xs text-slate-400 font-mono italic">
                        No persistent telephony identifiers observed
                      </span>
                    )}
                  </div>
                </div>
              </div>

              {/* 4-Stage Attack Lifecycle Pipeline */}
              <div className="grid grid-cols-1 sm:grid-cols-4 gap-2">
                <div className="p-2.5 bg-white rounded-lg border border-slate-200 shadow-subtle flex flex-col justify-between">
                  <div>
                    <span className="text-[9px] font-mono uppercase text-slate-400 font-semibold">1. Delivery</span>
                    <div className="text-xs font-bold text-slate-800 mt-0.5">Bulk Gateway</div>
                    <p className="text-[10px] text-slate-500 mt-0.5">Automated sender routing deceptive SMS/WhatsApp.</p>
                  </div>
                  <div className="text-[10px] text-blue-600 font-mono font-medium mt-2">Sender Header</div>
                </div>

                <div className="p-2.5 bg-white rounded-lg border border-slate-200 shadow-subtle flex flex-col justify-between">
                  <div>
                    <span className="text-[9px] font-mono uppercase text-slate-400 font-semibold">2. Pretext Lure</span>
                    <div className="text-xs font-bold text-slate-800 mt-0.5 truncate">
                      {Array.isArray(selectedCampaign?.primary_tactics)
                        ? selectedCampaign?.primary_tactics.join(", ")
                        : selectedCampaign?.primary_tactic || "Account Coercion"}
                    </div>
                    <p className="text-[10px] text-slate-500 mt-0.5 truncate">
                      Impersonation of {selectedCampaign?.targeted_entity ?? selectedCampaign?.target_brand ?? "institution"}.
                    </p>
                  </div>
                  <div className="text-[10px] text-amber-600 font-mono font-medium mt-2">Psychological Coercion</div>
                </div>

                <div className="p-2.5 bg-white rounded-lg border border-slate-200 shadow-subtle flex flex-col justify-between">
                  <div>
                    <span className="text-[9px] font-mono uppercase text-slate-400 font-semibold">3. Credential Trap</span>
                    <div className="text-xs font-bold text-slate-800 mt-0.5">Cloned Web Portal</div>
                    <p className="text-[10px] text-slate-500 mt-0.5">Typo-squatted domains hosting fake netbanking forms.</p>
                  </div>
                  <div className="text-[10px] text-rose-600 font-mono font-medium mt-2">Zero-Hop Detected</div>
                </div>

                <div className="p-2.5 bg-white rounded-lg border border-slate-200 shadow-subtle flex flex-col justify-between">
                  <div>
                    <span className="text-[9px] font-mono uppercase text-slate-400 font-semibold">4. Interception</span>
                    <div className="text-xs font-bold text-slate-800 mt-0.5">Credential Harvest</div>
                    <p className="text-[10px] text-slate-500 mt-0.5">OTP relays and unauthorized fund withdrawal.</p>
                  </div>
                  <div className="text-[10px] text-purple-600 font-mono font-medium mt-2">Active Mitigation</div>
                </div>
              </div>
            </div>

            {/* Mandatory Scientific & Legal Caveat */}
            <div className="p-3 rounded-lg bg-amber-50/80 border border-amber-200 text-xs text-amber-900 flex items-start space-x-2.5">
              <Info className="w-4 h-4 text-amber-700 shrink-0 mt-0.5" />
              <div className="text-[11px] leading-relaxed">
                <strong className="block text-amber-950 font-semibold mb-0.5">
                  Model 4 Governance & Scientific Attribution Policy
                </strong>
                Unsupervised density clustering (HDBSCAN on sentence embeddings) identifies mathematical and linguistic similarity across deceptive lures. An unsupervised cluster <strong>does not prove a single criminal organization or coordinated syndicate</strong> without external human corroboration and independent legal subpoena verification.
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
