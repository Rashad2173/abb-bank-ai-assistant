"""Extract phase: cached HTML → ``abb_pages.jsonl`` + ``scrape_report.json``.

Steps
-----
1. Parse every cached page in parallel (see :func:`extract.page.extract_page`).
2. Order pages from most general to most specific URL (``/ferdi`` before
   ``/ferdi/kartlar/...``) — that order decides which page keeps a repeated
   block (see step 3).
3. Remove cross-page repetition: text blocks that appear on many pages
   (banners, promo teasers) and FAQ items shared between pages are kept **once**,
   on the first (most general) page that has them.
4. Group blocks into sections under their heading hierarchy, drop empty and
   duplicate pages.
5. Add the service network documents (branches, ATMs, terminals), write the
   output and a quality report.
"""

from __future__ import annotations

import hashlib
import json
import logging
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime
from functools import partial
from urllib.parse import urlsplit

from .config import ScraperConfig
from .discovery import category_of, cms_path, language_of
from .extract.html_content import Block
from .extract.page import PageContent, extract_page
from .extract.service_network import service_network_documents
from .extract.text import detect_language, fingerprint
from .models import FaqItem, FetchRecord, Language, Page, Section
from .storage import RawPageStore

log = logging.getLogger(__name__)

RepeatKey = tuple[str, str]
"""``(language, fingerprint)`` — repetition is counted per language."""


@dataclass
class _Draft:
    """A parsed page before cross-page cleanup."""

    record: FetchRecord
    lang: Language
    """Language of the text — not always the URL's language (see :func:`_drop_untranslated_copies`)."""
    content: PageContent

    @property
    def url(self) -> str:
        return self.record.final_url

    @property
    def sort_key(self) -> tuple[int, str]:
        return (urlsplit(self.url).path.count("/"), self.url)


@dataclass
class ExtractionReport:
    pages_written: int = 0
    skipped_empty: list[str] = field(default_factory=list)
    skipped_duplicate: dict[str, str] = field(default_factory=dict)
    skipped_untranslated: dict[str, str] = field(default_factory=dict)
    """EN/RU URLs whose text is an untranslated copy → the original page."""
    failed_fetches: list[str] = field(default_factory=list)
    boilerplate_blocks: list[str] = field(default_factory=list)
    without_cms_entity: list[str] = field(default_factory=list)
    """Pages whose CMS data was not found in the RSC payload (HTML-only extraction)."""


def run_extraction(config: ScraperConfig, store: RawPageStore) -> ExtractionReport:
    report = ExtractionReport()
    drafts = _parse_cached_pages(store, config, report)
    drafts = _drop_untranslated_copies(drafts, report)
    drafts.sort(key=lambda d: d.sort_key)

    frequent = _find_frequent_blocks(drafts, config)
    report.boilerplate_blocks = sorted(set(frequent.values()))

    pages = _assemble_pages(drafts, set(frequent), config, report)
    pages += _service_network_pages(config)
    _write_jsonl(pages, config)
    report.pages_written = len(pages)
    _write_report(pages, report, config)
    log.info("Wrote %d pages to %s", len(pages), config.pages_path)
    return report


# --------------------------------------------------------------------------- #
# Step 1 — parse
# --------------------------------------------------------------------------- #

def _parse_cached_pages(store: RawPageStore, config: ScraperConfig, report: ExtractionReport) -> list[_Draft]:
    records: dict[str, FetchRecord] = {}
    for record in store.records():
        if record.error or record.status != 200:
            if record.status != 404:
                report.failed_fetches.append(record.url)
        elif record.cache_file and record.final_url not in records:  # skip redirects to known pages
            records[record.final_url] = record

    parse = partial(_parse_record, store)
    if config.extract_workers > 1:
        with ProcessPoolExecutor(max_workers=config.extract_workers) as pool:
            drafts = list(pool.map(parse, records.values(), chunksize=32))
    else:
        drafts = [parse(record) for record in records.values()]

    report.without_cms_entity = [d.url for d in drafts if not d.content.has_cms_entity]
    log.info("Parsed %d cached pages", len(drafts))
    return drafts


def _parse_record(store: RawPageStore, record: FetchRecord) -> _Draft:
    lang = language_of(record.final_url)
    html = store.load_html(record.cache_file)
    return _Draft(record=record, lang=lang, content=extract_page(record.final_url, lang, html))


def _drop_untranslated_copies(drafts: list[_Draft], report: ExtractionReport) -> list[_Draft]:
    """Use the language of the *text*, and drop EN/RU pages that were never translated.

    E.g. ``/en/haqqimizda/satinalmalar/...`` shows the Azerbaijani tender text
    with only the date translated. When the original page exists it is kept
    and the copy dropped; otherwise the page stays, labelled with its real
    language.
    """
    paths_by_lang: dict[str, dict[str, str]] = defaultdict(dict)
    for draft in drafts:
        paths_by_lang[draft.lang].setdefault(cms_path(draft.url), draft.url)

    kept = []
    for draft in drafts:
        text_lang = detect_language(_body_text(draft.content)) or draft.lang
        original = paths_by_lang[text_lang].get(cms_path(draft.url))
        if text_lang != draft.lang and original:
            report.skipped_untranslated[draft.url] = original
            continue
        draft.lang = text_lang
        kept.append(draft)
    return kept


def _body_text(content: PageContent) -> str:
    text = " ".join(block.text for block in content.blocks if not block.is_heading)
    return text + " ".join(f"{item.question} {item.answer}" for item in content.faq)


# --------------------------------------------------------------------------- #
# Step 3 — cross-page repetition
# --------------------------------------------------------------------------- #

def _find_frequent_blocks(drafts: list[_Draft], config: ScraperConfig) -> dict[RepeatKey, str]:
    """Blocks that occur on many pages of the same language → ``{key: example text}``."""
    page_counts: Counter[RepeatKey] = Counter()
    example: dict[RepeatKey, str] = {}
    pages_per_lang: Counter[str] = Counter(d.lang for d in drafts)

    for draft in drafts:
        keys = {}
        for block in draft.content.blocks:
            keys.setdefault((draft.lang, fingerprint(block.text)), block.text)
        page_counts.update(keys.keys())
        for key, text in keys.items():
            example.setdefault(key, text)

    def threshold(lang: str) -> float:
        return max(config.boilerplate_min_pages, config.boilerplate_page_ratio * pages_per_lang[lang])

    return {key: example[key] for key, count in page_counts.items() if count >= threshold(key[0])}


class _KeepOnce:
    """Lets repeated content through only the first time it is seen."""

    def __init__(self) -> None:
        self._seen: set[RepeatKey] = set()

    def first_time(self, key: RepeatKey) -> bool:
        if key in self._seen:
            return False
        self._seen.add(key)
        return True


# --------------------------------------------------------------------------- #
# Step 4 — assemble
# --------------------------------------------------------------------------- #

def _assemble_pages(
    drafts: list[_Draft], frequent: set[RepeatKey], config: ScraperConfig, report: ExtractionReport
) -> list[Page]:
    keep_once = _KeepOnce()
    seen_content: dict[str, str] = {}
    pages: list[Page] = []

    for draft in drafts:
        content = draft.content
        blocks = [
            block for block in content.blocks
            if (key := (draft.lang, fingerprint(block.text))) not in frequent or keep_once.first_time(key)
        ]
        if _is_home_page(draft.url):
            blocks += _contact_blocks(content.footer_blocks)
        # Every FAQ repetition counts: shared FAQ lists would otherwise flood search results.
        faq = [
            item for item in content.faq
            if keep_once.first_time((draft.lang, fingerprint(f"{item.question}\n{item.answer}")))
        ]

        page = _make_page(
            url=draft.url,
            lang=draft.lang,
            category=category_of(draft.url),
            title=content.title,
            description=content.description,
            breadcrumbs=content.breadcrumbs,
            blocks=blocks,
            faq=faq,
            last_modified=draft.record.last_modified,
            fetched_at=draft.record.fetched_at,
        )
        if page.char_count < config.min_page_chars:
            report.skipped_empty.append(draft.url)
        elif page.content_hash in seen_content:
            report.skipped_duplicate[draft.url] = seen_content[page.content_hash]
        else:
            seen_content[page.content_hash] = draft.url
            pages.append(page)
    return pages


def _service_network_pages(config: ScraperConfig) -> list[Page]:
    """Branches, ATMs and terminals (fetched separately by :mod:`service_network`)."""
    if not config.service_network_path.exists():
        log.warning("No service network data at %s — run the crawl first", config.service_network_path)
        return []
    data = json.loads(config.service_network_path.read_text(encoding="utf-8"))
    fetched_at = datetime.fromisoformat(data["fetched_at"])
    return [
        _make_page(url=doc.url, lang="az", category="service_network", title=doc.title, description=None,
                   breadcrumbs=doc.breadcrumbs, blocks=doc.blocks, faq=[], last_modified=None,
                   fetched_at=fetched_at)
        for doc in service_network_documents(data)
    ]


def _make_page(*, blocks: list[Block], faq: list[FaqItem], **fields) -> Page:
    """Build a :class:`Page` from content blocks; adds sections, size and content hash."""
    sections = build_sections(blocks)
    text = "\n".join(p for s in sections for p in s.paragraphs)
    text += "".join(f"\n{item.question}\n{item.answer}" for item in faq)
    return Page(
        sections=sections,
        faq=faq,
        content_hash=hashlib.sha256(text.encode()).hexdigest()[:16],
        char_count=len(text),
        **fields,
    )


def _is_home_page(url: str) -> bool:
    return urlsplit(url).path.strip("/") in ("", "en", "ru")


def _contact_blocks(footer_blocks: list[Block]) -> list[Block]:
    """The footer (phone, e-mail, address …) as its own section of the home page."""
    if not footer_blocks:
        return []
    return [Block("ABB — contact information / əlaqə", heading_level=2), *footer_blocks]


def build_sections(blocks: list[Block]) -> list[Section]:
    """Group body blocks under the heading hierarchy that precedes them.

    A heading that gets no content of its own before the next heading of the
    same or a higher level is not a section title but a list item styled as a
    heading (e.g. the steps of "How to order": each step is an ``<h3>``). It
    becomes a paragraph of the enclosing section instead of being lost.
    """
    sections: list[Section] = []
    heading_stack: list[tuple[int, str]] = []
    top_is_empty = False  # the innermost heading has no content yet

    def add_paragraph(text: str) -> None:
        path = [heading for _, heading in heading_stack]
        if not sections or sections[-1].heading_path != path:
            sections.append(Section(heading_path=path))
        sections[-1].paragraphs.append(text)

    for block in blocks:
        if block.is_heading:
            if heading_stack and fingerprint(heading_stack[-1][1]) == fingerprint(block.text):
                continue  # e.g. a tab "Tariflər" directly inside a section "Tariflər"
            if top_is_empty and block.heading_level <= heading_stack[-1][0]:
                add_paragraph(heading_stack.pop()[1])
            while heading_stack and heading_stack[-1][0] >= block.heading_level:
                heading_stack.pop()
            heading_stack.append((block.heading_level, block.text))
            top_is_empty = True
        else:
            add_paragraph(block.text)
            top_is_empty = False

    if top_is_empty:
        add_paragraph(heading_stack.pop()[1])
    return sections


# --------------------------------------------------------------------------- #
# Output
# --------------------------------------------------------------------------- #

def _write_jsonl(pages: list[Page], config: ScraperConfig) -> None:
    config.pages_path.parent.mkdir(parents=True, exist_ok=True)
    with config.pages_path.open("w", encoding="utf-8") as fh:
        for page in pages:
            fh.write(page.model_dump_json() + "\n")


def _write_report(pages: list[Page], report: ExtractionReport, config: ScraperConfig) -> None:
    by_category: dict[str, Counter[str]] = defaultdict(Counter)
    for page in pages:
        by_category[page.lang][page.category] += 1

    summary = {
        "pages_written": report.pages_written,
        "total_chars": sum(p.char_count for p in pages),
        "faq_items": sum(len(p.faq) for p in pages),
        "pages_by_language": dict(Counter(p.lang for p in pages)),
        "pages_by_category": {lang: dict(c.most_common()) for lang, c in by_category.items()},
        "skipped_empty": len(report.skipped_empty),
        "skipped_duplicate": len(report.skipped_duplicate),
        "skipped_untranslated_copies": len(report.skipped_untranslated),
        "pages_without_cms_entity": len(report.without_cms_entity),
        "failed_fetches": report.failed_fetches,
        "boilerplate_blocks_kept_once": report.boilerplate_blocks,
        "skipped_empty_urls": report.skipped_empty,
        "skipped_duplicate_urls": report.skipped_duplicate,
        "skipped_untranslated_urls": report.skipped_untranslated,
        "without_cms_entity_urls": report.without_cms_entity,
    }
    config.report_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
