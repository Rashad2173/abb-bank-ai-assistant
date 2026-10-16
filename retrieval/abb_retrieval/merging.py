"""Merging repeated chunks.

Repeated chunks occupy several search results with the same text and push the
relevant chunk out of the top k. Two cases are merged; the kept chunk lists
the other pages (``related_urls``, ``categories``) and their source positions
(``aliases`` — needed to map evaluation evidence).

* **Identical chunks** — the same text on several pages (e.g. "/" and "/ferdi").
* **Shared tender sections** — every tender page is kept complete, but some
  sections (supplier requirements, evaluation procedure) are word for word the
  same on hundreds of tenders. A chunk whose *body* is shared by many tenders
  becomes one chunk titled as common to all tenders.
"""

from __future__ import annotations

from collections import defaultdict

from .config import ChunkingConfig
from .models import Chunk, ChunkAlias
from .text import fingerprint
from .tokens import TokenCounter

COMMON_SECTION_TITLES = {
    "az": "Satınalmalar (bütün tenderlər üçün ümumi)",
    "en": "Procurement (common to all tenders)",
    "ru": "Закупки (общее для всех тендеров)",
}


def merge_repeated_chunks(chunks: list[Chunk], config: ChunkingConfig, count_tokens: TokenCounter) -> list[Chunk]:
    return merge_identical_chunks(merge_shared_sections(chunks, config, count_tokens))


def merge_identical_chunks(chunks: list[Chunk]) -> list[Chunk]:
    kept: dict[str, Chunk] = {}
    for chunk in chunks:
        first = kept.setdefault(fingerprint(chunk.text), chunk)
        if first is not chunk:
            _absorb(first, chunk)
    return list(kept.values())


def merge_shared_sections(chunks: list[Chunk], config: ChunkingConfig, count_tokens: TokenCounter) -> list[Chunk]:
    groups: dict[tuple[str, str], list[Chunk]] = defaultdict(list)
    for chunk in chunks:
        if chunk.category in config.shared_section_categories:
            groups[(chunk.lang, fingerprint(body_of(chunk)))].append(chunk)

    shared = {key: group for key, group in groups.items()
              if len({c.url for c in group}) >= config.shared_section_min_pages}
    merged_ids: dict[str, Chunk] = {}
    for (lang, _), group in shared.items():
        common = _common_chunk(group[0], lang, count_tokens)
        for other in group[1:]:
            _absorb(common, other)
        for chunk in group:
            merged_ids[chunk.chunk_id] = common

    result, emitted = [], set()
    for chunk in chunks:
        replacement = merged_ids.get(chunk.chunk_id, chunk)
        if id(replacement) not in emitted:
            emitted.add(id(replacement))
            result.append(replacement)
    return result


def body_of(chunk: Chunk) -> str:
    """The chunk text without its context header (header and body are separated by a blank line)."""
    return chunk.text.split("\n\n", 1)[-1]


def _common_chunk(first: Chunk, lang: str, count_tokens: TokenCounter) -> Chunk:
    title = COMMON_SECTION_TITLES.get(lang, COMMON_SECTION_TITLES["az"])
    header = "\n".join([title, " > ".join(first.heading_path)]) if first.heading_path else title
    text = f"{header}\n\n{body_of(first)}"
    return first.model_copy(update={
        "title": title,
        "text": text,
        "token_count": count_tokens(text),  # the header changed
        "published": None,  # common to tenders of many dates
        "aliases": [*first.aliases, ChunkAlias(url=first.url, page_index=first.page_index,
                                               sources=first.sources, category=first.category)],
        "related_urls": list(first.related_urls),
        "categories": list(first.categories),
    })


def _absorb(kept: Chunk, other: Chunk) -> None:
    kept.aliases.append(ChunkAlias(url=other.url, page_index=other.page_index,
                                   sources=other.sources, category=other.category))
    kept.aliases.extend(other.aliases)
    for url in [other.url, *other.related_urls]:
        if url != kept.url and url not in kept.related_urls:
            kept.related_urls.append(url)
    for category in [other.category, *other.categories]:
        if category not in kept.categories:
            kept.categories.append(category)
