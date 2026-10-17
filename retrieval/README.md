# Retrieval — chunking, evaluation and embedding benchmark

Python package `abb_retrieval`. It turns the scraped documents
(`data/abb_pages.jsonl`) into retrieval chunks, maps two evaluation question sets
to those chunks and measures which embedding model and search method finds the
right chunks most reliably.

```bash
python -m abb_retrieval chunk               # data/chunks.jsonl + evaluation/reports/01_chunk_quality.md
python -m abb_retrieval evalset [--set b]   # map a question set's evidence to the current chunk ids
python -m abb_retrieval benchmark [--set b] # embedding benchmark report (GPU recommended)
python -m abb_retrieval index               # load the chunks into Milvus (docker compose up -d first)
python -m abb_retrieval milvus-check        # both question sets through Milvus vs. the exact search
python -m abb_retrieval freeze --corpus data/abb_pages.v1-042c420d.jsonl   # once, set A only
```

`text-embedding-3-large` needs `OPENAI_API_KEY` in `.env` (see `.env.example`).
Embeddings are cached under `data/embeddings/<model>/` — documents once per corpus
version, questions once per question set — so re-running costs nothing.

## Chunking

Rule-based, no model involved — every decision can be traced to a rule.

| Rule | Why |
|------|-----|
| Target 350, hard limit 512 tokens (bge-m3 tokenizer); small neighbouring sections are packed together | Fits every candidate model; small enough to be precise, large enough to keep a table or list together |
| Split at paragraph, then sentence boundaries, 1 paragraph overlap | No sentence is cut in half |
| A list's lead-in sentence is repeated in every window of the list | "The following documents are required:" stays with the items |
| Every chunk starts with a context header: page title, section path, campaign status / validity, publication date | The chunk is understandable on its own — for the embedding model and for the LLM |
| One FAQ item = one chunk | Question and answer are never separated |
| Identical chunks of several pages are stored once (other pages kept as aliases); common tender sections shared by ≥ 10 tenders are stored once | Duplicates would crowd out other results |

Result: **9 604 chunks** from 4 223 documents, median 341 tokens, none over the
limit. Report: [01_chunk_quality.md](../evaluation/reports/01_chunk_quality.md).

## Evaluation sets

Each question has its evidence — the passages that answer it — marked in
advance, so retrieval can be scored automatically.

| | Set A | Set B |
|---|---|---|
| File | `evaluation/abb_100_soru_kaynakli.md` | `evaluation/question_set_b.json` |
| Questions | 100 (115 evidence passages) | 100 (110 evidence passages) |
| Written | first, against corpus version `042c420d` | separately, only from pages set A does not use |
| Evidence given as | position in the corpus (`sections[2].paragraphs[0]`), frozen to text once | page URL + verbatim snippet |
| Languages | 90 AZ, 7 EN, 3 RU | 87 AZ, 7 EN, 6 RU (10 of them multi-source) |

Evidence is matched to chunks by **page URL + text**, so both sets survive
re-chunking. Table rows match across formats; a table header row alone is not
evidence; a sentence that appears under two tables only counts in its own section.
Reviewed equivalent passages are listed in `evaluation/evidence_additions.json`.

**Metrics.** *Recall@k* — share of a question's evidence in the top k results.
*Complete@5* — questions with **all** their evidence in the top 5 (what the LLM
needs to answer fully). *MRR@10* — 1 / rank of the first relevant chunk.

## Benchmark

Exact search over all 9 604 chunks (no index approximation), so the comparison
measures the models, not an index. Methods: BM25, dense, dense + BM25 and
dense + sparse (bge-m3's lexical weights), fused with Reciprocal Rank Fusion, each
optionally re-scored by **bge-reranker-v2-m3** over the top 30 candidates.

| Method | Complete@5 A | Complete@5 B | R@5 A / B | R@10 A / B | MRR A / B |
|--------|---:|---:|---:|---:|---:|
| **bge-m3 dense + sparse + reranker** (chosen) | 84 | 89 | 87 % / 90 % | 94 % / 92 % | 0.74 / 0.72 |
| bge-m3 dense + BM25 + reranker | 84 | 90 | 87 % / 91 % | 92 % / 94 % | 0.74 / 0.73 |
| text-embedding-3-large dense + BM25 + reranker | 85 | 88 | 88 % / 90 % | 94 % / 91 % | 0.76 / 0.72 |
| multilingual-e5-large-instruct dense + reranker | 85 | 88 | 86 % / 90 % | 92 % / 92 % | 0.75 / 0.73 |
| text-embedding-3-large dense + reranker | 86 | 85 | 88 % / 86 % | 93 % / 90 % | 0.77 / 0.69 |
| bge-m3 dense | 77 | 77 | 80 % / 80 % | 89 % / 88 % | 0.61 / 0.64 |
| multilingual-e5-large-instruct dense | 74 | 72 | 78 % / 74 % | 84 % / 82 % | 0.65 / 0.63 |
| text-embedding-3-large dense | 77 | 65 | 81 % / 68 % | 92 % / 82 % | 0.65 / 0.53 |
| BM25 | 58 | 53 | 62 % / 57 % | 70 % / 72 % | 0.52 / 0.47 |

Full reports, including results per question type and language and every missed
question: [02_embedding_benchmark.md](../evaluation/reports/02_embedding_benchmark.md) (set A),
[03_embedding_benchmark_set_b.md](../evaluation/reports/03_embedding_benchmark_set_b.md) (set B).

**Findings**

* The reranker is the largest single gain: every model goes from 142–154 to
  171–174 of 200 questions with all evidence in the top 5.
* With the reranker the models differ by 1–3 questions — within noise.
* Without it, **bge-m3 is the most consistent** (80 % Recall@5 on both sets);
  text-embedding-3-large led on set A but dropped to 68 % on set B, and e5 and
  text-embedding-3-large are weak on English/Russian questions.
* Part of the misses are evaluation artefacts rather than retrieval errors: an
  English question retrieving the English version of the right page, or the same
  fact on another page.

**Decision: bge-m3 dense + sparse, re-ranked by bge-reranker-v2-m3.** Most
consistent on both sets, one model yields both vectors for Milvus hybrid search,
open source and free to run, and the best fallback if the reranker is unavailable.

**Cost of the reranker.** ~1 s per question on a GPU (RTX 4060 Laptop) but ~47 s
on CPU — production needs a GPU host or a hosted reranker.

## Milvus

Collection `abb_chunks` (Milvus 3.0.2, see `docker-compose.yml`): the chunk text
and metadata (URL, title, language, categories, campaign status, dates) plus three
searchable representations.

| Field | Index | Used for |
|-------|-------|----------|
| `dense` — bge-m3, 1 024 dims | HNSW (M 16, efConstruction 200), inner product; search ef 200 | meaning |
| `sparse` — bge-m3 lexical weights | sparse inverted index, inner product | important words, learned |
| `bm25` — generated inside Milvus from `lexical_text` | sparse inverted index, BM25 (k1 1.5, b 0.75) | exact keywords |
| `lang`, `category`, `chunk_type` | inverted | filters |

**Azerbaijani letters in keyword search.** Milvus' `lowercase` filter turns "İ"
into "i̇" (i + combining dot), so "KREDİT" would not match "kredit", and its
`asciifolding` turns "ə" into "a", while people typing without an Azerbaijani
keyboard write "e" ("odenis" for "ödəniş"). `lexical_text` therefore maps
İ/ı → i and ə → e before indexing (the same is done to queries); the analyzer
folds the remaining letters (ş, ç, ğ, ö, ü).

**Check** ([04_milvus_check.md](../evaluation/reports/04_milvus_check.md)) — both
question sets through Milvus:

| | Set A | Set B |
|---|---:|---:|
| HNSW index recall (share of the exact dense top 10 found) | 99.7 % | 99.7 % |
| dense + sparse + reranker: Complete@5 | 84 / 100 (exact: 84) | 89 / 100 (exact: 89) |
| dense + sparse + reranker: Recall@10 | 94 % (exact: 94 %) | 92 % (exact: 92 %) |
| dense + BM25 (Milvus) + reranker: Complete@5 / Recall@10 | 84 / 92 % | 90 / 94 % |
| Hybrid search latency per question | 4–10 ms | |

Retrieval through Milvus reproduces the benchmark. Milvus' BM25 and bge-m3's
sparse vectors perform the same after reranking; dense + sparse stays the default.

## Layout

```
abb_retrieval/
├── chunking.py          # page → chunks (packing, splitting, context header)
├── merging.py           # identical chunks / common tender sections stored once
├── corpus.py            # load pages, chunk the corpus, read/write JSONL
├── evalset.py           # parse, freeze and map the question sets
├── embedders/           # bge-m3, multilingual-e5, text-embedding-3-large behind one interface
├── search.py            # BM25, dense and sparse scoring, Reciprocal Rank Fusion
├── metrics.py           # Recall@k, Complete@k, MRR
├── embedding_cache.py   # embeddings cached on disk, shared by all steps
├── benchmark.py         # runs all methods (exact search)
├── milvus_store.py      # Milvus schema, loading, hybrid search
├── milvus_check.py      # question sets through Milvus vs. the exact search
├── benchmark_report.py  # Markdown / JSON / per-question CSV reports
└── chunk_report.py      # chunk statistics + reviewable CSV
```
