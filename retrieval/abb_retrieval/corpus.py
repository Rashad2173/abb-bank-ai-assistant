"""Reading and writing the JSONL files the retrieval steps share."""

from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path

from pydantic import BaseModel

from .chunking import chunk_page
from .config import ChunkingConfig
from .models import Chunk, ChunkAlias, Question
from .text import fingerprint
from .tokens import TokenCounter


def load_pages(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def chunk_corpus(pages: list[dict], count_tokens: TokenCounter, config: ChunkingConfig) -> list[Chunk]:
    chunks = [chunk for index, page in enumerate(pages) for chunk in chunk_page(page, index, count_tokens, config)]
    return merge_identical_chunks(chunks)


def merge_identical_chunks(chunks: list[Chunk]) -> list[Chunk]:
    """Keep one chunk per identical text (e.g. the same block on "/" and "/ferdi").

    Identical chunks would occupy several search results with the same text.
    The kept chunk lists the other pages in ``related_urls`` and remembers
    their source positions in ``aliases`` (needed to map evaluation evidence).
    """
    kept: dict[str, Chunk] = {}
    for chunk in chunks:
        key = fingerprint(chunk.text)
        first = kept.get(key)
        if first is None:
            kept[key] = chunk
            continue
        first.aliases.append(ChunkAlias(url=chunk.url, page_index=chunk.page_index, sources=chunk.sources))
        if chunk.url != first.url and chunk.url not in first.related_urls:
            first.related_urls.append(chunk.url)
    return list(kept.values())


def write_jsonl(path: Path, items: Iterable[BaseModel]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        for item in items:
            fh.write(item.model_dump_json() + "\n")


def load_chunks(path: Path) -> list[Chunk]:
    with path.open(encoding="utf-8") as fh:
        return [Chunk.model_validate_json(line) for line in fh if line.strip()]


def load_questions(path: Path) -> list[Question]:
    with path.open(encoding="utf-8") as fh:
        return [Question.model_validate_json(line) for line in fh if line.strip()]
