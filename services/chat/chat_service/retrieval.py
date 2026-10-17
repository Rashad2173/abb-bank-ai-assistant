"""Finding the chunks for a question: Milvus hybrid search, then reranking.

Reranking is the one optional step: when the reranker is switched off, slow or
down, the answer is built from Milvus' own order (lower accuracy, but the user
still gets an answer) and the response says ``reranked: false``.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass

import numpy as np
from starlette.concurrency import run_in_threadpool

from abb_retrieval.milvus_store import MilvusStore, Query
from service_common import dependency
from service_common.inference_client import InferenceClient

from .config import Settings

log = logging.getLogger(__name__)


@dataclass
class Retrieval:
    chunks: list[dict]
    """Chunks for the LLM, best first, each with a ``score`` (reranker relevance, ``None`` if not reranked)."""
    reranked: bool
    retrieval_ms: float
    rerank_ms: float


class Retriever:
    def __init__(self, store: MilvusStore, inference: InferenceClient, settings: Settings) -> None:
        self.store = store
        self.inference = inference
        self.settings = settings

    async def retrieve(self, question: str) -> Retrieval:
        started = time.perf_counter()
        candidates = await self._candidates(question)
        retrieval_ms = _ms_since(started)

        started = time.perf_counter()
        scores = await self._rerank_scores(question, candidates)
        rerank_ms = _ms_since(started)

        if scores is None:
            chunks = [{**chunk, "score": None} for chunk in candidates]
        else:
            ranked = sorted(zip(scores, range(len(candidates))), key=lambda pair: -pair[0])
            chunks = [{**candidates[i], "score": round(score, 4)} for score, i in ranked
                      if score >= self.settings.min_rerank_score]
        return Retrieval(chunks=chunks[:self.settings.context_chunks], reranked=scores is not None,
                         retrieval_ms=retrieval_ms, rerank_ms=rerank_ms)

    async def _candidates(self, question: str) -> list[dict]:
        with dependency("inference service"):
            embedding = await self.inference.embed([question], kind="query")
        query = Query(text=question, dense=np.asarray(embedding.dense[0], dtype=np.float32), sparse=embedding.sparse[0])
        limit = self.settings.retrieval_candidates if self.settings.reranker == "http" else self.settings.context_chunks
        with dependency("Milvus"):
            ids = (await run_in_threadpool(self.store.search, [query], self.settings.retrieval_method, limit))[0]
            return await run_in_threadpool(self.store.fetch, ids)

    async def _rerank_scores(self, question: str, candidates: list[dict]) -> list[float] | None:
        if self.settings.reranker == "none" or not candidates:
            return None
        try:
            return await self.inference.rerank(question, [c["text"] for c in candidates],
                                               timeout=self.settings.rerank_timeout)
        except Exception as exc:  # timeout, connection refused, 5xx … — answer without reranking
            log.warning("reranker unavailable, using Milvus order", extra={"error": f"{type(exc).__name__}: {exc}"})
            return None


def _ms_since(started: float) -> float:
    return round(1000 * (time.perf_counter() - started), 1)
