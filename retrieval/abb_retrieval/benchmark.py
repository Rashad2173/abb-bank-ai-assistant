"""Embedding benchmark: which model / search method finds the right chunks?

For every model the chunks and the questions are embedded once (cached under
``data/embeddings/``) and searched exactly. Methods compared:

* ``BM25`` — keyword baseline,
* ``<model> dense`` — semantic similarity,
* ``<model> dense + BM25`` — hybrid, fused with Reciprocal Rank Fusion,
* ``bge-m3 sparse`` and ``bge-m3 dense + sparse`` — bge-m3's own lexical weights,
* ``… + reranker`` — the top candidates re-scored by bge-reranker-v2-m3.
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
from scipy import sparse as sp

from .embedders import Embedder, create_embedder
from .embedders.base import Embeddings
from .metrics import QuestionResult, evaluate_question
from .models import Chunk, Question
from .search import BM25, dense_scores, rank, reciprocal_rank_fusion, sparse_matrix, sparse_scores

log = logging.getLogger(__name__)

TOP_K = 50
RERANK_CANDIDATES = 30
RERANKER_ID = "BAAI/bge-reranker-v2-m3"
_BGE_M3_VOCABULARY = 250_002


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
            lexical = rank(sparse_scores(_csr(query_vectors.sparse), _csr(documents.sparse)), TOP_K)
            rankings[f"{name} sparse"] = lexical
            rankings[f"{name} dense + sparse"] = reciprocal_rank_fusion(dense, lexical, top_k=TOP_K)

    rerank_seconds = {}
    if rerank:
        reranker = _load_reranker()
        for method in [m for m in rankings if m != "BM25"]:
            started = time.perf_counter()
            rankings[f"{method} + reranker"] = _rerank(reranker, queries, texts, rankings[method])
            rerank_seconds[method] = time.perf_counter() - started

    result = BenchmarkResult(chunk_count=len(chunks), question_count=len(questions), model_stats=stats,
                             rerank_seconds=rerank_seconds)
    for method, per_query in rankings.items():
        ids = [[chunks[i].chunk_id for i in ranking] for ranking in per_query]
        result.rankings[method] = ids
        result.results[method] = [evaluate_question(q, r) for q, r in zip(questions, ids)]
    return result


# --------------------------------------------------------------------------- #
# Embedding with a disk cache
# --------------------------------------------------------------------------- #

def _embed(name: str, texts: list[str], queries: list[str], cache_dir: Path) -> tuple[Embeddings, Embeddings, ModelStats]:
    """Embeddings of chunks and questions; recomputed only when the texts change."""
    cache = cache_dir / name / f"{_fingerprint(texts)}-{_fingerprint(queries)}.npz"
    meta_path = cache.with_suffix(".json")
    if cache.exists():
        log.info("%s: using cached embeddings %s", name, cache.name)
        return (*_load(cache), ModelStats(**json.loads(meta_path.read_text())))

    embedder: Embedder = create_embedder(name)
    started = time.perf_counter()
    documents = embedder.embed_documents(texts)
    documents_seconds = time.perf_counter() - started
    started = time.perf_counter()
    query_vectors = embedder.embed_queries(queries)
    query_ms = 1000 * (time.perf_counter() - started) / len(queries)

    stats = ModelStats(name, embedder.dimension, round(documents_seconds, 1), round(query_ms, 1),
                       getattr(embedder, "tokens_used", 0))
    cache.parent.mkdir(parents=True, exist_ok=True)
    _save(cache, documents, query_vectors)
    meta_path.write_text(json.dumps(stats.__dict__))
    del embedder  # free GPU memory before the next model
    _free_gpu()
    return documents, query_vectors, stats


def _fingerprint(texts: list[str]) -> str:
    return hashlib.sha256("\x1e".join(texts).encode()).hexdigest()[:12]


def _save(path: Path, documents: Embeddings, queries: Embeddings) -> None:
    arrays = {"doc_dense": documents.dense, "query_dense": queries.dense}
    for prefix, emb in (("doc", documents), ("query", queries)):
        if emb.sparse is not None:
            matrix = _csr(emb.sparse)
            arrays |= {f"{prefix}_sp_data": matrix.data, f"{prefix}_sp_indices": matrix.indices,
                       f"{prefix}_sp_indptr": matrix.indptr}
    np.savez_compressed(path, **arrays)


def _load(path: Path) -> tuple[Embeddings, Embeddings]:
    data = np.load(path)

    def sparse(prefix: str):
        if f"{prefix}_sp_data" not in data:
            return None
        matrix = sp.csr_matrix((data[f"{prefix}_sp_data"], data[f"{prefix}_sp_indices"], data[f"{prefix}_sp_indptr"]),
                               shape=(len(data[f"{prefix}_dense"]), _BGE_M3_VOCABULARY))
        return [dict(zip(row.indices.tolist(), row.data.tolist())) for row in matrix]

    return (Embeddings(data["doc_dense"], sparse("doc")), Embeddings(data["query_dense"], sparse("query")))


def _csr(vectors: list[dict[int, float]]) -> sp.csr_matrix:
    return sparse_matrix(vectors, _BGE_M3_VOCABULARY)


# --------------------------------------------------------------------------- #
# Reranking
# --------------------------------------------------------------------------- #

def _load_reranker():
    from FlagEmbedding import FlagReranker
    return FlagReranker(RERANKER_ID, use_fp16=True)


def _rerank(reranker, queries: list[str], texts: list[str], rankings: list[list[int]]) -> list[list[int]]:
    reranked = []
    for query, ranking in zip(queries, rankings):
        candidates = ranking[:RERANK_CANDIDATES]
        scores = reranker.compute_score([[query, texts[i]] for i in candidates], max_length=1024)
        reranked.append([doc for _, doc in sorted(zip(scores, candidates), key=lambda pair: -pair[0])])
    return reranked


def _free_gpu() -> None:
    try:
        import torch
        torch.cuda.empty_cache()
    except ImportError:
        pass
