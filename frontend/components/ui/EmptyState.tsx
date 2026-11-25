"use client";

import React from "react";
import { FolderSearch, Plus } from "lucide-react";

interface EmptyStateProps {
  icon?: React.ReactNode;
  title: string;
  description: string;
  actionLabel?: string;
  onAction?: () => void;
}

export function EmptyState({
  icon,
  title,
  description,
  actionLabel,
  onAction,
}: EmptyStateProps) {
  return (
    <div className="cyber-panel p-10 text-center flex flex-col items-center justify-center my-4">
      <div className="w-12 h-12 rounded-full bg-[#170A12] border border-[#481326] flex items-center justify-center text-[#FF3D70] mb-3">
        {icon || <FolderSearch className="w-6 h-6 text-[#FF3D70]" />}
      </div>
      <h3 className="text-base font-semibold text-white mb-1">{title}</h3>
      <p className="text-sm text-[#A1A1AA] max-w-sm mb-5 leading-relaxed">{description}</p>
      {actionLabel && onAction && (
        <button onClick={onAction} className="cyber-btn-primary">
          <Plus className="w-3.5 h-3.5" />
          <span>{actionLabel}</span>
        </button>
      )}
    </div>
  );
}
