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
    <div className="bg-white p-10 rounded-xl border border-slate-200 shadow-subtle text-center flex flex-col items-center justify-center my-4">
      <div className="w-12 h-12 rounded-full bg-slate-100 flex items-center justify-center text-slate-500 mb-3">
        {icon || <FolderSearch className="w-6 h-6 text-slate-400" />}
      </div>
      <h3 className="text-base font-semibold text-slate-900 mb-1">{title}</h3>
      <p className="text-sm text-slate-500 max-w-sm mb-5 leading-relaxed">{description}</p>
      {actionLabel && onAction && (
        <button
          onClick={onAction}
          className="inline-flex items-center space-x-1.5 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-xs font-medium rounded-lg shadow-sm transition-colors"
        >
          <Plus className="w-3.5 h-3.5" />
          <span>{actionLabel}</span>
        </button>
      )}
    </div>
  );
}
