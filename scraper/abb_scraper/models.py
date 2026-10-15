"""Data models shared by the crawl and extract phases."""

from __future__ import annotations

from datetime import date, datetime
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
    also_on: list[str] = Field(default_factory=list)
    """Other pages showing the same item. Items repeated on many pages are stored
    once (on the most general page); this keeps the link to the other products."""


class Document(BaseModel):
    """A file (mostly PDF: tariffs, terms, reports) linked from the page."""

    title: str
    url: str


class Validity(BaseModel):
    """When a time-limited offer (campaign) applies."""

    valid_from: date | None = None
    valid_until: date | None = None
    is_active: bool | None = None
    """``None`` when the page gives no information."""


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
    documents: list[Document] = Field(default_factory=list)
    validity: Validity | None = None
    """Only for campaigns."""
    published: date | None = None
    """News, press releases, CSR and tenders: the date shown on the page."""
    coordinates: tuple[float, float] | None = None
    """``(lat, lng)`` — only for branches."""
    last_modified: str | None = None
    fetched_at: datetime
    content_hash: str
    char_count: int
