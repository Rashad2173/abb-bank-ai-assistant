"""Parser for the Next.js App Router "Flight" (RSC) payload.

abb-bank.az is a Next.js site. Besides the rendered HTML, every page embeds the
React Server Components payload in ``self.__next_f.push([1, "..."])`` scripts.
Some content is *only* present there — most importantly accordion/FAQ answers,
which are not rendered into the HTML until the user clicks them.

Flight payload format (one row per record)::

    <hex id>:<json>\n            -> a JSON value (React tree, props, CMS data)
    <hex id>:T<hex len>,<text>   -> a raw text chunk of <len> UTF-8 bytes
    <hex id>:I[...]\n            -> module import (ignored)
    <hex id>:HL[...]\n           -> resource hint (ignored)
"""

from __future__ import annotations

import json
import re
from collections.abc import Iterator
from typing import Any

_PUSH_RE = re.compile(r'self\.__next_f\.push\(\[1,("(?:[^"\\]|\\.)*")\]\)', re.S)
_ROW_TAG_RE = re.compile(r"[A-Z]*")


def extract_flight_payload(html: str) -> str:
    """Concatenate all Flight chunks embedded in the page's ``<script>`` tags."""
    return "".join(json.loads(chunk) for chunk in _PUSH_RE.findall(html))


def parse_flight_rows(payload: str) -> dict[str, Any]:
    """Split a Flight payload into ``{row_id: value}``.

    JSON rows are decoded, text rows (``T``) are kept as strings and all other
    row types (imports, hints, errors) are skipped. Text rows are length
    prefixed in *bytes*, so parsing is done on the UTF-8 encoded payload.
    """
    data = payload.encode("utf-8")
    rows: dict[str, Any] = {}
    pos = 0

    while pos < len(data):
        colon = data.find(b":", pos)
        if colon == -1:
            break
        row_id = data[pos:colon].decode().strip()
        pos = colon + 1

        if data[pos:pos + 1] == b"T":
            comma = data.find(b",", pos)
            length = int(data[pos + 1:comma], 16)
            start = comma + 1
            rows[row_id] = data[start:start + length].decode("utf-8", errors="replace")
            pos = start + length
            continue

        end = data.find(b"\n", pos)
        end = len(data) if end == -1 else end
        line = data[pos:end].decode("utf-8", errors="replace")
        pos = end + 1

        tag = _ROW_TAG_RE.match(line).group()
        if tag:
            continue
        try:
            rows[row_id] = json.loads(line)
        except json.JSONDecodeError:
            continue

    return rows


def iter_dicts(value: Any) -> Iterator[dict[str, Any]]:
    """Yield every dict nested anywhere inside ``value``, in document order."""
    stack = [value]
    while stack:
        item = stack.pop()
        if isinstance(item, dict):
            yield item
            stack.extend(reversed(list(item.values())))
        elif isinstance(item, list):
            stack.extend(reversed(item))


def extract_accordion_items(scope: Any, rows: dict[str, Any]) -> list[tuple[str, str]]:
    """Return ``(question, answer_html)`` pairs of the accordion/FAQ items in ``scope``.

    ``scope`` is the part of the payload to search (usually the page's CMS
    entity); ``rows`` are all payload rows, used to resolve references. In the
    CMS data an accordion item is ``{"id", "trigger", "content"}``. Long answers
    may be stored in a separate text row and referenced as ``"$<row id>"``.
    """
    items: list[tuple[str, str]] = []
    for node in iter_dicts(scope):
        question, answer = node.get("trigger"), node.get("content")
        if not (isinstance(question, str) and isinstance(answer, str)):
            continue
        item = (question, _resolve_reference(answer, rows))
        # The same question may have different answers (e.g. per insurance product).
        if question.strip() and item[1].strip() and item not in items:
            items.append(item)
    return items


def _resolve_reference(value: str, rows: dict[str, Any]) -> str:
    if value.startswith("$") and isinstance(rows.get(value[1:]), str):
        return rows[value[1:]]
    return value
