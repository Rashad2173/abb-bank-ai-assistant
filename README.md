<p align="center">
  <img src="frontend/public/abb-logo.png" alt="ABB" height="64">
</p>

<h1 align="center">ABB Bank AI Assistant</h1>

<p align="center">
  A chat assistant that answers questions about <b>ABB Bank</b> from the content of its official website,
  <a href="https://abb-bank.az">abb-bank.az</a> — in Azerbaijani, English and Russian, with a cited source for every fact.
</p>

<p align="center">
  <a href="https://github.com/Rashad2173/abb-bank-ai-assistant/actions/workflows/ci.yml"><img alt="CI" src="https://github.com/Rashad2173/abb-bank-ai-assistant/actions/workflows/ci.yml/badge.svg"></a>
  <img alt="Python" src="https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white">
  <img alt="FastAPI" src="https://img.shields.io/badge/FastAPI-microservices-009688?logo=fastapi&logoColor=white">
  <img alt="Milvus" src="https://img.shields.io/badge/Milvus-3.0-00A1EA">
  <img alt="OpenAI" src="https://img.shields.io/badge/OpenAI-Responses%20API-412991?logo=openai&logoColor=white">
  <img alt="React" src="https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=black">
  <img alt="Docker" src="https://img.shields.io/badge/Docker-compose-2496ED?logo=docker&logoColor=white">
</p>

<p align="center">
  <img src="assets/screenshots/chat.png" alt="Chat: a question typed without Azerbaijani letters and a follow-up, answered with sources" width="860">
</p>

The site is scraped, split into passages and stored in **Milvus**; for each question the most relevant
passages are retrieved, re-ranked, and an **OpenAI** model writes the answer from them only. Questions
outside ABB's scope — other banks, personal advice, prompt injection — are refused. Every
design decision was made by measurement on question sets with known answers.

> Case study for ABB. Requirements and where each is met: [REQUIREMENTS.md](REQUIREMENTS.md).

## Results

All numbers are measured; the sets and reports are in [evaluation/](evaluation/README.md).

| | |
|---|---|
| **Scraping** — CMS text of the site present in the output | **99.9 %** of 15 646 lines |
| **Retrieval** — the needed passage among the 10 given to the model (200 questions, 2 independent sets) | **94 %** · all evidence in the top 5: **174 / 200** |
| **Answers** — 56 unseen questions graded against the source text | **54 correct, 1 partial, 1 wrong · 0 invented facts** |
| **Without a GPU** — reranker off, 15 chunks to the model | 185 / 200 with all evidence in front of the model (186 with the GPU) |
| **Guardrail** — independent set of 80 adversarial questions (16 injection techniques) | **80 / 80** · 0 legitimate questions refused · 0 prompt leaks |
| **Speed** | answers stream word by word: the first words after ~3–4 s, complete after ~3–7 s (search ≈ 10 ms, reranking ≈ 1 s on a GPU, the LLM the rest) |

## Quick start

Requires Docker and an OpenAI API key. Two ways to run it — pick the one that matches the machine:

| | **With an NVIDIA GPU** (best accuracy) | **Without one** (Mac, most laptops) |
|---|---|---|
| Command | `docker compose up -d --build` | `docker compose -f docker-compose.yml -f docker-compose.cpu.yml up -d --build` |
| Reranker | bge-reranker-v2-m3 on the GPU, ~1 s | off — on a CPU it would take ~45 s per question |
| Chunks given to the model | 10, re-ranked | 15, in Milvus' hybrid order |
| Questions with all their evidence in front of the model (200) | **186** | **185** |
| Inference image | PyTorch with CUDA, 12.5 GB | CPU build of PyTorch, 2.6 GB |

```bash
git clone https://github.com/Rashad2173/abb-bank-ai-assistant.git && cd abb-bank-ai-assistant
cp .env.example .env                 # put OPENAI_API_KEY into .env
docker compose up -d --build         # (or the CPU command above) → http://localhost:8080
```

| Address | What |
|---|---|
| http://localhost:8080 | the application |
| http://localhost:8001/docs … :8005/docs | Swagger UI of chat, analytics, ingestion, inference, scraper |
| http://localhost:8000 | Attu — browse the Milvus collection (server address `milvus:19530`) |

* **First start:** the inference service downloads its models (~4.5 GB with the reranker) into a volume.
* **The search index starts empty:** open the app and learn the site from its link (or upload a file).
  A first crawl takes ~30 minutes (polite: 6 parallel requests); with an existing page cache
  (`SCRAPER_DATA=./data docker compose up -d`) about 3 minutes.
* **GPU mode** needs the NVIDIA driver and Docker's GPU support (Docker Desktop with WSL 2 on Windows,
  the NVIDIA Container Toolkit on Linux). The CPU mode uses the CPU build of PyTorch, which also exists
  for ARM; it has not been tried on an Apple Silicon Mac.
* **Publishing it:** set `ACCESS_CODE` in `.env`. Visitors then enter the code once (kept for 30 days),
  the API answers `401` without it, and questions are limited to 20 a minute per visitor. Empty — the
  default — leaves the app open.

## Using the app

<table>
<tr>
<td width="50%"><img src="assets/screenshots/data-step.png" alt="Data step"></td>
<td width="50%"><img src="assets/screenshots/guardrail.png" alt="Refused questions"></td>
</tr>
<tr>
<td><b>1 · Data.</b> The knowledge base and its state, and three ways in: the data already indexed,
the site learned from its link — every stage shown live (pages found and read, documents, chunks,
embeddings) — or <code>abb_pages.jsonl</code> / PDF / TXT uploads. <b>Add</b> keeps what is indexed,
<b>Replace</b> makes the new data the whole knowledge base; only new or changed chunks are embedded.
The data is kept in the browser's localStorage (compressed: 21 MB → 1.5 M characters).</td>
<td><b>2 · Chat.</b> Answers stream word by word, in the question's language, with numbered sources, campaign status and dates.
Follow-up questions, quoting part of an answer, a conversation sidebar, dark mode, AZ / EN / RU interface.
Off-topic questions, other banks, personal advice and prompt injection are refused.</td>
</tr>
</table>

<p align="center">
  <img src="assets/screenshots/dashboard.png" alt="Dashboard" width="860"><br>
  <b>3 · Dashboard.</b> Questions per day and hour, outcomes, languages, refusal reasons, answer times,
  most cited pages and the latest questions — stored in PostgreSQL.
</p>

## Architecture

```mermaid
flowchart LR
    UI["Web app<br/>React · nginx :8080"]
    subgraph services [" "]
        CHAT["chat :8001<br/>plan → search → rerank<br/>→ OpenAI → guardrail"]
        ING["ingestion :8003<br/>chunk → diff → embed"]
        SCR["scraper :8005<br/>crawl → extract"]
        ANA["analytics :8002"]
        INF["inference :8004<br/>bge-m3 · bge-reranker-v2-m3<br/>(GPU)"]
    end
    MIL[("Milvus<br/>dense · sparse · BM25")]
    PG[("PostgreSQL")]
    OAI(["OpenAI"])

    UI --> CHAT & ING & SCR & ANA
    SCR --> ING
    CHAT --> INF & MIL & OAI
    CHAT -. after answering .-> ANA
    ING --> INF & MIL
    ANA --> PG
```

Five FastAPI services and the web app, talking JSON over HTTP ([services/README.md](services/README.md)).
Every service has `GET /health` and `GET /ready` (dependencies checked), carries an `X-Request-ID` through
all calls and logs, and returns errors as JSON. If the reranker is slow or down, the chat answers from
Milvus' order instead of failing; if analytics is down, chatting is unaffected.

## How it works

**Scraping** ([scraper/](scraper/README.md)) — abb-bank.az is a Next.js site: accordion answers, inactive
tabs (tariffs, rate tables) and parts of pages exist only in the React Server Components payload, and the
branch / ATM locator loads its data through Server Actions. The scraper reads all of these, replays streamed
content in reading order, writes tables as `Column: value` rows, drops ≈ 3 000 untranslated page copies and
repeated banners, and marks each campaign as active or ended. Result: 4 223 documents in three languages.

**Chunking** ([retrieval/](retrieval/README.md)) — rule-based and reviewable: ≤ 512 tokens (target 350);
small sections packed together; long sections split at paragraph and sentence boundaries with one paragraph of
overlap (a list's lead-in sentence instead, so items keep their condition); one FAQ item per chunk; every
chunk starts with its page title, section path, campaign status and date. 9 604 chunks.

**Embedding model** — chosen by benchmark on this site's own content: bge-m3, multilingual-e5-large-instruct
and OpenAI text-embedding-3-large, on two independent sets of 100 questions with evidence marked in advance.

| Dense search, no reranker | All evidence in top 5 (set A + set B) | Recall@5 A / B |
|---|---:|---:|
| **bge-m3** | **154 / 200** | 80 % / 80 % |
| multilingual-e5-large-instruct | 146 / 200 | 78 % / 74 % |
| text-embedding-3-large | 142 / 200 | 81 % / 68 % |

With the reranker all three reach 171–174 / 200; bge-m3 was the most consistent across the two sets, gives a
dense and a sparse vector from one model, and runs locally at no per-query cost.

**Retrieval** — the question is planned first (follow-ups resolved; English and Russian questions also searched
in Azerbaijani, since some pages exist only in Azerbaijani; tender notices left out unless asked about), then
searched in Milvus three ways — bge-m3 dense, bge-m3 sparse and Milvus BM25 (with Azerbaijani letters
normalised) — fused with Reciprocal Rank Fusion. The top 30 are re-scored by the **bge-reranker-v2-m3**
cross-encoder and the best 10 go to the model.

**Generation** — `gpt-6-luna` through the OpenAI Responses API with a strict JSON schema (status, refusal
reason, language, answer with `[S1]` citations), streamed to the browser as it is written: the service reads the answer text out of the JSON while it is generated and sends it line by line (NDJSON); the final, checked answer replaces the streamed text. The prompt allows only the given sources, asks for the
direct answer first and then the details a customer needs next, prefers tariff tables when the site contradicts
itself, and never presents an ended campaign as available. Prompts are plain files in
[services/chat/chat_service/prompts/](services/chat/chat_service/prompts/).

**Guardrail** — in layers: input limits → scope decided in the same LLM call before the sources are read
(no extra latency) → sources treated as data, not instructions → citations checked in code (unknown labels
removed, refusals carry no sources, uncited answers flagged) → measured on 144 questions.

## Repository

```
├── scraper/              abb-bank.az scraper (Python package abb_scraper)
├── retrieval/            chunking, Milvus store, benchmarks (abb_retrieval)
├── services/             chat · analytics · ingestion · inference · scraper (FastAPI) + service_common
├── frontend/             React app (Vite, TypeScript), nginx config
├── evaluation/           test sets (retrieval / guardrail / answers) + reports 00–10
├── scripts/              smoke test, evaluation runners, Wikipedia → upload file
├── tests/                pytest suite
├── docker-compose.yml    the whole application (docker-compose.cpu.yml: machines without a GPU)
└── REQUIREMENTS.md       the brief's requirements and where each is met
```

## Development

Python ≥ 3.12, Node 22.

```bash
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt                    # PyTorch with CUDA: see retrieval/requirements.txt
docker compose up -d milvus postgres attu              # infrastructure only
# services natively, one terminal each (see services/README.md), then the UI:
cd frontend && npm install && npm run dev              # → http://localhost:5173 (proxies /api to the services)

pytest                                                 # 237 tests
ruff check . && ruff format --check .                  # Python lint + formatting
cd frontend && npm run lint && npm test                # Biome lint + formatting, UI unit tests
python scripts/smoke_test.py                           # end-to-end check of the running services
```

[CI](.github/workflows/ci.yml) runs the linters, the type check, both test suites and the Docker
builds on every push.

The offline pipeline (scrape → chunk → benchmark → Milvus check) and its commands are described in
[scraper/README.md](scraper/README.md), [retrieval/README.md](retrieval/README.md) and
[evaluation/README.md](evaluation/README.md).

## Known limitations

* The scraper is built for abb-bank.az and refuses other sites; other sources can be added as upload files.
* Tables inside PDFs lose their column structure in text extraction; text-heavy PDFs work well.
* The reranker needs a GPU for interactive answers; the CPU mode switches it off and gives the model 15
  chunks instead, which recovers almost all of the difference (report 10).
* Two same-shaped tables on one page can occasionally be mixed up in an answer (1 of 56 graded answers).

---

<sub>Demo project for a case study — not an official ABB service. ABB logo: Azərbaycan Beynəlxalq Bankı,
CC BY-SA 4.0 (Wikimedia Commons).</sub>
