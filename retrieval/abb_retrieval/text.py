"""Text comparison helper.

Same rule as the scraper's fingerprint (kept separate so that the retrieval
package only depends on the scraper's *output*, not on its code).
"""

from __future__ import annotations

import re

_WHITESPACE_RE = re.compile(r"\s+")
# Azerbaijani dotted/dotless I: "İ".casefold() is "i̇" (i + combining dot), so all
# four variants are mapped to "i" before comparing.
_I_VARIANTS = str.maketrans({"İ": "i", "I": "i", "ı": "i"})


def fingerprint(text: str) -> str:
    """Key for comparing texts regardless of case and spacing."""
    return _WHITESPACE_RE.sub(" ", text).strip().translate(_I_VARIANTS).casefold()


# Azerbaijani letters people type without an Azerbaijani keyboard: "ə" as "e",
# "ı"/"İ" as "i". The other letters (ş, ç, ğ, ö, ü) are folded by the keyword
# index's own analyzer (asciifolding).
_LEXICAL_LETTERS = str.maketrans({"İ": "i", "I": "i", "ı": "i", "Ə": "e", "ə": "e"})


def lexical_form(text: str) -> str:
    """Text as the keyword (BM25) index sees it — applied to chunks and queries alike.

    Milvus' lowercase filter turns "İ" into "i̇" (i + combining dot) and its
    asciifolding turns "ə" into "a", so "KREDİT" would not match "kredit" and
    "odenis" would not match "ödəniş" without this step.
    """
    return text.translate(_LEXICAL_LETTERS)
