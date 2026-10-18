"""JSON contract of the chat service."""

from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, Field, field_validator

Status = Literal["answered", "greeting", "out_of_scope", "no_information"]
"""* ``answered`` — answered from the sources (with citations),
* ``greeting`` — small talk ("Salam", "what can you do?"),
* ``out_of_scope`` — refused: not about ABB, other banks, personal advice, prompt injection …,
* ``no_information`` — about ABB, but the sources do not contain the answer."""

RefusalReason = Literal["none", "off_topic", "other_bank", "personal_advice", "prompt_injection", "harmful"]


class Turn(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(max_length=4000)


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=1000)
    history: list[Turn] = Field(default_factory=list, max_length=20)
    """Earlier turns of the conversation, oldest first — lets "and in dollars?" be understood."""
    session_id: str | None = Field(default=None, max_length=64)
    quote: str | None = Field(default=None, max_length=2000)
    """A passage of an earlier answer the user is replying to ("which ones?" about a quoted list)."""

    @field_validator("question")
    @classmethod
    def not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("the question is empty")
        return value.strip()


class Source(BaseModel):
    id: str
    """The citation label used in the answer: ``S1``, ``S2`` …"""
    title: str
    url: str
    published: date | None = None
    is_active: bool | None = None
    """Campaigns: is the offer still running."""
    valid_until: date | None = None


class Timings(BaseModel):
    rewrite_ms: float = 0.0
    retrieval_ms: float
    rerank_ms: float
    generation_ms: float
    total_ms: float


class ChatResponse(BaseModel):
    answer: str
    status: Status
    refusal_reason: RefusalReason
    language: str
    sources: list[Source]
    """The sources the answer cites, in citation order."""
    standalone_question: str
    """The question, understandable without the conversation (rewritten when there was history)."""
    search_queries: list[str]
    """What was searched: the question, plus its Azerbaijani version for other languages."""
    reranked: bool
    """False when the reranker was off or unavailable (Milvus' order was used)."""
    model: str
    timings: Timings
    request_id: str
