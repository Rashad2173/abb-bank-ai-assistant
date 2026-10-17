"""Dashboard aggregates.

Computed in Python over the period's rows: simple, identical on PostgreSQL and
SQLite (tests), and fast for the volumes of a demo (tens of thousands of rows).
At larger scale these become SQL ``GROUP BY`` queries or a materialized view.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Sequence
from datetime import UTC, date, datetime, timedelta

from .db import Interaction
from .schemas import DayCount, LatencyStats, SourceCount, Stats

BAKU_OFFSET = timedelta(hours=4)
TOP_SOURCES = 10
REFUSED = "out_of_scope"


def compute_stats(rows: Sequence[Interaction], days: int, today: date) -> Stats:
    statuses = Counter(row.status for row in rows)
    per_day = {today - timedelta(days=offset): Counter() for offset in range(days - 1, -1, -1)}
    hours = [0] * 24
    sources: Counter[str] = Counter()
    titles: dict[str, str] = {}
    for row in rows:
        local = _baku(row.created_at)
        if local.date() in per_day:
            per_day[local.date()][row.status] += 1
        hours[local.hour] += 1
        for source in row.sources:
            sources[source["url"]] += 1
            titles[source["url"]] = source["title"]
    answered = [row for row in rows if row.status == "answered"]

    return Stats(
        period_days=days,
        total=len(rows),
        by_status=dict(statuses),
        by_refusal_reason=dict(Counter(row.refusal_reason for row in rows if row.status == REFUSED)),
        by_language=dict(Counter(row.language for row in rows)),
        per_day=[DayCount(date=day, total=sum(c.values()), answered=c["answered"], refused=c[REFUSED],
                          no_information=c["no_information"]) for day, c in per_day.items()],
        by_hour=hours,
        latency=_latency([row.total_ms for row in rows]),
        reranked_share=_share(sum(row.reranked for row in rows), len(rows)),
        grounded_share=_share(sum(row.grounded for row in answered), len(answered)),
        tokens={"input": sum(row.input_tokens for row in rows), "output": sum(row.output_tokens for row in rows)},
        top_sources=[SourceCount(url=url, title=titles[url], count=n) for url, n in sources.most_common(TOP_SOURCES)],
    )


def period_start(days: int, today: date) -> datetime:
    """UTC instant at which the period's first (Baku) day begins."""
    first_day = today - timedelta(days=days - 1)
    return datetime(first_day.year, first_day.month, first_day.day, tzinfo=UTC) - BAKU_OFFSET


def baku_today() -> date:
    return (datetime.now(UTC) + BAKU_OFFSET).date()


def _baku(moment: datetime) -> datetime:
    if moment.tzinfo is None:  # SQLite returns naive UTC
        moment = moment.replace(tzinfo=UTC)
    return moment.astimezone(UTC) + BAKU_OFFSET


def _latency(values: list[float]) -> LatencyStats:
    if not values:
        return LatencyStats(avg_ms=0, p50_ms=0, p95_ms=0)
    ordered = sorted(values)
    return LatencyStats(avg_ms=round(sum(ordered) / len(ordered), 1), p50_ms=_percentile(ordered, 0.50),
                        p95_ms=_percentile(ordered, 0.95))


def _percentile(ordered: list[float], q: float) -> float:
    return round(ordered[min(len(ordered) - 1, int(q * len(ordered)))], 1)


def _share(part: int, whole: int) -> float:
    return round(part / whole, 4) if whole else 0.0
