"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { MessageSquare, Link2, Image as ImageIcon, Layers } from "lucide-react";

const TABS = [
  { href: "/analyze/text", label: "Text / Message", icon: MessageSquare },
  { href: "/analyze/url", label: "URL", icon: Link2 },
  { href: "/analyze/image", label: "Screenshot", icon: ImageIcon },
  { href: "/investigation", label: "Comprehensive", icon: Layers },
];

export function AnalyzeModeTabs() {
  const pathname = usePathname();

  return (
    <div className="flex flex-wrap items-center gap-2 border-b border-[#1E293B] pb-3 mb-5">
      {TABS.map((tab) => {
        const Icon = tab.icon;
        const active = pathname === tab.href;
        return (
          <Link
            key={tab.href}
            href={tab.href}
            className={`px-3.5 py-2 rounded-lg text-xs font-semibold inline-flex items-center space-x-2 transition-colors border ${
              active
                ? "bg-cyan-950/60 border-cyan-500/60 text-cyan-300 shadow-sm"
                : "bg-[#0F172A] border-[#1E293B] text-slate-400 hover:text-slate-200 hover:border-slate-700"
            }`}
          >
            <Icon className="w-3.5 h-3.5" />
            <span>{tab.label}</span>
          </Link>
        );
      })}
    </div>
  );
}
