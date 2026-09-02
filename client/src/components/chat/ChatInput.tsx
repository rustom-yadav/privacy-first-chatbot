"use client";

import { useState, useRef, useEffect, useCallback } from "react";

interface ChatInputProps {
  onSend: (message: string) => void;
  isLoading: boolean;
  maxLength?: number;
}

export default function ChatInput({
  onSend,
  isLoading,
  maxLength = 2000,
}: ChatInputProps) {
  const [value, setValue] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea
  const adjustHeight = useCallback(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, 160)}px`;
  }, []);

  useEffect(() => {
    adjustHeight();
  }, [value, adjustHeight]);

  const handleSend = () => {
    const trimmed = value.trim();
    if (!trimmed || isLoading || trimmed.length > maxLength) return;
    onSend(trimmed);
    setValue("");
    // Reset textarea height
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const charCount = value.length;
  const isOverLimit = charCount > maxLength;
  const isEmpty = !value.trim();

  return (
    <div className="p-4 border-t border-border-subtle">
      <div className="glass rounded-2xl p-3 flex items-end gap-3 transition-all focus-within:border-brand-primary/40">
        {/* Textarea */}
        <textarea
          ref={textareaRef}
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask a question about your documents..."
          disabled={isLoading}
          rows={1}
          className="flex-1 bg-transparent text-sm text-text-primary placeholder:text-text-muted resize-none outline-none min-h-[24px] max-h-[160px] leading-relaxed disabled:opacity-50"
          id="chat-input"
        />

        {/* Right side: char count + send button */}
        <div className="flex items-center gap-2 shrink-0">
          {/* Character count (visible when typing) */}
          {charCount > 0 && (
            <span
              className={`text-xs tabular-nums transition-colors ${
                isOverLimit ? "text-status-down" : "text-text-muted"
              }`}
            >
              {charCount}/{maxLength}
            </span>
          )}

          {/* Send button */}
          <button
            onClick={handleSend}
            disabled={isLoading || isEmpty || isOverLimit}
            className="flex items-center justify-center w-9 h-9 rounded-xl bg-gradient-brand text-white transition-all hover:opacity-90 active:scale-95 disabled:opacity-30 disabled:cursor-not-allowed cursor-pointer"
            title="Send message (Enter)"
            id="send-button"
          >
            {isLoading ? (
              <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
            ) : (
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 12L3.269 3.126A59.768 59.768 0 0121.485 12 59.77 59.77 0 013.27 20.876L5.999 12zm0 0h7.5" />
              </svg>
            )}
          </button>
        </div>
      </div>

      {/* Hint */}
      <p className="text-xs text-text-muted mt-2 ml-1">
        Press <kbd className="px-1.5 py-0.5 rounded bg-surface-overlay text-text-secondary text-[10px] font-mono">Enter</kbd> to send
        · <kbd className="px-1.5 py-0.5 rounded bg-surface-overlay text-text-secondary text-[10px] font-mono">Shift + Enter</kbd> for new line
      </p>
    </div>
  );
}
