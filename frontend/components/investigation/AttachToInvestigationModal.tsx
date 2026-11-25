"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { AlertCircle, CheckCircle2, FolderPlus, Link2, Lock, X } from "lucide-react";
import {
  attachAnalysisToInvestigation,
  createInvestigation,
  getInvestigations,
  getStoredToken,
  InvestigationSummaryItem,
} from "@/lib/api";
import { GlowButton } from "@/components/product/GlowButton";

interface AttachToInvestigationModalProps {
  isOpen: boolean;
  analysisId: string | null;
  onClose: () => void;
}

export function AttachToInvestigationModal({
  isOpen,
  analysisId,
  onClose,
}: AttachToInvestigationModalProps) {
  const router = useRouter();
  const [hasToken, setHasToken] = useState(false);
  const [mode, setMode] = useState<"existing" | "new">("existing");
  const [investigations, setInvestigations] = useState<InvestigationSummaryItem[]>([]);
  const [selectedInvId, setSelectedInvId] = useState("");
  const [newTitle, setNewTitle] = useState("");
  const [newSeverity, setNewSeverity] = useState("high");
  const [newVisibility, setNewVisibility] = useState("Private");

  const [loadingList, setLoadingList] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [attachedInvId, setAttachedInvId] = useState<string | null>(null);

  useEffect(() => {
    if (!isOpen) return;
    setError(null);
    setAttachedInvId(null);
    const tokenPresent = Boolean(getStoredToken());
    setHasToken(tokenPresent);
    if (!tokenPresent) return;

    setLoadingList(true);
    getInvestigations()
      .then((list) => {
        setInvestigations(list || []);
        if (list && list.length > 0) {
          setSelectedInvId(list[0].id);
        }
      })
      .catch(() => setInvestigations([]))
      .finally(() => setLoadingList(false));
  }, [isOpen]);

  if (!isOpen || !analysisId) return null;

  const handleAttachExisting = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedInvId) {
      setError("Select an investigation first.");
      return;
    }
    setSubmitting(true);
    setError(null);
    try {
      await attachAnalysisToInvestigation(selectedInvId, analysisId);
      setAttachedInvId(selectedInvId);
    } catch (err: any) {
      setError(err?.message || "Failed to attach analysis.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleCreateAndAttach = async (e: React.FormEvent) => {
    e.preventDefault();
    if (newTitle.trim().length < 3) {
      setError("Investigation title must be at least 3 characters.");
      return;
    }
    setSubmitting(true);
    setError(null);
    try {
      const created = await createInvestigation({
        title: newTitle.trim(),
        severity: newSeverity,
        visibility: newVisibility,
      });
      await attachAnalysisToInvestigation(created.id, analysisId);
      setAttachedInvId(created.id);
    } catch (err: any) {
      setError(err?.message || "Failed to create investigation and attach analysis.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-[#050306]/85 backdrop-blur-sm p-4">
      <div className="cyber-modal w-full max-w-lg p-6 space-y-5">
        <div className="flex items-center justify-between border-b border-[#481326] pb-3">
          <div>
            <h3 className="font-mono text-sm font-bold uppercase tracking-wider text-white">
              Attach Analysis to Investigation
            </h3>
            <p className="font-mono text-[11px] text-[#A1A1AA] mt-0.5">
              Analysis ID: {analysisId}
            </p>
          </div>
          <button
            type="button"
            aria-label="Close modal"
            onClick={onClose}
            className="text-[#A1A1AA] hover:text-white p-1"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {!hasToken ? (
          <div className="p-4 rounded-lg border border-[#481326] bg-[#050306] text-center space-y-3">
            <Lock className="mx-auto h-8 w-8 text-[#FF3D70]" />
            <p className="text-xs text-[#A1A1AA]">
              Sign in to attach analyses to existing or newly created investigations.
            </p>
            <Link href="/login">
              <GlowButton variant="primary" size="sm">SIGN IN</GlowButton>
            </Link>
          </div>
        ) : attachedInvId ? (
          <div className="space-y-4">
            <div className="flex items-start gap-2.5 rounded-lg border border-[#00D68F]/50 bg-[#00D68F]/10 p-3.5 text-xs text-[#00D68F]">
              <CheckCircle2 className="h-4 w-4 shrink-0 mt-0.5" />
              <span>
                Analysis attached to investigation <strong>{attachedInvId}</strong>.
                Graph nodes and timeline events have been updated.
              </span>
            </div>
            <div className="flex justify-end gap-3">
              <GlowButton variant="secondary" size="sm" onClick={onClose}>
                Close
              </GlowButton>
              <GlowButton
                variant="primary"
                size="sm"
                onClick={() => {
                  onClose();
                  router.push(`/investigations/${attachedInvId}`);
                }}
              >
                Open Investigation
              </GlowButton>
            </div>
          </div>
        ) : (
          <>
            <div className="flex gap-2">
              <button
                type="button"
                onClick={() => {
                  setMode("existing");
                  setError(null);
                }}
                className={`flex-1 py-2 px-3 rounded-lg font-mono text-xs border transition-colors flex items-center justify-center gap-1.5 ${
                  mode === "existing"
                    ? "border-[#FF174F] bg-[#FF174F]/15 text-white font-semibold"
                    : "border-[#481326] bg-[#050306] text-[#A1A1AA]"
                }`}
              >
                <Link2 className="w-3.5 h-3.5" />
                <span>Existing Case</span>
              </button>
              <button
                type="button"
                onClick={() => {
                  setMode("new");
                  setError(null);
                }}
                className={`flex-1 py-2 px-3 rounded-lg font-mono text-xs border transition-colors flex items-center justify-center gap-1.5 ${
                  mode === "new"
                    ? "border-[#FF174F] bg-[#FF174F]/15 text-white font-semibold"
                    : "border-[#481326] bg-[#050306] text-[#A1A1AA]"
                }`}
              >
                <FolderPlus className="w-3.5 h-3.5" />
                <span>New Case</span>
              </button>
            </div>

            {error && (
              <div className="flex items-start gap-2 rounded-lg border border-[#FF174F]/60 bg-[#FF174F]/10 p-3 text-xs text-[#FF3D70]">
                <AlertCircle className="h-4 w-4 shrink-0 mt-0.5" />
                <span>{error}</span>
              </div>
            )}

            {mode === "existing" ? (
              <form onSubmit={handleAttachExisting} className="space-y-4">
                <div>
                  <label className="block font-mono text-[11px] uppercase text-[#A1A1AA] mb-1.5">
                    Select Investigation
                  </label>
                  {loadingList ? (
                    <div className="text-xs font-mono text-[#A1A1AA]">Loading cases...</div>
                  ) : investigations.length === 0 ? (
                    <div className="text-xs text-[#A1A1AA]">
                      No existing investigations found. Switch to <strong>New Case</strong> to create one.
                    </div>
                  ) : (
                    <select
                      value={selectedInvId}
                      onChange={(e) => setSelectedInvId(e.target.value)}
                      className="cyber-select w-full"
                    >
                      {investigations.map((inv) => (
                        <option key={inv.id} value={inv.id}>
                          {inv.id} — {inv.title} ({inv.visibility || "Organization"})
                        </option>
                      ))}
                    </select>
                  )}
                </div>
                <div className="flex justify-end gap-2">
                  <GlowButton type="button" variant="secondary" size="sm" onClick={onClose}>
                    Cancel
                  </GlowButton>
                  <GlowButton type="submit" variant="primary" size="sm" disabled={submitting || !selectedInvId}>
                    {submitting ? "ATTACHING..." : "Attach Analysis"}
                  </GlowButton>
                </div>
              </form>
            ) : (
              <form onSubmit={handleCreateAndAttach} className="space-y-4">
                <div>
                  <label className="block font-mono text-[11px] uppercase text-[#A1A1AA] mb-1.5">
                    Investigation Title
                  </label>
                  <input
                    type="text"
                    required
                    value={newTitle}
                    onChange={(e) => setNewTitle(e.target.value)}
                    placeholder="e.g. SBI KYC Phishing Campaign"
                    className="cyber-input"
                  />
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block font-mono text-[11px] uppercase text-[#A1A1AA] mb-1.5">
                      Severity
                    </label>
                    <select
                      value={newSeverity}
                      onChange={(e) => setNewSeverity(e.target.value)}
                      className="cyber-select w-full"
                    >
                      <option value="critical">Critical</option>
                      <option value="high">High</option>
                      <option value="medium">Medium</option>
                      <option value="low">Low</option>
                    </select>
                  </div>
                  <div>
                    <label className="block font-mono text-[11px] uppercase text-[#A1A1AA] mb-1.5">
                      Visibility
                    </label>
                    <select
                      value={newVisibility}
                      onChange={(e) => setNewVisibility(e.target.value)}
                      className="cyber-select w-full"
                    >
                      <option value="Private">Private (Owner Only)</option>
                      <option value="Organization">Organization</option>
                    </select>
                  </div>
                </div>
                <div className="flex justify-end gap-2">
                  <GlowButton type="button" variant="secondary" size="sm" onClick={onClose}>
                    Cancel
                  </GlowButton>
                  <GlowButton type="submit" variant="primary" size="sm" disabled={submitting}>
                    {submitting ? "CREATING & ATTACHING..." : "Create & Attach"}
                  </GlowButton>
                </div>
              </form>
            )}
          </>
        )}
      </div>
    </div>
  );
}
