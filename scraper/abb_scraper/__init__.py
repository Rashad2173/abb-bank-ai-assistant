"""Scraper that extracts the textual content of the ABB Bank website (abb-bank.az).

The work is split in two independent phases:

1. **crawl**   — discover URLs (sitemap + link following) and download the raw
   HTML into a local cache.
2. **extract** — parse the cached HTML into clean, structured page documents
   (``data/abb_pages.jsonl``) and write a quality report.

Keeping the phases separate means extraction rules can be improved and re-run
without downloading the site again.
"""

__version__ = "1.0.0"
