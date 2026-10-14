"""Data models shared by the crawl and extract phases."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

Language = Literal["az", "en", "ru"]


class FetchRecord(BaseModel):
    """One line of the crawl manifest: what was downloaded and where it is cached."""

    url: str
    status: int
    final_url: str
    fetched_at: datetime
    cache_file: str | None = None
    last_modified: str | None = None
    error: str | None = None


class Section(BaseModel):
    """A run of text that belongs under one heading.

    ``heading_path`` holds the full heading hierarchy (e.g. ``["Nağd kredit",
    "Üstünlükləri"]``) so each section keeps its context when it is later split
    into chunks.
    """

    heading_path: list[str] = Field(default_factory=list)
    paragraphs: list[str] = Field(default_factory=list)


class FaqItem(BaseModel):
    question: str
    answer: str


class Page(BaseModel):
    """A fully extracted page — one line in ``abb_pages.jsonl``."""

    url: str
    lang: Language
    title: str
    description: str | None = None
    breadcrumbs: list[str] = Field(default_factory=list)
    category: str
    sections: list[Section] = Field(default_factory=list)
    faq: list[FaqItem] = Field(default_factory=list)
    last_modified: str | None = None
    fetched_at: datetime
    content_hash: str
    char_count: int
