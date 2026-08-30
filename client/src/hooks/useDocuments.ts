"use client";

import { useState, useCallback, useEffect } from "react";
import {
  listDocuments,
  uploadDocument,
  deleteDocument as apiDeleteDocument,
} from "@/lib/api";
import type { DocumentInfo } from "@/lib/types";

export function useDocuments() {
  const [documents, setDocuments] = useState<DocumentInfo[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [uploadSuccess, setUploadSuccess] = useState<string | null>(null);

  /**
   * Fetches the list of all ingested documents.
   */
  const fetchDocuments = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await listDocuments();

      if (response.success && response.data) {
        setDocuments(response.data);
      } else {
        setError(response.error || "Failed to load documents.");
      }
    } catch {
      setError("Could not connect to API. Is the server running?");
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Uploads a PDF file for RAG ingestion.
   */
  const upload = useCallback(
    async (file: File) => {
      setIsUploading(true);
      setError(null);
      setUploadSuccess(null);

      // Client-side validation
      if (!file.name.toLowerCase().endsWith(".pdf")) {
        setError("Only PDF files are allowed.");
        setIsUploading(false);
        return false;
      }

      // 50 MB limit (matching API)
      if (file.size > 50 * 1024 * 1024) {
        setError("File size exceeds 50 MB limit.");
        setIsUploading(false);
        return false;
      }

      try {
        const response = await uploadDocument(file);

        if (response.success && response.data) {
          setUploadSuccess(
            `"${response.data.filename}" uploaded — ${response.data.chunk_count} chunks created.`
          );
          // Refresh document list
          await fetchDocuments();
          return true;
        } else {
          setError(response.error || "Upload failed.");
          return false;
        }
      } catch {
        setError("Network error during upload.");
        return false;
      } finally {
        setIsUploading(false);
      }
    },
    [fetchDocuments]
  );

  /**
   * Deletes a document and its vectors.
   */
  const deleteDoc = useCallback(
    async (filename: string) => {
      setError(null);

      try {
        const response = await apiDeleteDocument(filename);

        if (response.success) {
          // Refresh list
          await fetchDocuments();
          return true;
        } else {
          setError(response.error || "Failed to delete document.");
          return false;
        }
      } catch {
        setError("Network error during deletion.");
        return false;
      }
    },
    [fetchDocuments]
  );

  /**
   * Clears the upload success message.
   */
  const dismissSuccess = useCallback(() => {
    setUploadSuccess(null);
  }, []);

  // Fetch documents on mount
  useEffect(() => {
    // eslint-disable-next-line
    fetchDocuments();
  }, [fetchDocuments]);

  return {
    documents,
    isLoading,
    isUploading,
    error,
    uploadSuccess,
    upload,
    deleteDoc,
    fetchDocuments,
    dismissSuccess,
    setError,
  };
}
