"use client";

import React, { useState } from "react";
import Navbar from "@/components/Navbar";
import TelemetryCards from "@/components/TelemetryCards";
import ScanWorkbench from "@/components/ScanWorkbench";
import KillChainGraph from "@/components/KillChainGraph";
import IncidentFeed from "@/components/IncidentFeed";

export default function DashboardPage() {
  const [activeScan, setActiveScan] = useState<any>(null);

  return (
    <main className="min-h-screen bg-background">
      <Navbar />

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Top-level intelligence metrics */}
        <TelemetryCards />

        {/* Live scanner workbench */}
        <ScanWorkbench onResult={(res) => setActiveScan(res)} />

        {/* Interactive kill chain diagram */}
        <KillChainGraph />

        {/* Real-time incident logs */}
        <IncidentFeed />
      </div>

      {/* Footer */}
      <footer className="mt-12 py-6 border-t border-border bg-surface text-center text-xs font-mono text-slate-500">
        TRUSTLENS AI Platform | Production Machine Learning Edition | Multi-Modal Digital Fraud Intelligence
      </footer>
    </main>
  );
}
