"""JSON contracts of the scraper service."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

ScrapeStatus = Literal["queued", "discovering", "crawling", "network", "extracting", "indexing", "done", "failed"]


class ScrapeRequest(BaseModel):
    url: str = Field(min_length=1, max_length=500)
    mode: Literal["replace", "append"] = "replace"


class RecentUrl(BaseModel):
    url: str
    outcome: Literal["cached", "fetched", "failed"]


class ScrapeJob(BaseModel):
    job_id: str
    url: str
    mode: Literal["replace", "append"]
    status: ScrapeStatus
    # crawl
    discovered: int = 0
    fetched: int = 0
    from_cache: int = 0
    failed: int = 0
    remaining: int = 0
    recent: list[RecentUrl] = Field(default_factory=list)
    """The last URLs handled, newest first."""
    # extraction and indexing
    pages: int = 0
    chunks: int = 0
    unchanged: int = 0
    to_embed: int = 0
    embedded: int = 0
    deleted: int = 0
    error: str | None = None
    started_at: datetime
    finished_at: datetime | None = None
