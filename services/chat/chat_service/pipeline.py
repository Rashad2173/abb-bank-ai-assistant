"""One question, start to finish: answered at once (:meth:`ChatPipeline.run`) or streamed.

Both share the steps before the answer (:meth:`ChatPipeline.prepare`: planning,
search, reranking) and after it (:meth:`ChatPipeline._finish`: the guardrail
checks, timings and what analytics stores), so a streamed answer is checked
exactly like one returned at once.
"""

from __future__ import annotations

import logging
import time
from collections.abc import AsyncIterator
from dataclasses import dataclass

from openai import OpenAIError

from service_common import dependency, request_id

from .config import Settings
from .generator import Generation, Generator
from .guardrail import check_answer
from .prompts import source_label, with_quote
from .query import QueryPlanner, SearchPlan
from .retrieval import Retrieval, Retriever
from .schemas import ChatRequest, ChatResponse, Source, Timings, Turn

log = logging.getLogger(__name__)


@dataclass
class Outcome:
    response: ChatResponse
    interaction: dict
    """What the analytics service stores."""


@dataclass
class Prepared:
    """A question with everything the answer needs: the plan and the retrieved chunks."""

    request: ChatRequest
    request_id: str
    history: list[Turn]
    message: str
    """The question as the model sees it (with the quoted passage, if any)."""
    plan: SearchPlan
    retrieval: Retrieval
    started: float
    rewrite_ms: float


class ChatPipeline:
    def __init__(self, retriever: Retriever, generator: Generator, settings: Settings) -> None:
        self.retriever = retriever
        self.generator = generator
        self.settings = settings
        self.planner = QueryPlanner(generator, settings.query_expansion, settings.procurement_filter)

    async def prepare(self, request: ChatRequest) -> Prepared:
        started = time.perf_counter()
        history = request.history[-self.settings.history_turns :]
        message = with_quote(request.question, request.quote)

        step = time.perf_counter()
        with dependency("OpenAI", OpenAIError):
            plan = await self.planner.plan(message, history, quoted=bool(request.quote))
        rewrite_ms = _ms_since(step)

        retrieval = await self.retriever.retrieve(plan, rerank=request.rerank)
        return Prepared(request, request_id(), history, message, plan, retrieval, started, rewrite_ms)

    async def run(self, request: ChatRequest) -> Outcome:
        prepared = await self.prepare(request)
        step = time.perf_counter()
        with dependency("OpenAI", OpenAIError):
            generation = await self.generator.answer(prepared.message, prepared.retrieval.chunks, prepared.history)
        return self._finish(prepared, generation, generation_ms=_ms_since(step))

    async def stream(self, prepared: Prepared) -> AsyncIterator[dict | Outcome]:
        """Events for the client, then the :class:`Outcome`.

        * ``{"type": "sources", "sources": [...]}`` — the chunks given to the model, labelled S1 …
          (the streamed text cites them),
        * ``{"type": "status", "status": ...}`` — answered / refused …, known before the text,
        * ``{"type": "delta", "text": ...}`` — the next piece of the answer,
        * the :class:`Outcome`, whose checked response replaces the streamed text.
        """
        chunks = prepared.retrieval.chunks
        yield {
            "type": "sources",
            "sources": [_source(source_label(i), chunk).model_dump(mode="json") for i, chunk in enumerate(chunks)],
        }
        step = time.perf_counter()
        first_token_ms: float | None = None
        status_sent = False
        generation: Generation | None = None
        with dependency("OpenAI", OpenAIError):
            async for item in self.generator.answer_stream(prepared.message, chunks, prepared.history):
                if isinstance(item, Generation):
                    generation = item
                    continue
                if item.status and not status_sent:
                    status_sent = True
                    yield {"type": "status", "status": item.status}
                if item.text:
                    first_token_ms = first_token_ms or _ms_since(prepared.started)
                    yield {"type": "delta", "text": item.text}
        if generation is None:  # the generator raises before this; kept for the type checker
            raise RuntimeError("the answer stream produced no answer")
        yield self._finish(prepared, generation, generation_ms=_ms_since(step), first_token_ms=first_token_ms)

    def _finish(
        self, prepared: Prepared, generation: Generation, generation_ms: float, first_token_ms: float | None = None
    ) -> Outcome:
        request, plan, retrieval = prepared.request, prepared.plan, prepared.retrieval
        checked = check_answer(generation, retrieval.chunks)
        sources = [_source(label, chunk) for label, chunk in zip(checked.labels, checked.cited, strict=True)]
        timings = Timings(
            rewrite_ms=prepared.rewrite_ms,
            retrieval_ms=retrieval.retrieval_ms,
            rerank_ms=retrieval.rerank_ms,
            generation_ms=generation_ms,
            first_token_ms=first_token_ms,
            total_ms=_ms_since(prepared.started),
        )
        response = ChatResponse(
            answer=generation.answer,
            status=generation.status,
            refusal_reason=generation.refusal_reason,
            language=generation.language,
            sources=sources,
            standalone_question=plan.standalone,
            search_queries=plan.queries,
            reranked=retrieval.reranked,
            model=self.settings.openai_chat_model,
            timings=timings,
            request_id=prepared.request_id,
        )
        log.info(
            "answered",
            extra={
                "status": response.status,
                "reranked": response.reranked,
                "sources": len(sources),
                "first_token_ms": first_token_ms,
                "total_ms": timings.total_ms,
            },
        )
        interaction = {
            "request_id": response.request_id,
            "session_id": request.session_id,
            "question": request.question,
            "standalone_question": plan.standalone,
            "answer": response.answer,
            "status": response.status,
            "refusal_reason": response.refusal_reason,
            "language": response.language,
            "grounded": checked.grounded,
            "sources": [{"url": s.url, "title": s.title} for s in sources],
            "retrieved_chunk_ids": [chunk["chunk_id"] for chunk in retrieval.chunks],
            "top_score": retrieval.chunks[0]["score"] if retrieval.chunks else None,
            "model": response.model,
            "reranked": response.reranked,
            "input_tokens": generation.input_tokens,
            "output_tokens": generation.output_tokens,
            **timings.model_dump(exclude={"first_token_ms"}),
        }
        return Outcome(response=response, interaction=interaction)


def _source(label: str, chunk: dict) -> Source:
    return Source(
        id=label,
        title=chunk["title"],
        url=chunk["url"],
        published=chunk.get("published"),
        is_active=chunk.get("is_active"),
        valid_until=chunk.get("valid_until"),
    )


def _ms_since(started: float) -> float:
    return round(1000 * (time.perf_counter() - started), 1)
