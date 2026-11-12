"use client";

import React from "react";

interface PageHeaderProps {
  title: string;
  description?: string;
  badge?: {
    text: string;
    variant?: "blue" | "green" | "amber" | "red" | "neutral";
  };
  actions?: React.ReactNode;
}

export function PageHeader({
  title,
  description,
  badge,
  actions,
}: PageHeaderProps) {
  const badgeColors = {
    blue: "bg-blue-50 text-blue-700 border-blue-200",
    green: "bg-emerald-50 text-emerald-700 border-emerald-200",
    amber: "bg-amber-50 text-amber-700 border-amber-200",
    red: "bg-red-50 text-red-700 border-red-200",
    neutral: "bg-slate-100 text-slate-700 border-slate-200",
  };

  return (
    <div className="flex flex-col md:flex-row md:items-center justify-between pb-6 mb-6 border-b border-slate-200/80 gap-4">
      <div>
        <div className="flex items-center space-x-3">
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">{title}</h1>
          {badge && (
            <span
              className={`text-xs px-2.5 py-0.5 rounded-full font-medium border ${
                badgeColors[badge.variant || "blue"]
              }`}
            >
              {badge.text}
            </span>
          )}
        </div>
        {description && <p className="text-sm text-slate-500 mt-1">{description}</p>}
      </div>

      {actions && <div className="flex items-center space-x-2.5 shrink-0">{actions}</div>}
    </div>
  );
}

