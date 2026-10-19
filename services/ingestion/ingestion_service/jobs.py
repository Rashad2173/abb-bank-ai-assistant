"""The ingestion job (one at a time, state kept in memory)."""

from __future__ import annotations

import asyncio
import logging
import uuid
from datetime import UTC, datetime

import numpy as np
from starlette.concurrency import run_in_threadpool

from abb_retrieval.config import ChunkingConfig
from abb_retrieval.corpus import chunk_corpus
from abb_retrieval.embedders.base import Embeddings
from abb_retrieval.milvus_store import MilvusStore, content_hash
from abb_retrieval.models import Chunk
from abb_retrieval.tokens import TokenCounter
from service_common.inference_client import InferenceClient

from .schemas import IngestMode, Job

log = logging.getLogger(__name__)


class JobRunning(RuntimeError):
    pass


class Ingestor:
    def __init__(
        self, store: MilvusStore, inference: InferenceClient, count_tokens: TokenCounter, embed_batch: int
    ) -> None:
        self.store = store
        self.inference = inference
        self.count_tokens = count_tokens
        self.embed_batch = embed_batch
        self.jobs: dict[str, Job] = {}
        self.last_job: Job | None = None
        self._task: asyncio.Task | None = None

    def start(self, pages: list[dict], mode: IngestMode = "replace") -> Job:
        if self._task is not None and not self._task.done():
            raise JobRunning(f"Job {self.last_job.job_id} is still running")
        job = Job(
            job_id=uuid.uuid4().hex[:12], status="queued", mode=mode, pages=len(pages), started_at=datetime.now(UTC)
        )
        self.jobs[job.job_id] = self.last_job = job
        self._task = asyncio.create_task(self._run(job, pages))
        return job

    async def wait(self) -> None:
        """Until the current job has finished (tests, shutdown)."""
        if self._task is not None:
            await asyncio.gather(self._task, return_exceptions=True)

    async def _run(self, job: Job, pages: list[dict]) -> None:
        try:
            job.status = "chunking"
            chunks = await run_in_threadpool(chunk_corpus, pages, self.count_tokens, ChunkingConfig())
            job.chunks = len(chunks)

            job.status = "comparing"
            stored = await run_in_threadpool(self._stored_hashes)
            changed = [c for c in chunks if stored.get(c.chunk_id) != content_hash(c)]
            # Replace: what the upload no longer contains goes. Append: everything stored stays.
            removed = sorted(set(stored) - {c.chunk_id for c in chunks}) if job.mode == "replace" else []
            job.unchanged, job.to_embed = len(chunks) - len(changed), len(changed)

            if changed:
                job.status = "embedding"
                embeddings = await self._embed(changed, job)
            job.status = "writing"
            if changed:
                await run_in_threadpool(self.store.upsert, changed, embeddings)
            await run_in_threadpool(self.store.delete, removed)
            job.deleted = len(removed)
            job.status = "done"
            log.info("ingestion finished", extra=job.model_dump(mode="json"))
        except Exception as exc:
            job.status, job.error = "failed", f"{type(exc).__name__}: {exc}"[:500]
            log.exception("ingestion failed", extra={"job_id": job.job_id})
        finally:
            job.finished_at = datetime.now(UTC)

    def _stored_hashes(self) -> dict[str, str]:
        if not self.store.exists():
            self.store.recreate()
            return {}
        return self.store.content_hashes()

    async def _embed(self, chunks: list[Chunk], job: Job) -> Embeddings:
        dense: list[list[float]] = []
        sparse: list[dict[int, float]] = []
        for start in range(0, len(chunks), self.embed_batch):
            batch = chunks[start : start + self.embed_batch]
            result = await self.inference.embed([c.text for c in batch], kind="document")
            dense += result.dense
            sparse += result.sparse
            job.embedded += len(batch)
        return Embeddings(dense=np.asarray(dense, dtype=np.float32), sparse=sparse)
