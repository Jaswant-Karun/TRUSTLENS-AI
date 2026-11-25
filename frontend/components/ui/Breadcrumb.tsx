"use client";

import React from "react";
import Link from "next/link";
import { ChevronRight, Home } from "lucide-react";

export interface BreadcrumbItem {
  label: string;
  href?: string;
}

export function Breadcrumb({ items }: { items: BreadcrumbItem[] }) {
  return (
    <nav aria-label="Breadcrumb" className="flex items-center space-x-1.5 text-xs font-mono text-[#A1A1AA] mb-2 font-medium">
      <Link href="/" aria-label="Home" className="flex items-center hover:text-[#FF3D70] transition-colors">
        <Home className="w-3.5 h-3.5" />
      </Link>
      {items.map((item, idx) => {
        const isLast = idx === items.length - 1;
        return (
          <React.Fragment key={idx}>
            <ChevronRight className="w-3.5 h-3.5 text-[#481326] shrink-0" />
            {item.href && !isLast ? (
              <Link href={item.href} className="hover:text-white transition-colors">
                {item.label}
              </Link>
            ) : (
              <span className={isLast ? "text-[#FF3D70] font-semibold" : ""}>{item.label}</span>
            )}
          </React.Fragment>
        );
      })}
    </nav>
  );
}
