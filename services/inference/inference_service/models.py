"""Loading and running the models.

The models are not thread-safe and share one GPU, so calls run one at a time
in a worker thread (the event loop stays free for health checks meanwhile).
"""

from __future__ import annotations

import asyncio
import logging
import time

from starlette.concurrency import run_in_threadpool

from abb_retrieval.benchmark import RERANKER_ID
from abb_retrieval.embedders.bge_m3 import BgeM3Embedder

from .config import Settings

log = logging.getLogger(__name__)

RERANK_MAX_LENGTH = 1024  # tokens of question + passage (chunks are ≤ 512)


class Models:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.device = _resolve_device(settings.device)
        self.embedder: BgeM3Embedder | None = None
        self.reranker = None
        self._lock = asyncio.Lock()

    @property
    def embed_model(self) -> str:
        return BgeM3Embedder.model_id

    @property
    def rerank_model(self) -> str:
        return RERANKER_ID

    async def load(self) -> None:
        await run_in_threadpool(self._load)

    def _load(self) -> None:
        started = time.perf_counter()
        fp16 = self.device == "cuda"
        self.embedder = BgeM3Embedder(use_fp16=fp16, devices=self.device)
        if self.settings.load_reranker:
            from FlagEmbedding import FlagReranker
            self.reranker = FlagReranker(RERANKER_ID, use_fp16=fp16, devices=[self.device])
        log.info("models loaded", extra={"device": self.device, "reranker": self.reranker is not None,
                                         "seconds": round(time.perf_counter() - started, 1)})

    async def embed(self, texts: list[str], kind: str):
        embedder = self._require(self.embedder, "embedding model")
        method = embedder.embed_queries if kind == "query" else embedder.embed_documents
        async with self._lock:
            return await run_in_threadpool(method, texts)

    async def rerank(self, query: str, documents: list[str]) -> list[float]:
        reranker = self._require(self.reranker, "reranker")
        pairs = [[query, document] for document in documents]
        async with self._lock:
            scores = await run_in_threadpool(reranker.compute_score, pairs, max_length=RERANK_MAX_LENGTH, normalize=True)
        return [float(s) for s in (scores if isinstance(scores, list) else [scores])]

    @staticmethod
    def _require(model, name: str):
        if model is None:
            raise ModelUnavailable(f"The {name} is not loaded on this instance")
        return model


class ModelUnavailable(RuntimeError):
    pass


def _resolve_device(setting: str) -> str:
    if setting != "auto":
        return setting
    import torch
    return "cuda" if torch.cuda.is_available() else "cpu"
