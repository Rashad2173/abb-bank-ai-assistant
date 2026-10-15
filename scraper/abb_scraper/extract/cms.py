"""Text of the page's CMS components, taken from the RSC payload.

abb-bank.az pages are built from CMS (Strapi) components stored in the page
entity's ``sections`` list. Much of that content never reaches the server
rendered HTML: inactive tabs (tariffs, conditions), card comparisons and whole
client-rendered sections. This module renders those components to
:class:`Block` objects.

The payload also contains the entities of the page's *parent* pages, so only
the entity whose ``url`` matches the page being extracted is used.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Iterator
from typing import Any

from .html_content import Block, html_fragment_to_text
from .rsc import iter_dicts
from .text import fingerprint, is_document_url

# Components that hold no textual content of their own (widgets, link lists,
# calculators, application forms, the app download banner).
EXCLUDED_COMPONENTS = frozenset({
    "tabs.loan-calculator", "tabs.deposit-calculator", "tabs.car-loan-calculator",
    "tabs.mortgage-calculator", "ui-sections.divider", "ui-sections.quick-links",
    "ui-sections.our-services", "ui-sections.relevant-now", "ui-sections.campaigns",
    "ui-sections.currency", "full-page.service-network", "ui-sections.app-banner",
})
EXCLUDED_COMPONENT_PREFIXES = ("forms.",)

# Sub-trees that are never content: media, buttons, SEO, translations, parents.
SKIPPED_KEYS = frozenset({
    "buttons", "button", "localizations", "seo", "parent", "image", "img", "images",
    "icon", "iconBefore", "iconAfter", "qr_image", "inner_image", "mobile_download_button",
    "download_links", "section_settings", "layout_data", "url", "spacing",
})
# Scalar fields that hold technical values, not text.
TECHNICAL_KEYS = frozenset({
    "__component", "id", "documentId", "createdAt", "updatedAt", "publishedAt", "locale",
    "slug", "link", "href", "provider", "layout", "variant", "size", "theme", "background",
    "bullet", "tableTheme", "tableVariant", "tagColor", "gtm_event_name", "aria_label",
    "name", "hash", "ext", "mime", "etag", "tab_query_parameter_key", "visa_reference_id",
    "mastercard_reference_id", "alternativeText", "caption", "pageRatingTheme",
})
HEADING_KEYS = ("title", "heading_before", "heading_gradient", "heading_after")
FAQ_KEYS = frozenset({"trigger", "content"})

# Identifiers such as "spacing-400", "gray-check", "aws-s3" and colours like "#0056C1".
# Pure numbers ("937", "2024") are content, so at least one letter is required.
_TECHNICAL_VALUE_RE = re.compile(r"(?=[a-z0-9_-]*[a-z])[a-z0-9_-]+|#[0-9a-fA-F]{3,8}")
_ROW_REFERENCE_RE = re.compile(r"\$([0-9a-f]+)")
_MAX_HEADING_LEVEL = 4


def find_page_entity(rows: dict[str, Any], path: str, lang: str) -> dict[str, Any] | None:
    """The CMS entity of the page at ``path`` (e.g. ``"ferdi/kartlar"``), if present."""
    path = path.strip("/")
    for node in iter_dicts(list(rows.values())):
        if (
            isinstance(node.get("sections"), list)
            and isinstance(node.get("url"), str)
            and node["url"].strip("/") == path
            and node.get("locale", lang) == lang
        ):
            return node
    return None


def component_blocks(entity: dict[str, Any], rows: dict[str, Any], html_texts: Iterable[str]) -> list[Block]:
    """Render the entity's components, skipping lines the page's HTML already shows.

    Content that is both rendered and in the payload therefore appears once.
    CMS items are *not* checked against each other: two cards may share a
    description or a "Credit limit: 30 000 AZN" row and each card must stay
    complete.
    """
    renderer = _Renderer(rows, KnownText(html_texts))
    blocks: list[Block] = []
    for component in entity["sections"]:
        if isinstance(component, dict) and _is_content_component(component):
            blocks.extend(renderer.render(component, level=2))
    return blocks


def _is_content_component(component: dict[str, Any]) -> bool:
    kind = component.get("__component", "")
    return kind not in EXCLUDED_COMPONENTS and not kind.startswith(EXCLUDED_COMPONENT_PREFIXES)


class KnownText:
    """Answers "does the page already contain this line?".

    Comparison ignores case, spacing and list markers ("1.", "-"), and a long
    line also counts as known when it is part of a longer HTML block — the CMS
    and the HTML often wrap the same sentences differently.
    """

    _LIST_MARKER_RE = re.compile(r"^(\d+[.)]|[-•*])\s+")
    _MIN_SUBSTRING_MATCH = 40  # shorter lines ("22%") would match by accident

    def __init__(self, texts: Iterable[str]) -> None:
        self._keys = {self._key(text) for text in texts}
        self._joined = "\n".join(self._keys)

    def __contains__(self, text: str) -> bool:
        key = self._key(text)
        return key in self._keys or (len(key) >= self._MIN_SUBSTRING_MATCH and key in self._joined)

    @classmethod
    def _key(cls, text: str) -> str:
        return cls._LIST_MARKER_RE.sub("", fingerprint(text))


class _Renderer:
    """Turns one component tree into heading and text blocks."""

    def __init__(self, rows: dict[str, Any], known: KnownText) -> None:
        self.rows = rows
        self.known = known

    def render(self, node: Any, level: int) -> Iterator[Block]:
        node = self._resolve(node)
        if isinstance(node, list):
            for item in node:
                yield from self.render(item, level)
            return
        if not isinstance(node, dict) or _is_media(node) or _is_faq_item(node):
            return

        if isinstance(node.get("trigger"), list):  # a tab: its title is an internal CMS name
            yield from self._render_tab(node, level)
            return

        heading = self._heading(node)
        if heading and (documents := _document_urls(node)):
            # e.g. a report list item: its title plus the PDF file it links to
            heading += " " + " ".join(f"({url})" for url in documents)
        fields = list(self._text_fields(node))
        child_blocks = [
            block
            for key, value in node.items()
            if key not in SKIPPED_KEYS and isinstance(self._resolve(value), (dict, list))
            for block in self.render(value, level + 1)
        ]

        # Children without text (e.g. only an image or a PDF file) do not make
        # the node a container — it is rendered like a leaf.
        if not child_blocks:
            yield from self._leaf_blocks(heading, fields, level)
            return

        if heading:
            yield Block(heading, min(level, _MAX_HEADING_LEVEL))
        for line in self._new_lines(fields):
            yield Block(line)
        yield from child_blocks

    def _render_tab(self, tab: dict[str, Any], level: int) -> Iterator[Block]:
        titles = [t.get("title") for t in tab["trigger"] if isinstance(t, dict)]
        heading = " / ".join(_clean(t) for t in titles if isinstance(t, str) and _clean(t))
        if heading:
            yield Block(heading, min(level, _MAX_HEADING_LEVEL))
        yield from self.render(tab.get("content", []), level + 1)

    def _leaf_blocks(self, heading: str | None, fields: list[str], level: int) -> Iterator[Block]:
        """A node without children, e.g. a tariff row or a card.

        * label + value → one line: ``"İllik faiz dərəcəsi: 22%"``
        * title + several values → the title becomes a heading for them
        * only a title → a plain line (list items such as product names)

        A leaf is kept as a whole unless *all* of its parts are already known,
        so a label never gets separated from its value.
        """
        lines = [line for field in fields for line in field.split("\n") if line]
        parts = [heading, *lines] if heading else lines
        if all(part in self.known for part in parts):
            return

        # A pair means two separate one-line fields — never two lines of one rich text.
        values = [heading, *fields] if heading else fields
        if len(values) == 2 and "\n" not in "".join(values) and len(values[0]) <= 80:
            yield Block(f"{values[0]}: {values[1]}")
            return
        if heading and lines:
            yield Block(heading, min(level, _MAX_HEADING_LEVEL))
            parts = lines
        for part in parts:
            yield Block(part)

    def _heading(self, node: dict[str, Any]) -> str | None:
        parts = [_clean(node[k]) for k in HEADING_KEYS if isinstance(node.get(k), str)]
        heading = " ".join(p for p in parts if p)
        return heading or None

    def _text_fields(self, node: dict[str, Any]) -> Iterator[str]:
        for key, value in node.items():
            if key in HEADING_KEYS or key in TECHNICAL_KEYS or key in SKIPPED_KEYS:
                continue
            value = self._resolve(value)
            if isinstance(value, str) and not _TECHNICAL_VALUE_RE.fullmatch(value.strip()):
                text = html_fragment_to_text(value)
                if text:
                    yield text

    def _new_lines(self, fields: Iterable[str]) -> Iterator[str]:
        """Lines of ``fields`` that the page does not contain yet."""
        for field in fields:
            for line in field.split("\n"):
                if line and line not in self.known:
                    yield line

    def _resolve(self, value: Any) -> Any:
        """Follow a ``"$<row id>"`` reference to the row it points to."""
        if isinstance(value, str):
            match = _ROW_REFERENCE_RE.fullmatch(value)
            if match and match.group(1) in self.rows:
                return self.rows[match.group(1)]
        return value


def _clean(text: str) -> str:
    return html_fragment_to_text(text)


def _is_media(node: dict[str, Any]) -> bool:
    return "mime" in node or "formats" in node


def _document_urls(node: dict[str, Any]) -> list[str]:
    """URLs of document files (PDF …) attached directly to the node."""
    urls = []
    for value in node.values():
        for item in value if isinstance(value, list) else [value]:
            if isinstance(item, dict) and _is_media(item) and is_document_url(str(item.get("url", ""))):
                urls.append(item["url"])
    return list(dict.fromkeys(urls))


def _is_faq_item(node: dict[str, Any]) -> bool:
    """FAQ items are extracted separately (see :func:`rsc.extract_accordion_items`)."""
    return FAQ_KEYS <= node.keys() and isinstance(node.get("trigger"), str)
