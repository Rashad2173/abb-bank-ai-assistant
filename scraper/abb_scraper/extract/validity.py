"""Is a campaign still running?

Campaign pages state their period ("07.05.2025 - 23.05.2025") and often a status
("Aktiv deyil", "Qeyd: Kampaniya müddəti bitmişdir.", "Кампания завершена",
"The campaign has ended"). An explicit status wins; otherwise the end date is
compared with the day the page was fetched.
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from datetime import date, datetime

from ..models import Validity

_PERIOD_RE = re.compile(r"(\d{2})\.(\d{2})\.(\d{4})\s*[-–—]\s*(\d{2})\.(\d{2})\.(\d{4})")
_ENDED_RE = re.compile(
    r"aktiv deyil|bitmişdir|bitib|başa çatıb|müddəti bitmiş"
    r"|неактивн|завершил|завершен|закончил"
    r"|not active|inactive|has (already |now )?ended|has expired|period has expired",
    re.IGNORECASE,
)
_ACTIVE_RE = re.compile(r"^(aktivdir|aktiv|активно|active)$", re.IGNORECASE)
_MAX_STATUS_LINE = 120
"""Status labels and notes are short lines; long paragraphs (the terms) are not searched."""


def campaign_validity(texts: Iterable[str], fetched_at: datetime) -> Validity:
    texts = list(texts)
    valid_from, valid_until = _first_period(texts)
    status_lines = [text.strip() for text in texts if len(text) <= _MAX_STATUS_LINE]

    if any(_ENDED_RE.search(line) for line in status_lines):
        is_active = False
    elif any(_ACTIVE_RE.match(line) for line in status_lines):
        is_active = True
    elif valid_until is not None:
        is_active = valid_until >= fetched_at.date()
    else:
        is_active = None
    return Validity(valid_from=valid_from, valid_until=valid_until, is_active=is_active)


def _first_period(texts: list[str]) -> tuple[date | None, date | None]:
    for text in texts:
        match = _PERIOD_RE.search(text)
        if match:
            d1, m1, y1, d2, m2, y2 = map(int, match.groups())
            try:
                return date(y1, m1, d1), date(y2, m2, d2)
            except ValueError:  # an impossible date typed into the CMS
                continue
    return None, None
