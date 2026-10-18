"""One question, start to finish."""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass

from openai import OpenAIError

from service_common import dependency, request_id

from .config import Settings
from .generator import Generator
from .guardrail import check_answer
from .prompts import with_quote
from .query import QueryPlanner
from .retrieval import Retriever
from .schemas import ChatRequest, ChatResponse, Source, Timings

log = logging.getLogger(__name__)


@dataclass
class Outcome:
    response: ChatResponse
    interaction: dict
    """What the analytics service stores."""


class ChatPipeline:
    def __init__(self, retriever: Retriever, generator: Generator, settings: Settings) -> None:
        self.retriever = retriever
        self.generator = generator
        self.settings = settings
        self.planner = QueryPlanner(generator, settings.query_expansion, settings.procurement_filter)

    async def run(self, request: ChatRequest) -> Outcome:
        started = time.perf_counter()
        history = request.history[-self.settings.history_turns:]
        message = with_quote(request.question, request.quote)

        step = time.perf_counter()
        with dependency("OpenAI", OpenAIError):
            plan = await self.planner.plan(message, history, quoted=bool(request.quote))
        rewrite_ms = _ms_since(step)

        retrieval = await self.retriever.retrieve(plan)

        step = time.perf_counter()
        with dependency("OpenAI", OpenAIError):
            generation = await self.generator.answer(message, retrieval.chunks, history)
        generation_ms = _ms_since(step)

        checked = check_answer(generation, retrieval.chunks)
        sources = [_source(label, chunk) for label, chunk in zip(checked.labels, checked.cited)]
        timings = Timings(rewrite_ms=rewrite_ms, retrieval_ms=retrieval.retrieval_ms, rerank_ms=retrieval.rerank_ms,
                          generation_ms=generation_ms, total_ms=_ms_since(started))
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
            request_id=request_id(),
        )
        log.info("answered", extra={"status": response.status, "reranked": response.reranked,
                                    "sources": len(sources), "total_ms": timings.total_ms})
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
            **timings.model_dump(),
        }
        return Outcome(response=response, interaction=interaction)


def _source(label: str, chunk: dict) -> Source:
    return Source(id=label, title=chunk["title"], url=chunk["url"], published=chunk.get("published"),
                  is_active=chunk.get("is_active"), valid_until=chunk.get("valid_until"))


def _ms_since(started: float) -> float:
    return round(1000 * (time.perf_counter() - started), 1)
