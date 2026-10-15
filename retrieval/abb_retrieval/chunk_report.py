"""Human-readable quality report of the chunks (Markdown + CSV for spreadsheets)."""

from __future__ import annotations

import csv
import random
from collections import Counter
from pathlib import Path

from .config import ChunkingConfig
from .models import Chunk

_BUCKETS = (0, 50, 100, 200, 300, 400, 512, 10_000)
_SAMPLE_SEED = 42


def write_chunk_report(chunks: list[Chunk], config: ChunkingConfig, markdown_path: Path, csv_path: Path) -> None:
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.write_text(_markdown(chunks, config), encoding="utf-8")
    with csv_path.open("w", encoding="utf-8-sig", newline="") as fh:  # BOM: Excel opens UTF-8 correctly
        writer = csv.writer(fh)
        writer.writerow(["chunk_id", "url", "lang", "category", "chunk_type", "token_count", "title",
                         "heading_path", "text"])
        for c in chunks:
            writer.writerow([c.chunk_id, c.url, c.lang, c.category, c.chunk_type, c.token_count, c.title,
                             " > ".join(c.heading_path), c.text])


def _markdown(chunks: list[Chunk], config: ChunkingConfig) -> str:
    tokens = sorted(c.token_count for c in chunks)
    over_limit = [c for c in chunks if c.token_count > config.max_tokens]
    rng = random.Random(_SAMPLE_SEED)
    by_page = Counter(c.url for c in chunks)

    lines = [
        "# Chunk quality report",
        "",
        f"Settings: target {config.target_tokens} tokens, max {config.max_tokens}, "
        f"overlap {config.overlap_paragraphs} paragraph(s), tokenizer `{config.tokenizer}`.",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Chunks | {len(chunks)} |",
        f"| Source pages | {len(by_page)} |",
        f"| By type | {_counts(c.chunk_type for c in chunks)} |",
        f"| By language | {_counts(c.lang for c in chunks)} |",
        f"| Tokens p10 / p50 / p90 / p99 / max | {' / '.join(str(_pct(tokens, p)) for p in (10, 50, 90, 99))}"
        f" / {tokens[-1]} |",
        f"| Total tokens | {sum(tokens):,} |",
        f"| Over the {config.max_tokens}-token limit | {len(over_limit)} |",
        f"| Pages split into more than 10 chunks | {sum(n > 10 for n in by_page.values())} |",
        "",
        "## By category",
        "",
        "| Category | Chunks | Median tokens |",
        "|----------|-------:|--------------:|",
    ]
    for category, count in Counter(c.category for c in chunks).most_common():
        cat_tokens = sorted(c.token_count for c in chunks if c.category == category)
        lines.append(f"| {category} | {count} | {_pct(cat_tokens, 50)} |")

    lines += ["", "## Token distribution", "", "| Tokens | Chunks | |", "|--------|-------:|---|"]
    for low, high in zip(_BUCKETS, _BUCKETS[1:]):
        n = sum(low <= t < high for t in tokens)
        lines.append(f"| {low}–{high - 1 if high < 10_000 else '…'} | {n} | {'█' * round(40 * n / len(tokens))} |")

    lines += _samples("Random samples", rng.sample(chunks, min(15, len(chunks))))
    lines += _samples("One sample per category",
                      [rng.choice([c for c in chunks if c.category == cat])
                       for cat in sorted({c.category for c in chunks})])
    lines += _samples("Smallest chunks", sorted(chunks, key=lambda c: c.token_count)[:5])
    lines += _samples("Largest chunks", sorted(chunks, key=lambda c: -c.token_count)[:3])
    return "\n".join(lines) + "\n"


def _samples(title: str, chunks: list[Chunk]) -> list[str]:
    lines = ["", f"## {title}", ""]
    for c in chunks:
        lines += [
            f"### `{c.chunk_id}` — {c.chunk_type}, {c.lang}, {c.category}, {c.token_count} tokens",
            "",
            f"<{c.url}>",
            "",
            "```text",
            c.text,
            "```",
            "",
        ]
    return lines


def _counts(values) -> str:
    return ", ".join(f"{key}: {n}" for key, n in Counter(values).most_common())


def _pct(sorted_values: list[int], percentile: int) -> int:
    return sorted_values[min(len(sorted_values) - 1, len(sorted_values) * percentile // 100)]
