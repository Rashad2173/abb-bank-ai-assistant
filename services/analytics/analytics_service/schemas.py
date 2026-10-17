"""JSON contracts of the analytics service."""

from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class SourceRef(BaseModel):
    url: str
    title: str


class InteractionIn(BaseModel):
    """One question and its answer, as the chat service reports it."""

    request_id: str = Field(max_length=64)
    session_id: str | None = Field(default=None, max_length=64)
    question: str
    standalone_question: str
    answer: str
    status: str = Field(max_length=32)
    refusal_reason: str = Field(default="none", max_length=32)
    language: str = Field(max_length=16)
    grounded: bool
    sources: list[SourceRef] = Field(default_factory=list)
    retrieved_chunk_ids: list[str] = Field(default_factory=list)
    top_score: float | None = None
    model: str = Field(max_length=64)
    reranked: bool
    input_tokens: int = 0
    output_tokens: int = 0
    rewrite_ms: float = 0.0
    retrieval_ms: float = 0.0
    rerank_ms: float = 0.0
    generation_ms: float = 0.0
    total_ms: float = 0.0


class InteractionOut(InteractionIn):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


class InteractionPage(BaseModel):
    items: list[InteractionOut]
    total: int


class DayCount(BaseModel):
    date: date
    total: int
    answered: int
    refused: int
    no_information: int


class LatencyStats(BaseModel):
    avg_ms: float
    p50_ms: float
    p95_ms: float


class SourceCount(BaseModel):
    url: str
    title: str
    count: int


class Stats(BaseModel):
    period_days: int
    total: int
    by_status: dict[str, int]
    by_refusal_reason: dict[str, int]
    by_language: dict[str, int]
    per_day: list[DayCount]
    by_hour: list[int]
    """Questions per hour of the day (Baku time), index 0–23."""
    latency: LatencyStats
    """End-to-end answer time."""
    reranked_share: float
    """Share of answers built with the reranker (the rest fell back to Milvus' order)."""
    grounded_share: float
    """Share of "answered" answers that cite a source."""
    tokens: dict[str, int]
    top_sources: list[SourceCount]
