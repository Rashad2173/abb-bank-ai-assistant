# Services

Five FastAPI services and one shared package. They call each other over HTTP
with JSON bodies; every request carries an `X-Request-ID` that appears in the
logs of every service it touches.

```
                    ┌────────────── inference :8004 ──────────────┐
                    │  POST /v1/embed   (bge-m3 dense + sparse)    │
                    │  POST /v1/rerank  (bge-reranker-v2-m3)       │
                    └──────▲───────────────────────────▲──────────┘
                           │                           │
 UI ── POST /v1/chat ──▶ chat :8001 ──▶ Milvus        ingestion :8003 ◀── POST /v1/ingest ── UI
                           │   └──────▶ OpenAI          │  └──────▶ Milvus
                           ▼                            
                  analytics :8002 ──▶ PostgreSQL ◀── GET /v1/stats ── UI (dashboard)
```

| Package | Responsibility |
|---------|----------------|
| `common/service_common` | app factory (`/health`, `/ready`, request ids, JSON errors), JSON logging, settings base, inference client |
| `inference/inference_service` | loads the two local models once; serialises GPU work |
| `chat/chat_service` | retrieval, reranking with fallback, prompt, OpenAI call, guardrail checks |
| `analytics/analytics_service` | `interactions` table, browsing, dashboard statistics |
| `ingestion/ingestion_service` | chunking uploaded pages (or PDF / TXT documents), diff against Milvus, embedding and upserting changes |
| `scraper/scraper_service` | runs the abb-bank.az scraper from a link (crawl → branch network → extraction) and hands the pages to ingestion, with live progress |

Retrieval code is not duplicated: the services import `retrieval/abb_retrieval`
(chunker, Milvus schema and search) — the same code the benchmark validated.

## Running in Docker

`docker compose up -d --build` from the repository root starts everything (see the main
README). `services/Dockerfile` has one target per service; only `inference` carries
PyTorch and the models.

## Running locally

```bash
docker compose up -d                       # Milvus, Attu (:8000), PostgreSQL (:5433)
# one terminal per service, from the repository root (PYTHONPATH separator ';' on Windows, ':' elsewhere)
PYTHONPATH="services/common;retrieval;services/inference" uvicorn inference_service.main:app --port 8004
PYTHONPATH="services/common;retrieval;services/analytics" uvicorn analytics_service.main:app --port 8002
PYTHONPATH="services/common;retrieval;services/chat"      uvicorn chat_service.main:app --port 8001
PYTHONPATH="services/common;retrieval;services/ingestion" uvicorn ingestion_service.main:app --port 8003
PYTHONPATH="services/common;retrieval;scraper;services/scraper" uvicorn scraper_service.main:app --port 8005

python scripts/smoke_test.py               # health, readiness, three chat questions, analytics
python scripts/smoke_test.py --ingest data/abb_pages.jsonl
```

Settings come from environment variables or `.env` (see `.env.example`).
Interactive API docs: `http://localhost:<port>/docs`.

## API

| Endpoint | Body → response |
|----------|-----------------|
| `POST chat /v1/chat` | `{question, history?, session_id?, quote?, rerank?}` (`rerank: false` answers from Milvus' order, as without a GPU) → `{answer, status, refusal_reason, language, sources[], standalone_question, search_queries, reranked, model, timings, request_id}` |
| `POST chat /v1/chat/stream` | the same request → `application/x-ndjson`, one event per line: `sources` (the chunks given to the model) → `status` → `delta` … (pieces of the answer) → `done` (the `/v1/chat` response, checked). Failures before the first byte are ordinary JSON errors; later ones arrive as an `error` event |
| `POST analytics /v1/interactions` | one interaction (sent by chat) → stored row with `id`, `created_at` |
| `GET analytics /v1/interactions` | `?limit&offset&status` → `{items, total}`, newest first |
| `GET analytics /v1/stats` | `?days=30` → totals by status / refusal reason / language, per day, per hour, latency p50/p95, reranker and citation shares, tokens, top sources |
| `POST ingestion /v1/ingest` | `{pages: [...], mode: replace \| append}` (the `abb_pages.jsonl` format) → `202` job. `replace`: the upload becomes the knowledge base; `append`: added, nothing deleted (`scripts/wikipedia_to_pages.py` builds such a file from Wikipedia) |
| `GET ingestion /v1/ingest/{id}` | job progress: `chunking → comparing → embedding → writing → done/failed` |
| `POST ingestion /v1/ingest/files` | multipart PDF / TXT files + `mode` (default `append`) → job and the pages built from them |
| `GET ingestion /v1/corpus` | chunks in Milvus + last job |
| `POST scraper /v1/scrape` | `{url, mode}` — only abb-bank.az (anything else: `422` with the reason) → `202` job |
| `GET scraper /v1/scrape/{id}` | stage, counters (pages found / fetched / from cache, documents, chunks, embedded) and the last URLs read |
| `GET scraper /v1/scrape/{id}/pages` | the extracted `abb_pages.jsonl` of a finished job (the UI keeps it in localStorage) |
| `POST inference /v1/embed` | `{texts, kind: query/document}` → `{dense, sparse}` |
| `POST inference /v1/rerank` | `{query, documents}` → `{scores}` (0–1) |
| `GET <any> /health`, `/ready` | liveness; readiness with one entry per dependency (`503` if any fails) |

Chat `status`: `answered` (from the sources, with `[S1]` citations), `greeting`,
`out_of_scope` (with `refusal_reason`: off_topic, other_bank, personal_advice,
prompt_injection, harmful) or `no_information` (about ABB, but not in the sources).

## Design decisions

| Decision | Why |
|----------|-----|
| Models in their own inference service | Only this service needs PyTorch and a GPU; chat and ingestion stay small and can run anywhere |
| Reranker optional at request time | A slow (> 5 s) or failed reranker call falls back to Milvus' order — lower accuracy, but the user still gets an answer (`reranked: false`, counted on the dashboard) |
| Structured LLM output (strict JSON schema) | The service knows whether a question was answered, refused or not covered without parsing free text |
| Streaming the structured answer | The JSON is streamed as it is written; `chat_service/streaming.py` reads the `answer` field out of it piece by piece (escapes cut between pieces included), and the status is known before the text because strict output writes keys in schema order. The guardrail checks run on the complete answer, which replaces the streamed text |
| Guardrail in layers, no framework | Input validation (schema) → scope rules in the prompt, decided in the same LLM call (no extra latency) → sources marked as data, not instructions → citation checks in code → measured with a test set |
| Citations checked in code | Labels that do not match a given source are removed; refusals carry no sources; uncited answers are flagged (`grounded: false`) |
| Recording after the response | The chat service sends the interaction to analytics as a background task; a failure is logged and never breaks chatting |
| Ingestion diffs by content hash | An upload replaces the corpus, but only new or changed chunks are embedded — re-uploading the same 4 223 pages takes ~12 s |
| CPU mode gives the model 15 chunks | Without the reranker, 15 chunks in Milvus' order put almost as many questions' evidence in front of the model as 10 re-ranked ones: 185 vs. 186 of 200 (evaluation report 10) |
| Optional access code in nginx | A public demo spends the project's OpenAI budget: with `ACCESS_CODE` set, the UI and the API need the code (kept in a cookie), and questions are limited to 20 a minute per visitor. Empty (the default): open |
| `.env` wins over machine variables | A stray `OPENAI_API_KEY` in the user's environment must not silently replace the project's key |
