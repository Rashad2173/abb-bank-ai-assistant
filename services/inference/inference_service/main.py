"""Inference service API.  Run: ``uvicorn inference_service.main:app --port 8004``"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request

from service_common import configure_logging, create_app

from . import __version__
from .config import Settings
from .models import Models, ModelUnavailable
from .schemas import EmbedRequest, EmbedResponse, RerankRequest, RerankResponse

SERVICE = "inference"


def build_app(settings: Settings | None = None, models: Models | None = None) -> FastAPI:
    """``models`` can be injected (tests); otherwise they are loaded at start-up."""
    settings = settings or Settings()
    configure_logging(SERVICE, settings.log_level)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        if models is None:
            app.state.models = Models(settings)
            await app.state.models.load()
        else:
            app.state.models = models
        yield

    app = create_app(SERVICE, __version__, ready_checks=_ready_checks, lifespan=lifespan)

    @app.post("/v1/embed", response_model=EmbedResponse, tags=["inference"])
    async def embed(body: EmbedRequest, request: Request) -> EmbedResponse:
        if len(body.texts) > settings.max_batch:
            raise HTTPException(413, f"At most {settings.max_batch} texts per request")
        models_: Models = request.app.state.models
        embeddings = await _call(models_.embed(body.texts, body.kind))
        return EmbedResponse(
            model=models_.embed_model,
            dense=embeddings.dense.tolist(),
            sparse=[{str(token): weight for token, weight in vector.items()} for vector in embeddings.sparse],
        )

    @app.post("/v1/rerank", response_model=RerankResponse, tags=["inference"])
    async def rerank(body: RerankRequest, request: Request) -> RerankResponse:
        if len(body.documents) > settings.rerank_max_documents:
            raise HTTPException(413, f"At most {settings.rerank_max_documents} documents per request")
        models_: Models = request.app.state.models
        scores = await _call(models_.rerank(body.query, body.documents))
        return RerankResponse(model=models_.rerank_model, scores=scores)

    return app


async def _call(coroutine):
    try:
        return await coroutine
    except ModelUnavailable as exc:
        raise HTTPException(503, str(exc)) from exc


def _ready_checks(app: FastAPI):
    async def embedding_model() -> str:
        models: Models = app.state.models
        if models.embedder is None:
            raise ModelUnavailable("not loaded")
        return f"{models.embed_model} on {models.device}"

    async def reranker() -> str:
        models: Models = app.state.models
        if models.reranker is not None:
            return f"{models.rerank_model} on {models.device}"
        if not models.settings.load_reranker:
            return "disabled on this instance"
        raise ModelUnavailable("not loaded")

    return {"embedding_model": embedding_model, "reranker": reranker}


app = build_app()
