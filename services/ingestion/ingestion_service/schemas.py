"""JSON contracts of the ingestion service."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class Page(BaseModel):
    """One scraped page — the fields the chunker needs; everything else is kept as is."""

    model_config = ConfigDict(extra="allow")

    url: str
    title: str
    lang: str
    category: str
    sections: list[dict] = Field(default_factory=list)
    faq: list[dict] = Field(default_factory=list)


class IngestRequest(BaseModel):
    pages: list[Page] = Field(min_length=1)


JobStatus = Literal["queued", "chunking", "comparing", "embedding", "writing", "done", "failed"]


class Job(BaseModel):
    job_id: str
    status: JobStatus
    pages: int
    chunks: int = 0
    unchanged: int = 0
    to_embed: int = 0
    embedded: int = 0
    deleted: int = 0
    error: str | None = None
    started_at: datetime
    finished_at: datetime | None = None


class CorpusInfo(BaseModel):
    collection: str
    chunks: int
    last_job: Job | None
