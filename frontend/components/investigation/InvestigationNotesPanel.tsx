"use client";

import React, { useState, useEffect, useCallback } from "react";
import {
  getInvestigationNotes,
  addInvestigationNote,
  deleteInvestigationNote,
  InvestigationNoteItem,
} from "@/lib/api";
import { MessageSquare, Send, Trash2, RefreshCw, AlertCircle, CheckCircle2 } from "lucide-react";

export function InvestigationNotesPanel({
  investigationId,
  onNotesChanged,
}: {
  investigationId: string;
  onNotesChanged?: () => void;
}) {
  const [notes, setNotes] = useState<InvestigationNoteItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [content, setContent] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const loadNotes = useCallback(async () => {
    setLoading(true);
    try {
      const items = await getInvestigationNotes(investigationId);
      setNotes(items || []);
    } catch (err: any) {
      setErrorMsg(err?.message || "Could not load investigation notes.");
    } finally {
      setLoading(false);
    }
  }, [investigationId]);

  useEffect(() => {
    loadNotes();
  }, [loadNotes]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = content.trim();
    if (!trimmed || submitting) return;

    setSubmitting(true);
    setErrorMsg(null);
    setSuccessMsg(null);
    try {
      await addInvestigationNote(investigationId, trimmed);
      setContent("");
      setSuccessMsg("Note saved.");
      await loadNotes();
      if (onNotesChanged) onNotesChanged();
      setTimeout(() => setSuccessMsg(null), 3000);
    } catch (err: any) {
      setErrorMsg(err?.message || "Authorization or validation error saving note.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (noteId: string) => {
    setErrorMsg(null);
    try {
      await deleteInvestigationNote(investigationId, noteId);
      await loadNotes();
    } catch (err: any) {
      setErrorMsg(err?.message || "Not authorized to delete this note.");
    }
  };

  return (
    <div className="p-4 space-y-3 font-sans text-xs border-t border-[#3A4553]">
      <div className="flex items-center justify-between">
        <span className="font-mono text-[11px] uppercase tracking-wider text-[#22D3EE] font-semibold flex items-center space-x-1.5">
          <MessageSquare className="w-3.5 h-3.5" />
          <span>Analyst Notes ({notes.length})</span>
        </span>
      </div>

      <form onSubmit={handleSubmit} className="space-y-2">
        <textarea
          rows={2}
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder="Add persistent investigation note (requires sign-in)..."
          className="w-full p-2 rounded bg-[#181E28] border border-[#3A4553] text-slate-100 placeholder-slate-500 text-xs focus:outline-none focus:border-[#60A5FA]"
        />
        <button
          type="submit"
          disabled={submitting || !content.trim()}
          className="w-full py-1.5 px-3 rounded bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white font-semibold text-xs inline-flex items-center justify-center space-x-1.5"
        >
          {submitting ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Send className="w-3.5 h-3.5" />}
          <span>{submitting ? "Saving..." : "Save Note"}</span>
        </button>
      </form>

      {errorMsg && (
        <div className="p-2 rounded bg-rose-950/60 border border-rose-800/70 text-rose-300 text-[11px] flex items-center space-x-1.5">
          <AlertCircle className="w-3.5 h-3.5 shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}

      {successMsg && (
        <div className="p-2 rounded bg-emerald-950/60 border border-emerald-800/70 text-emerald-300 text-[11px] flex items-center space-x-1.5">
          <CheckCircle2 className="w-3.5 h-3.5 shrink-0" />
          <span>{successMsg}</span>
        </div>
      )}

      {loading ? (
        <div className="text-[11px] text-slate-400">Loading notes...</div>
      ) : notes.length === 0 ? (
        <div className="text-[11px] text-slate-500 italic">No notes recorded for this investigation yet.</div>
      ) : (
        <div className="space-y-2 max-h-56 overflow-y-auto">
          {notes.map((n) => (
            <div key={n.note_id} className="p-2.5 rounded bg-[#181E28] border border-[#3A4553] space-y-1">
              <div className="flex items-center justify-between text-[10px] font-mono text-slate-400">
                <span>
                  {n.author_role} • {n.author_id.slice(0, 8)}
                </span>
                <button
                  type="button"
                  onClick={() => handleDelete(n.note_id)}
                  title="Delete note"
                  className="text-slate-500 hover:text-rose-400"
                >
                  <Trash2 className="w-3 h-3" />
                </button>
              </div>
              <p className="text-slate-200 whitespace-pre-wrap break-words">{n.content}</p>
              <div className="text-[10px] font-mono text-slate-500">
                {new Date(n.created_at).toLocaleString()}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
