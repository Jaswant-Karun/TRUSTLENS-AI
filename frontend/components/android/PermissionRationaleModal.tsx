"use client";

import React from "react";
import { Bell, Camera, Image as ImageIcon, ShieldCheck, X } from "lucide-react";

export type SensitivePermissionKind = "camera" | "photos" | "notifications";

interface PermissionRationaleModalProps {
  kind: SensitivePermissionKind | null;
  onConfirm: () => void;
  onCancel: () => void;
}

const RATIONALE_COPY: Record<
  SensitivePermissionKind,
  {
    title: string;
    description: string;
    dataScope: string;
    icon: React.ComponentType<{ className?: string }>;
  }
> = {
  camera: {
    title: "Camera Permission Required",
    description:
      "TRUSTLENS AI uses your camera only when you choose to capture a photo of a suspicious SMS, QR letter, or payment notice for OCR fraud analysis.",
    dataScope:
      "Images are validated (10 MB max, magic-byte checked) and analyzed only when you tap Scan. Background camera access is never used.",
    icon: Camera,
  },
  photos: {
    title: "Photo Library Access Required",
    description:
      "TRUSTLENS AI needs access to your selected screenshot or image from the gallery so it can extract text via OCR and inspect it for scam indicators.",
    dataScope:
      "Only the specific image you pick is read into app memory; TRUSTLENS AI never scans your photo library in the background.",
    icon: ImageIcon,
  },
  notifications: {
    title: "Push Notification Permission",
    description:
      "Enable Android push notifications to receive alerts about investigation updates and consented threat intelligence advisories.",
    dataScope:
      "Notifications respect your consent preferences and never include raw sensitive message text in lock-screen previews.",
    icon: Bell,
  },
};

export function PermissionRationaleModal({
  kind,
  onConfirm,
  onCancel,
}: PermissionRationaleModalProps) {
  if (!kind) return null;
  const info = RATIONALE_COPY[kind];
  const Icon = info.icon;

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="perm-rationale-title"
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 px-4 backdrop-blur-sm"
    >
      <div className="w-full max-w-md rounded-xl border border-[#FF174F]/50 bg-[#0A050A] p-5 shadow-[0_0_30px_rgba(255,23,79,0.25)]">
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-center gap-2.5">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg border border-[#FF174F]/40 bg-[#FF174F]/15 text-[#FF3D70]">
              <Icon className="h-5 w-5" />
            </div>
            <h2
              id="perm-rationale-title"
              className="font-mono text-sm font-bold uppercase tracking-wider text-white"
            >
              {info.title}
            </h2>
          </div>
          <button
            type="button"
            onClick={onCancel}
            aria-label="Close permission explanation"
            className="rounded p-1 text-[#A1A1AA] hover:text-white"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        <p className="mt-3 text-xs leading-relaxed text-slate-300">
          {info.description}
        </p>

        <div className="mt-3 flex items-start gap-2 rounded-lg border border-[#481326] bg-[#10070D] p-3 text-[11px] text-[#A1A1AA]">
          <ShieldCheck className="mt-0.5 h-4 w-4 shrink-0 text-[#00D68F]" />
          <span>{info.dataScope}</span>
        </div>

        <div className="mt-5 flex items-center justify-end gap-2.5">
          <button
            type="button"
            onClick={onCancel}
            className="rounded-lg border border-[#481326] bg-[#10070D] px-3.5 py-2 font-mono text-xs text-[#A1A1AA] hover:text-white"
          >
            Not Now
          </button>
          <button
            type="button"
            onClick={onConfirm}
            className="rounded-lg border border-[#FF174F] bg-[#FF174F] px-4 py-2 font-mono text-xs font-semibold text-white hover:bg-[#FF3D70]"
          >
            Continue
          </button>
        </div>
      </div>
    </div>
  );
}
