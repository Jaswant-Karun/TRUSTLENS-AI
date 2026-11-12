"use client";

import React from "react";
import { TrendingUp, TrendingDown, Minus, AlertCircle } from "lucide-react";

interface MetricCardProps {
  title: string;
  value?: string | number | null;
  subtitle?: string;
  icon: React.ComponentType<{ className?: string }>;
  trend?: {
    direction: "up" | "down" | "neutral";
    label: string;
    positive?: boolean;
  };
  badge?: string;
  loading?: boolean;
  unavailable?: boolean;
  accentColor?: "blue" | "cyan" | "emerald" | "amber" | "rose" | "slate";
}

export function MetricCard({
  title,
  value,
  subtitle,
  icon: Icon,
  trend,
  badge,
  loading = false,
  unavailable = false,
  accentColor = "blue",
}: MetricCardProps) {
  const accentStyles = {
    blue: "text-blue-600 bg-blue-50 border-blue-100",
    cyan: "text-sky-600 bg-sky-50 border-sky-100",
    emerald: "text-emerald-600 bg-emerald-50 border-emerald-100",
    amber: "text-amber-600 bg-amber-50 border-amber-100",
    rose: "text-rose-600 bg-rose-50 border-rose-100",
    slate: "text-slate-600 bg-slate-100 border-slate-200",
  };

  if (loading) {
    return (
      <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-subtle animate-pulse flex flex-col justify-between h-[130px]">
        <div className="flex justify-between items-center">
          <div className="h-3 w-24 bg-slate-200 rounded"></div>
          <div className="w-8 h-8 rounded-lg bg-slate-100"></div>
        </div>
        <div className="h-7 w-28 bg-slate-200 rounded"></div>
        <div className="h-3 w-20 bg-slate-100 rounded"></div>
      </div>
    );
  }

  return (
    <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-subtle hover:border-slate-300 transition-all flex flex-col justify-between">
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-500 font-mono">
          {title}
        </span>
        <div className={`p-2 rounded-lg border ${accentStyles[accentColor]}`}>
          <Icon className="w-4 h-4" />
        </div>
      </div>

      <div>
        <div className="flex items-baseline space-x-2">
          {unavailable ? (
            <div className="flex items-center space-x-1.5 text-slate-400 text-sm font-medium py-1">
              <AlertCircle className="w-4 h-4" />
              <span>Unavailable</span>
            </div>
          ) : (
            <div className="text-2xl font-bold text-slate-900 tracking-tight font-sans">
              {value !== undefined && value !== null ? value : "—"}
            </div>
          )}
          {badge && (
            <span className="text-[11px] font-medium px-2 py-0.5 rounded bg-slate-100 text-slate-600 border border-slate-200">
              {badge}
            </span>
          )}
        </div>

        <div className="flex items-center justify-between text-xs text-slate-500 mt-2 font-medium">
          {subtitle && <span>{subtitle}</span>}
          {trend && (
            <div
              className={`flex items-center space-x-1 font-mono text-[11px] ${
                trend.positive === undefined
                  ? "text-slate-500"
                  : trend.positive
                  ? "text-emerald-600"
                  : "text-rose-600"
              }`}
            >
              {trend.direction === "up" && <TrendingUp className="w-3.5 h-3.5" />}
              {trend.direction === "down" && <TrendingDown className="w-3.5 h-3.5" />}
              {trend.direction === "neutral" && <Minus className="w-3.5 h-3.5" />}
              <span>{trend.label}</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
