"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { MessageSquare, Link2, Image as ImageIcon, Layers } from "lucide-react";

const TABS = [
  { href: "/analyze/text", label: "Message Scanner", icon: MessageSquare },
  { href: "/analyze/url", label: "URL Shield", icon: Link2 },
  { href: "/analyze/image", label: "Screenshot OCR", icon: ImageIcon },
  { href: "/investigation", label: "Multi-Modal Studio", icon: Layers },
];

export function AnalyzeModeTabs() {
  const pathname = usePathname();

  return (
    <div className="flex flex-wrap items-center gap-2 border-b border-[#481326]/70 pb-3 mb-5">
      {TABS.map((tab) => {
        const Icon = tab.icon;
        const active = pathname === tab.href;
        return (
          <Link
            key={tab.href}
            href={tab.href}
            aria-current={active ? "page" : undefined}
            className={`px-3.5 py-2 rounded-lg text-xs font-mono font-semibold inline-flex items-center space-x-2 transition-colors border ${
              active
                ? "bg-[#FF174F]/15 border-[#FF174F] text-white shadow-[0_0_14px_rgba(255,23,79,0.22)]"
                : "bg-[#10070D] border-[#481326] text-[#A1A1AA] hover:text-white hover:border-[#FF174F]/60"
            }`}
          >
            <Icon className={`w-3.5 h-3.5 ${active ? "text-[#FF3D70]" : ""}`} />
            <span>{tab.label}</span>
          </Link>
        );
      })}
    </div>
  );
}
