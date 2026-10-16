"""Split scraped pages into retrieval chunks.

Rules
-----
* Every **FAQ item** is its own chunk (question + answer) — the most precise
  unit for question answering.
* **Sections** are packed: neighbouring small sections of a page are merged
  until the chunk reaches ``target_tokens`` (23 % of all sections are shorter
  than 80 characters and meaningless on their own).
* A section larger than ``max_tokens`` is split into windows of whole
  paragraphs, repeating ``overlap_paragraphs`` paragraph(s) at the start of the
  next window; a single oversized paragraph is split into sentences.
* Every chunk starts with a **context header** — the page title and the section
  path — so that a line like "İllik faiz dərəcəsi: 22%" still says what it
  belongs to ("TamKart Gold Kredit > Tariflər").

Each chunk records which positions of the page it covers (``sources``), so
evaluation questions that point at a page position can be mapped to chunks.
"""

from __future__ import annotations

import hashlib
import re
from collections.abc import Iterator
from dataclasses import dataclass

from .config import ChunkingConfig
from .models import Chunk
from .tokens import TokenCounter

_SENTENCE_END_RE = re.compile(r"(?<=[.!?…])\s+")
_HEADER_RESERVE = 8  # tokens for separators/newlines not counted piece by piece
_FAQ_LABELS = {
    "az": ("Tez-tez verilən suallar", "Sual", "Cavab"),
    "en": ("Frequently asked questions", "Question", "Answer"),
    "ru": ("Часто задаваемые вопросы", "Вопрос", "Ответ"),
}
# (label, active, ended)
_CAMPAIGN_STATUS_LABELS = {
    "az": ("Kampaniya statusu", "aktivdir", "bitib"),
    "en": ("Campaign status", "active", "ended"),
    "ru": ("Статус кампании", "действует", "завершена"),
}
_DATE_LABELS = {"az": "Tarix", "en": "Date", "ru": "Дата"}
_LIST_ITEM_RE = re.compile(r"^(-|\d+[.)])\s")


@dataclass(frozen=True)
class _Piece:
    """One paragraph (or part of one) and where it comes from."""

    source: str
    text: str
    tokens: int


@dataclass(frozen=True)
class _Part:
    """A section, or a window of a section, that goes into one chunk as a whole."""

    path: tuple[str, ...]
    pieces: tuple[_Piece, ...]

    @property
    def tokens(self) -> int:
        return sum(piece.tokens for piece in self.pieces)


def chunk_page(page: dict, page_index: int, count_tokens: TokenCounter, config: ChunkingConfig) -> list[Chunk]:
    return _PageChunker(page, page_index, count_tokens, config).chunks()


class _PageChunker:
    def __init__(self, page: dict, page_index: int, count_tokens: TokenCounter, config: ChunkingConfig) -> None:
        self.page = page
        self.page_index = page_index
        self.count = count_tokens
        self.config = config
        self.title: str = page["title"]
        self.validity: dict = page.get("validity") or {}
        self.status_line = _campaign_status_line(self.validity, page["lang"])
        self.date_line = _date_line(page.get("published"), page["lang"])
        self._chunks: list[Chunk] = []

    def chunks(self) -> list[Chunk]:
        parts = [window for part in self._section_parts() for window in self._split_oversized(part)]
        for group in self._pack(parts):
            self._emit_section_chunk(group)
        for index, item in enumerate(self.page.get("faq", [])):
            self._emit_faq_chunks(index, item["question"], item["answer"], item.get("also_on", []))
        return self._chunks

    # ------------------------------------------------------------------ #
    # Sections
    # ------------------------------------------------------------------ #

    def _section_parts(self) -> Iterator[_Part]:
        for s_index, section in enumerate(self.page.get("sections", [])):
            pieces = tuple(
                _Piece(f"sections[{s_index}].paragraphs[{p_index}]", text, self.count(text))
                for p_index, text in enumerate(section["paragraphs"])
            )
            if pieces:
                yield _Part(self._path_without_title(section["heading_path"]), pieces)

    def _path_without_title(self, heading_path: list[str]) -> tuple[str, ...]:
        """The page title is always in the header, so it is not repeated in the path."""
        path = tuple(heading_path)
        return path[1:] if path and path[0] == self.title else path

    def _body_budget(self, path: tuple[str, ...]) -> int:
        return self.config.max_tokens - self.count(self._header(path)) - _HEADER_RESERVE

    def _split_oversized(self, part: _Part) -> Iterator[_Part]:
        """Paragraph windows (with overlap) for a section that exceeds the token limit.

        A window that starts inside a list begins with the list's lead-in
        sentence ("Aşağıdakılar gəlir vergisindən azaddır:") instead of the
        plain overlap, so the items keep the condition they belong to.
        """
        budget = self._body_budget(part.path)
        if part.tokens <= budget:
            yield part
            return

        pieces = [small for piece in part.pieces for small in self._split_piece(piece, budget)]
        window: list[_Piece] = []
        lead_in: _Piece | None = None
        for piece in pieces:
            if window and sum(p.tokens for p in window) + piece.tokens > budget:
                yield _Part(part.path, tuple(window))
                carry = self._carry_over(window, lead_in, piece)
                # Carry over only when it leaves room for new content.
                window = carry if sum(p.tokens for p in carry) + piece.tokens <= budget else []
            window.append(piece)
            if _is_lead_in(piece.text):
                lead_in = piece
            elif not _is_list_item(piece.text):
                lead_in = None  # a normal paragraph ends the list
        if window:
            yield _Part(part.path, tuple(window))

    def _carry_over(self, window: list[_Piece], lead_in: _Piece | None, next_piece: _Piece) -> list[_Piece]:
        if lead_in is not None and _is_list_item(next_piece.text):
            return [lead_in]
        return window[-self.config.overlap_paragraphs:] if self.config.overlap_paragraphs else []

    def _split_piece(self, piece: _Piece, budget: int) -> Iterator[_Piece]:
        """A paragraph longer than the budget, as sentence groups (or hard cuts as a last resort)."""
        if piece.tokens <= budget:
            yield piece
            return
        group = ""
        for sentence in _SENTENCE_END_RE.split(piece.text):
            for part in self._hard_split(sentence, budget):
                candidate = f"{group} {part}".strip()
                if group and self.count(candidate) > budget:
                    yield _Piece(piece.source, group, self.count(group))
                    group = part
                else:
                    group = candidate
        if group:
            yield _Piece(piece.source, group, self.count(group))

    def _hard_split(self, text: str, budget: int) -> Iterator[str]:
        """Cut a single over-long sentence (e.g. a huge table row) at word boundaries."""
        if self.count(text) <= budget:
            yield text
            return
        words, current = text.split(), []
        for word in words:
            if current and self.count(" ".join([*current, word])) > budget:
                yield " ".join(current)
                current = []
            current.append(word)
        if current:
            yield " ".join(current)

    def _pack(self, parts: list[_Part]) -> Iterator[list[_Part]]:
        """Greedily merge consecutive parts while the chunk stays within the target size."""
        group: list[_Part] = []
        for part in parts:
            if group and self._estimated_tokens([*group, part]) > self.config.target_tokens:
                yield group
                group = []
            group.append(part)
        if group:
            yield group

    def _estimated_tokens(self, group: list[_Part]) -> int:
        prefix = _common_prefix([part.path for part in group])
        subheadings = sum(self.count(" > ".join(part.path[len(prefix):])) for part in group)
        return self.count(self._header(prefix)) + subheadings + sum(part.tokens for part in group)

    def _emit_section_chunk(self, group: list[_Part]) -> None:
        prefix = _common_prefix([part.path for part in group])
        lines: list[str] = []
        previous_subpath: tuple[str, ...] = ()
        for part in group:
            subpath = part.path[len(prefix):]
            if subpath and subpath != previous_subpath:
                lines.append("## " + " > ".join(subpath))
            previous_subpath = subpath
            lines += [piece.text for piece in part.pieces]

        body_words = sum(len(piece.text.split()) for part in group for piece in part.pieces)
        if body_words < self.config.min_body_words:
            return  # a leftover label without information
        sources = list(dict.fromkeys(piece.source for part in group for piece in part.pieces))
        self._add("section", prefix, self._header(prefix) + "\n\n" + "\n".join(lines), sources)

    # ------------------------------------------------------------------ #
    # FAQ
    # ------------------------------------------------------------------ #

    def _emit_faq_chunks(self, index: int, question: str, answer: str, also_on: list[str]) -> None:
        faq_label, q_label, a_label = _FAQ_LABELS.get(self.page["lang"], _FAQ_LABELS["az"])
        path = (faq_label,)
        question_line = f"{q_label}: {question}"
        budget = self._body_budget(path) - self.count(question_line) - self.count(a_label) - 2

        answer_piece = _Piece(f"faq[{index}]", answer, self.count(answer))
        for part in self._split_piece(answer_piece, budget):
            text = f"{self._header(path)}\n\n{question_line}\n{a_label}: {part.text}"
            self._add("faq", path, text, [answer_piece.source], related_urls=also_on)

    # ------------------------------------------------------------------ #

    def _header(self, path: tuple[str, ...]) -> str:
        """Page title, campaign status / publication date (if any) and section path."""
        lines = [self.title, self.status_line, self.date_line, " > ".join(path)]
        return "\n".join(line for line in lines if line)

    def _add(self, chunk_type: str, path: tuple[str, ...], text: str, sources: list[str],
             related_urls: list[str] | None = None) -> None:
        url = self.page["url"]
        self._chunks.append(Chunk(
            chunk_id=f"{hashlib.sha1(url.encode()).hexdigest()[:10]}-{len(self._chunks):03d}",
            url=url,
            lang=self.page["lang"],
            category=self.page["category"],
            title=self.title,
            heading_path=list(path),
            chunk_type=chunk_type,
            text=text,
            token_count=self.count(text),
            page_index=self.page_index,
            sources=sources,
            is_active=self.validity.get("is_active"),
            valid_until=self.validity.get("valid_until"),
            published=self.page.get("published"),
            related_urls=related_urls or [],
            categories=[self.page["category"]],
        ))


def _is_list_item(text: str) -> bool:
    return bool(_LIST_ITEM_RE.match(text))


def _is_lead_in(text: str) -> bool:
    """A sentence introducing the list that follows ("…tələb olunur:")."""
    return text.rstrip().endswith(":") and not _is_list_item(text)


def _date_line(published: str | None, lang: str) -> str | None:
    """E.g. "Tarix: 09.06.2022" — lets the reader see that a news item is old."""
    if not published:
        return None
    return f"{_DATE_LABELS.get(lang, _DATE_LABELS['az'])}: {_format_date(published)}"


def _campaign_status_line(validity: dict, lang: str) -> str | None:
    """E.g. "Kampaniya statusu: bitib (07.05.2025 – 23.05.2025)" — tells the LLM an offer is over."""
    if validity.get("is_active") is None:
        return None
    label, active, ended = _CAMPAIGN_STATUS_LABELS.get(lang, _CAMPAIGN_STATUS_LABELS["az"])
    line = f"{label}: {active if validity['is_active'] else ended}"
    start, end = validity.get("valid_from"), validity.get("valid_until")
    if start and end:
        line += f" ({_format_date(start)} – {_format_date(end)})"
    return line


def _format_date(iso_date: str) -> str:
    year, month, day = str(iso_date).split("-")
    return f"{day}.{month}.{year}"


def _common_prefix(paths: list[tuple[str, ...]]) -> tuple[str, ...]:
    prefix = paths[0]
    for path in paths[1:]:
        length = 0
        while length < min(len(prefix), len(path)) and prefix[length] == path[length]:
            length += 1
        prefix = prefix[:length]
    return prefix
