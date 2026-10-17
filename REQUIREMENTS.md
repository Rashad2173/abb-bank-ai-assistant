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
| 2.1 | **Data Upload** — user uploads the extracted data | ⬜ | |
| 2.2 | Uploaded data is stored in the browser's **local storage** | ⬜ | |
| 2.3 | Backend service that interacts with an **OpenAI LLM** | ⬜ | |
| 2.4 | Extracted data formatted into a **vector database** (Milvus) compatible with OpenAI's requirements | ✅ | `retrieval/abb_retrieval/milvus_store.py`, `docker-compose.yml` — validated in `evaluation/reports/04_milvus_check.md` |
| 2.5 | After successful processing, show a **chat interface** | ⬜ | |
| 2.6 | Answers stay **within the context of ABB information** | ⬜ | |
| 2.7 | **Microservice architecture** for question handling and response generation, communicating in **JSON** | ⬜ | |
| 2.8 | Store **questions, answers and timestamps** in a database | ⬜ | |

## 3. Data Visualization
| # | Requirement | Status | Where |
|---|-------------|--------|-------|
| 3.1 | Charting library visualizes stored questions/answers (insights into user interactions) | ⬜ | |

## 4. Containerization
| # | Requirement | Status | Where |
|---|-------------|--------|-------|
| 4.1 | Application and dependencies packaged as Docker image(s) | ⬜ | |

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
| **bge-m3 dense + sparse + bge-reranker-v2-m3** | 173/200 questions with all evidence in the top 5 over two independent question sets; most consistent without the reranker too (`retrieval/README.md`) |
| Reranker needs a GPU (or a hosted reranker) in production | ~1 s per question on a GPU, ~47 s on CPU |
| Scraped chunks must be **human-reviewable** | Chunks will be checked manually |

## Notes for answer generation
- Some source pages contradict themselves (DigiDeposit 9.5 % vs 10 %, TamKart Gold
  grace period "60 ay" vs "60 gün"). The scraper keeps the source text; the generation
  prompt must prefer tariff tables and mention a conflict instead of picking silently.
- Campaigns carry `is_active`; news carry a publication date — answers about current
  offers must not present ended or old offers as valid.

## Known constraints / risks
- Browser `localStorage` is limited to ~5–10 MB per origin; the full site dump
  (3 languages, ~7k URLs) may exceed it → needs compression and/or a scoped upload.
  To be decided when building 2.2.

## Extras (only after all requirements above are ✅)
Candidates noted so far:
- Text of linked PDF documents (tariffs, terms) — the chatbot could quote detailed tariffs
- Report/document links (PDF URLs) next to document titles, so answers can link to them
