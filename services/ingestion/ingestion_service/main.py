"""Ingestion service API.  Run: ``uvicorn ingestion_service.main:app --port 8003``"""

from __future__ import annotations

from contextlib import asynccontextmanager

from typing import Annotated

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from starlette.concurrency import run_in_threadpool

from abb_retrieval.config import ChunkingConfig
from abb_retrieval.milvus_store import MilvusStore
from abb_retrieval.tokens import TokenCounter, load_token_counter
from service_common import configure_logging, create_app, dependency
from service_common.inference_client import InferenceClient

from . import __version__
from .config import Settings
from .documents import UnreadableDocument, page_from_file
from .jobs import Ingestor, JobRunning
from .schemas import CorpusInfo, FileIngestResponse, IngestMode, IngestRequest, Job

SERVICE = "ingestion"


def build_app(settings: Settings | None = None, count_tokens: TokenCounter | None = None) -> FastAPI:
    """``count_tokens`` can be injected (tests); otherwise the bge-m3 tokenizer is loaded."""
    settings = settings or Settings()
    configure_logging(SERVICE, settings.log_level)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        counter = count_tokens or await run_in_threadpool(load_token_counter, ChunkingConfig().tokenizer)
        inference = InferenceClient(settings.inference_url, timeout=settings.embed_timeout)
        app.state.store = MilvusStore(settings.milvus_uri, settings.milvus_collection)
        app.state.inference = inference
        app.state.ingestor = Ingestor(app.state.store, inference, counter, settings.embed_batch)
        yield
        await app.state.ingestor.wait()
        await inference.close()

    app = create_app(SERVICE, __version__, ready_checks=_ready_checks, lifespan=lifespan)

    @app.post("/v1/ingest", response_model=Job, status_code=202, tags=["ingestion"])
    async def ingest(body: IngestRequest, request: Request) -> Job:
        if len(body.pages) > settings.max_pages:
            raise HTTPException(413, f"At most {settings.max_pages} pages per upload")
        try:
            return request.app.state.ingestor.start([page.model_dump() for page in body.pages], body.mode)
        except JobRunning as exc:
            raise HTTPException(409, str(exc)) from exc

    @app.post("/v1/ingest/files", response_model=FileIngestResponse, status_code=202, tags=["ingestion"])
    async def ingest_files(request: Request, files: Annotated[list[UploadFile], File()],
                           mode: Annotated[IngestMode, Form()] = "append") -> FileIngestResponse:
        """PDF / TXT documents → pages → the same job as ``/v1/ingest`` (default: added to the index)."""
        if len(files) > settings.max_files:
            raise HTTPException(413, f"At most {settings.max_files} files per upload")
        pages = []
        for upload in files:
            data = await upload.read()
            if len(data) > settings.max_file_mb * 1024 * 1024:
                raise HTTPException(413, f"{upload.filename}: larger than {settings.max_file_mb} MB")
            try:
                pages.append(await run_in_threadpool(page_from_file, upload.filename or "document", data))
            except UnreadableDocument as exc:
                raise HTTPException(422, str(exc)) from exc
        try:
            job = request.app.state.ingestor.start(pages, mode)
        except JobRunning as exc:
            raise HTTPException(409, str(exc)) from exc
        return FileIngestResponse(job=job, pages=pages)

    @app.get("/v1/ingest/{job_id}", response_model=Job, tags=["ingestion"])
    async def job_status(job_id: str, request: Request) -> Job:
        job = request.app.state.ingestor.jobs.get(job_id)
        if job is None:
            raise HTTPException(404, f"Unknown job {job_id}")
        return job

    @app.get("/v1/corpus", response_model=CorpusInfo, tags=["ingestion"])
    async def corpus(request: Request) -> CorpusInfo:
        store: MilvusStore = request.app.state.store
        with dependency("Milvus"):
            count = await run_in_threadpool(lambda: store.count() if store.exists() else 0)
        return CorpusInfo(collection=store.collection, chunks=count, last_job=request.app.state.ingestor.last_job)

    return app


def _ready_checks(app: FastAPI):
    async def milvus() -> str:
        store: MilvusStore = app.state.store
        exists = await run_in_threadpool(store.exists)
        return f"collection {store.collection!r} {'exists' if exists else 'will be created on first upload'}"

    async def inference() -> str:
        return await app.state.inference.ready()

    return {"milvus": milvus, "inference": inference}


app = build_app()
