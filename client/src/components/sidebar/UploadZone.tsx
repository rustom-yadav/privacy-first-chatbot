'use client';

import { useRef, useState, useCallback } from 'react';

interface UploadZoneProps {
  onUpload: (file: File) => Promise<boolean>;
  isUploading: boolean;
}

export default function UploadZone({ onUpload, isUploading }: UploadZoneProps) {
  const [isDragOver, setIsDragOver] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFiles = useCallback(
    async (files: FileList | null) => {
      if (!files || files.length === 0) return;
      const file = files[0];
      await onUpload(file);
      // Reset input
      if (inputRef.current) inputRef.current.value = '';
    },
    [onUpload]
  );

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragOver(false);
      handleFiles(e.dataTransfer.files);
    },
    [handleFiles]
  );

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  return (
    <div
      onDrop={handleDrop}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onClick={() => !isUploading && inputRef.current?.click()}
      className={`relative rounded-xl border-2 border-dashed p-3 text-center cursor-pointer transition-all ${
        isDragOver
          ? 'drop-zone-active border-brand-primary bg-brand-glow'
          : 'border-border-subtle hover:border-text-muted/30 hover:bg-surface-overlay/30'
      } ${isUploading ? 'pointer-events-none opacity-60' : ''}`}
      id="upload-zone"
    >
      <input
        ref={inputRef}
        type="file"
        accept=".pdf"
        onChange={(e) => handleFiles(e.target.files)}
        className="hidden"
        disabled={isUploading}
        id="file-upload-input"
      />

      {isUploading ? (
        <div className="flex flex-row items-center justify-center gap-3 py-1">
          <svg
            className="w-5 h-5 animate-spin text-brand-primary"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
            />
          </svg>
          <p className="text-xs text-text-secondary">Processing...</p>
        </div>
      ) : (
        <div className="flex flex-row items-center justify-center gap-3 py-1">
          <div className="w-8 h-8 rounded-lg bg-brand-glow flex items-center justify-center shrink-0">
            <svg
              className="w-4 h-4 text-brand-primary"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={2}
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5"
              />
            </svg>
          </div>
          <div className="text-left">
            <p className="text-xs font-medium text-text-primary leading-tight">
              Drop PDF or click
            </p>
            <p className="text-[10px] text-text-muted mt-0.5">Max 50 MB</p>
          </div>
        </div>
      )}
    </div>
  );
}
