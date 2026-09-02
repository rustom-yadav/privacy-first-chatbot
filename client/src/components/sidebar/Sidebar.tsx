"use client";

import { useEffect, useState } from "react";
import DocumentCard from "./DocumentCard";
import UploadZone from "./UploadZone";
import StatusBadge from "./StatusBadge";
import { healthCheck } from "@/lib/api";
import type { DocumentInfo } from "@/lib/types";

interface SidebarProps {
  documents: DocumentInfo[];
  isLoadingDocs: boolean;
  isUploading: boolean;
  uploadSuccess: string | null;
  docError: string | null;
  onUpload: (file: File) => Promise<boolean>;
  onDeleteDoc: (filename: string) => Promise<boolean>;
  onDismissSuccess: () => void;
  onNewChat: () => void;
  isOpen: boolean;
  onClose: () => void;
}

export default function Sidebar({
  documents,
  isLoadingDocs,
  isUploading,
  uploadSuccess,
  docError,
  onUpload,
  onDeleteDoc,
  onDismissSuccess,
  onNewChat,
  isOpen,
  onClose,
}: SidebarProps) {
  const [healthStatus, setHealthStatus] = useState<
    "healthy" | "degraded" | "down" | "checking"
  >("checking");

  // Check health on mount and periodically
  useEffect(() => {
    const checkHealth = async () => {
      const result = await healthCheck();
      if (result) {
        setHealthStatus(result.status);
      } else {
        setHealthStatus("down");
      }
    };

    checkHealth();
    const interval = setInterval(checkHealth, 30000); // every 30 seconds
    return () => clearInterval(interval);
  }, []);

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/60 z-40 lg:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed lg:static inset-y-0 left-0 z-50 w-72 bg-surface-raised border-r border-border-subtle flex flex-col transition-transform duration-300 lg:translate-x-0 ${
          isOpen ? "translate-x-0" : "-translate-x-full"
        }`}
        id="sidebar"
      >
        {/* Branding */}
        <div className="px-5 py-5 border-b border-border-subtle">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-brand flex items-center justify-center shrink-0">
              <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z" />
              </svg>
            </div>
            <div className="min-w-0">
              <h2 className="text-sm font-bold text-text-primary truncate">
                Privacy-First
              </h2>
              <p className="text-xs text-text-muted">Chatbot</p>
            </div>

            {/* Mobile close */}
            <button
              onClick={onClose}
              className="lg:hidden ml-auto p-1.5 rounded-lg hover:bg-surface-overlay text-text-muted hover:text-text-primary transition-colors cursor-pointer"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        {/* New Chat button */}
        <div className="px-4 py-3">
          <button
            onClick={onNewChat}
            className="w-full flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl bg-gradient-brand text-white text-sm font-medium hover:opacity-90 active:scale-[0.98] transition-all cursor-pointer"
            id="new-chat-button"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
            </svg>
            New Chat
          </button>
        </div>

        {/* Documents section */}
        <div className="flex-1 overflow-y-auto px-4 pb-4">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-xs font-semibold text-text-muted uppercase tracking-wider">
              Documents
            </h3>
            {documents.length > 0 && (
              <span className="text-xs text-text-muted bg-surface-overlay px-2 py-0.5 rounded-full">
                {documents.length}
              </span>
            )}
          </div>

          {/* Upload zone */}
          <div className="mb-3">
            <UploadZone onUpload={onUpload} isUploading={isUploading} />
          </div>

          {/* Upload success message */}
          {uploadSuccess && (
            <div className="mb-3 px-3 py-2.5 rounded-xl bg-brand-primary/10 border border-brand-primary/20 animate-fade-in">
              <div className="flex items-start gap-2">
                <svg className="w-4 h-4 text-brand-primary shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <p className="text-xs text-brand-primary flex-1">{uploadSuccess}</p>
                <button onClick={onDismissSuccess} className="text-brand-primary/50 hover:text-brand-primary cursor-pointer">
                  <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>
          )}

          {/* Document error */}
          {docError && (
            <div className="mb-3 px-3 py-2.5 rounded-xl bg-status-down/10 border border-status-down/20 animate-fade-in">
              <p className="text-xs text-status-down">{docError}</p>
            </div>
          )}

          {/* Document list */}
          {isLoadingDocs ? (
            <div className="space-y-2">
              {[1, 2].map((i) => (
                <div key={i} className="h-16 rounded-xl animate-shimmer" />
              ))}
            </div>
          ) : documents.length === 0 ? (
            <div className="text-center py-6">
              <svg className="w-10 h-10 text-text-muted/30 mx-auto mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m6.75 12H9.75m0 0l2.25-2.25M9.75 15l2.25 2.25M13.5 3H7.5A2.25 2.25 0 005.25 5.25v13.5A2.25 2.25 0 007.5 21h9a2.25 2.25 0 002.25-2.25V8.25" />
              </svg>
              <p className="text-xs text-text-muted">No documents yet</p>
              <p className="text-xs text-text-muted/60 mt-0.5">
                Upload a PDF to get started
              </p>
            </div>
          ) : (
            <div className="space-y-2">
              {documents.map((doc) => (
                <DocumentCard
                  key={doc.filename}
                  document={doc}
                  onDelete={onDeleteDoc}
                />
              ))}
            </div>
          )}
        </div>

        {/* Footer: Health status */}
        <div className="px-4 py-3 border-t border-border-subtle">
          <StatusBadge status={healthStatus} />
        </div>
      </aside>
    </>
  );
}
