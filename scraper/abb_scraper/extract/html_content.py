"""Extract the readable content of an abb-bank.az page from its HTML.

The page is reduced to an ordered list of :class:`Block` objects — headings and
text paragraphs — with navigation, footer, forms, buttons and the responsive
duplicates (the site renders the same block separately for mobile and desktop)
removed.
"""

from __future__ import annotations

import re
from collections.abc import Iterator
from dataclasses import dataclass, field

from bs4 import BeautifulSoup, NavigableString, Tag
from bs4.element import PreformattedString

from .text import decode_cf_email, fingerprint, normalize_text

BLOCK_TAGS = (
    "address", "article", "aside", "blockquote", "dd", "div", "dl", "dt",
    "fieldset", "figcaption", "figure", "footer", "h1", "h2", "h3", "h4", "h5",
    "h6", "header", "hr", "li", "main", "ol", "p", "pre", "section", "table",
    "tbody", "td", "tfoot", "th", "thead", "tr", "ul",
)

NON_CONTENT_TAGS = (
    "script", "style", "noscript", "svg", "template", "form", "button", "input",
    "select", "textarea", "img", "picture", "video", "iframe", "dialog", "nav",
    "header", "footer",
)
NON_CONTENT_SELECTORS = (
    "#rate-this-page",               # "Rate this page" widget
    "[role=dialog]",
    "[class*=typography-body-button]",  # call-to-action button labels
)

# The site styles most headings with utility classes instead of <h*> tags.
HEADING_CLASS_LEVELS = (
    ("typography-title-display", 1),
    ("typography-title-heading", 2),
    ("typography-title-subhead", 3),
)

_STREAM_SWAP_RE = re.compile(r'\$RC\("(B:\d+)","(S:\d+)"\)')
_STEP_NUMBER_RE = re.compile(r"\d{1,2}")
_MIN_PREVIEW_CHARS = 30


@dataclass(frozen=True)
class Block:
    text: str
    heading_level: int | None = None
    """``None`` for body text, 1 (most important) … 4 for headings."""

    @property
    def is_heading(self) -> bool:
        return self.heading_level is not None


@dataclass
class ParsedHtml:
    title: str
    description: str | None
    lang: str | None
    breadcrumbs: list[str] = field(default_factory=list)
    blocks: list[Block] = field(default_factory=list)
    footer_blocks: list[Block] = field(default_factory=list)
    """Site-wide footer (contact details). Identical on every page."""


def parse_html(html: str) -> ParsedHtml:
    """Parse a full page into its title, metadata and content blocks."""
    soup = BeautifulSoup(html, "lxml")
    _decode_cf_emails(soup)
    _inline_streamed_segments(soup, html)

    breadcrumbs = _extract_breadcrumbs(soup)
    footer_blocks = _extract_footer(soup)
    root = _content_root(soup)
    _remove_non_content(root)

    blocks = _drop_truncated_previews(_dedupe(iter_blocks(root)))
    return ParsedHtml(
        title=_extract_title(soup, blocks),
        description=_meta_content(soup, "description"),
        lang=soup.html.get("lang") if soup.html else None,
        breadcrumbs=breadcrumbs,
        blocks=blocks,
        footer_blocks=footer_blocks,
    )


def html_fragment_to_text(fragment: str) -> str:
    """Convert a CMS rich-text fragment (e.g. an FAQ answer) to plain text."""
    if "<" not in fragment:  # plain or markdown-like text: keep its line structure
        lines = (normalize_text(line) for line in fragment.splitlines())
        return "\n".join(line for line in lines if line)
    soup = BeautifulSoup(fragment, "lxml")
    root = soup.body or soup
    return "\n".join(block.text for block in _dedupe(iter_blocks(root)))


def iter_blocks(node: Tag) -> Iterator[Block]:
    """Yield the text blocks below ``node`` in reading order.

    An element that contains no block-level descendants is treated as one
    block (its inline children — links, bold text … — are joined). Tables are
    flattened row by row as ``cell | cell | cell``.
    """
    for child in node.children:
        if isinstance(child, PreformattedString):  # comments, CDATA, doctype
            continue
        if isinstance(child, NavigableString):
            text = normalize_text(child)
            if not _is_noise(text):
                yield Block(text)
            continue
        if not isinstance(child, Tag):
            continue

        if child.name == "table":
            yield from _table_blocks(child)
        elif child.find(BLOCK_TAGS):
            yield from iter_blocks(child)
        else:
            text = normalize_text(child.get_text(" "))
            if _is_noise(text):
                continue
            if child.name == "li":
                text = f"- {text}"
            yield Block(text, _heading_level(child))


# --------------------------------------------------------------------------- #
# Internals
# --------------------------------------------------------------------------- #

def _decode_cf_emails(soup: BeautifulSoup) -> None:
    """Replace Cloudflare e-mail protection placeholders with the real address."""
    for node in soup.select("[data-cfemail]"):
        node.replace_with(decode_cf_email(node["data-cfemail"]))


def _inline_streamed_segments(soup: BeautifulSoup, html: str) -> None:
    """Move streamed content (``<div hidden id="S:n">``) into its placeholder.

    Next.js streams slow parts of the page at the end of the document and
    swaps them into ``<template id="B:n">`` placeholders with ``$RC(...)``.
    Doing the same swap keeps the content in its real reading order.
    """
    swaps = dict(_STREAM_SWAP_RE.findall(html))
    for placeholder_id, segment_id in swaps.items():
        placeholder = soup.find("template", id=placeholder_id)
        segment = soup.find("div", id=segment_id)
        if placeholder is None or segment is None:
            continue
        for child in list(segment.children):
            placeholder.insert_before(child.extract())
        placeholder.decompose()
        segment.decompose()


def _content_root(soup: BeautifulSoup) -> Tag:
    """The element that wraps the page content (the parent of the site header)."""
    header = soup.find("header")
    if header is not None and isinstance(header.parent, Tag):
        root = header.parent
    else:
        root = soup.body or soup

    # Streamed segments without a placeholder would otherwise be lost.
    for segment in soup.select("div[hidden][id^='S:']"):
        root.append(segment.extract())
    return root


def _remove_non_content(root: Tag) -> None:
    for node in root.find_all(NON_CONTENT_TAGS):
        node.decompose()
    for selector in NON_CONTENT_SELECTORS:
        for node in root.select(selector):
            node.decompose()


def _table_blocks(table: Tag) -> Iterator[Block]:
    for row in table.find_all("tr"):
        cells = [normalize_text(cell.get_text(" ")) for cell in row.find_all(["th", "td"])]
        cells = [cell for cell in cells if cell]
        if cells:
            yield Block(" | ".join(cells))


def _heading_level(tag: Tag) -> int | None:
    if tag.name in ("h1", "h2", "h3"):
        return int(tag.name[1])
    if tag.name in ("h4", "h5", "h6"):
        return 4
    classes = " ".join(tag.get("class", []))
    for class_prefix, level in HEADING_CLASS_LEVELS:
        if class_prefix in classes:
            return level
    return None


def _dedupe(blocks: Iterator[Block]) -> list[Block]:
    """Drop repeated blocks (the responsive mobile/desktop and carousel copies)."""
    seen: set[str] = set()
    unique: list[Block] = []
    for block in blocks:
        key = fingerprint(block.text)
        if key in seen:
            continue
        seen.add(key)
        unique.append(block)
    return unique


def _drop_truncated_previews(blocks: list[Block]) -> list[Block]:
    """Drop teasers like "ABB təşkilat..." whose full text is also on the page."""
    texts = [fingerprint(b.text) for b in blocks]

    def is_preview(i: int) -> bool:
        stem = texts[i].rstrip(".…").strip()
        return (
            texts[i].endswith(("...", "…"))
            and len(stem) >= _MIN_PREVIEW_CHARS
            and any(stem in other for j, other in enumerate(texts) if j != i)
        )

    return [block for i, block in enumerate(blocks) if not is_preview(i)]


def _is_noise(text: str) -> bool:
    """Empty text, separators like "•" and carousel step counters like "1", "2", "3"."""
    has_alnum = any(char.isalnum() for char in text)
    return not has_alnum or bool(_STEP_NUMBER_RE.fullmatch(text))


def _extract_breadcrumbs(soup: BeautifulSoup) -> list[str]:
    nav = soup.find("nav", attrs={"aria-label": "breadcrumb"})
    if nav is None:
        return []
    return [normalize_text(s) for s in nav.stripped_strings if not _is_noise(s)]


def _extract_footer(soup: BeautifulSoup) -> list[Block]:
    footer = soup.find("footer")
    if footer is None:
        return []
    _remove_non_content(footer)  # drops the footer's link menus
    return _dedupe(iter_blocks(footer))


def _extract_title(soup: BeautifulSoup, blocks: list[Block]) -> str:
    """The visible H1, else the first heading, else ``<title>``.

    ``<title>`` is the last resort: many pages only have a generic site title
    there ("ABB", "ABB - Müasir, Faydalı, Universal").
    """
    headings = [b for b in blocks if b.is_heading]
    h1 = next((b for b in headings if b.heading_level == 1), None)
    if h1 or headings:
        return (h1 or headings[0]).text
    title = soup.title.get_text() if soup.title else ""
    return normalize_text(title) or "ABB"


def _meta_content(soup: BeautifulSoup, name: str) -> str | None:
    tag = soup.find("meta", attrs={"name": name})
    content = normalize_text(tag.get("content", "")) if tag else ""
    return content or None
