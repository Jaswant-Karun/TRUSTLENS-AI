"use client";

import React, { useRef, useEffect } from "react";
import { Search, X } from "lucide-react";

interface InvestigationSearchProps {
  value: string;
  onChange: (value: string) => void;
  matchesCount?: number;
  placeholder?: string;
  className?: string;
}

export function InvestigationSearch({
  value,
  onChange,
  matchesCount,
  placeholder = "Filter nodes...",
  className = "",
}: InvestigationSearchProps) {
  const inputRef = useRef<HTMLInputElement>(null);

  // Keyboard shortcut: '/' focuses search input
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (
        e.key === "/" &&
        document.activeElement?.tagName !== "INPUT" &&
        document.activeElement?.tagName !== "TEXTAREA"
      ) {
        e.preventDefault();
        inputRef.current?.focus();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  return (
    <div
      className={`relative flex items-center bg-[#252D38]/90 backdrop-blur-md border border-[#3A4553] rounded-md h-8 px-2 shadow-xl ${className}`}
    >
      <Search className="w-3.5 h-3.5 text-slate-400 mr-2 shrink-0" />
      <input
        ref={inputRef}
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        className="bg-transparent text-xs text-slate-200 placeholder-slate-400 focus:outline-none w-28 md:w-36 font-sans"
      />
      {value ? (
        <button
          onClick={() => onChange("")}
          title="Clear Search"
          className="text-slate-400 hover:text-white ml-1 shrink-0"
        >
          <X className="w-3 h-3" />
        </button>
      ) : (
        <span className="hidden md:inline-block text-[9px] font-mono text-slate-500 bg-[#181E28] px-1 rounded ml-1 border border-[#3A4553]/60">
          /
        </span>
      )}

      {/* Match indicator pill */}
      {value && matchesCount !== undefined && (
        <span className="ml-1.5 text-[9px] font-mono font-bold text-cyan-400 bg-cyan-950/80 px-1 py-0.2 rounded border border-cyan-800/60 shrink-0">
          {matchesCount}
        </span>
      )}
    </div>
  );
}
