"use client";

import React from "react";

interface PageHeaderProps {
  title: string;
  description?: string;
  badge?: {
    text: string;
    variant?: "blue" | "green" | "amber" | "red" | "neutral" | "purple" | "rose";
  };
  actions?: React.ReactNode;
}

export function PageHeader({
  title,
  description,
  badge,
  actions,
}: PageHeaderProps) {
  const badgeColors: Record<string, string> = {
    blue: "bg-[#FF174F]/15 text-[#FF3D70] border-[#481326]",
    green: "bg-[#00D68F]/15 text-[#00D68F] border-[#00D68F]/40",
    amber: "bg-[#FFB020]/15 text-[#FFB020] border-[#FFB020]/40",
    red: "bg-[#FF174F]/20 text-[#FF174F] border-[#FF174F]/50",
    neutral: "bg-[#170A12] text-[#A1A1AA] border-[#481326]",
    purple: "bg-[#C2185B]/20 text-[#FF3D70] border-[#C2185B]/50",
    rose: "bg-[#FF174F]/15 text-[#FF3D70] border-[#FF174F]/40",
  };

  return (
    <div className="flex flex-col md:flex-row md:items-center justify-between pb-6 mb-6 border-b border-[#481326]/80 gap-4">
      <div>
        <div className="flex flex-wrap items-center gap-3">
          <h1 className="text-xl sm:text-2xl font-bold text-white tracking-tight font-mono">{title}</h1>
          {badge && (
            <span
              className={`text-xs px-2.5 py-0.5 rounded-full font-mono font-medium border ${
                badgeColors[badge.variant || "rose"]
              }`}
            >
              {badge.text}
            </span>
          )}
        </div>
        {description && <p className="text-sm text-[#A1A1AA] mt-1">{description}</p>}
      </div>

      {actions && <div className="flex items-center space-x-2.5 shrink-0">{actions}</div>}
    </div>
  );
}
