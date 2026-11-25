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
  accentColor = "rose",
}: MetricCardProps) {
  const accentStyles = {
    blue: "text-[#FF3D70] bg-[#FF174F]/15 border-[#481326]",
    cyan: "text-[#FF3D70] bg-[#C2185B]/15 border-[#481326]",
    emerald: "text-[#00D68F] bg-[#00D68F]/10 border-[#00D68F]/30",
    amber: "text-[#FFB020] bg-[#FFB020]/10 border-[#FFB020]/30",
    rose: "text-[#FF174F] bg-[#FF174F]/15 border-[#FF174F]/40",
    slate: "text-[#A1A1AA] bg-[#170A12] border-[#481326]",
  };

  if (loading) {
    return (
      <div className="cyber-panel p-5 animate-pulse flex flex-col justify-between h-[130px]">
        <div className="flex justify-between items-center">
          <div className="h-3 w-24 bg-[#481326]/60 rounded"></div>
          <div className="w-8 h-8 rounded-lg bg-[#170A12]"></div>
        </div>
        <div className="h-7 w-28 bg-[#481326]/60 rounded"></div>
        <div className="h-3 w-20 bg-[#170A12] rounded"></div>
      </div>
    );
  }

  return (
    <div className="cyber-panel p-5 hover:border-[#FF174F]/60 transition-all flex flex-col justify-between">
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs font-semibold uppercase tracking-wider text-[#A1A1AA] font-mono">
          {title}
        </span>
        <div className={`p-2 rounded-lg border ${accentStyles[accentColor]}`}>
          <Icon className="w-4 h-4" />
        </div>
      </div>

      <div>
        <div className="flex items-baseline space-x-2">
          {unavailable ? (
            <div className="flex items-center space-x-1.5 text-[#A1A1AA] text-sm font-medium py-1">
              <AlertCircle className="w-4 h-4" />
              <span>Unavailable</span>
            </div>
          ) : (
            <div className="text-2xl font-bold text-white tracking-tight font-sans">
              {value !== undefined && value !== null ? value : "—"}
            </div>
          )}
          {badge && (
            <span className="text-[11px] font-mono font-medium px-2 py-0.5 rounded bg-[#170A12] text-[#FF3D70] border border-[#481326]">
              {badge}
            </span>
          )}
        </div>

        <div className="flex items-center justify-between text-xs text-[#A1A1AA] mt-2 font-medium">
          {subtitle && <span>{subtitle}</span>}
          {trend && (
            <div
              className={`flex items-center space-x-1 font-mono text-[11px] ${
                trend.positive === undefined
                  ? "text-[#A1A1AA]"
                  : trend.positive
                  ? "text-[#00D68F]"
                  : "text-[#FF174F]"
              }`}
            >
              {trend.direction === "up" && <TrendingUp className="w-3 h-3" />}
              {trend.direction === "down" && <TrendingDown className="w-3 h-3" />}
              {trend.direction === "neutral" && <Minus className="w-3 h-3" />}
              <span>{trend.label}</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
