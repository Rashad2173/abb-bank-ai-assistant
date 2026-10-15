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
