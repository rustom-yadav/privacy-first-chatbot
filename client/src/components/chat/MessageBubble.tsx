"use client";

import { useState } from "react";
import type { Message } from "@/lib/types";

interface MessageBubbleProps {
  message: Message;
}

export default function MessageBubble({ message }: MessageBubbleProps) {
  const [showSources, setShowSources] = useState(false);
  const [copied, setCopied] = useState(false);
  const isHuman = message.role === "human";

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(message.content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Clipboard API may fail in some contexts
    }
  };

  return (
    <div
      className={`flex w-full mb-4 ${isHuman ? "justify-end animate-slide-right" : "justify-start animate-slide-left"}`}
    >
      <div
        className={`relative max-w-[80%] lg:max-w-[70%] rounded-2xl px-5 py-3.5 ${
          isHuman
            ? "bg-gradient-brand text-white rounded-br-md"
            : "glass text-text-primary rounded-bl-md"
        }`}
      >
        {/* Role badge */}
        <div
          className={`flex items-center gap-2 mb-2 text-xs font-medium ${
            isHuman ? "text-emerald-100" : "text-text-muted"
          }`}
        >
          <span className="text-sm">{isHuman ? "👤" : "🤖"}</span>
          <span>{isHuman ? "You" : "AI Assistant"}</span>
          {!isHuman && message.responseTimeMs && (
            <span className="ml-auto text-text-muted opacity-60">
              {(message.responseTimeMs / 1000).toFixed(1)}s
            </span>
          )}
        </div>

        {/* Message content */}
        <div className="text-sm leading-relaxed whitespace-pre-wrap break-words">
          {message.content}
        </div>

        {/* AI-only: Copy button + Sources */}
        {!isHuman && (
          <div className="mt-3 flex items-center gap-3 flex-wrap">
            {/* Copy button */}
            <button
              onClick={handleCopy}
              className="flex items-center gap-1 text-xs text-text-muted hover:text-text-primary transition-colors cursor-pointer"
              title="Copy response"
            >
              {copied ? (
                <>
                  <svg className="w-3.5 h-3.5 text-brand-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                  </svg>
                  <span className="text-brand-primary">Copied</span>
                </>
              ) : (
                <>
                  <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                  </svg>
                  <span>Copy</span>
                </>
              )}
            </button>

            {/* Source toggle */}
            {message.sources && message.sources.length > 0 && (
              <button
                onClick={() => setShowSources(!showSources)}
                className="flex items-center gap-1 text-xs text-brand-primary hover:text-brand-primary-light transition-colors cursor-pointer"
              >
                <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <span>
                  {showSources ? "Hide" : "Show"} Sources ({message.sources.length})
                </span>
              </button>
            )}
          </div>
        )}

        {/* Expanded sources */}
        {showSources && message.sources && message.sources.length > 0 && (
          <div className="mt-3 pt-3 border-t border-border-subtle">
            <div className="flex flex-wrap gap-2">
              {message.sources.map((src, i) => (
                <span
                  key={`${src.filename}-${src.page}-${i}`}
                  className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-brand-glow text-brand-primary text-xs font-medium"
                >
                  <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                  </svg>
                  {src.filename} · p.{src.page}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
