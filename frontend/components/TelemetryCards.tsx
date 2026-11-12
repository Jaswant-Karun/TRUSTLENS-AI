"use client";

import React from "react";
import { ShieldAlert, Globe2, Network, Cpu } from "lucide-react";

export default function TelemetryCards() {
  const cards = [
    {
      title: "Processed Scans",
      value: "42,890",
      change: "+12.4% this week",
      icon: ShieldAlert,
      color: "text-cyberCyan",
      border: "border-cyberCyan/20",
      bg: "bg-cyberCyan/5",
    },
    {
      title: "Blocked Threat Vectors",
      value: "14,203",
      change: "33.1% threat ratio",
      icon: Globe2,
      color: "text-cyberRed",
      border: "border-cyberRed/20",
      bg: "bg-cyberRed/5",
    },
    {
      title: "Coordinated Campaigns",
      value: "18 Clusters",
      change: "HDBSCAN Discovery",
      icon: Network,
      color: "text-cyberAmber",
      border: "border-cyberAmber/20",
      bg: "bg-cyberAmber/5",
    },
    {
      title: "Inference Latency",
      value: "18.5 ms",
      change: "Intel 12th Gen CPU",
      icon: Cpu,
      color: "text-cyberGreen",
      border: "border-cyberGreen/20",
      bg: "bg-cyberGreen/5",
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      {cards.map((card, idx) => {
        const Icon = card.icon;
        return (
          <div
            key={idx}
            className={`p-4 rounded-xl bg-card border ${card.border} flex flex-col justify-between transition-all hover:translate-y-[-2px]`}
          >
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs uppercase tracking-wider text-slate-400 font-mono">
                {card.title}
              </span>
              <div className={`p-2 rounded-lg ${card.bg} ${card.color}`}>
                <Icon className="w-4 h-4" />
              </div>
            </div>
            <div>
              <div className="text-2xl font-bold text-white tracking-tight">
                {card.value}
              </div>
              <div className="text-xs text-slate-500 font-mono mt-1">
                {card.change}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}

