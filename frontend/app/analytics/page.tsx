"use client";

import React, { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import { TopNavigation } from "@/components/investigation/TopNavigation";
import { getAnalyticsOverview, AnalyticsOverviewResponse } from "@/lib/api";
import {
  Activity,
  History,
  Shield,
  BarChart3,
  RefreshCw,
  AlertCircle,
  Calendar,
  Filter,
} from "lucide-react";

function BarList({
  title,
  items,
  labelKey,
  valueKey,
  barColor = "bg-blue-500",
}: {
  title: string;
  items: Record<string, any>[];
  labelKey: string;
  valueKey: string;
  barColor?: string;
}) {
  const maxVal = items.reduce((m, it) => Math.max(m, Number(it[valueKey] || 0)), 0) || 1;
  return (
    <div className="bg-[#252D38] border border-[#3A4553] rounded-lg p-5 space-y-3 shadow-xl">
      <h2 className="text-xs font-bold uppercase tracking-wider text-slate-300">{title}</h2>
      {items.length === 0 ? (
        <p className="text-xs text-slate-500 italic py-4">No persisted records for this measurement.</p>
      ) : (
        <div className="space-y-2.5">
          {items.slice(0, 10).map((it, idx) => {
            const val = Number(it[valueKey] || 0);
            const pct = Math.max(4, Math.round((val / maxVal) * 100));
            return (
              <div key={idx} className="space-y-1">
                <div className="flex justify-between text-xs">
                  <span className="text-slate-200 truncate max-w-[75%]">{String(it[labelKey])}</span>
                  <span className="font-mono text-slate-300">{val}</span>
                </div>
                <div className="w-full h-1.5 bg-[#171C25] rounded overflow-hidden">
                  <div className={`h-full ${barColor} rounded`} style={{ width: `${pct}%` }} />
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

export default function AnalyticsPage() {
  const [data, setData] = useState<AnalyticsOverviewResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [source, setSource] = useState("all");

  const loadAnalytics = useCallback(async () => {
    setLoading(true);
    setErrorMsg(null);
    try {
      const res = await getAnalyticsOverview({
        start_date: startDate || undefined,
        end_date: endDate || undefined,
        source,
      });
      setData(res);
    } catch (err: any) {
      setErrorMsg(err?.message || "Failed to load database analytics.");
    } finally {
      setLoading(false);
    }
  }, [startDate, endDate, source]);

  useEffect(() => {
    loadAnalytics();
  }, [loadAnalytics]);

  return (
    <div className="min-h-screen bg-[#181E28] text-[#F8FAFC] flex flex-col font-sans">
      <TopNavigation />

      <main className="flex-1 p-6 md:p-8 max-w-7xl w-full mx-auto space-y-6">
        {/* Header & Sub-workspace links */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 pb-4 border-b border-[#3A4553]">
          <div>
            <h1 className="text-xl font-bold text-white tracking-wide">
              SOC Analytics & Performance Center
            </h1>
            <p className="text-xs text-slate-400 mt-1">
              Live database-aggregated telemetry across analyses, URLs, tactics, campaign clusters, human reviews, and model benchmarks.
            </p>
          </div>
          <div className="flex flex-wrap gap-2 text-xs">
            <Link
              href="/models"
              className="px-3 py-1.5 rounded bg-[#252D38] border border-[#3A4553] hover:border-emerald-500/60 text-emerald-300 inline-flex items-center space-x-1"
            >
              <Activity className="w-3.5 h-3.5" />
              <span>Model Benchmarks</span>
            </Link>
            <Link
              href="/history"
              className="px-3 py-1.5 rounded bg-[#252D38] border border-[#3A4553] hover:border-blue-500/60 text-blue-300 inline-flex items-center space-x-1"
            >
              <History className="w-3.5 h-3.5" />
              <span>Audit Ledger</span>
            </Link>
            <Link
              href="/reports"
              className="px-3 py-1.5 rounded bg-[#252D38] border border-[#3A4553] hover:border-rose-500/60 text-rose-300 inline-flex items-center space-x-1"
            >
              <Shield className="w-3.5 h-3.5" />
              <span>Reports & Exports</span>
            </Link>
          </div>
        </div>

        {/* Date Range & Source Filters */}
        <div className="bg-[#252D38] border border-[#3A4553] rounded-lg p-4 flex flex-wrap items-end gap-4 text-xs">
          <div>
            <label className="block text-[10px] text-slate-400 uppercase mb-1">Start Date</label>
            <input
              type="date"
              aria-label="Start date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              className="px-3 py-1.5 bg-[#171C25] border border-[#3A4553] rounded text-slate-200"
            />
          </div>
          <div>
            <label className="block text-[10px] text-slate-400 uppercase mb-1">End Date</label>
            <input
              type="date"
              aria-label="End date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              className="px-3 py-1.5 bg-[#171C25] border border-[#3A4553] rounded text-slate-200"
            />
          </div>
          <div>
            <label className="block text-[10px] text-slate-400 uppercase mb-1">Source Channel</label>
            <select
              aria-label="Source filter"
              value={source}
              onChange={(e) => setSource(e.target.value)}
              className="px-3 py-1.5 bg-[#171C25] border border-[#3A4553] rounded text-slate-200"
            >
              <option value="all">All Sources</option>
              <option value="text">Text / SMS</option>
              <option value="url">URL Scanner</option>
              <option value="image">Screenshot OCR</option>
              <option value="comprehensive">Comprehensive</option>
              <option value="community_report">Community Reports</option>
            </select>
          </div>
          {(startDate || endDate || source !== "all") && (
            <button
              onClick={() => {
                setStartDate("");
                setEndDate("");
                setSource("all");
              }}
              className="px-3 py-1.5 rounded bg-[#171C25] border border-[#3A4553] text-slate-300 hover:text-white"
            >
              Clear Filters
            </button>
          )}
        </div>

        {loading ? (
          <div className="p-12 text-center text-xs text-slate-400 flex flex-col items-center space-y-2">
            <RefreshCw className="w-5 h-5 animate-spin text-blue-400" />
            <span>Aggregating live database records...</span>
          </div>
        ) : errorMsg ? (
          <div className="p-8 bg-[#252D38] border border-rose-700/60 rounded-lg text-center text-xs text-rose-300">
            {errorMsg}
          </div>
        ) : data ? (
          <>
            {/* Live Summary Counters */}
            <div className="grid grid-cols-2 md:grid-cols-6 gap-4">
              {[
                { label: "Analyses", val: data.summary.total_analyses },
                { label: "Suspicious URLs", val: data.summary.total_suspicious_urls },
                { label: "Community Reports", val: data.summary.total_community_reports },
                { label: "Campaign Clusters", val: data.summary.total_campaigns },
                { label: "Threat Indicators", val: data.summary.total_threat_indicators },
                { label: "Investigations", val: data.summary.total_investigations },
              ].map((kpi) => (
                <div
                  key={kpi.label}
                  className="bg-[#252D38] border border-[#3A4553] rounded-lg p-4 shadow"
                >
                  <div className="text-[10px] uppercase text-slate-400">{kpi.label}</div>
                  <div className="text-2xl font-bold text-white font-mono mt-1">{kpi.val}</div>
                </div>
              ))}
            </div>

            {data.limitations.length > 0 && (
              <div className="bg-amber-950/40 border border-amber-800/60 rounded-lg p-3 text-xs text-amber-200 space-y-1">
                {data.limitations.map((lim, i) => (
                  <div key={i} className="flex items-center space-x-2">
                    <AlertCircle className="w-3.5 h-3.5 text-amber-400 shrink-0" />
                    <span>{lim}</span>
                  </div>
                ))}
              </div>
            )}

            {/* Distributions Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <BarList
                title="Analysis Volume Over Time"
                items={data.analysis_volume_over_time}
                labelKey="date"
                valueKey="total"
                barColor="bg-blue-500"
              />
              <BarList
                title="Model Prediction Distribution"
                items={data.model_prediction_distribution}
                labelKey="label"
                valueKey="count"
                barColor="bg-rose-500"
              />
              <BarList
                title="Language Distribution"
                items={data.language_distribution}
                labelKey="language"
                valueKey="count"
                barColor="bg-cyan-500"
              />
              <BarList
                title="Scam Category Distribution"
                items={data.scam_category_distribution}
                labelKey="category"
                valueKey="count"
                barColor="bg-amber-500"
              />
              <BarList
                title="URL Classification Distribution"
                items={data.url_classification_distribution}
                labelKey="classification"
                valueKey="count"
                barColor="bg-orange-500"
              />
              <BarList
                title="Tactic Detection Distribution"
                items={data.tactic_detection_distribution}
                labelKey="tactic"
                valueKey="count"
                barColor="bg-purple-500"
              />
              <BarList
                title="Campaign Cluster Sizes (Top 10)"
                items={data.campaign_cluster_sizes}
                labelKey="name"
                valueKey="size"
                barColor="bg-indigo-500"
              />
              <BarList
                title="Human-Review Outcomes"
                items={data.human_review_outcomes}
                labelKey="outcome"
                valueKey="count"
                barColor="bg-emerald-500"
              />

              {/* Model Evaluation Metrics Card */}
              <div className="bg-[#252D38] border border-[#3A4553] rounded-lg p-5 space-y-3 shadow-xl">
                <h2 className="text-xs font-bold uppercase tracking-wider text-slate-300">
                  Model Evaluation Benchmarks
                </h2>
                {Object.keys(data.model_evaluation_metrics || {}).length === 0 ? (
                  <p className="text-xs text-slate-500 italic">No model evaluation metrics loaded.</p>
                ) : (
                  <div className="space-y-2 text-xs">
                    {Object.entries(data.model_evaluation_metrics).map(([key, m]: [string, any]) => (
                      <div key={key} className="bg-[#171C25] p-2.5 rounded border border-[#3A4553]">
                        <div className="font-semibold text-emerald-300">{m?.name || key}</div>
                        <div className="text-[11px] text-slate-400 font-mono mt-0.5">
                          {m?.macro_f1 ? `Macro F1: ${m.macro_f1} ` : ""}
                          {m?.roc_auc ? `ROC-AUC: ${m.roc_auc} ` : ""}
                          {m?.f1_score ? `F1: ${m.f1_score} ` : ""}
                          {m?.silhouette_score ? `Silhouette: ${m.silhouette_score}` : ""}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </>
        ) : null}
      </main>
    </div>
  );
}
