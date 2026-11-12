"use client";

import React from "react";

/**
 * Interactive & Accessible Confusion Matrix Chart
 * Inspired by DataRobot ML evaluation matrices with authentic mathematical values.
 */
interface ConfusionMatrixProps {
  tn: number;
  fp: number;
  fn: number;
  tp: number;
  title?: string;
  labels?: [string, string];
}

export function ConfusionMatrixChart({
  tn,
  fp,
  fn,
  tp,
  title = "Confusion Matrix (Held-out Test Set)",
  labels = ["Legitimate", "Threat / Scam"],
}: ConfusionMatrixProps) {
  const total = tn + fp + fn + tp;
  if (total === 0) return null;

  const precision = tp + fp > 0 ? (tp / (tp + fp)) : 0;
  const recall = tp + fn > 0 ? (tp / (tp + fn)) : 0;
  const f1 = precision + recall > 0 ? (2 * precision * recall) / (precision + recall) : 0;
  const accuracy = (tp + tn) / total;

  return (
    <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-subtle">
      <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-100">
        <div>
          <h3 className="text-sm font-semibold text-slate-900">{title}</h3>
          <p className="text-xs text-slate-500 mt-0.5">Total Benchmark Samples: {total.toLocaleString()}</p>
        </div>
        <div className="flex items-center space-x-3 text-xs font-mono">
          <div className="text-slate-600">
            F1: <span className="font-bold text-slate-900">{(f1 * 100).toFixed(1)}%</span>
          </div>
          <div className="text-slate-600">
            Acc: <span className="font-bold text-slate-900">{(accuracy * 100).toFixed(1)}%</span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 items-center">
        {/* 2x2 Matrix Grid */}
        <div className="md:col-span-2">
          <div className="text-center text-[11px] font-mono uppercase text-slate-400 font-semibold mb-2">
            Predicted Class
          </div>
          <div className="flex items-center">
            <div className="writing-vertical -rotate-180 text-[11px] font-mono uppercase text-slate-400 font-semibold mr-3 transform">
              Actual Class
            </div>
            <div className="flex-1 grid grid-cols-2 gap-2 text-center font-mono">
              {/* Header */}
              <div className="text-[11px] text-slate-500 font-medium pb-1">{labels[0]} (0)</div>
              <div className="text-[11px] text-slate-500 font-medium pb-1">{labels[1]} (1)</div>

              {/* TN Cell */}
              <div className="p-4 rounded-lg bg-blue-50/70 border border-blue-200/80 flex flex-col justify-center">
                <span className="text-xs text-blue-700 font-medium">True Negative (TN)</span>
                <span className="text-lg font-bold text-blue-900 my-1">{tn.toLocaleString()}</span>
                <span className="text-[11px] text-blue-600">{((tn / total) * 100).toFixed(1)}%</span>
              </div>

              {/* FP Cell */}
              <div className="p-4 rounded-lg bg-amber-50/60 border border-amber-200/80 flex flex-col justify-center">
                <span className="text-xs text-amber-700 font-medium">False Positive (FP)</span>
                <span className="text-lg font-bold text-amber-900 my-1">{fp.toLocaleString()}</span>
                <span className="text-[11px] text-amber-600">{((fp / total) * 100).toFixed(1)}%</span>
              </div>

              {/* FN Cell */}
              <div className="p-4 rounded-lg bg-rose-50/60 border border-rose-200/80 flex flex-col justify-center">
                <span className="text-xs text-rose-700 font-medium">False Negative (FN)</span>
                <span className="text-lg font-bold text-rose-900 my-1">{fn.toLocaleString()}</span>
                <span className="text-[11px] text-rose-600">{((fn / total) * 100).toFixed(1)}%</span>
              </div>

              {/* TP Cell */}
              <div className="p-4 rounded-lg bg-emerald-50/70 border border-emerald-200/80 flex flex-col justify-center">
                <span className="text-xs text-emerald-700 font-medium">True Positive (TP)</span>
                <span className="text-lg font-bold text-emerald-900 my-1">{tp.toLocaleString()}</span>
                <span className="text-[11px] text-emerald-600">{((tp / total) * 100).toFixed(1)}%</span>
              </div>
            </div>
          </div>
        </div>

        {/* Statistical Summary Column */}
        <div className="bg-slate-50 p-4 rounded-lg border border-slate-200 space-y-3 text-xs">
          <div className="font-semibold text-slate-800 font-mono uppercase text-[11px] border-b border-slate-200 pb-1.5">
            Class Performance
          </div>
          <div className="flex justify-between items-center py-1 border-b border-slate-200/60">
            <span className="text-slate-500">Precision:</span>
            <span className="font-mono font-bold text-slate-900">{(precision * 100).toFixed(2)}%</span>
          </div>
          <div className="flex justify-between items-center py-1 border-b border-slate-200/60">
            <span className="text-slate-500">Recall / Sensitivity:</span>
            <span className="font-mono font-bold text-slate-900">{(recall * 100).toFixed(2)}%</span>
          </div>
          <div className="flex justify-between items-center py-1 border-b border-slate-200/60">
            <span className="text-slate-500">Specificity (TNR):</span>
            <span className="font-mono font-bold text-slate-900">{((tn / (tn + fp)) * 100).toFixed(2)}%</span>
          </div>
          <div className="flex justify-between items-center py-1">
            <span className="text-slate-500">False Positive Rate:</span>
            <span className="font-mono font-bold text-amber-700">{((fp / (tn + fp)) * 100).toFixed(2)}%</span>
          </div>
        </div>
      </div>
    </div>
  );
}

/**
 * Clean Horizontal Bar Chart for Categorical Distributions
 */
export interface BarItem {
  label: string;
  value: number;
  percentage?: number;
  color?: string;
}

export function BarChart({
  title,
  subtitle,
  items,
}: {
  title: string;
  subtitle?: string;
  items: BarItem[];
}) {
  const maxVal = Math.max(...items.map((i) => i.value), 1);

  return (
    <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-subtle">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-slate-900">{title}</h3>
        {subtitle && <p className="text-xs text-slate-500 mt-0.5">{subtitle}</p>}
      </div>

      <div className="space-y-3.5">
        {items.map((item, idx) => {
          const widthPct = Math.round((item.value / maxVal) * 100);
          return (
            <div key={idx} className="space-y-1">
              <div className="flex justify-between items-center text-xs">
                <span className="text-slate-700 font-medium">{item.label}</span>
                <span className="font-mono text-slate-500">
                  {item.value.toLocaleString()} {item.percentage ? `(${item.percentage}%)` : ""}
                </span>
              </div>
              <div className="w-full h-2.5 bg-slate-100 rounded-full overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all duration-500 ${
                    item.color || "bg-blue-600"
                  }`}
                  style={{ width: `${Math.max(widthPct, 2)}%` }}
                ></div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
