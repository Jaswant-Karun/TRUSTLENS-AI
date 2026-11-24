"use client";

import React, { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import {
  ShieldAlert,
  AlertTriangle,
  ArrowLeft,
  RotateCcw,
} from "lucide-react";
import { InvestigationWorkspace } from "@/components/investigation/InvestigationWorkspace";
import {
  InvestigationData,
  adaptBackendNode,
  adaptBackendEdge,
  adaptBackendTimeline,
} from "@/components/investigation/types";
import {
  getInvestigation,
  getInvestigationGraph,
  getInvestigationTimeline,
} from "@/lib/api";
import { EmptyInvestigationState } from "@/components/investigation/EmptyInvestigationState";

export default function InvestigationDetailPage() {
  const params = useParams();
  const router = useRouter();
  const id = (params?.id as string) || "INV-2026-0011";

  const [investigation, setInvestigation] = useState<InvestigationData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const controller = new AbortController();
    setLoading(true);
    setError(null);

    // Parallel fetch of dossier metadata, graph topology, and multi-track timeline
    Promise.all([
      getInvestigation(id, controller.signal),
      getInvestigationGraph(id, controller.signal),
      getInvestigationTimeline(id, controller.signal),
    ])
      .then(([detail, graphData, timelineData]) => {
        const adaptedNodes = (graphData.nodes || []).map(adaptBackendNode);
        const adaptedEdges = (graphData.edges || []).map(adaptBackendEdge);
        const adaptedTimeline = (timelineData.timeline || []).map(adaptBackendTimeline);

        const createdDate = new Date(detail.created_at);
        const updatedDate = new Date(detail.updated_at);

        const liveData: InvestigationData = {
          id: detail.id,
          title: detail.title,
          description: detail.description || "Active cyber threat investigation dossier.",
          severity: (detail.severity as any) || "high",
          visibility: (detail.visibility as any) || "Organization",
          status: (detail.status === "active" ? "Active" : detail.status === "mitigated" ? "Closed" : "Under Review") as any,
          created: {
            date: isNaN(createdDate.getTime()) ? detail.created_at : createdDate.toLocaleString("en-US", { dateStyle: "medium", timeStyle: "short" }),
            author: "Senior Analyst (RS)",
            relative: "Persisted in MongoDB",
          },
          lastModified: {
            date: isNaN(updatedDate.getTime()) ? detail.updated_at : updatedDate.toLocaleString("en-US", { dateStyle: "medium", timeStyle: "short" }),
            author: "SOC Lead (TK)",
            relative: "Live Intelligence",
          },
          objectsCount: adaptedNodes.length,
          tasksCount: adaptedTimeline.filter((t) => t.track === "tasks").length,
          commentsCount: detail.comments_count || 0,
          sources: detail.sources || ["MongoDB Atlas", "TRUSTLENS ML Telemetry"],
          tags: detail.tags || [],
          attributes: detail.attributes || {},
          nodes: adaptedNodes,
          edges: adaptedEdges,
          timeline: adaptedTimeline,
        };

        setInvestigation(liveData);
      })
      .catch((err: any) => {
        if (err.name === "AbortError") return;
        setError(err?.message || `Investigation '${id}' could not be loaded from backend.`);
      })
      .finally(() => {
        setLoading(false);
      });

    return () => {
      controller.abort();
    };
  }, [id]);

  // 1. Loading State
  if (loading) {
    return (
      <div className="w-screen h-screen flex flex-col items-center justify-center bg-[#171C25] text-slate-200 select-none space-y-4">
        <div className="relative">
          <div className="w-14 h-14 rounded-full border-2 border-[#3A4553] border-t-cyan-400 animate-spin"></div>
          <ShieldAlert className="w-6 h-6 text-cyan-400 absolute inset-0 m-auto" />
        </div>
        <div className="text-center space-y-1">
          <p className="font-mono text-sm font-semibold text-white">Loading Threat Investigation Dossier</p>
          <p className="font-mono text-xs text-slate-500">Querying MongoDB Atlas and live graph topology ({id})...</p>
        </div>
      </div>
    );
  }

  // 2. Error / 404 State
  if (error || !investigation) {
    return (
      <div className="w-screen h-screen flex flex-col items-center justify-center bg-[#171C25] text-slate-200 select-none p-6">
        <div className="max-w-md w-full bg-[#252D38] border border-rose-800/80 rounded-lg p-6 shadow-2xl text-center space-y-4">
          <div className="w-12 h-12 rounded-full bg-rose-950/80 border border-rose-600/50 flex items-center justify-center mx-auto text-rose-400">
            <AlertTriangle className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-base font-bold text-white">Investigation Not Found</h2>
            <p className="text-xs text-rose-300 font-mono mt-1">{error || `No dossier found for '${id}'`}</p>
          </div>
          <div className="flex items-center justify-center space-x-3 pt-2">
            <button
              onClick={() => window.location.reload()}
              className="flex items-center space-x-1.5 px-3 py-1.5 bg-[#181E28] hover:bg-[#202731] border border-[#3A4553] text-slate-200 rounded text-xs font-mono"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Retry</span>
            </button>
            <Link
              href="/investigations"
              className="flex items-center space-x-1.5 px-3.5 py-1.5 bg-blue-600 hover:bg-blue-500 text-white rounded text-xs font-semibold shadow-lg shadow-blue-900/30"
            >
              <ArrowLeft className="w-3.5 h-3.5" />
              <span>Back to Directory</span>
            </Link>
          </div>
        </div>
      </div>
    );
  }

  // 3. Empty Graph State
  if (investigation.nodes.length === 0) {
    return (
      <div className="w-screen h-screen flex flex-col bg-[#171C25] text-slate-100">
        <EmptyInvestigationState
          message={`Investigation '${investigation.id}' has no graph objects yet.`}
          onCreateClick={() => {
            router.push("/investigations");
          }}
        />
      </div>
    );
  }

  // 4. Render Live Investigation Workspace
  return (
    <InvestigationWorkspace
      investigation={investigation}
      onUpdateInvestigation={(updated) => setInvestigation(updated)}
    />
  );
}
