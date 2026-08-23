/**
 * Type-safe API client for the Privacy-First Chatbot backend.
 *
 * All calls go through Next.js rewrites (/api/* → backend),
 * so no CORS issues in development.
 */

import type {
  APIResponse,
  ChatResponseData,
  ClearHistoryResponseData,
  DocumentInfo,
  HealthCheckResponse,
  UploadResponseData,
} from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// ── Helper ─────────────────────────────────────────────────────────

async function apiFetch<T>(
  path: string,
  options?: RequestInit
): Promise<APIResponse<T>> {
  const url = `${API_BASE}${path}`;

  const res = await fetch(url, {
    ...options,
    headers: {
       "Content-Type": "application/json", 
       ...options?.headers
    },
  });

  if (!res.ok) {
    const errorBody = await res.json().catch(() => null);
    return {
      success: false,
      data: null,
      error: errorBody?.detail || errorBody?.error || `HTTP ${res.status}`,
    };
  }

  return res.json();
}

// ── Chat Endpoints ─────────────────────────────────────────────────

export async function sendChat(
  query: string,
  sessionId?: string | null
): Promise<APIResponse<ChatResponseData>> {
  return apiFetch<ChatResponseData>("/api/chat/", {
    method: "POST",
    body: JSON.stringify({
      query,
      session_id: sessionId || null,
    }),
  });
}

export async function clearHistory(
  sessionId: string
): Promise<APIResponse<ClearHistoryResponseData>> {
  return apiFetch<ClearHistoryResponseData>(`/api/chat/history?session_id=${encodeURIComponent(sessionId)}`, {
    method: "DELETE",
  });
}

// ── Document Endpoints ─────────────────────────────────────────────

export async function uploadDocument(
  file: File
): Promise<APIResponse<UploadResponseData>> {
  const formData = new FormData();
  formData.append("file", file);

  const url = `${API_BASE}/api/document/upload`;

  const res = await fetch(url, {
    method: "POST",
    body: formData,
    // No Content-Type header — browser sets it with boundary for multipart
  });

  if (!res.ok) {
    const errorBody = await res.json().catch(() => null);
    return {
      success: false,
      data: null,
      error: errorBody?.detail || errorBody?.error || `Upload failed: HTTP ${res.status}`,
    };
  }

  return res.json();
}

export async function listDocuments(): Promise<APIResponse<DocumentInfo[]>> {
  return apiFetch<DocumentInfo[]>("/api/document/list", { method: "GET" });
}

export async function deleteDocument(
  filename: string
): Promise<APIResponse<{ message: string }>> {
  return apiFetch(`/api/document/${encodeURIComponent(filename)}`, {
    method: "DELETE",
  });
}

// ── Health Check ───────────────────────────────────────────────────

export async function healthCheck(): Promise<HealthCheckResponse | null> {
  try {
    const url = `${API_BASE}/health`;
    const res = await fetch(url);
    if (!res.ok) return null;
    return res.json();
  } catch {
    return null;
  }
}
