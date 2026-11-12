"use client";

import React from "react";
import { Loader2 } from "lucide-react";

export function Spinner({ size = "md", label }: { size?: "sm" | "md" | "lg"; label?: string }) {
  const sizeMap = {
    sm: "w-4 h-4",
    md: "w-6 h-6",
    lg: "w-8 h-8",
  };

  return (
    <div className="flex items-center justify-center space-x-2 py-4">
      <Loader2 className={`${sizeMap[size]} text-blue-600 animate-spin`} />
      {label && <span className="text-xs text-slate-500 font-medium">{label}</span>}
    </div>
  );
}

export function SkeletonMetrics() {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 animate-pulse">
      {[1, 2, 3, 4].map((i) => (
        <div key={i} className="bg-white p-5 rounded-xl border border-slate-200 shadow-subtle space-y-3">
          <div className="flex justify-between items-center">
            <div className="h-3 w-24 bg-slate-200 rounded"></div>
            <div className="w-8 h-8 rounded-lg bg-slate-100"></div>
          </div>
          <div className="h-7 w-20 bg-slate-200 rounded"></div>
          <div className="h-3 w-32 bg-slate-100 rounded"></div>
        </div>
      ))}
    </div>
  );
}

export function SkeletonCard() {
  return (
    <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-subtle animate-pulse space-y-4">
      <div className="h-4 w-1/3 bg-slate-200 rounded"></div>
      <div className="h-3 w-2/3 bg-slate-100 rounded"></div>
      <div className="h-24 bg-slate-50 rounded-lg border border-slate-100"></div>
    </div>
  );
}

export function SkeletonTable({ rows = 5 }: { rows?: number }) {
  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-subtle overflow-hidden animate-pulse">
      <div className="h-10 bg-slate-100 border-b border-slate-200"></div>
      <div className="divide-y divide-slate-100">
        {Array.from({ length: rows }).map((_, i) => (
          <div key={i} className="p-4 flex items-center justify-between space-x-4">
            <div className="h-3.5 w-16 bg-slate-200 rounded"></div>
            <div className="h-3.5 w-24 bg-slate-100 rounded"></div>
            <div className="h-3.5 flex-1 bg-slate-100 rounded max-w-md"></div>
            <div className="h-6 w-16 bg-slate-200 rounded-full"></div>
            <div className="h-3.5 w-12 bg-slate-100 rounded"></div>
          </div>
        ))}
      </div>
    </div>
  );
}

export function SkeletonChart() {
  return (
    <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-subtle animate-pulse space-y-4">
      <div className="flex justify-between items-center">
        <div className="h-4 w-36 bg-slate-200 rounded"></div>
        <div className="h-6 w-20 bg-slate-100 rounded"></div>
      </div>
      <div className="h-48 bg-slate-50 rounded-lg flex items-end p-4 space-x-3">
        {[40, 75, 55, 90, 65, 80, 45, 95].map((height, idx) => (
          <div
            key={idx}
            className="flex-1 bg-slate-200 rounded-t"
            style={{ height: `${height}%` }}
          ></div>
        ))}
      </div>
    </div>
  );
}
