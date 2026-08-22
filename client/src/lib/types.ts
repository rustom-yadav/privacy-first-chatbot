/**
 * TypeScript interfaces matching the API's Pydantic schemas.
 * Keeps frontend ↔ backend contract type-safe.
 */

// ── Generic API Response Envelope ──────────────────────────────────

export interface APIResponse<T = unknown> {
  success: boolean;
  data: T | null;
  error: string | null;
}

// ── Chat Schemas ───────────────────────────────────────────────────

export interface ChatRequest {
  query: string;
  session_id?: string | null;
}

export interface SourceInfo {
  filename: string;
  page: number;
}

export interface ChatResponseData {
  query: string;
  answer: string;
  session_id: string;
  sources: SourceInfo[];
  response_time_ms: number;
}

// ── Document Schemas ───────────────────────────────────────────────

export interface DocumentInfo {
  filename: string;
  chunk_count: number;
}

export interface UploadResponseData {
  filename: string;
  chunk_count: number;
  message: string;
}

// ── Health Check ───────────────────────────────────────────────────

export interface DependencyStatus {
  status: "up" | "down";
  host?: string;
  model?: string;
  total_chunks?: number;
}

export interface HealthCheckResponse {
  status: "healthy" | "degraded";
  app: string;
  dependencies: {
    ollama: DependencyStatus;
    chromadb: DependencyStatus;
  };
}

// ── Local UI State ─────────────────────────────────────────────────

export interface Message {
  id: string;
  role: "human" | "ai";
  content: string;
  sources?: SourceInfo[];
  responseTimeMs?: number;
  timestamp: number;
}
