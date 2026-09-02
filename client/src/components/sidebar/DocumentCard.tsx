"use client";

import type { DocumentInfo } from "@/lib/types";
import { useState } from "react";

interface DocumentCardProps {
  document: DocumentInfo;
  onDelete: (filename: string) => Promise<boolean>;
}

export default function DocumentCard({ document, onDelete }: DocumentCardProps) {
  const [isDeleting, setIsDeleting] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);

  const handleDelete = async () => {
    setIsDeleting(true);
    await onDelete(document.filename);
    setIsDeleting(false);
    setShowConfirm(false);
  };

  return (
    <div className="group glass-light rounded-xl p-3 hover:border-brand-primary/20 transition-all animate-fade-in">
      <div className="flex items-start gap-3">
        {/* File icon */}
        <div className="w-9 h-9 rounded-lg bg-brand-glow flex items-center justify-center shrink-0 mt-0.5">
          <svg className="w-4.5 h-4.5 text-brand-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
          </svg>
        </div>

        {/* Info */}
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-text-primary truncate" title={document.filename}>
            {document.filename}
          </p>
          <p className="text-xs text-text-muted mt-0.5">
            {document.chunk_count} chunks
          </p>
        </div>

        {/* Delete button */}
        {!showConfirm ? (
          <button
            onClick={() => setShowConfirm(true)}
            className="opacity-0 group-hover:opacity-100 p-1.5 rounded-lg hover:bg-status-down/10 text-text-muted hover:text-status-down transition-all cursor-pointer"
            title="Delete document"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M14.74 9l-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 01-2.244 2.077H8.084a2.25 2.25 0 01-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 00-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 013.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 00-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 00-7.5 0" />
            </svg>
          </button>
        ) : (
          <div className="flex items-center gap-1">
            <button
              onClick={handleDelete}
              disabled={isDeleting}
              className="p-1.5 rounded-lg bg-status-down/10 text-status-down hover:bg-status-down/20 transition-colors disabled:opacity-50 cursor-pointer"
              title="Confirm delete"
            >
              {isDeleting ? (
                <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
              ) : (
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                </svg>
              )}
            </button>
            <button
              onClick={() => setShowConfirm(false)}
              className="p-1.5 rounded-lg hover:bg-surface-overlay text-text-muted hover:text-text-primary transition-colors cursor-pointer"
              title="Cancel"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
