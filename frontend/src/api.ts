// Calls to the services. All go through /api/<service> — the Vite dev proxy or nginx
// forwards them, so the browser only ever talks to its own origin.

import type { ChatResponse, CorpusInfo, IngestJob, IngestMode, Interaction, Page, Stats, Turn } from "./types";

export class ApiError extends Error {
  constructor(
    message: string,
    readonly status: number,
    readonly code: string,
    readonly requestId: string | null,
  ) {
    super(message);
  }
}

async function call<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(path, {
      ...init,
      headers: { "Content-Type": "application/json", ...init?.headers },
    });
  } catch {
    throw new ApiError("network", 0, "network", null);
  }
  if (!response.ok) {
    // Services answer errors as {"error": {"code", "message"}, "request_id"}.
    const body = await response.json().catch(() => null);
    throw new ApiError(
      body?.error?.message ?? response.statusText,
      response.status,
      body?.error?.code ?? "error",
      body?.request_id ?? response.headers.get("X-Request-ID"),
    );
  }
  return response.json() as Promise<T>;
}

export const api = {
  chat: (question: string, history: Turn[], sessionId: string, quote?: string) =>
    call<ChatResponse>("/api/chat/v1/chat", {
      method: "POST",
      body: JSON.stringify({ question, history, session_id: sessionId, quote: quote || null }),
    }),

  ingest: (pages: Page[], mode: IngestMode) =>
    call<IngestJob>("/api/ingestion/v1/ingest", { method: "POST", body: JSON.stringify({ pages, mode }) }),

  job: (jobId: string) => call<IngestJob>(`/api/ingestion/v1/ingest/${jobId}`),

  corpus: () => call<CorpusInfo>("/api/ingestion/v1/corpus"),

  stats: (days: number) => call<Stats>(`/api/analytics/v1/stats?days=${days}`),

  interactions: (limit: number) =>
    call<{ items: Interaction[]; total: number }>(`/api/analytics/v1/interactions?limit=${limit}`),
};
