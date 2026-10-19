"""Everything that can be extracted from one page, combining all sources.

* the server-rendered HTML (:mod:`.html_content`),
* the page's CMS components that the HTML does not render — inactive tabs,
  client-rendered sections (:mod:`.cms`),
* the page's FAQ / accordion items (:mod:`.rsc`),
* the documents (PDF …) the page links to.
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import unquote, urlsplit

from ..discovery import cms_path
from ..models import Document, FaqItem
from .cms import component_blocks, find_page_entity
from .html_content import Block, html_fragment_to_text, parse_html
from .rsc import extract_accordion_items, extract_flight_payload, parse_flight_rows
from .text import fingerprint, is_document_url, is_placeholder

_LINK_IN_TEXT_RE = re.compile(r"\((https?://[^\s()]+)\)")
# Link texts that say nothing about the document; the label before them is used instead.
_GENERIC_LINK_TEXTS = frozenset(
    fingerprint(t)
    for t in (
        "Yüklə",
        "Yükləyin",
        "Ətraflı",
        "Bax",
        "Endir",
        "Endirin",
        "Download",
        "More",
        "Details",
        "Скачать",
        "Подробнее",
        "PDF",
    )
)
_MIN_WORDS = 2
"""A broken CMS entry has a one-word question *and* a one-word answer ("Məlumat" /
"əməliyyatları."). A one-word title over a real explanation ("Məlumat" + 2 000
characters) and a short answer to a real question ("Bəli.") are both content."""


@dataclass
class PageContent:
    title: str
    description: str | None
    breadcrumbs: list[str]
    blocks: list[Block]
    footer_blocks: list[Block]
    faq: list[FaqItem] = field(default_factory=list)
    documents: list[Document] = field(default_factory=list)
    has_cms_entity: bool = False


def extract_page(url: str, lang: str, html: str) -> PageContent:
    parsed = parse_html(html)
    rows = parse_flight_rows(extract_flight_payload(html))
    entity = find_page_entity(rows, cms_path(url), lang)

    blocks = list(parsed.blocks)
    if entity is not None:
        cms_blocks = component_blocks(entity, rows, html_texts=[b.text for b in blocks])
        if cms_blocks:
            # Re-open the page title so CMS sections do not nest under the last HTML heading.
            blocks += [Block(parsed.title, heading_level=1), *cms_blocks]
    blocks = [b for b in blocks if not is_placeholder(b.text)]

    # Only the page's own sections — the entity also embeds its parent pages.
    faq_scope = entity["sections"] if entity is not None else list(rows.values())
    faq = _extract_faq(faq_scope, rows)

    return PageContent(
        title=parsed.title,
        description=parsed.description,
        breadcrumbs=parsed.breadcrumbs,
        blocks=blocks,
        footer_blocks=parsed.footer_blocks,
        faq=faq,
        documents=documents_in([b.text for b in blocks] + [item.answer for item in faq]),
        has_cms_entity=entity is not None,
    )


def documents_in(texts: Iterable[str]) -> list[Document]:
    """Documents linked in the texts as ``label (https://…/file.pdf)``, in order of appearance."""
    found: dict[str, Document] = {}
    for text in texts:
        for match in _LINK_IN_TEXT_RE.finditer(text):
            url = match.group(1)
            if is_document_url(url) and url not in found:
                found[url] = Document(title=_document_title(text[: match.start()], url), url=url)
    return list(found.values())


def _document_title(text_before: str, url: str) -> str:
    """ "Bütün kart tarifləri (PDF): Yüklə" → "Bütün kart tarifləri (PDF)"; else the file name."""
    text = _LINK_IN_TEXT_RE.sub("", text_before)
    parts = [part.strip(" ;-–") for part in text.split(":") if part.strip(" ;-–")]
    while parts and fingerprint(parts[-1]) in _GENERIC_LINK_TEXTS:
        parts.pop()
    if parts:
        return parts[-1][-150:]
    return unquote(urlsplit(url).path.rsplit("/", 1)[-1])


def _extract_faq(scope: Any, rows: dict[str, Any]) -> list[FaqItem]:
    """FAQ items, without CMS placeholders ("Bura mətn yazılmalıdır") and broken entries."""
    faq = []
    for question_html, answer_html in extract_accordion_items(scope, rows):
        question, answer = html_fragment_to_text(question_html), html_fragment_to_text(answer_html)
        is_broken = len(question.split()) < _MIN_WORDS and len(answer.split()) < _MIN_WORDS
        if is_placeholder(question) or is_placeholder(answer) or is_broken:
            continue
        faq.append(FaqItem(question=question, answer=answer))
    return faq
