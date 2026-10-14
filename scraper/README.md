# ABB website scraper

Extracts the textual content of [abb-bank.az](https://abb-bank.az) in all three
languages (AZ / EN / RU) into a clean, structured JSONL file that the chat
application ingests.

```bash
pip install -r scraper/requirements.txt
cd scraper
python -m abb_scraper run        # crawl + extract
```

| Command | What it does |
|---------|--------------|
| `python -m abb_scraper crawl` | Discovers all pages and downloads them into `data/raw/` (resumable), then the service network |
| `python -m abb_scraper network` | Only (re-)downloads the service network: branches, ATMs, terminals |
| `python -m abb_scraper extract` | Builds `data/abb_pages.jsonl` and `data/scrape_report.json` from the cache |
| `python -m abb_scraper run` | Crawl + extract |

Options: `--max-pages N` (trial run), `--concurrency N` (parallel requests,
default 6), `--workers N` (extraction processes), `--no-follow-links`,
`--data-dir PATH`.

## How the site is built — and why that matters

The scraper design follows from what the site analysis showed:

| Finding | Consequence |
|---------|-------------|
| Next.js App Router site; pages are server-rendered | Plain HTTP + HTML parsing works; no headless browser needed (fast, light) |
| Slow parts are **streamed**: `<template id="B:n">` placeholders are filled from `<div hidden id="S:n">` at the end of the document | The swap is replayed so text keeps its real reading order |
| Every block is rendered twice (mobile + desktop variants), carousels repeat slides | Repeated blocks within a page are removed |
| **Accordion/FAQ answers, inactive tabs (tariffs, interest-rate tables, card comparisons) and some whole sections are not in the HTML at all** — they only exist in the React Server Components (RSC) payload as CMS data | The RSC payload is parsed and the page's CMS components are rendered to text |
| The RSC payload also embeds the *parent* pages' CMS data | Only the CMS entity whose `url` equals the page's path is used |
| Banners, promo teasers and FAQ lists repeat across dozens of pages | Repeated content is kept **once**, on the most general page (prevents duplicate chunks in the vector DB) |
| E-mail addresses are obfuscated by Cloudflare | Decoded (`data-cfemail`) |
| CMS editors paste look-alike characters (Cyrillic `ә` instead of `ə`) | Normalized, so search treats them as the same word |
| The sitemap is large (~7k URLs) but not complete | Links found on pages are crawled as well |
| Many EN/RU pages were never translated (≈3 000 tenders, news, campaigns show the Azerbaijani text) | The text's real language is detected; a copy is dropped when the original exists |
| Branch/ATM locator pages are empty in the HTML — the browser loads the data via **Next.js Server Actions** and a REST API | The scraper calls the same endpoints; action ids are looked up by name in the site's JavaScript (they change with every deployment) |
| Some list items are styled as headings without text below them (steps of "how to order") | They are kept as list items instead of being dropped as empty sections |

## Pipeline

```
crawl                                     extract
─────                                     ───────
sitemap.xml ─┐                            cached HTML ──► per page (parallel):
             ├─► queue ─► fetch (retry) ─►  data/raw/      • HTML content     (html_content.py)
page links ──┘             │                               • CMS components   (cms.py, rsc.py)
                           └─► new links                   • FAQ items        (rsc.py)
                                                         ──► cross-page de-duplication
                                                         ──► sections by heading hierarchy
                                                         ──► abb_pages.jsonl + scrape_report.json
```

Crawl and extract are separate phases: extraction rules can be changed and
re-run in seconds against the cache without downloading the site again.

### Modules (`abb_scraper/`)

| Module | Responsibility |
|--------|----------------|
| `config.py` | All settings in one dataclass |
| `models.py` | Pydantic models: `FetchRecord`, `Page`, `Section`, `FaqItem` |
| `discovery.py` | Sitemap parsing, link extraction, URL normalization, language/category |
| `crawler.py` | Async crawler: concurrency limit, retries with back-off, resume |
| `service_network.py` | Branches, sub-branches, offices abroad (Server Actions), ATMs and terminals (REST API) |
| `http.py` | Shared HTTP client and retry policy |
| `storage.py` | Gzip cache of raw pages + append-only crawl manifest |
| `extract/html_content.py` | HTML → ordered heading/text blocks |
| `extract/rsc.py` | Next.js Flight (RSC) payload parser, FAQ items |
| `extract/cms.py` | The page's CMS components → text blocks |
| `extract/page.py` | Combines HTML, CMS and FAQ for one page |
| `extract/service_network.py` | Service network data → one document per branch, ATMs/terminals per city, overview |
| `extract/text.py` | Normalization (Azerbaijani-aware), fingerprints, language detection |
| `pipeline.py` | Extract phase orchestration, de-duplication, output |

## Output

`data/abb_pages.jsonl` — one page per line:

```json
{
  "url": "https://abb-bank.az/ferdi/kartlar/kredit-kartlari/tamkart-visa-gold",
  "lang": "az",
  "title": "TamKart Gold Kredit",
  "description": "TamKart Visa Gold kredit kartı ilə taksit və keşbek ...",
  "breadcrumbs": ["Fərdi", "Kartlar", "Kredit kartları", "TamKart Gold Kredit"],
  "category": "ferdi",
  "sections": [
    {
      "heading_path": ["TamKart Gold Kredit", "Tariflər"],
      "paragraphs": ["İllik faiz dərəcəsi: 22%", "Komissiya: Kredit üzrə - 2,5% ( min. 2 AZN); ..."]
    }
  ],
  "faq": [{"question": "Kredit kartı nədir?", "answer": "Kredit kartı bank tərəfindən ..."}],
  "last_modified": "2026-09-02T11:42:58+04:00",
  "fetched_at": "2026-10-14T16:31:07Z",
  "content_hash": "3f9c1b0e5a7d2c41",
  "char_count": 2481
}
```

`heading_path` keeps the full heading hierarchy, so every section still knows
its context after it is split into chunks for the vector database.

`data/scrape_report.json` — quality report: page counts per language and
category, skipped empty/duplicate pages, failed fetches, pages without CMS data
and the list of repeated blocks that were kept only once.

## Result (crawl of 2026-10-14)

| Metric | Value |
|--------|-------|
| URLs discovered | 7 397 (sitemap 7 187 + 209 found via links + home) |
| Fetched | 7 232 × HTTP 200, 165 × 404 (dead sitemap entries), 0 failures |
| Unique pages | 7 178 (98 redirects) |
| Written documents | **4 420** — 3 996 web pages + 424 service-network documents |
| Dropped | 3 003 untranslated copies, 106 duplicates, 73 empty pages |
| Text / FAQ | 8.7 M characters, 1 550 FAQ items |
| Service network | 79 branches, 8 sub-branches, 2 offices abroad, 941 ATMs, 277 terminals |
| **CMS coverage** | **100 %** of 16 240 CMS text lines (803 pages) are in the output — 97.9 % on their page, 2.1 % kept once on a more general page |
| Run time | crawl ≈ 30 min (4 pages/s, polite), extract ≈ 2 min (parallel) |

## Politeness

`robots.txt` allows crawling. The crawler identifies itself, limits itself to
6 parallel requests and backs off exponentially on `429`/`5xx` responses.
