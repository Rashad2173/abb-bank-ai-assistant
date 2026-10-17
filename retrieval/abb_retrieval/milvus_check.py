"""Does retrieval through Milvus find the same chunks as the exact benchmark?

The benchmark searched exactly (every chunk scored with numpy). Milvus uses
indexes — HNSW for dense vectors is approximate — and its own BM25. This check
runs both question sets through Milvus and compares:

* **index recall** — share of the exact dense top 10 that HNSW also returns,
* the retrieval metrics of every Milvus method next to the exact search,
* search latency per question.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path

from .benchmark import RERANK_CANDIDATES, TOP_K, load_reranker, rerank
from .embedding_cache import EmbeddingCache, to_csr
from .metrics import Summary, evaluate_question, summarize
from .milvus_store import HNSW_EF, HNSW_PARAMS, METHODS, MilvusStore, Query
from .models import Chunk, Question
from .search import dense_scores, rank, reciprocal_rank_fusion, sparse_scores

MODEL = "bge-m3"
RERANKED_METHODS = ("dense+sparse", "dense+bm25")
_EXACT_EQUIVALENT = {"dense": "dense", "sparse": "sparse", "dense+sparse": "dense + sparse"}


@dataclass
class SetResult:
    name: str
    questions: int
    index_recall_at_10: float
    milvus: dict[str, Summary]
    exact: dict[str, Summary]
    latency_ms: dict[str, float]
    """Average search time per question (one question per request)."""


def check(store: MilvusStore, chunks: list[Chunk], question_sets: dict[str, list[Question]],
          cache_dir: Path) -> list[SetResult]:
    cache = EmbeddingCache(MODEL, cache_dir)
    documents, _ = cache.documents([c.text for c in chunks])
    by_id = {c.chunk_id: c.text for c in chunks}
    reranker = load_reranker()

    results = []
    for name, questions in question_sets.items():
        vectors, _ = cache.queries([q.question for q in questions])
        queries = [Query(q.question, vectors.dense[i], vectors.sparse[i]) for i, q in enumerate(questions)]
        texts = [q.question for q in questions]

        exact = _exact_rankings(vectors, documents, chunks)
        milvus = {method: store.search(queries, method, limit=TOP_K) for method in METHODS}
        for method in RERANKED_METHODS:
            milvus[f"{method} + reranker"] = _rerank_ids(reranker, texts, milvus[method], by_id)

        results.append(SetResult(
            name=name,
            questions=len(questions),
            index_recall_at_10=_overlap(milvus["dense"], exact["dense"], k=10),
            milvus={m: _summary(questions, r) for m, r in milvus.items()},
            exact={m: _summary(questions, r) for m, r in exact.items()},
            latency_ms={m: _latency(store, queries, m) for m in ("dense", "dense+sparse", "dense+bm25")},
        ))
    return results


def _exact_rankings(vectors, documents, chunks: list[Chunk]) -> dict[str, list[list[str]]]:
    dense = rank(dense_scores(vectors.dense, documents.dense), TOP_K)
    lexical = rank(sparse_scores(to_csr(vectors.sparse), to_csr(documents.sparse)), TOP_K)
    rankings = {"dense": dense, "sparse": lexical, "dense + sparse": reciprocal_rank_fusion(dense, lexical, top_k=TOP_K)}
    return {m: [[chunks[i].chunk_id for i in r] for r in per_query] for m, per_query in rankings.items()}


def _rerank_ids(reranker, queries: list[str], rankings: list[list[str]], by_id: dict[str, str]) -> list[list[str]]:
    candidates = [ranking[:RERANK_CANDIDATES] for ranking in rankings]
    ids = sorted({cid for ranking in candidates for cid in ranking})
    position = {cid: i for i, cid in enumerate(ids)}
    reranked = rerank(reranker, queries, [by_id[cid] for cid in ids], [[position[c] for c in r] for r in candidates])
    return [[ids[i] for i in ranking] for ranking in reranked]


def _summary(questions: list[Question], rankings: list[list[str]]) -> Summary:
    return summarize([evaluate_question(q, r) for q, r in zip(questions, rankings)], breakdown=False)


def _overlap(found: list[list[str]], reference: list[list[str]], k: int) -> float:
    return sum(len(set(f[:k]) & set(r[:k])) / k for f, r in zip(found, reference)) / len(reference)


def _latency(store: MilvusStore, queries: list[Query], method: str, sample: int = 50) -> float:
    started = time.perf_counter()
    for query in queries[:sample]:
        store.search([query], method, limit=TOP_K)
    return round(1000 * (time.perf_counter() - started) / min(sample, len(queries)), 1)


# --------------------------------------------------------------------------- #
# Report
# --------------------------------------------------------------------------- #

def write_report(results: list[SetResult], chunk_count: int, path: Path) -> None:
    lines = [
        "# Milvus retrieval check",
        "",
        f"{chunk_count:,} chunks in Milvus (bge-m3 dense + sparse vectors, built-in BM25). Both question sets "
        "run through Milvus and compared with the exact search of the benchmark.",
        "",
        f"* Dense index: HNSW {HNSW_PARAMS}, search ef = {HNSW_EF}, inner product (= cosine).",
        "* Sparse: bge-m3 lexical weights, sparse inverted index. BM25: Milvus full-text search over the "
        "chunk text with Azerbaijani letters normalised (ə→e, ı/İ→i, accents folded).",
        "* Hybrid methods: Reciprocal Rank Fusion (k = 60) inside Milvus' `hybrid_search`; reranker: "
        f"bge-reranker-v2-m3 over the top {RERANK_CANDIDATES}.",
        "",
    ]
    for result in results:
        lines += [
            f"## {result.name} ({result.questions} questions)",
            "",
            f"HNSW index recall: **{100 * result.index_recall_at_10:.1f}%** of the exact dense top 10 returned by Milvus.",
            "",
            "| Method | Complete@5 | R@1 | R@5 | R@10 | MRR@10 | Exact search R@5 |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
        for method, s in result.milvus.items():
            exact = result.exact.get(_EXACT_EQUIVALENT.get(method, ""))
            lines.append(
                f"| {method} | {round(s.complete[5] * s.count)}/{s.count} | {_pct(s.recall[1])} | {_pct(s.recall[5])} | "
                f"{_pct(s.recall[10])} | {s.mrr:.3f} | {_pct(exact.recall[5]) if exact else '–'} |"
            )
        lines += ["", "Search latency per question (Milvus only, embedding and reranking excluded): "
                  + ", ".join(f"{m} {ms} ms" for m, ms in result.latency_ms.items()), ""]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
    path.with_suffix(".json").write_text(json.dumps([
        {"set": r.name, "questions": r.questions, "index_recall_at_10": round(r.index_recall_at_10, 4),
         "latency_ms": r.latency_ms,
         "milvus": {m: {"complete@5": s.complete[5], "recall": s.recall, "mrr": round(s.mrr, 4)} for m, s in r.milvus.items()},
         "exact": {m: {"complete@5": s.complete[5], "recall": s.recall, "mrr": round(s.mrr, 4)} for m, s in r.exact.items()}}
        for r in results
    ], indent=1), encoding="utf-8")


def _pct(value: float) -> str:
    return f"{100 * value:.0f}%"
