"""Scraper service: from a link to an indexed knowledge base, with live progress.

``POST /v1/scrape {url, mode}`` runs the abb-bank.az scraper (``scraper/``) and
hands its output to the ingestion service:

1. **discovering** — sitemap and links of already downloaded pages,
2. **crawling**    — pages are downloaded (pages in the cache are reused, so a
   repeat run only fetches what is new),
3. **network**     — branches, ATMs and terminals from the site's own API,
4. **extracting**  — HTML + CMS data → ``abb_pages.jsonl``,
5. **indexing**    — the ingestion service chunks, embeds and writes to Milvus.

``GET /v1/scrape/{job_id}`` reports counters and the last URLs handled, so the
UI can show the work as it happens. The scraper is built for abb-bank.az (it
reads the site's CMS data and APIs); other sites are refused with a clear message.
"""

__version__ = "1.0.0"
