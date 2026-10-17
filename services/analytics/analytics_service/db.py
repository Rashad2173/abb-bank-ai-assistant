"""The ``interactions`` table.

The schema is created at start-up (``create_all``). One table that only grows
needs no migration tool yet; Alembic would be the next step once the schema
starts to change.
"""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import JSON, Boolean, DateTime, Float, Integer, String, Text, create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from sqlalchemy.pool import StaticPool


class Base(DeclarativeBase):
    pass


class Interaction(Base):
    __tablename__ = "interactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True,
                                                 default=lambda: datetime.now(UTC))
    request_id: Mapped[str] = mapped_column(String(64), index=True)
    session_id: Mapped[str | None] = mapped_column(String(64), index=True)
    question: Mapped[str] = mapped_column(Text)
    standalone_question: Mapped[str] = mapped_column(Text)
    answer: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(32), index=True)
    refusal_reason: Mapped[str] = mapped_column(String(32))
    language: Mapped[str] = mapped_column(String(16))
    grounded: Mapped[bool] = mapped_column(Boolean)
    sources: Mapped[list] = mapped_column(JSON)
    retrieved_chunk_ids: Mapped[list] = mapped_column(JSON)
    top_score: Mapped[float | None] = mapped_column(Float)
    model: Mapped[str] = mapped_column(String(64))
    reranked: Mapped[bool] = mapped_column(Boolean)
    input_tokens: Mapped[int] = mapped_column(Integer)
    output_tokens: Mapped[int] = mapped_column(Integer)
    rewrite_ms: Mapped[float] = mapped_column(Float)
    retrieval_ms: Mapped[float] = mapped_column(Float)
    rerank_ms: Mapped[float] = mapped_column(Float)
    generation_ms: Mapped[float] = mapped_column(Float)
    total_ms: Mapped[float] = mapped_column(Float)


def make_engine(url: str) -> Engine:
    if url.startswith("sqlite"):  # tests: one shared in-memory database
        return create_engine(url, connect_args={"check_same_thread": False}, poolclass=StaticPool)
    return create_engine(url, pool_pre_ping=True, pool_size=5, max_overflow=5)


def make_session_factory(engine: Engine) -> sessionmaker:
    return sessionmaker(engine, expire_on_commit=False)
