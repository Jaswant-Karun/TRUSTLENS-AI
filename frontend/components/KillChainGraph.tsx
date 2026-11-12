"use client";

import React, { useState } from "react";
import { Network, ShieldCheck, AlertCircle, ArrowRight, Info } from "lucide-react";

interface NodeDetail {
  id: string;
  label: string;
  type: string;
  threatLevel: string;
  details: string;
  iocs: string[];
}

const NODES: NodeDetail[] = [
  {
    id: "origin",
    label: "Attack Origin",
    type: "Origin Host / Gateway",
    threatLevel: "high",
    details: "Unregistered VoIP SMS Gateway routing bulk deceptive SMS packets.",
    iocs: ["Sender ID: VK-SBIBNK", "IP: 198.51.100.44"],
  },
  {
    id: "lure",
    label: "Deceptive Lure",
    type: "Hinglish Smishing",
    threatLevel: "critical",
    details: "Social-engineering pretext threatening immediate bank account deactivation.",
    iocs: ["Text: 'SBI khata turant band...'", "Tactic: Artificial Urgency"],
  },
  {
    id: "url",
    label: "Phishing Landing",
    type: "Credential Stealer",
    threatLevel: "critical",
    details: "Cloned netbanking portal hosting fake KYC PAN/Aadhaar update forms.",
    iocs: ["URL: http://192.168.1.50/sbi-kyc", "Entropy: 4.38"],
  },
  {
    id: "harvest",
    label: "OTP Interceptor",
    type: "Two-Factor Bypass",
    threatLevel: "critical",
    details: "Live websocket listener harvesting 6-digit transaction authorization codes.",
    iocs: ["Target: Netbanking 2FA", "Payload: Reverse OTP relay"],
  },
  {
    id: "mule",
    label: "Mule Account",
    type: "Intermediate Layer",
    threatLevel: "medium",
    details: "Compromised regional savings account used to layer stolen funds.",
    iocs: ["UPI: payment98@okhdfcbank", "Account: 3491029482"],
  },
  {
    id: "exit",
    label: "Exit Point",
    type: "Cryptocurrency / Cashout",
    threatLevel: "high",
    details: "Instant P2P cryptocurrency purchase and wallet withdrawal.",
    iocs: ["Exit Channel: USDT P2P", "Volume: INR 48,500"],
  },
];

export default function KillChainGraph() {
  const [selectedNode, setSelectedNode] = useState<NodeDetail>(NODES[1]);

  return (
    <div className="bg-card border border-border rounded-xl p-6 mb-6">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-base font-semibold text-white flex items-center space-x-2">
            <Network className="w-4 h-4 text-cyberCyan" />
            <span>Interactive Attack Kill-Chain & Intelligence Graph</span>
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Traces the attack lifecycle from vector origin through social engineering to monetary exfiltration.
          </p>
        </div>
        <div className="text-xs font-mono text-slate-500 bg-surface px-2.5 py-1 rounded border border-border">
          CLICK NODE TO INSPECT
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Visual Graph View */}
        <div className="lg:col-span-3 bg-surface border border-border rounded-lg p-5 flex flex-col justify-center">
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3 relative">
            {NODES.map((node, i) => {
              const isSelected = selectedNode.id === node.id;
              return (
                <div key={node.id} className="flex flex-col items-center">
                  <button
                    onClick={() => setSelectedNode(node)}
                    className={`w-full p-3 rounded-lg border text-center transition-all flex flex-col items-center justify-center min-h-[90px] ${
                      isSelected
                        ? "border-cyberGreen bg-cyberGreen/10 shadow-lg shadow-cyberGreen/10"
                        : "border-border bg-card hover:border-slate-600"
                    }`}
                  >
                    <div className="text-[10px] uppercase font-mono text-slate-400 mb-1">
                      Step {i + 1}
                    </div>
                    <div className="text-xs font-bold text-slate-200">{node.label}</div>
                    <div
                      className={`mt-1.5 px-2 py-0.5 rounded-full text-[9px] font-mono uppercase ${
                        node.threatLevel === "critical"
                          ? "bg-cyberRed/20 text-cyberRed"
                          : node.threatLevel === "high"
                          ? "bg-cyberAmber/20 text-cyberAmber"
                          : "bg-cyberCyan/20 text-cyberCyan"
                      }`}
                    >
                      {node.threatLevel}
                    </div>
                  </button>
                  {i < NODES.length - 1 && (
                    <div className="hidden lg:block absolute" style={{ left: `${(i + 1) * 16.66 - 2}%`, top: "35%" }}>
                      <ArrowRight className="w-4 h-4 text-slate-600" />
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* Node detail inspector panel */}
        <div className="bg-surface border border-border rounded-lg p-4 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-2 border-b border-border mb-3">
              <span className="text-xs font-mono uppercase text-slate-400">Node Telemetry</span>
              <span className="text-xs font-mono text-cyberGreen font-bold uppercase">{selectedNode.label}</span>
            </div>
            <div className="text-xs text-slate-300 mb-3">{selectedNode.details}</div>
            
            <div className="text-[11px] font-mono text-slate-400 uppercase mb-1.5">Observed IOCs & Rules:</div>
            <div className="space-y-1">
              {selectedNode.iocs.map((ioc, idx) => (
                <div key={idx} className="p-1.5 rounded bg-card border border-border text-[11px] font-mono text-slate-300">
                  {ioc}
                </div>
              ))}
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-border flex items-center justify-between text-[11px] font-mono text-slate-500">
            <span>Status: Mapped</span>
            <span className="text-cyberCyan">Confidence: 94.2%</span>
          </div>
        </div>
      </div>
    </div>
  );
}

