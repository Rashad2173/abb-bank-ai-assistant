// JSON contracts of the services (see services/README.md).

export type ChatStatus = "answered" | "greeting" | "out_of_scope" | "no_information";

export interface Source {
  id: string;
  title: string;
  url: string;
  published: string | null;
  is_active: boolean | null;
  valid_until: string | null;
}

export interface Timings {
  rewrite_ms: number;
  retrieval_ms: number;
  rerank_ms: number;
  generation_ms: number;
  total_ms: number;
}

export interface ChatResponse {
  answer: string;
  status: ChatStatus;
  refusal_reason: string;
  language: string;
  sources: Source[];
  standalone_question: string;
  search_queries: string[];
  reranked: boolean;
  model: string;
  timings: Timings;
  request_id: string;
}

export interface Turn {
  role: "user" | "assistant";
  content: string;
}

export type IngestMode = "replace" | "append";

export type JobStatus = "queued" | "chunking" | "comparing" | "embedding" | "writing" | "done" | "failed";

export interface IngestJob {
  job_id: string;
  status: JobStatus;
  mode: IngestMode;
  pages: number;
  chunks: number;
  unchanged: number;
  to_embed: number;
  embedded: number;
  deleted: number;
  error: string | null;
  started_at: string;
  finished_at: string | null;
}

export interface CorpusInfo {
  collection: string;
  chunks: number;
  last_job: IngestJob | null;
}

export interface DayCount {
  date: string;
  total: number;
  answered: number;
  refused: number;
  no_information: number;
}

export interface Stats {
  period_days: number;
  total: number;
  by_status: Record<string, number>;
  by_refusal_reason: Record<string, number>;
  by_language: Record<string, number>;
  per_day: DayCount[];
  by_hour: number[];
  latency: { avg_ms: number; p50_ms: number; p95_ms: number };
  reranked_share: number;
  grounded_share: number;
  tokens: { input: number; output: number };
  top_sources: { url: string; title: string; count: number }[];
}

export interface Interaction {
  id: number;
  created_at: string;
  question: string;
  answer: string;
  status: ChatStatus;
  refusal_reason: string;
  language: string;
  total_ms: number;
  sources: { url: string; title: string }[];
}

/** One scraped page — the fields the UI reads; the rest is passed through to ingestion. */
export interface Page {
  url: string;
  title: string;
  lang: string;
  category: string;
  sections?: unknown[];
  faq?: unknown[];
  [key: string]: unknown;
}
