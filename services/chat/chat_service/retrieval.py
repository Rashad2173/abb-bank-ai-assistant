"""Finding the chunks for a question: Milvus hybrid search, then reranking.

Reranking is the one optional step: when the reranker is switched off (for the
service, or for one question), slow or down, the answer is built from Milvus' own
order (slightly lower accuracy — report 10 — but the user still gets an answer)
and the response says ``reranked: false``.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass

import numpy as np
from starlette.concurrency import run_in_threadpool

from abb_retrieval.milvus_store import MilvusStore, Query
from abb_retrieval.search import reciprocal_rank_fusion
from service_common import dependency
from service_common.inference_client import InferenceClient

from .config import Settings
from .query import PROCUREMENT_FILTER, SearchPlan

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

    async def retrieve(self, plan: SearchPlan, rerank: bool = True) -> Retrieval:
        """``rerank=False`` skips the reranker for this question (it is also skipped when the service has none)."""
        rerank = rerank and self.settings.reranker == "http"
        started = time.perf_counter()
        candidates = await self._candidates(plan, self.settings.retrieval_candidates if rerank else None)
        retrieval_ms = _ms_since(started)

        started = time.perf_counter()
        scores = await self._rerank_scores(plan.standalone, candidates) if rerank else None
        rerank_ms = _ms_since(started)

        if scores is None:
            chunks = [{**chunk, "score": None} for chunk in candidates]
        else:
            ranked = sorted(enumerate(scores), key=lambda pair: -pair[1])
            chunks = [
                {**candidates[i], "score": round(score, 4)}
                for i, score in ranked
                if score >= self.settings.min_rerank_score
            ]
        return Retrieval(
            chunks=chunks[: self.settings.context_chunks],
            reranked=scores is not None,
            retrieval_ms=retrieval_ms,
            rerank_ms=rerank_ms,
        )

    async def _candidates(self, plan: SearchPlan, limit: int | None) -> list[dict]:
        """Every query searched in Milvus; several result lists are fused with Reciprocal Rank Fusion.

        ``limit``: candidates for the reranker; ``None`` (no reranking) fetches just the chunks the LLM gets.
        """
        limit = limit or self.settings.context_chunks
        with dependency("inference service"):
            embedding = await self.inference.embed(plan.queries, kind="query")
        queries = [
            Query(text=text, dense=np.asarray(embedding.dense[i], dtype=np.float32), sparse=embedding.sparse[i])
            for i, text in enumerate(plan.queries)
        ]
        search_filter = "" if plan.include_procurement else PROCUREMENT_FILTER
        with dependency("Milvus"):
            rankings = await run_in_threadpool(
                self.store.search, queries, self.settings.retrieval_method, limit, search_filter
            )
            ids = (
                rankings[0] if len(rankings) == 1 else reciprocal_rank_fusion(*([r] for r in rankings), top_k=limit)[0]
            )
            return await run_in_threadpool(self.store.fetch, ids)

    async def _rerank_scores(self, question: str, candidates: list[dict]) -> list[float] | None:
        if not candidates:
            return None
        try:
            return await self.inference.rerank(
                question, [c["text"] for c in candidates], timeout=self.settings.rerank_timeout
            )
        except Exception as exc:  # timeout, connection refused, 5xx … — answer without reranking
            log.warning("reranker unavailable, using Milvus order", extra={"error": f"{type(exc).__name__}: {exc}"})
            return None


def _ms_since(started: float) -> float:
    return round(1000 * (time.perf_counter() - started), 1)
