"""Everything that can be extracted from one page, combining all sources.

* the server-rendered HTML (:mod:`.html_content`),
* the page's CMS components that the HTML does not render — inactive tabs,
  client-rendered sections (:mod:`.cms`),
* the page's FAQ / accordion items (:mod:`.rsc`).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ..discovery import cms_path
from ..models import FaqItem
from .cms import component_blocks, find_page_entity
from .html_content import Block, html_fragment_to_text, parse_html
from .rsc import extract_accordion_items, extract_flight_payload, parse_flight_rows


@dataclass
class PageContent:
    title: str
    description: str | None
    breadcrumbs: list[str]
    blocks: list[Block]
    footer_blocks: list[Block]
    faq: list[FaqItem] = field(default_factory=list)
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

    # Only the page's own sections — the entity also embeds its parent pages.
    faq_scope = entity["sections"] if entity is not None else list(rows.values())

    return PageContent(
        title=parsed.title,
        description=parsed.description,
        breadcrumbs=parsed.breadcrumbs,
        blocks=blocks,
        footer_blocks=parsed.footer_blocks,
        faq=_extract_faq(faq_scope, rows),
        has_cms_entity=entity is not None,
    )


def _extract_faq(scope: Any, rows: dict[str, Any]) -> list[FaqItem]:
    faq = []
    for question, answer_html in extract_accordion_items(scope, rows):
        answer = html_fragment_to_text(answer_html)
        if answer:
            faq.append(FaqItem(question=html_fragment_to_text(question), answer=answer))
    return faq
