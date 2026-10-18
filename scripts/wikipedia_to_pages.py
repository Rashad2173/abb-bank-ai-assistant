"""Turn Wikipedia articles into upload files (the abb_pages.jsonl format).

    python scripts/wikipedia_to_pages.py "az:Azərbaycan Beynəlxalq Bankı" "en:International Bank of Azerbaijan" \
        --out data/wikipedia_abb.jsonl

Upload the result in the UI with "Add" (append) to add Wikipedia to the knowledge
base without removing the website data. Text comes from the MediaWiki API as
plain text; every "== Heading ==" becomes a section.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from urllib.parse import quote

import httpx

USER_AGENT = "abb-assistant-case-study/1.0 (https://github.com/Rashad2173/abb-bank-ai-assistant)"  # Wikimedia: identify + contact
_HEADING_RE = re.compile(r"^(=+)\s*(.*?)\s*\1\s*$")
_SKIPPED_SECTIONS = {"istinadlar", "xarici keçidlər", "həmçinin bax", "mənbə", "references", "external links",
                     "see also", "notes", "sources", "further reading"}


def fetch(lang: str, title: str) -> tuple[str, str]:
    """``(canonical title, plain text)`` of one article."""
    response = httpx.get(
        f"https://{lang}.wikipedia.org/w/api.php",
        params={"action": "query", "prop": "extracts", "explaintext": 1, "exsectionformat": "wiki",
                "redirects": 1, "titles": title, "format": "json", "formatversion": 2},
        headers={"User-Agent": USER_AGENT}, timeout=30,
    )
    response.raise_for_status()
    page = response.json()["query"]["pages"][0]
    if page.get("missing"):
        raise SystemExit(f"{lang}.wikipedia.org has no article {title!r}")
    return page["title"], page["extract"]


def to_page(lang: str, title: str, text: str) -> dict:
    sections: list[dict] = []
    path: list[str] = [title]
    paragraphs: list[str] = []
    skipping = False

    def flush() -> None:
        if paragraphs and not skipping:
            sections.append({"heading_path": list(path), "paragraphs": list(paragraphs)})
        paragraphs.clear()

    for line in text.splitlines():
        heading = _HEADING_RE.match(line)
        if heading:
            flush()
            level = len(heading.group(1)) - 1  # "==" is level 1 under the title
            path = path[:level] + [heading.group(2)]
            skipping = heading.group(2).strip().lower() in _SKIPPED_SECTIONS
        elif line.strip():
            paragraphs.append(line.strip())
    flush()
    return {
        "url": f"https://{lang}.wikipedia.org/wiki/{quote(title.replace(' ', '_'))}",
        "title": f"{title} — Wikipedia",
        "lang": lang,
        "category": "wikipedia",
        "sections": sections,
        "faq": [],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("articles", nargs="+", help='"lang:Title", e.g. "az:Azərbaycan Beynəlxalq Bankı"')
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    pages = []
    for article in args.articles:
        lang, _, title = article.partition(":")
        canonical, text = fetch(lang, title)
        page = to_page(lang, canonical, text)
        pages.append(page)
        words = sum(len(p.split()) for s in page["sections"] for p in s["paragraphs"])
        print(f"{lang}: {canonical} — {len(page['sections'])} sections, {words} words")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("".join(json.dumps(p, ensure_ascii=False) + "\n" for p in pages), encoding="utf-8")
    print(f"→ {args.out}")


if __name__ == "__main__":
    main()
