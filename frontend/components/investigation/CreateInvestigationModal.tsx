"use client";

import React, { useState } from "react";
import { X, Shield, Plus, AlertTriangle, Layers } from "lucide-react";

interface CreateInvestigationModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: {
    title: string;
    description: string;
    severity: "critical" | "high" | "medium" | "low";
    targetEntity: string;
    initialPayload: string;
    tags: string[];
  }) => void;
}

export function CreateInvestigationModal({
  isOpen,
  onClose,
  onSubmit,
}: CreateInvestigationModalProps) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [severity, setSeverity] = useState<"critical" | "high" | "medium" | "low">("high");
  const [targetEntity, setTargetEntity] = useState("State Bank of India (SBI)");
  const [initialPayload, setInitialPayload] = useState("");
  const [tagInput, setTagInput] = useState("smishing, kyc_fraud, m1_bilstm");

  if (!isOpen) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;
    const tags = tagInput
      .split(",")
      .map((t) => t.trim())
      .filter(Boolean);
    onSubmit({
      title,
      description,
      severity,
      targetEntity,
      initialPayload,
      tags,
    });
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-black/75 backdrop-blur-sm z-50 flex items-center justify-center p-4 select-none">
      <div className="bg-[#252D38] border border-[#3A4553] rounded-lg shadow-2xl max-w-lg w-full text-slate-200 overflow-hidden font-sans">
        {/* Header */}
        <div className="p-4 border-b border-[#3A4553] flex items-center justify-between bg-[#202731]">
          <div className="flex items-center space-x-2">
            <div className="w-6 h-6 rounded bg-blue-600/20 border border-blue-500/40 flex items-center justify-center">
              <Plus className="w-3.5 h-3.5 text-blue-400" />
            </div>
            <h3 className="font-semibold text-sm text-white">Create Threat Investigation Dossier</h3>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-white">
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Form Body */}
        <form onSubmit={handleSubmit} className="p-5 space-y-4 text-xs">
          <div>
            <label className="block text-[11px] font-mono text-slate-400 uppercase tracking-wider mb-1.5">
              Investigation Title *
            </label>
            <input
              type="text"
              required
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g. Analysis of Urgent Electricity Bill Disconnection Syndicate"
              className="w-full bg-[#181E28] border border-[#3A4553] rounded px-3 py-2 text-white placeholder-slate-500 focus:outline-none focus:border-cyan-400"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-[11px] font-mono text-slate-400 uppercase tracking-wider mb-1.5">
                Severity
              </label>
              <select
                value={severity}
                onChange={(e) => setSeverity(e.target.value as any)}
                className="w-full bg-[#181E28] border border-[#3A4553] rounded px-3 py-2 text-white focus:outline-none focus:border-cyan-400"
              >
                <option value="critical">CRITICAL (Active Financial Threat)</option>
                <option value="high">HIGH (Active Phishing Lure)</option>
                <option value="medium">MEDIUM (Suspicious Indicator)</option>
                <option value="low">LOW (Informational / Benign)</option>
              </select>
            </div>

            <div>
              <label className="block text-[11px] font-mono text-slate-400 uppercase tracking-wider mb-1.5">
                Targeted Institution
              </label>
              <input
                type="text"
                value={targetEntity}
                onChange={(e) => setTargetEntity(e.target.value)}
                placeholder="e.g. State Bank of India, BSES"
                className="w-full bg-[#181E28] border border-[#3A4553] rounded px-3 py-2 text-white focus:outline-none focus:border-cyan-400"
              />
            </div>
          </div>

          <div>
            <label className="block text-[11px] font-mono text-slate-400 uppercase tracking-wider mb-1.5">
              Description & Pretext Summary
            </label>
            <textarea
              rows={3}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Provide context regarding observed social engineering tactics, delivery channels, and campaign targets..."
              className="w-full bg-[#181E28] border border-[#3A4553] rounded px-3 py-2 text-white placeholder-slate-500 focus:outline-none focus:border-cyan-400 resize-none"
            />
          </div>

          <div>
            <label className="block text-[11px] font-mono text-slate-400 uppercase tracking-wider mb-1.5">
              Initial Malicious Message or Phishing URL
            </label>
            <textarea
              rows={2}
              value={initialPayload}
              onChange={(e) => setInitialPayload(e.target.value)}
              placeholder="Paste raw SMS message, email body, or target extraction URL..."
              className="w-full bg-[#181E28] border border-[#3A4553] rounded px-3 py-2 text-white placeholder-slate-500 focus:outline-none focus:border-cyan-400 resize-none font-mono text-[11px]"
            />
          </div>

          <div>
            <label className="block text-[11px] font-mono text-slate-400 uppercase tracking-wider mb-1.5">
              Threat Tags (Comma Separated)
            </label>
            <input
              type="text"
              value={tagInput}
              onChange={(e) => setTagInput(e.target.value)}
              className="w-full bg-[#181E28] border border-[#3A4553] rounded px-3 py-2 text-white focus:outline-none focus:border-cyan-400 font-mono text-[11px]"
            />
          </div>

          <div className="pt-3 border-t border-[#3A4553] flex items-center justify-end space-x-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-1.5 bg-[#181E28] hover:bg-[#1E2631] text-slate-300 rounded text-xs"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-1.5 bg-blue-600 hover:bg-blue-500 text-white rounded text-xs font-semibold shadow-md shadow-blue-600/30"
            >
              Initialize Workspace
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
