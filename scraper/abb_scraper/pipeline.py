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
import re
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime
from functools import partial
from urllib.parse import urlsplit

from .config import ScraperConfig
from .discovery import category_of, cms_path, language_of
from .extract.dates import published_date
from .extract.html_content import Block
from .extract.page import PageContent, extract_page
from .extract.service_network import service_network_documents
from .extract.text import detect_language, fingerprint
from .extract.validity import campaign_validity
from .models import FaqItem, FetchRecord, Language, Page, Section
from .storage import RawPageStore

log = logging.getLogger(__name__)

RepeatKey = tuple[str, str]
"""``(language, fingerprint)`` — repetition is counted per language."""

_MIN_WORDS_OF_BOILERPLATE = 4
"""Shorter blocks are labels ("Məbləğ"), which belong next to each page's own values."""
_MIN_WORDS_OF_A_STATEMENT = 3
"""A lone heading without content is kept as text only from this length on."""
_CONTACT_LINE_RE = re.compile(r"^[^:]{2,30}:\s*\S")
_DATED_CATEGORIES = frozenset({"news", "press_releases", "csr", "procurement"})


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

    for draft in drafts:
        if category_of(draft.url) in config.boilerplate_exempt_categories:
            continue
        keys = {}
        for block in draft.content.blocks:
            if _can_be_boilerplate(block):
                keys.setdefault((draft.lang, fingerprint(block.text)), block.text)
        page_counts.update(keys.keys())
        for key, text in keys.items():
            example.setdefault(key, text)

    return {key: example[key] for key, count in page_counts.items() if count >= config.boilerplate_min_pages}


def _can_be_boilerplate(block: Block) -> bool:
    """Only sentence-like body text (banners, legal boilerplate) is de-duplicated across pages.

    Headings ("Tariflər") and short labels ("Məbləğ", "Faiz dərəcəsi") repeat on
    every product page too, but each time next to that page's own values —
    removing them would leave "70 000 AZN-dək" without saying what it is.
    """
    return not block.is_heading and len(block.text.split()) >= _MIN_WORDS_OF_BOILERPLATE


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


def _faq_key(lang: str, item: FaqItem) -> RepeatKey:
    return (lang, fingerprint(f"{item.question}\n{item.answer}"))


def _pages_per_faq_item(drafts: list[_Draft]) -> dict[RepeatKey, list[str]]:
    """Every FAQ item → the pages showing it, most general page first."""
    pages: dict[RepeatKey, list[str]] = defaultdict(list)
    for draft in drafts:
        for key in dict.fromkeys(_faq_key(draft.lang, item) for item in draft.content.faq):
            pages[key].append(draft.url)
    return pages


def _faq_for_page(draft: _Draft, faq_pages: dict[RepeatKey, list[str]], config: ScraperConfig) -> list[FaqItem]:
    """FAQ items shown on a few product pages stay on each of them (they describe those
    products); items repeated across many pages are kept once, on the most general
    page, and remember the other pages in ``also_on``."""
    kept = []
    for item in draft.content.faq:
        urls = faq_pages[_faq_key(draft.lang, item)]
        if len(urls) <= config.faq_max_shared_pages:
            kept.append(item)
        elif urls[0] == draft.url:
            kept.append(item.model_copy(update={"also_on": urls[1:]}))
    return kept


def _assemble_pages(
    drafts: list[_Draft], frequent: set[RepeatKey], config: ScraperConfig, report: ExtractionReport
) -> list[Page]:
    keep_once = _KeepOnce()
    faq_pages = _pages_per_faq_item(drafts)
    seen_content: dict[str, str] = {}
    pages: list[Page] = []

    for draft in drafts:
        content = draft.content
        category = category_of(draft.url)
        if category in config.boilerplate_exempt_categories:
            blocks = list(content.blocks)
        else:
            blocks = [
                block
                for block in content.blocks
                if (key := (draft.lang, fingerprint(block.text))) not in frequent or keep_once.first_time(key)
            ]
        if _is_home_page(draft.url):
            blocks += _contact_blocks(content.footer_blocks)

        page = _make_page(
            url=draft.url,
            lang=draft.lang,
            category=category,
            title=content.title,
            description=content.description,
            breadcrumbs=content.breadcrumbs,
            blocks=blocks,
            faq=_faq_for_page(draft, faq_pages, config),
            documents=content.documents,
            validity=(
                campaign_validity([b.text for b in content.blocks], draft.record.fetched_at)
                if category == "campaigns"
                else None
            ),
            published=published_date(b.text for b in content.blocks) if category in _DATED_CATEGORIES else None,
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
        _make_page(
            url=doc.url,
            lang="az",
            category="service_network",
            title=doc.title,
            description=None,
            breadcrumbs=doc.breadcrumbs,
            blocks=doc.blocks,
            faq=[],
            coordinates=doc.coordinates,
            last_modified=None,
            fetched_at=fetched_at,
        )
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
    """The footer's contact lines ("Tel: …", "E-poçt: …", "Ünvan: …") as a section of the home page.

    The rest of the footer is link menus and app-store teasers.
    """
    contacts = [b for b in footer_blocks if _CONTACT_LINE_RE.match(b.text)]
    if not contacts:
        return []
    return [Block("ABB — contact information / əlaqə", heading_level=2), *contacts]


def build_sections(blocks: list[Block]) -> list[Section]:
    """Group body blocks under the heading hierarchy that precedes them.

    Headings that get no content of their own:

    * a **run of two or more sibling** empty headings is a list styled as
      headings (the steps of "How to order" are ``<h3>`` each) — they become
      paragraphs of the enclosing section;
    * a **single** empty heading of one or two words is a widget label (a tab
      "Detallar" whose content went to the FAQ, an "ABB mobile" banner title
      whose text was kept on another page) — it is dropped; a longer one is a
      statement ("Pul köçürməsi həqiqətən sürətlidir") and is kept.
    """
    sections: list[Section] = []
    stack: list[tuple[int, str]] = []
    top_is_empty = False  # the innermost heading has no content yet
    empty_siblings: list[str] = []  # empty headings directly before the current one, same level

    def add_paragraph(text: str, path: list[str]) -> None:
        if not sections or sections[-1].heading_path != path:
            sections.append(Section(heading_path=path))
        sections[-1].paragraphs.append(text)

    def settle_empty_siblings(path: list[str]) -> None:
        is_list = len(empty_siblings) >= 2
        for text in empty_siblings:
            if is_list or len(text.split()) >= _MIN_WORDS_OF_A_STATEMENT:
                add_paragraph(text, path)
        empty_siblings.clear()

    def path(entries: list[tuple[int, str]]) -> list[str]:
        return [heading for _, heading in entries]

    for block in blocks:
        if not block.is_heading:
            if top_is_empty:  # the current heading is a real one; its empty siblings before it are settled
                settle_empty_siblings(path(stack[:-1]))
            add_paragraph(block.text, path(stack))
            top_is_empty = False
            continue

        if stack and fingerprint(stack[-1][1]) == fingerprint(block.text):
            continue  # e.g. a tab "Tariflər" directly inside a section "Tariflər"
        if top_is_empty:
            level = stack[-1][0]
            if block.heading_level > level:  # the empty heading turns out to be a parent
                settle_empty_siblings(path(stack[:-1]))
            else:  # it stays empty: one more in the run
                empty_siblings.append(stack.pop()[1])
                if block.heading_level < level:  # the run of siblings ends here
                    settle_empty_siblings(path(stack))
        while stack and stack[-1][0] >= block.heading_level:
            stack.pop()
        stack.append((block.heading_level, block.text))
        top_is_empty = True

    if top_is_empty:
        empty_siblings.append(stack.pop()[1])
    settle_empty_siblings(path(stack))
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
