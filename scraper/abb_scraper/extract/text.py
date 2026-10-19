"""Text normalization helpers (with Azerbaijani-specific fixes)."""

from __future__ import annotations

import html
import re
import unicodedata

# Look-alike characters that CMS editors paste instead of the Azerbaijani schwa.
# Without this, "Əmanət" and "Әmanət" would be different words for search.
_SCHWA_LOOKALIKES = str.maketrans(
    {
        "ә": "ə",  # Cyrillic small schwa  ә
        "Ә": "Ə",  # Cyrillic capital schwa Ә
        "ǝ": "ə",  # Latin small turned e  ǝ
        "Ǝ": "Ə",  # Latin capital reversed E Ǝ
    }
)

_INVISIBLE_RE = re.compile("[​‌‍⁠﻿­]")
_WHITESPACE_RE = re.compile(r"\s+")
_MARKDOWN_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")
_MARKDOWN_EMPHASIS_RE = re.compile(r"(\*\*|__)(.+?)\1")
_DOCUMENT_URL_RE = re.compile(r"^https?://\S+\.(pdf|docx?|xlsx?|pptx?)(\?\S*)?$", re.IGNORECASE)


def normalize_text(text: str) -> str:
    """Return ``text`` in canonical form: NFC, fixed schwa, single spaces.

    HTML entities are decoded as well — some CMS texts are escaped twice
    (``&amp;uuml;``), so they still contain ``&uuml;`` after HTML parsing.
    Markdown emphasis (``**Yükləyin**``) is removed; markdown links keep only
    their text, except links to documents (tariff PDFs …), which keep the URL:
    ``Yüklə (https://…/tarif.pdf)``.
    """
    text = unicodedata.normalize("NFC", html.unescape(text))
    text = text.translate(_SCHWA_LOOKALIKES)
    text = _INVISIBLE_RE.sub("", text)
    text = _MARKDOWN_EMPHASIS_RE.sub(r"\2", text)
    text = _MARKDOWN_LINK_RE.sub(_render_markdown_link, text)
    return _WHITESPACE_RE.sub(" ", text).strip()


_PLACEHOLDER_RE = re.compile(
    r"^(dummy|test(\s+test)*|lorem ipsum.*)$|bura\s+m[eə]tn\s+yaz[ıi]lmal[ıi]d[ıi]r",
    re.IGNORECASE,
)


def is_placeholder(text: str) -> bool:
    """Text an editor left in the CMS instead of content ("dummy", "test test",
    "Bura mətn yazılmalıdır" = "text goes here")."""
    return bool(_PLACEHOLDER_RE.search(normalize_text(text)))


def is_document_url(url: str) -> bool:
    return bool(_DOCUMENT_URL_RE.match(url.strip()))


def _render_markdown_link(match: re.Match) -> str:
    label, url = match.groups()
    return f"{label} ({url})" if is_document_url(url) else label


# Azerbaijani has dotted/dotless I (İ/i, I/ı); plain casefold() turns "İ" into
# "i̇" (i + combining dot). For comparison purposes all four become "i".
_I_VARIANTS = str.maketrans({"İ": "i", "I": "i", "ı": "i"})


def fingerprint(text: str) -> str:
    """Key used to detect duplicate blocks regardless of case or spacing."""
    return normalize_text(text).translate(_I_VARIANTS).casefold()


_AZERBAIJANI_LETTERS = frozenset("əƏğĞıİşŞçÇöÖüÜ")
_MIN_LETTERS_FOR_DETECTION = 80
_CYRILLIC_SHARE = 0.4
_AZERBAIJANI_SHARE = 0.025
"""ə alone is ~5–8 % of the letters of Azerbaijani text and ~0 % of English text."""


def detect_language(text: str) -> str | None:
    """Language of ``text`` (``"az"``, ``"en"`` or ``"ru"``) from its letters.

    The site has many EN/RU pages whose text was never translated; this tells
    them apart. Returns ``None`` when there is too little text to decide.
    """
    letters = [char for char in text if char.isalpha()]
    if len(letters) < _MIN_LETTERS_FOR_DETECTION:
        return None
    cyrillic = sum("Ѐ" <= char <= "ӿ" for char in letters) / len(letters)
    if cyrillic >= _CYRILLIC_SHARE:
        return "ru"
    azerbaijani = sum(char in _AZERBAIJANI_LETTERS for char in letters) / len(letters)
    return "az" if azerbaijani >= _AZERBAIJANI_SHARE else "en"


def decode_cf_email(encoded: str) -> str:
    """Decode a Cloudflare-obfuscated e-mail (``data-cfemail`` attribute).

    The first byte is an XOR key that is applied to every following byte.
    """
    key = int(encoded[:2], 16)
    return "".join(chr(int(encoded[i : i + 2], 16) ^ key) for i in range(2, len(encoded), 2))
