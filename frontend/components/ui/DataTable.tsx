"use client";

import React from "react";
import { ChevronLeft, ChevronRight, Inbox } from "lucide-react";
import { SkeletonTable } from "./LoadingStates";

export interface Column<T = any> {
  header: string;
  accessorKey?: keyof T | string;
  cell?: (row: T) => React.ReactNode;
  align?: "left" | "center" | "right";
  className?: string;
}

interface DataTableProps<T = any> {
  columns: Column<T>[];
  data: T[];
  loading?: boolean;
  emptyTitle?: string;
  emptyDescription?: string;
  onRowClick?: (row: T) => void;
  pagination?: {
    currentPage: number;
    totalPages: number;
    totalItems?: number;
    onPageChange: (page: number) => void;
  };
}

export function DataTable<T = any>({
  columns,
  data,
  loading = false,
  emptyTitle = "No records found",
  emptyDescription = "There are currently no items matching your criteria.",
  onRowClick,
  pagination,
}: DataTableProps<T>) {
  if (loading) {
    return <SkeletonTable rows={5} />;
  }

  if (!data || data.length === 0) {
    return (
      <div className="cyber-panel p-12 text-center flex flex-col items-center justify-center">
        <div className="w-12 h-12 rounded-full bg-[#170A12] border border-[#481326] flex items-center justify-center text-[#FF3D70] mb-3">
          <Inbox className="w-6 h-6" />
        </div>
        <h4 className="text-sm font-semibold text-white mb-1">{emptyTitle}</h4>
        <p className="text-xs text-[#A1A1AA] max-w-sm">{emptyDescription}</p>
      </div>
    );
  }

  const alignClasses = {
    left: "text-left",
    center: "text-center",
    right: "text-right",
  };

  return (
    <div className="cyber-panel overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs font-sans">
          <thead className="bg-[#170A12] text-[#A1A1AA] font-semibold border-b border-[#481326] tracking-wider font-mono uppercase text-[11px]">
            <tr>
              {columns.map((col, idx) => (
                <th
                  key={idx}
                  className={`py-3 px-4 ${alignClasses[col.align || "left"]} ${col.className || ""}`}
                >
                  {col.header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-[#481326]/50 text-white/90">
            {data.map((row, rowIdx) => (
              <tr
                key={rowIdx}
                onClick={() => onRowClick && onRowClick(row)}
                className={`transition-colors ${
                  onRowClick
                    ? "cursor-pointer hover:bg-[#170A12]/80"
                    : "hover:bg-[#170A12]/40"
                }`}
              >
                {columns.map((col, colIdx) => {
                  let content: React.ReactNode = null;
                  if (col.cell) {
                    content = col.cell(row);
                  } else if (col.accessorKey) {
                    content = String((row as any)[col.accessorKey] ?? "—");
                  }

                  return (
                    <td
                      key={colIdx}
                      className={`py-3.5 px-4 ${alignClasses[col.align || "left"]} ${col.className || ""}`}
                    >
                      {content}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {pagination && pagination.totalPages > 1 && (
        <div className="px-4 py-3 bg-[#170A12]/80 border-t border-[#481326] flex items-center justify-between text-xs text-[#A1A1AA] font-medium">
          <div>
            Page {pagination.currentPage} of {pagination.totalPages}
            {pagination.totalItems !== undefined && ` (${pagination.totalItems} total items)`}
          </div>
          <div className="flex items-center space-x-1.5">
            <button
              onClick={() => pagination.onPageChange(pagination.currentPage - 1)}
              disabled={pagination.currentPage <= 1}
              aria-label="Previous page"
              className="p-1.5 rounded border border-[#481326] bg-[#050306] text-white hover:border-[#FF174F] disabled:opacity-40 disabled:pointer-events-none transition-colors"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <button
              onClick={() => pagination.onPageChange(pagination.currentPage + 1)}
              disabled={pagination.currentPage >= pagination.totalPages}
              aria-label="Next page"
              className="p-1.5 rounded border border-[#481326] bg-[#050306] text-white hover:border-[#FF174F] disabled:opacity-40 disabled:pointer-events-none transition-colors"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
