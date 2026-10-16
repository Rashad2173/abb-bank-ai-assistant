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
    """Embeddings of chunks and questions, cached separately.

    Chunks are embedded once per corpus version; a new question set only
    embeds its questions.
    """
    model_dir = cache_dir / name
    embedder = _LazyEmbedder(name)  # loaded only if something is not cached
    documents, doc_meta = _cached(model_dir / f"docs-{_fingerprint(texts)}.npz", embedder,
                                  lambda model: model.embed_documents(texts))
    query_vectors, query_meta = _cached(model_dir / f"queries-{_fingerprint(queries)}.npz", embedder,
                                        lambda model: model.embed_queries(queries))
    embedder.release()

    stats = ModelStats(
        model=name,
        dimension=int(documents.dense.shape[1]),
        documents_seconds=doc_meta["seconds"],
        query_ms=round(1000 * query_meta["seconds"] / len(queries), 1),
        api_tokens=doc_meta.get("api_tokens", 0),
    )
    return documents, query_vectors, stats


class _LazyEmbedder:
    """Creates the (large) model only when an embedding has to be computed."""

    def __init__(self, name: str) -> None:
        self.name = name
        self._model: Embedder | None = None

    def get(self) -> Embedder:
        self._model = self._model or create_embedder(self.name)
        return self._model

    @property
    def tokens_used(self) -> int:
        """Tokens billed so far (hosted APIs only)."""
        return getattr(self._model, "tokens_used", 0)

    def release(self) -> None:
        if self._model is not None:
            self._model = None
            _free_gpu()  # before the next model is loaded


def _cached(path: Path, embedder: _LazyEmbedder, compute) -> tuple[Embeddings, dict]:
    """Load ``path``, or compute (with timing and billed tokens) and store the embeddings."""
    meta_path = path.with_suffix(".json")
    if path.exists():
        log.info("using cached embeddings %s", path)
        return _load(path), json.loads(meta_path.read_text())
    model = embedder.get()
    tokens_before, started = embedder.tokens_used, time.perf_counter()
    embeddings = compute(model)
    meta = {"seconds": round(time.perf_counter() - started, 1), "api_tokens": embedder.tokens_used - tokens_before}
    path.parent.mkdir(parents=True, exist_ok=True)
    _save(path, embeddings)
    meta_path.write_text(json.dumps(meta))
    return embeddings, meta


def _fingerprint(texts: list[str]) -> str:
    return hashlib.sha256("\x1e".join(texts).encode()).hexdigest()[:12]


def _save(path: Path, embeddings: Embeddings) -> None:
    arrays = {"dense": embeddings.dense}
    if embeddings.sparse is not None:
        matrix = _csr(embeddings.sparse)
        arrays |= {"sp_data": matrix.data, "sp_indices": matrix.indices, "sp_indptr": matrix.indptr}
    np.savez_compressed(path, **arrays)


def _load(path: Path) -> Embeddings:
    data = np.load(path)
    sparse = None
    if "sp_data" in data:
        matrix = sp.csr_matrix((data["sp_data"], data["sp_indices"], data["sp_indptr"]),
                               shape=(len(data["dense"]), _BGE_M3_VOCABULARY))
        sparse = [dict(zip(row.indices.tolist(), row.data.tolist())) for row in matrix]
    return Embeddings(data["dense"], sparse)


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
