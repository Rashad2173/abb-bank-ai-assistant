"""Paths and tunable settings."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class ChunkingConfig:
    target_tokens: int = 350
    """Small neighbouring sections are packed together up to this size."""
    max_tokens: int = 512
    """Hard limit. Larger sections are split at paragraph (then sentence) boundaries."""
    overlap_paragraphs: int = 1
    """Paragraphs repeated at the start of the next window when a section is split."""
    min_body_words: int = 4
    """Section chunks with less text than this ("Все", "Sual-cavab") carry no information."""
    shared_section_categories: tuple[str, ...] = ("procurement",)
    shared_section_min_pages: int = 10
    """A chunk body found word for word on this many tender pages is a common section
    (supplier requirements …) and is stored once — see :mod:`merging`."""
    tokenizer: str = "BAAI/bge-m3"
    """Token counts use this tokenizer (all candidate models allow >= 512 tokens)."""


@dataclass(frozen=True)
class Paths:
    data_dir: Path = field(default=PROJECT_ROOT / "data")
    evaluation_dir: Path = field(default=PROJECT_ROOT / "evaluation")

    @property
    def pages(self) -> Path:
        return self.data_dir / "abb_pages.jsonl"

    @property
    def chunks(self) -> Path:
        return self.data_dir / "chunks.jsonl"

    @property
    def embeddings_dir(self) -> Path:
        return self.data_dir / "embeddings"

    @property
    def question_set(self) -> Path:
        return self.evaluation_dir / "abb_100_soru_kaynakli.md"

    @property
    def questions(self) -> Path:
        return self.evaluation_dir / "questions.jsonl"

    @property
    def evidence_additions(self) -> Path:
        return self.evaluation_dir / "evidence_additions.json"

    @property
    def reports_dir(self) -> Path:
        return self.evaluation_dir / "reports"
