"""Chat service API.  Run: ``uvicorn chat_service.main:app --port 8001``"""

from __future__ import annotations

import json
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import BackgroundTasks, FastAPI, Request
from fastapi.responses import StreamingResponse
from openai import AsyncOpenAI
from starlette.concurrency import run_in_threadpool

from abb_retrieval.milvus_store import MilvusStore
from service_common import DependencyUnavailable, ErrorBody, ErrorResponse, configure_logging, create_app
from service_common.inference_client import InferenceClient

from . import __version__
from .analytics_client import AnalyticsClient
from .config import Settings
from .generator import Generator
from .pipeline import ChatPipeline, Outcome, Prepared
from .retrieval import Retriever
from .schemas import ChatRequest, ChatResponse

SERVICE = "chat"
STREAM_MEDIA_TYPE = "application/x-ndjson"

log = logging.getLogger(__name__)


def build_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings()
    configure_logging(SERVICE, settings.log_level)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        inference = InferenceClient(settings.inference_url, timeout=settings.embed_timeout)
        openai_client = AsyncOpenAI(
            api_key=settings.openai_api_key or None, timeout=settings.llm_timeout, max_retries=2
        )
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

    @app.post(
        "/v1/chat/stream",
        tags=["chat"],
        response_class=StreamingResponse,
        responses={200: {"content": {STREAM_MEDIA_TYPE: {}}, "description": "One JSON event per line"}},
    )
    async def chat_stream(body: ChatRequest, request: Request) -> StreamingResponse:
        """The answer as it is written: one JSON object per line.

        ``sources`` (the chunks given to the model) → ``status`` → ``delta`` … (pieces of the
        answer) → ``done`` (the checked :class:`ChatResponse`, the same as ``POST /v1/chat``).
        Planning and search run before the first byte, so their failures are ordinary JSON
        errors (``503``); a failure while the answer streams arrives as an ``error`` event.
        """
        prepared = await request.app.state.pipeline.prepare(body)
        return StreamingResponse(
            _events(request.app, prepared),
            media_type=STREAM_MEDIA_TYPE,
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},  # nginx: pass each line on at once
        )

    return app


async def _events(app: FastAPI, prepared: Prepared) -> AsyncIterator[str]:
    try:
        async for item in app.state.pipeline.stream(prepared):
            if isinstance(item, Outcome):
                yield _line({"type": "done", "response": item.response.model_dump(mode="json")})
                await app.state.analytics.record(item.interaction)  # the client already has the answer
            else:
                yield _line(item)
    except DependencyUnavailable as exc:
        log.error("dependency unavailable", exc_info=exc.__cause__ or exc, extra={"dependency": exc.dependency})
        yield _error_line(prepared, "dependency_unavailable", str(exc))
    except Exception:
        log.exception("unhandled error while streaming")
        yield _error_line(prepared, "internal_error", "Internal error - see the service log for this request id.")


def _line(event: dict) -> str:
    return json.dumps(event, ensure_ascii=False) + "\n"


def _error_line(prepared: Prepared, code: str, message: str) -> str:
    body = ErrorResponse(error=ErrorBody(code=code, message=message), request_id=prepared.request_id)
    return _line({"type": "error", **body.model_dump()})


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
