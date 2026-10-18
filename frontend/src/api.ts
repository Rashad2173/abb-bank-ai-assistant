// Calls to the services. All go through /api/<service> — the Vite dev proxy or nginx
// forwards them, so the browser only ever talks to its own origin.

import type { ChatResponse, CorpusInfo, IngestJob, IngestMode, Interaction, Page, ScrapeJob, Stats, Turn } from "./types";

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
  // A FormData body sets its own multipart content type.
  const json = !(init?.body instanceof FormData);
  try {
    response = await fetch(path, {
      ...init,
      headers: { ...(json ? { "Content-Type": "application/json" } : {}), ...init?.headers },
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

  /** PDF / TXT documents: the service extracts their text and returns the pages it built. */
  ingestFiles: (files: File[], mode: IngestMode) => {
    const form = new FormData();
    files.forEach((file) => form.append("files", file));
    form.append("mode", mode);
    return call<{ job: IngestJob; pages: Page[] }>("/api/ingestion/v1/ingest/files", { method: "POST", body: form });
  },

  job: (jobId: string) => call<IngestJob>(`/api/ingestion/v1/ingest/${jobId}`),

  corpus: () => call<CorpusInfo>("/api/ingestion/v1/corpus"),

  scrape: (url: string, mode: IngestMode) =>
    call<ScrapeJob>("/api/scraper/v1/scrape", { method: "POST", body: JSON.stringify({ url, mode }) }),

  scrapeJob: (jobId: string) => call<ScrapeJob>(`/api/scraper/v1/scrape/${jobId}`),

  /** The extracted pages of a finished scrape (JSON Lines) — kept in localStorage like an upload. */
  scrapedPages: async (jobId: string) => {
    const response = await fetch(`/api/scraper/v1/scrape/${jobId}/pages`);
    if (!response.ok) throw new ApiError(response.statusText, response.status, "error", null);
    return response.text();
  },

  stats: (days: number) => call<Stats>(`/api/analytics/v1/stats?days=${days}`),

  interactions: (limit: number) =>
    call<{ items: Interaction[]; total: number }>(`/api/analytics/v1/interactions?limit=${limit}`),
};
