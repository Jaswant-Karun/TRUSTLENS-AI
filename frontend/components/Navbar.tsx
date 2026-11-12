"use client";

import React from "react";
import { Shield, Activity, Terminal, ExternalLink } from "lucide-react";

export default function Navbar() {
  return (
    <header className="border-b border-border bg-surface/80 backdrop-blur-md sticky top-0 z-50 px-6 py-3">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        {/* Brand identity */}
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-lg bg-cyberGreen/10 border border-cyberGreen/30 flex items-center justify-center text-cyberGreen shadow-lg shadow-cyberGreen/10">
            <Shield className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-bold text-lg tracking-wider text-white">TRUSTLENS</span>
              <span className="text-xs px-2 py-0.5 rounded-full bg-cyberGreen/20 text-cyberGreen font-mono font-semibold border border-cyberGreen/30">
                AI ML
              </span>
            </div>
            <p className="text-xs text-slate-400">
              Detect the deception before people lose their money.
            </p>
          </div>
        </div>

        {/* System telemetry status */}
        <div className="hidden md:flex items-center space-x-6 text-xs font-mono">
          <div className="flex items-center space-x-2">
            <span className="relative flex h-2.5 w-2.5">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyberGreen opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-cyberGreen"></span>
            </span>
            <span className="text-slate-300">SYSTEM: ACTIVE</span>
          </div>

          <div className="flex items-center space-x-2 text-slate-400 border-l border-border pl-6">
            <Activity className="w-4 h-4 text-cyberCyan" />
            <span>BACKEND: FASTAPI [8000]</span>
          </div>

          <a
            href="http://127.0.0.1:8000/docs"
            target="_blank"
            rel="noreferrer"
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-md bg-card hover:bg-cardHover border border-border text-slate-300 transition-colors"
          >
            <Terminal className="w-3.5 h-3.5 text-cyberGreen" />
            <span>API Docs</span>
            <ExternalLink className="w-3 h-3 text-slate-500" />
          </a>
        </div>
      </div>
    </header>
  );
}
