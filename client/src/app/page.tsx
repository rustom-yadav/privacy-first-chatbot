"use client";

import { useState } from "react";
import ChatWindow from "@/components/chat/ChatWindow";
import Sidebar from "@/components/sidebar/Sidebar";
import { useChat } from "@/hooks/useChat";
import { useDocuments } from "@/hooks/useDocuments";

export default function Home() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const chat = useChat();
  const docs = useDocuments();

  return (
    <div className="flex h-screen bg-surface-base overflow-hidden" id="app-root">
      {/* Sidebar */}
      <Sidebar
        documents={docs.documents}
        isLoadingDocs={docs.isLoading}
        isUploading={docs.isUploading}
        uploadSuccess={docs.uploadSuccess}
        docError={docs.error}
        onUpload={docs.upload}
        onDeleteDoc={docs.deleteDoc}
        onDismissSuccess={docs.dismissSuccess}
        onNewChat={chat.startNewChat}
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />

      {/* Main content */}
      <main className="flex-1 flex flex-col min-w-0">
        {/* Mobile top bar */}
        <div className="lg:hidden flex items-center gap-3 px-4 py-3 border-b border-border-subtle bg-surface-raised">
          <button
            onClick={() => setSidebarOpen(true)}
            className="p-2 rounded-lg hover:bg-surface-overlay text-text-secondary hover:text-text-primary transition-colors cursor-pointer"
            aria-label="Open sidebar"
            id="mobile-menu-button"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5" />
            </svg>
          </button>
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-lg bg-gradient-brand flex items-center justify-center">
              <svg className="w-3.5 h-3.5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z" />
              </svg>
            </div>
            <span className="text-sm font-semibold text-text-primary">
              Privacy-First Chatbot
            </span>
          </div>
        </div>

        {/* Chat Window */}
        <ChatWindow
          messages={chat.messages}
          isLoading={chat.isLoading}
          error={chat.error}
          onSend={chat.sendMessage}
          onDismissError={() => chat.setError(null)}
        />
      </main>
    </div>
  );
}
