"""Publication date of news-like pages ("16 İyul, 2024", "15 апреля, 2024", "15 April, 2021").

News and press releases describe offers that may be long over; the date lets
search filters and the answer generator tell old offers from current ones.
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from datetime import date

_MONTHS = {
    # Azerbaijani
    "yanvar": 1,
    "fevral": 2,
    "mart": 3,
    "aprel": 4,
    "may": 5,
    "iyun": 6,
    "iyul": 7,
    "avqust": 8,
    "sentyabr": 9,
    "oktyabr": 10,
    "noyabr": 11,
    "dekabr": 12,
    # English
    "january": 1,
    "february": 2,
    "march": 3,
    "april": 4,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12,
    # Russian (genitive, as used in dates)
    "января": 1,
    "февраля": 2,
    "марта": 3,
    "апреля": 4,
    "мая": 5,
    "июня": 6,
    "июля": 7,
    "августа": 8,
    "сентября": 9,
    "октября": 10,
    "ноября": 11,
    "декабря": 12,
}
_DATE_RE = re.compile(r"^(\d{1,2})\s+([^\W\d_]+),?\s+(\d{4})$")
_I_VARIANTS = str.maketrans({"İ": "i", "I": "i", "ı": "i"})
_MAX_DATE_LINE = 25


def published_date(texts: Iterable[str]) -> date | None:
    """The first line of the page that is just a date."""
    for text in texts:
        if len(text) > _MAX_DATE_LINE:
            continue
        match = _DATE_RE.match(text.strip())
        if match:
            day, month_name, year = match.groups()
            month = _MONTHS.get(month_name.translate(_I_VARIANTS).lower())
            if month:
                try:
                    return date(int(year), month, int(day))
                except ValueError:
                    continue
    return None
