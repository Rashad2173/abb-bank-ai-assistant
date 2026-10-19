"""Data quality checks of the extracted corpus → ``evaluation/reports/00_data_quality.md``.

* **CMS coverage** — every text line (>= 20 characters) of each page's own CMS
  components must appear in the output: on the page itself or, for repeated
  content kept once, elsewhere in the same language.
* **Structure checks** — tables, campaign validity, linked documents, FAQ
  placement, service network grouping, unique URLs.
"""

from __future__ import annotations

import json
import random
import re
from collections import Counter
from pathlib import Path
from typing import Any

from .config import ScraperConfig
from .discovery import cms_path
from .extract.cms import _TECHNICAL_VALUE_RE, EXCLUDED_COMPONENTS, SKIPPED_KEYS, TECHNICAL_KEYS, find_page_entity
from .extract.html_content import html_fragment_to_text
from .extract.rsc import extract_flight_payload, parse_flight_rows
from .extract.text import fingerprint
from .storage import RawPageStore

_MIN_LINE = 20
_LIST_MARKER_RE = re.compile(r"^(\d+[.)]|[-•*])\s+")


def run_quality_checks(config: ScraperConfig, store: RawPageStore, report_path: Path) -> Path:
    pages = [json.loads(line) for line in config.pages_path.open(encoding="utf-8")]
    coverage = _cms_coverage(pages, store)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(_markdown(pages, coverage), encoding="utf-8")
    return report_path


# --------------------------------------------------------------------------- #
# CMS coverage
# --------------------------------------------------------------------------- #


def _cms_coverage(pages: list[dict], store: RawPageStore) -> dict[str, Any]:
    page_text = {p["url"]: _searchable(p) for p in pages}
    corpus = {}
    for p in pages:
        corpus.setdefault(p["lang"], []).append(page_text[p["url"]])
    corpus = {lang: "\n".join(texts) for lang, texts in corpus.items()}
    records = {r.final_url: r for r in store.records() if r.cache_file}

    checked = on_page = elsewhere = 0
    missing: list[tuple[str, str]] = []
    for page in pages:
        record = records.get(page["url"])
        if record is None:
            continue
        rows = parse_flight_rows(extract_flight_payload(store.load_html(record.cache_file)))
        entity = find_page_entity(rows, cms_path(page["url"]), page["lang"])
        if entity is None:
            continue
        for line in set(_cms_lines(entity["sections"])):
            key = _LIST_MARKER_RE.sub("", fingerprint(line))[:120]
            checked += 1
            if key in page_text[page["url"]]:
                on_page += 1
            elif key in corpus[page["lang"]]:
                elsewhere += 1
            else:
                missing.append((page["url"], line))
    return {"lines": checked, "on_page": on_page, "elsewhere": elsewhere, "missing": missing}


def _searchable(page: dict) -> str:
    parts = [page["title"]] + [h for s in page["sections"] for h in s["heading_path"]]
    parts += [p for s in page["sections"] for p in s["paragraphs"]]
    parts += [f"{f['question']} {f['answer']}" for f in page["faq"]]
    return fingerprint(" \n ".join(parts))


def _cms_lines(node: Any, component: str = "") -> list[str]:
    """Text lines of CMS components, with the same exclusions as the renderer."""
    lines: list[str] = []
    if isinstance(node, list):
        for item in node:
            lines += _cms_lines(item, component)
    elif isinstance(node, dict):
        component = node.get("__component", component)
        if "mime" in node or "formats" in node or component in EXCLUDED_COMPONENTS or component.startswith("forms."):
            return lines
        is_tab = isinstance(node.get("trigger"), list)
        for key, value in node.items():
            if key in SKIPPED_KEYS or key in TECHNICAL_KEYS or (is_tab and key == "title"):
                continue
            if isinstance(value, str):
                if not _TECHNICAL_VALUE_RE.fullmatch(value.strip()):
                    lines += [line for line in html_fragment_to_text(value).split("\n") if len(line) >= _MIN_LINE]
            else:
                lines += _cms_lines(value, component)
    return lines


# --------------------------------------------------------------------------- #
# Report
# --------------------------------------------------------------------------- #


def _markdown(pages: list[dict], coverage: dict[str, Any]) -> str:
    lines = ["# Data quality report", "", f"Corpus: `data/abb_pages.jsonl` — {len(pages):,} documents.", ""]

    total = coverage["lines"]
    lines += [
        "## 1. CMS coverage",
        "",
        "Every text line (≥ 20 characters) of each page's own CMS components looked up in the output. "
        "This measures *presence* of the text, not semantic correctness (table relations, conditions "
        "staying with their lists) — those are covered by the structure checks below and by manual review. "
        "PDF contents are out of scope; documents are kept as links.",
        "",
        "| | Lines | Share |",
        "|---|---:|---:|",
        f"| Checked | {total:,} | |",
        f"| On the page itself | {coverage['on_page']:,} | {_pct(coverage['on_page'], total)} |",
        f"| Kept once on a more general page | {coverage['elsewhere']:,} | {_pct(coverage['elsewhere'], total)} |",
        f"| **Missing** | **{len(coverage['missing'])}** | **{_pct(len(coverage['missing']), total)}** |",
        "",
    ]
    lines += [f"- {url} — {text[:120]}" for url, text in coverage["missing"][:20]]

    table_rows = [
        p
        for page in pages
        for s in page["sections"]
        for p in s["paragraphs"]
        if "; " in p and ": " in p and p.count(": ") >= 2
    ]
    sample = next(
        (
            p
            for page in pages
            if page["url"].endswith("/ferdi/emanetler/digideposit")
            for s in page["sections"]
            for p in s["paragraphs"]
            if p.startswith("Müddət: 1 ay")
        ),
        "–",
    )
    lines += [
        "## 2. Tables",
        "",
        f"Rows written as labelled values (`Column: value; …`): {len(table_rows):,}. "
        "Empty cells are kept as `–` so values cannot shift columns.",
        "",
        f"DigiDeposit, 1 month (AZN): `{sample}`",
        "",
    ]

    campaigns = [p for p in pages if p["category"] == "campaigns"]
    status = Counter(
        {True: "active", False: "ended", None: "unknown"}[(p.get("validity") or {}).get("is_active")] for p in campaigns
    )
    lines += [
        "## 3. Campaign validity",
        "",
        f"{len(campaigns)} campaign pages: " + ", ".join(f"{k} {v}" for k, v in status.most_common()) + ".",
        "",
        "| Active campaigns (sample) | Period |",
        "|---|---|",
    ]
    active = [p for p in campaigns if (p.get("validity") or {}).get("is_active")]
    for page in active[:10]:
        v = page["validity"]
        lines.append(f"| {page['title']} | {v.get('valid_from') or '?'} – {v.get('valid_until') or '?'} |")

    documents = [d for p in pages for d in p.get("documents", [])]
    unique = {d["url"] for d in documents}
    lines += [
        "",
        "## 4. Linked documents (PDF …)",
        "",
        f"{len(unique):,} unique documents linked from {sum(bool(p.get('documents')) for p in pages):,} pages; "
        "links are kept inline in the text, e.g.:",
        "",
    ]
    rng = random.Random(1)
    lines += [f"- {d['title']} — <{d['url']}>" for d in rng.sample(documents, min(5, len(documents)))]

    faq = [f for p in pages for f in p["faq"]]
    by_url = {p["url"]: p for p in pages}
    black_edition = by_url.get(
        "https://abb-bank.az/ferdi/kartlar/debet-kartlari/azal-miles-visa-platinum-mc-black-edition"
    )
    lines += [
        "",
        "## 5. FAQ placement",
        "",
        f"{len(faq):,} FAQ items. Items on up to 3 pages stay on each page (product context); "
        f"{sum(bool(f.get('also_on')) for f in faq)} widely repeated items are kept once and list the "
        "other pages in `also_on`.",
        "",
        f"AZAL Miles Black Edition card page: {len(black_edition['faq']) if black_edition else '–'} FAQ items.",
        "",
    ]

    network = [p for p in pages if p["category"] == "service_network"]
    atm_cities = [p["title"].split(" — ", 1)[1] for p in network if "bankomatları" in p["title"]]
    lines += [
        "## 6. Service network",
        "",
        f"{len(network)} documents; ATMs grouped into {len(atm_cities)} cities "
        f"(e.g. {', '.join(atm_cities[:8])}); branch documents carry coordinates: "
        f"{sum(p.get('coordinates') is not None for p in network)}.",
        "",
    ]

    urls = Counter(p["url"] for p in pages)
    generic = sum(p["title"] in ("ABB", "ABB - Müasir, Faydalı, Universal") for p in pages)
    lines += [
        "## 7. Consistency",
        "",
        f"- Duplicate URLs: {sum(n > 1 for n in urls.values())}",
        f"- Pages with a generic site title instead of their own: {generic}",
        f"- Documents by language: {dict(Counter(p['lang'] for p in pages))}",
        f"- Documents by category: {dict(Counter(p['category'] for p in pages).most_common())}",
        "",
    ]
    return "\n".join(lines) + "\n"


def _pct(part: int, total: int) -> str:
    return f"{100 * part / total:.2f}%" if total else "–"
