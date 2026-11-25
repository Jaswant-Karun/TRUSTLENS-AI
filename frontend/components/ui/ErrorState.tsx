"use client";

import React from "react";
import { AlertCircle, RefreshCw } from "lucide-react";

interface ErrorStateProps {
  title?: string;
  message?: string;
  onRetry?: () => void;
  compact?: boolean;
}

export function ErrorState({
  title = "Failed to load data",
  message = "An error occurred while communicating with the backend API. Please check service health and try again.",
  onRetry,
  compact = false,
}: ErrorStateProps) {
  if (compact) {
    return (
      <div className="p-3 bg-[#FF174F]/10 border border-[#FF174F]/50 rounded-lg flex items-center justify-between text-xs text-[#FF3D70]">
        <div className="flex items-center space-x-2">
          <AlertCircle className="w-4 h-4 text-[#FF174F] shrink-0" />
          <span>{message}</span>
        </div>
        {onRetry && (
          <button
            onClick={onRetry}
            className="flex items-center space-x-1 font-semibold text-white hover:text-[#FF3D70] ml-3 underline"
          >
            <RefreshCw className="w-3 h-3" />
            <span>Retry</span>
          </button>
        )}
      </div>
    );
  }

  return (
    <div className="cyber-panel p-8 border-[#FF174F]/50 text-center flex flex-col items-center justify-center my-4">
      <div className="w-12 h-12 rounded-full bg-[#FF174F]/15 border border-[#FF174F]/40 flex items-center justify-center mb-3">
        <AlertCircle className="w-6 h-6 text-[#FF174F]" />
      </div>
      <h3 className="text-base font-semibold text-white mb-1">{title}</h3>
      <p className="text-sm text-[#A1A1AA] max-w-md mb-5 leading-relaxed">{message}</p>
      {onRetry && (
        <button onClick={onRetry} className="cyber-btn-secondary">
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Retry Request</span>
        </button>
      )}
    </div>
  );
}
