"""The evaluation question sets: parse them, freeze their evidence, map it to chunks.

The set (``evaluation/abb_100_soru_kaynakli.md``) is a human-readable Markdown
document written against one exact corpus version (its SHA-256 is stated in
the document). Every question points at positions in that corpus
(page line + ``sections[2].paragraphs[0]`` / ``faq[3]``).

Positions break as soon as the corpus is regenerated (a section more or less
shifts the indices), so the set is used in two steps:

1. **freeze** (once, against the documented corpus version): the text at every
   position is stored with the question in ``evaluation/questions.jsonl``.
2. **attach** (after every re-chunking): evidence is found by *page URL +
   text*, which survives changes of the corpus structure.

Set B (``evaluation/question_set_b.json``) is an independent second set, written
directly against the chunks: each source is a page URL plus verbatim snippets,
so it needs no freeze step (see :func:`parse_snippet_set`).
"""

from __future__ import annotations

import hashlib
import re
from collections import defaultdict
from pathlib import Path

from .models import Chunk, EvidenceRef, Question
from .text import fingerprint

# Section number in the document → question type.
CATEGORIES = {
    "1": "simple",
    "2": "paraphrase",
    "3": "terminology",
    "4": "numeric",
    "5": "multi_source",
    "6": "multilingual",
}

_CORPUS_SHA_RE = re.compile(r"\*\*Korpus SHA-256:\*\*\s*`([0-9a-f]{64})`")
_SECTION_RE = re.compile(r"^## (\d+)\.", re.M)
_QUESTION_RE = re.compile(r"^### (ABB-Q\d+)\s*$", re.M)
_TEXT_RE = re.compile(r"^\*\*Soru \((\w+)\):\*\*\s*(.+)$", re.M)
_ANSWER_RE = re.compile(r"^\*\*Beklenen cevap:\*\*\s*(.+)$", re.M)
_SOURCE_RE = re.compile(
    r"^\*\*Kaynak \d+:\*\*\s*\[[^\]]*\]\((?P<url>[^)]+)\)\s*$"
    r".*?^\*\*Korpus konumu:\*\*[^\n]*?satır \*\*(?P<line>\d+)\*\*;\s*`(?P<positions>[^`]+)`"
    r"(?P<rest>.*?)(?=^\*\*Kaynak \d+:|\Z)",
    re.M | re.S,
)
_QUOTE_RE = re.compile(r"^>\s?(.*)$", re.M)
_POSITION_RE = re.compile(r"sections\[(\d+)\]\.paragraphs\[(\d+)\]|faq\[(\d+)\]")


class CorpusMismatchError(RuntimeError):
    pass


# --------------------------------------------------------------------------- #
# Parsing the Markdown document
# --------------------------------------------------------------------------- #

def parse_question_set(markdown: str) -> list[Question]:
    sections = [(m.start(), m.group(1)) for m in _SECTION_RE.finditer(markdown)]
    starts = list(_QUESTION_RE.finditer(markdown))
    questions = []
    for i, match in enumerate(starts):
        end = starts[i + 1].start() if i + 1 < len(starts) else len(markdown)
        block = markdown[match.end():end]
        section = next(number for start, number in reversed(sections) if start < match.start())
        questions.append(_parse_block(match.group(1), CATEGORIES[section], block))
    return questions


def corpus_sha_of(markdown: str) -> str | None:
    match = _CORPUS_SHA_RE.search(markdown)
    return match.group(1) if match else None


def _parse_block(question_id: str, category: str, block: str) -> Question:
    text = _TEXT_RE.search(block)
    answer = _ANSWER_RE.search(block)
    if not (text and answer):
        raise ValueError(f"{question_id}: question or expected answer missing")
    evidence = [
        EvidenceRef(
            url=m["url"].strip(),
            page_index=int(m["line"]) - 1,  # the document counts lines from 1
            positions=[p.strip() for p in m["positions"].split(";") if p.strip()],
            quote=" ".join(_QUOTE_RE.findall(m["rest"])).strip(),
        )
        for m in _SOURCE_RE.finditer(block)
    ]
    if not evidence:
        raise ValueError(f"{question_id}: no source found")
    return Question(
        id=question_id,
        question=text.group(2).strip(),
        lang=text.group(1),
        category=category,
        expected_answer=answer.group(1).strip(),
        evidence=evidence,
    )


def parse_snippet_set(items: list[dict]) -> list[Question]:
    """Questions whose sources are ``{"url": …, "contains": [snippet, …]}``.

    A chunk of that URL holding any of the snippets counts as the evidence.
    """
    return [
        Question(
            id=item["id"],
            question=item["question"],
            lang=item["lang"],
            category=item["category"],
            expected_answer=item["expected_answer"],
            evidence=[EvidenceRef(url=source["url"], alternatives=source["contains"]) for source in item["evidence"]],
        )
        for item in items
    ]


# --------------------------------------------------------------------------- #
# Step 1 — freeze the evidence texts
# --------------------------------------------------------------------------- #

def freeze_evidence(questions: list[Question], pages: list[dict], corpus_path: Path, expected_sha: str | None) -> None:
    """Store the text at every evidence position. Only valid on the documented corpus version."""
    actual_sha = hashlib.sha256(corpus_path.read_bytes()).hexdigest()
    if expected_sha and actual_sha != expected_sha:
        raise CorpusMismatchError(
            f"The question set was written for corpus {expected_sha[:12]}…, but {corpus_path.name} is "
            f"{actual_sha[:12]}…. Freeze against the original corpus version."
        )
    for question in questions:
        for ref in question.evidence:
            page = pages[ref.page_index]
            if page["url"] != ref.url:
                raise CorpusMismatchError(f"{question.id}: line {ref.page_index + 1} is {page['url']}, not {ref.url}")
            ref.texts = [position_text(page, position) for position in ref.positions]
            ref.section_paths = [_section_path(page, position) for position in ref.positions]


def position_text(page: dict, position: str) -> str:
    """The paragraph or FAQ answer at ``sections[i].paragraphs[j]`` / ``faq[k]``."""
    section, paragraph, faq = _parse_position(position)
    if faq is not None:
        return page["faq"][int(faq)]["answer"]
    return page["sections"][int(section)]["paragraphs"][int(paragraph)]


def _section_path(page: dict, position: str) -> list[str]:
    section, _, faq = _parse_position(position)
    return [] if faq is not None else list(page["sections"][int(section)]["heading_path"])


def _parse_position(position: str) -> tuple[str | None, str | None, str | None]:
    match = _POSITION_RE.fullmatch(position)
    if match is None:
        raise ValueError(f"Unknown position notation: {position}")
    return match.groups()


def apply_additions(questions: list[Question], additions: list[dict]) -> None:
    """Register reviewed alternative passages (``evaluation/evidence_additions.json``)."""
    by_id = {q.id: q for q in questions}
    for addition in additions:
        ref = by_id[addition["question_id"]].evidence[addition["evidence"]]
        if ref.url != addition["url"]:
            raise ValueError(f"{addition['question_id']}: evidence {addition['evidence']} is {ref.url}")
        if addition["contains"] not in ref.alternatives:
            ref.alternatives.append(addition["contains"])


# --------------------------------------------------------------------------- #
# Step 2 — attach chunks
# --------------------------------------------------------------------------- #

def attach_chunks(questions: list[Question], chunks: list[Chunk], pages: list[dict]) -> list[str]:
    """Fill in the chunk ids of every piece of evidence; returns the problems found.

    A chunk contains an evidence text when one of its source positions holds
    that text on the same page (matched by URL, not by line number). Table rows
    also match when only their format changed (see :func:`table_cells`).
    Reviewed alternative passages (``ref.alternatives``) count as well.
    """
    index: dict[tuple[str, object], list[str]] = defaultdict(list)
    chunks_of_url: dict[str, list[Chunk]] = defaultdict(list)
    for chunk in chunks:
        # A merged chunk also stands for the chunks of other pages merged into it.
        for url, page_index, sources in [(chunk.url, chunk.page_index, chunk.sources),
                                         *((a.url, a.page_index, a.sources) for a in chunk.aliases)]:
            chunks_of_url[url].append(chunk)
            for source in sources:
                for key in _match_keys(position_text(pages[page_index], source)):
                    index[(url, key)].append(chunk.chunk_id)
    by_id = {chunk.chunk_id: chunk for chunk in chunks}

    problems = []
    for question in questions:
        for ref in question.evidence:
            if not (ref.texts or ref.alternatives):
                raise ValueError(f"{question.id}: evidence is not frozen yet (run the freeze step first)")
            ids = _chunks_with_evidence(ref, index, by_id) + _chunks_with_alternatives(ref, chunks_of_url)
            ref.chunk_ids = list(dict.fromkeys(ids))
            if not ref.chunk_ids:
                evidence = (ref.texts or ref.alternatives)[0]
                problems.append(f"{question.id}: no chunk of {ref.url} contains the evidence {evidence[:60]!r}")
    return problems


def _chunks_with_evidence(ref: EvidenceRef, index: dict[tuple[str, object], list[str]],
                          by_id: dict[str, Chunk]) -> list[str]:
    """Chunks containing the evidence.

    * A table header row ("Əmanət müddəti | Aylıq | Müddətin sonu") is shared by
      the AZN and the USD table; it only counts when the evidence has nothing
      more specific. Otherwise the chunk must contain the data row itself.
    * A sentence found in several chunks of the page ("no interest on early
      withdrawal" under both the AZN and the USD table) counts only in the
      chunk of the evidence's own section.
    """
    paths = ref.section_paths or [[] for _ in ref.texts]
    pairs = list(zip(ref.texts, paths))
    specific = [(text, path) for text, path in pairs if not _is_table_header(text)] or pairs

    ids = []
    for text, path in specific:
        found = list(dict.fromkeys(cid for key in _match_keys(text) for cid in index.get((ref.url, key), [])))
        if len(found) > 1 and path:
            found = [cid for cid in found if _is_in_section(by_id[cid], path[-1])] or found
        ids += found
    return ids


def _is_in_section(chunk: Chunk, heading: str) -> bool:
    """Is ``heading`` part of the chunk's context (header lines or a "## sub-heading")?"""
    header, _, body = chunk.text.partition("\n\n")
    context = header.split("\n") + [line for line in body.split("\n") if line.startswith("## ")]
    key = fingerprint(heading)
    return any(key in fingerprint(line) for line in context)


def _chunks_with_alternatives(ref: EvidenceRef, chunks_of_url: dict[str, list[Chunk]]) -> list[str]:
    snippets = [fingerprint(snippet) for snippet in ref.alternatives]
    return [chunk.chunk_id for chunk in chunks_of_url.get(ref.url, [])
            if any(snippet in fingerprint(chunk.text) for snippet in snippets)]


def _is_table_header(text: str) -> bool:
    """A table row of labels only (no digits) — in either row format."""
    return bool(table_cells(text)) and not any(char.isdigit() for char in text)


def table_cells(text: str) -> list[tuple[str, ...]]:
    """The cells of a table row in either format the scraper has written.

    * ``"12 ay | 8% | 9%"`` (earlier version: values only, empty cells dropped)
    * ``"Müddət: 12 ay; Aylıq: 8%; Müddətin sonu: 9%"`` (labelled, empty cell = "–")

    A labelled row yields its values *and* its labels (the old header row).
    """
    if " | " in text:
        return [tuple(_cell(c) for c in text.split("|") if _cell(c) not in _EMPTY_CELLS)]
    pairs = [part.split(": ", 1) for part in text.split("; ")]
    if len(pairs) < 2 or any(len(pair) != 2 for pair in pairs):
        return []
    labels = tuple(_cell(label) for label, _ in pairs)
    values = tuple(_cell(value) for _, value in pairs if _cell(value) not in _EMPTY_CELLS)
    return [values, labels]


_EMPTY_CELLS = frozenset({"", "–"})


def _cell(text: str) -> str:
    return fingerprint(text)


def _match_keys(text: str) -> list[object]:
    return [fingerprint(text), *(("cells", cells) for cells in table_cells(text))]
