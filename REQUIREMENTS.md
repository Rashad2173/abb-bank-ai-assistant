# Case Study Requirements Tracker

Single source of truth for what the ABB case study asks for. Every item maps to
the original brief; status is updated as the work progresses.

Legend: ⬜ not started · 🟨 in progress · ✅ done

## 1. Web Scraping
| # | Requirement | Status | Where |
|---|-------------|--------|-------|
| 1.1 | Script that parses the official ABB website (abb-bank.az) | ✅ | `scraper/` |
| 1.2 | Extracts **all** textual content | ✅ | `scraper/` — 99.9 % of CMS text lines present, see `evaluation/reports/00_data_quality.md` |

## 2. Web Application
| # | Requirement | Status | Where |
|---|-------------|--------|-------|
| 2.1 | **Data Upload** — user uploads the extracted data | ✅ | UI → Data: `abb_pages.jsonl` (also PDF/TXT documents, or the site learned from its link) → `services/ingestion` |
| 2.2 | Uploaded data is stored in the browser's **local storage** | ✅ | `frontend/src/storage.ts` — gzip + 15-bit packing: 21 MB → 1.5 M characters (fits the ~5 MB quota) |
| 2.3 | Backend service that interacts with an **OpenAI LLM** | ✅ | `services/chat` — gpt-6-luna, structured JSON answers |
| 2.4 | Extracted data formatted into a **vector database** (Milvus) compatible with OpenAI's requirements | ✅ | `retrieval/abb_retrieval/milvus_store.py`, `docker-compose.yml` — validated in `evaluation/reports/04_milvus_check.md` |
| 2.5 | After successful processing, show a **chat interface** | ✅ | The chat unlocks when the index holds processed data; first visits start on the data step |
| 2.6 | Answers stay **within the context of ABB information** | ✅ | Guardrail: 80 / 80 on an independent adversarial set (`evaluation/reports/06_guardrail_independent.md`) |
| 2.7 | **Microservice architecture** for question handling and response generation, communicating in **JSON** | ✅ | chat, inference, analytics, ingestion, scraper (`services/`) — JSON over HTTP, Swagger at `/docs` |
| 2.8 | Store **questions, answers and timestamps** in a database | ✅ | `services/analytics` — PostgreSQL table `interactions` |

## 3. Data Visualization
| # | Requirement | Status | Where |
|---|-------------|--------|-------|
| 3.1 | Charting library visualizes stored questions/answers (insights into user interactions) | ✅ | UI → Dashboard (Recharts): per day / hour, outcomes, languages, refusal reasons, latency, top sources |

## 4. Containerization
| # | Requirement | Status | Where |
|---|-------------|--------|-------|
| 4.1 | Application and dependencies packaged as Docker image(s) | ✅ | `services/Dockerfile` (one target per service), `frontend/Dockerfile`, `docker-compose.yml` — `docker compose up -d --build` |

## Evaluation criteria (apply to everything)
- **Functionality** — meets the requirements above and works as intended
- **Code quality** — clean, well-structured, easy to understand
- **Efficiency** — resource usage and response times
- **Design** — intuitive, user-friendly UI
- **Documentation** — implementation choices and functionality explained

## Project decisions
| Decision | Reason |
|----------|--------|
| Vector DB: **Milvus** | Required for this case |
| Embedding model chosen by **benchmark on Azerbaijani data** (bge-m3, text-embedding-3-large, multilingual-e5 candidates) | Site content is mostly Azerbaijani; accuracy over cost |
| **bge-m3 dense + sparse + Milvus BM25, re-ranked by bge-reranker-v2-m3** | bge-m3 was the most consistent model on two independent question sets (`retrieval/README.md`); adding BM25 catches rare exact words — 174/200 questions with all evidence in the top 5, Recall@10 94 % (`evaluation/reports/09_retrieval_methods.md`) |
| Reranker needs a GPU (or a hosted reranker) in production | ~1 s per question on a GPU, ~47 s on CPU |
| Scraped chunks must be **human-reviewable** | Chunks will be checked manually |

## Notes for answer generation
- Some source pages contradict themselves (DigiDeposit 9.5 % vs 10 %, TamKart Gold
  grace period "60 ay" vs "60 gün"). The scraper keeps the source text; the generation
  prompt must prefer tariff tables and mention a conflict instead of picking silently.
- Campaigns carry `is_active`; news carry a publication date — answers about current
  offers must not present ended or old offers as valid.

- Long lists (branches per city) are miscounted by the model → counts are computed by
  the scraper and written into the data.

## Known constraints / risks
- Browser `localStorage` is limited to ~5–10 MB per origin and the full site dump is
  ~21 MB → solved: gzip + 15-bit packing, 1.5 M characters (`frontend/src/storage.ts`).
- The reranker needs a GPU for interactive answers; without one the chat falls back to
  Milvus' order (lower accuracy).

## Extras (beyond the brief)
- Learning the site from its link, with live progress (scraper service)
- PDF / TXT document uploads; Add / Replace modes; only changed chunks are embedded
- Query planning: follow-ups, quoting part of an answer, Azerbaijani search for EN / RU questions
- Conversation sidebar, dark mode, AZ / EN / RU interface
- Evaluation sets and reports for every stage (`evaluation/`)
