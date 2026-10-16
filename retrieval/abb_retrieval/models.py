"""Data models: retrieval chunks and evaluation questions."""

from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, Field

ChunkType = Literal["section", "faq"]


class ChunkAlias(BaseModel):
    """Where an identical chunk of another page would have come from (it was merged)."""

    url: str
    page_index: int
    sources: list[str]
    category: str = ""


class Chunk(BaseModel):
    """One unit of retrieval — what gets embedded, stored in Milvus and shown to the LLM."""

    chunk_id: str
    url: str
    lang: str
    category: str
    title: str
    heading_path: list[str]
    chunk_type: ChunkType
    text: str
    """Context header (page title + section path) followed by the body."""
    token_count: int
    page_index: int
    """0-based line of the source page in ``abb_pages.jsonl``."""
    sources: list[str]
    """Positions in the source page this chunk covers, e.g. ``sections[2].paragraphs[0]``, ``faq[1]``."""
    is_active: bool | None = None
    """Campaigns only: is the offer still running (``None`` = unknown / not a campaign)."""
    valid_until: date | None = None
    published: date | None = None
    """News, press releases, CSR, tenders: the date shown on the page."""
    related_urls: list[str] = Field(default_factory=list)
    """Other pages with the same content (shared FAQ items, merged chunks)."""
    categories: list[str] = Field(default_factory=list)
    """All categories the chunk belongs to — more than one after merging (filter on this)."""
    aliases: list[ChunkAlias] = Field(default_factory=list)
    """Chunks of other pages merged into this one."""


class EvidenceRef(BaseModel):
    """One source a question needs. Multi-source questions have several."""

    url: str
    page_index: int
    positions: list[str]
    """Same notation as :attr:`Chunk.sources` — valid for the corpus version the set was written for."""
    texts: list[str] = Field(default_factory=list)
    """The paragraph / FAQ texts at ``positions``. They identify the evidence in any later corpus version."""
    section_paths: list[list[str]] = Field(default_factory=list)
    """Heading path of each text's section (empty for FAQ) — tells the AZN table from the USD table
    when both contain the same sentence."""
    alternatives: list[str] = Field(default_factory=list)
    """Other passages of the same page that answer equally well (``evaluation/evidence_additions.json``)."""
    quote: str = ""
    chunk_ids: list[str] = Field(default_factory=list)
    """Chunks containing this evidence — filled in once the corpus is chunked."""


class Question(BaseModel):
    id: str
    question: str
    lang: str
    category: str
    expected_answer: str
    evidence: list[EvidenceRef]
