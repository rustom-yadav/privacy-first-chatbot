'use client';

import { useRef, useEffect } from 'react';
import MessageBubble from './MessageBubble';
import ChatInput from './ChatInput';
import type { Message } from '@/lib/types';

interface ChatWindowProps {
  messages: Message[];
  isLoading: boolean;
  error: string | null;
  onSend: (message: string) => void;
  onDismissError: () => void;
}

function TypingIndicator() {
  return (
    <div className="flex justify-start mb-4 animate-fade-in">
      <div className="glass rounded-2xl rounded-bl-md px-5 py-4">
        <div className="flex items-center gap-2 mb-2 text-xs font-medium text-text-muted">
          <span className="text-sm">🤖</span>
          <span>AI Assistant</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="typing-dot w-2 h-2 rounded-full bg-brand-primary" />
          <span className="typing-dot w-2 h-2 rounded-full bg-brand-primary" />
          <span className="typing-dot w-2 h-2 rounded-full bg-brand-primary" />
        </div>
      </div>
    </div>
  );
}

function EmptyState() {
  return (
    <div className="flex flex-col items-center justify-center h-full text-center px-8 animate-fade-in">
      {/* Shield icon */}
      <div className="w-20 h-20 rounded-2xl bg-brand-glow flex items-center justify-center mb-6">
        <svg
          className="w-10 h-10 text-brand-primary"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          strokeWidth={1.5}
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z"
          />
        </svg>
      </div>

      <h2 className="text-2xl font-bold text-text-primary mb-2">
        Privacy-First AI Chat
      </h2>
      <p className="text-text-secondary max-w-md mb-8 leading-relaxed">
        Upload a PDF document from the sidebar, then ask questions about it.
        Everything runs locally — your data never leaves your machine.
      </p>

      {/* Feature cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 max-w-lg w-full">
        {[
          { icon: '🔒', title: '100% Private', desc: 'No cloud, no tracking' },
          { icon: '📄', title: 'PDF Support', desc: 'Upload & chat with docs' },
          { icon: '⚡', title: 'Local LLM', desc: 'Powered by Ollama' },
        ].map((f) => (
          <div
            key={f.title}
            className="glass-light rounded-xl p-4 text-center hover:border-brand-primary/20 transition-colors"
          >
            <span className="text-2xl mb-2 block">{f.icon}</span>
            <p className="text-sm font-semibold text-text-primary">{f.title}</p>
            <p className="text-xs text-text-muted mt-0.5">{f.desc}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

export default function ChatWindow({
  messages,
  isLoading,
  error,
  onSend,
  onDismissError,
}: ChatWindowProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  return (
    <div className="flex flex-col h-full" id="chat-window">
      {/* Header */}
      <div className="px-6 py-4 border-b border-border-subtle flex items-center gap-3">
        <div className="w-2.5 h-2.5 rounded-full bg-brand-primary animate-pulse-glow" />
        <h1 className="text-lg font-semibold text-text-primary">Chat</h1>
        {messages.length > 0 && (
          <span className="text-xs text-text-muted ml-auto">
            {messages.length} messages
          </span>
        )}
      </div>

      {/* Messages area */}
      <div className="flex-1 overflow-y-auto px-6 py-4">
        {messages.length === 0 && !isLoading ? (
          <EmptyState />
        ) : (
          <>
            {messages.map((msg) => (
              <MessageBubble key={msg.id} message={msg} />
            ))}
            {isLoading && <TypingIndicator />}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* Error banner */}
      {error && (
        <div className="mx-6 mb-2 px-4 py-3 rounded-xl bg-status-down/10 border border-status-down/20 flex items-center gap-3 animate-fade-in">
          <svg
            className="w-4 h-4 text-status-down shrink-0"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={2}
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z"
            />
          </svg>
          <p className="text-sm text-status-down flex-1">{error}</p>
          <button
            onClick={onDismissError}
            className="text-status-down/60 hover:text-status-down transition-colors cursor-pointer"
          >
            <svg
              className="w-4 h-4"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={2}
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>
      )}

      {/* Input */}
      <ChatInput onSend={onSend} isLoading={isLoading} />
    </div>
  );
}
