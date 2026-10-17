"""Chat service API.  Run: ``uvicorn chat_service.main:app --port 8001``"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import BackgroundTasks, FastAPI, Request
from openai import AsyncOpenAI
from starlette.concurrency import run_in_threadpool

from abb_retrieval.milvus_store import MilvusStore
from service_common import configure_logging, create_app
from service_common.inference_client import InferenceClient

from . import __version__
from .analytics_client import AnalyticsClient
from .config import Settings
from .generator import Generator
from .pipeline import ChatPipeline
from .retrieval import Retriever
from .schemas import ChatRequest, ChatResponse

SERVICE = "chat"


def build_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings()
    configure_logging(SERVICE, settings.log_level)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        inference = InferenceClient(settings.inference_url, timeout=settings.embed_timeout)
        openai_client = AsyncOpenAI(api_key=settings.openai_api_key or None, timeout=settings.llm_timeout, max_retries=2)
        store = MilvusStore(settings.milvus_uri, settings.milvus_collection)  # connects lazily on first call
        app.state.settings = settings
        app.state.store, app.state.inference, app.state.openai = store, inference, openai_client
        app.state.analytics = AnalyticsClient(settings.analytics_url, settings.analytics_timeout)
        app.state.pipeline = ChatPipeline(
            Retriever(store, inference, settings),
            Generator(openai_client, settings.openai_chat_model, settings.openai_reasoning_effort),
            settings,
        )
        yield
        await inference.close()
        await app.state.analytics.close()
        await openai_client.close()

    app = create_app(SERVICE, __version__, ready_checks=_ready_checks, lifespan=lifespan)

    @app.post("/v1/chat", response_model=ChatResponse, tags=["chat"])
    async def chat(body: ChatRequest, request: Request, background: BackgroundTasks) -> ChatResponse:
        outcome = await request.app.state.pipeline.run(body)
        background.add_task(request.app.state.analytics.record, outcome.interaction)  # after the response is sent
        return outcome.response

    return app


def _ready_checks(app: FastAPI):
    state = app.state

    async def milvus() -> str:
        return f"{await run_in_threadpool(state.store.count)} chunks in {state.store.collection!r}"

    async def inference() -> str:
        return await state.inference.ready()

    async def openai() -> str:
        if not state.settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is not set")
        model = await state.openai.models.retrieve(state.settings.openai_chat_model)
        return f"model {model.id} available"

    return {"milvus": milvus, "inference": inference, "openai": openai}


app = build_app()
