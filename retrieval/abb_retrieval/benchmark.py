"""Embedding benchmark: which model / search method finds the right chunks?

For every model the chunks and the questions are embedded once (cached, see
:mod:`embedding_cache`) and searched exactly. Methods compared:

* ``BM25`` — keyword baseline,
* ``<model> dense`` — semantic similarity,
* ``<model> dense + BM25`` — hybrid, fused with Reciprocal Rank Fusion,
* ``bge-m3 sparse`` and ``bge-m3 dense + sparse`` — bge-m3's own lexical weights,
* ``… + reranker`` — the top candidates re-scored by bge-reranker-v2-m3.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path

from .embedders.base import Embeddings
from .embedding_cache import EmbeddingCache, to_csr
from .metrics import QuestionResult, evaluate_question
from .models import Chunk, Question
from .search import BM25, dense_scores, rank, reciprocal_rank_fusion, sparse_scores

TOP_K = 50
RERANK_CANDIDATES = 30
RERANKER_ID = "BAAI/bge-reranker-v2-m3"


@dataclass
class ModelStats:
    model: str
    dimension: int
    documents_seconds: float
    query_ms: float
    """Average time to embed one question."""
    api_tokens: int = 0


@dataclass
class BenchmarkResult:
    chunk_count: int
    question_count: int
    results: dict[str, list[QuestionResult]] = field(default_factory=dict)
    rankings: dict[str, list[list[str]]] = field(default_factory=dict)
    model_stats: list[ModelStats] = field(default_factory=list)
    rerank_seconds: dict[str, float] = field(default_factory=dict)


def run_benchmark(
    chunks: list[Chunk], questions: list[Question], model_names: list[str], cache_dir: Path, rerank: bool = True
) -> BenchmarkResult:
    texts = [c.text for c in chunks]
    queries = [q.question for q in questions]
    rankings: dict[str, list[list[int]]] = {}

    bm25 = rank(BM25(texts).scores(queries), TOP_K)
    rankings["BM25"] = bm25

    stats = []
    for name in model_names:
        documents, query_vectors, model_stats = _embed(name, texts, queries, cache_dir)
        stats.append(model_stats)
        dense = rank(dense_scores(query_vectors.dense, documents.dense), TOP_K)
        rankings[f"{name} dense"] = dense
        rankings[f"{name} dense + BM25"] = reciprocal_rank_fusion(dense, bm25, top_k=TOP_K)
        if documents.sparse is not None:
            lexical = rank(sparse_scores(to_csr(query_vectors.sparse), to_csr(documents.sparse)), TOP_K)
            rankings[f"{name} sparse"] = lexical
            rankings[f"{name} dense + sparse"] = reciprocal_rank_fusion(dense, lexical, top_k=TOP_K)

    rerank_seconds = {}
    if rerank:
        reranker = load_reranker()
        for method in [m for m in rankings if m != "BM25"]:
            started = time.perf_counter()
            rankings[f"{method} + reranker"] = rerank(reranker, queries, texts, rankings[method])
            rerank_seconds[method] = time.perf_counter() - started

    result = BenchmarkResult(
        chunk_count=len(chunks), question_count=len(questions), model_stats=stats, rerank_seconds=rerank_seconds
    )
    for method, per_query in rankings.items():
        ids = [[chunks[i].chunk_id for i in ranking] for ranking in per_query]
        result.rankings[method] = ids
        result.results[method] = [evaluate_question(q, r) for q, r in zip(questions, ids, strict=True)]
    return result


# --------------------------------------------------------------------------- #
# Embedding (cached)
# --------------------------------------------------------------------------- #


def _embed(
    name: str, texts: list[str], queries: list[str], cache_dir: Path
) -> tuple[Embeddings, Embeddings, ModelStats]:
    cache = EmbeddingCache(name, cache_dir)
    documents, doc_meta = cache.documents(texts)
    query_vectors, query_meta = cache.queries(queries)
    cache.release()

    stats = ModelStats(
        model=name,
        dimension=int(documents.dense.shape[1]),
        documents_seconds=doc_meta["seconds"],
        query_ms=round(1000 * query_meta["seconds"] / len(queries), 1),
        api_tokens=doc_meta.get("api_tokens", 0),
    )
    return documents, query_vectors, stats


# --------------------------------------------------------------------------- #
# Reranking
# --------------------------------------------------------------------------- #


def load_reranker():
    from FlagEmbedding import FlagReranker

    return FlagReranker(RERANKER_ID, use_fp16=True)


def rerank(reranker, queries: list[str], texts: list[str], rankings: list[list[int]]) -> list[list[int]]:
    reranked = []
    for query, ranking in zip(queries, rankings, strict=True):
        candidates = ranking[:RERANK_CANDIDATES]
        scores = reranker.compute_score([[query, texts[i]] for i in candidates], max_length=1024)
        reranked.append([doc for _, doc in sorted(zip(scores, candidates, strict=True), key=lambda pair: -pair[0])])
    return reranked
