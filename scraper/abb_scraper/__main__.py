"""Command line interface.

Usage (from the ``scraper/`` directory)::

    python -m abb_scraper crawl     # download the site + service network into data/raw/
    python -m abb_scraper network   # only (re-)download the service network (branches, ATMs)
    python -m abb_scraper extract   # build data/abb_pages.jsonl from the cache
    python -m abb_scraper check     # data quality report (evaluation/reports/00_data_quality.md)
    python -m abb_scraper run       # crawl + extract
"""

from __future__ import annotations

import argparse
import asyncio
import logging
from dataclasses import replace
from pathlib import Path

from .config import ScraperConfig
from .crawler import Crawler
from .pipeline import run_extraction
from .quality import run_quality_checks
from .service_network import fetch_service_network
from .storage import RawPageStore


def main() -> None:
    args = _parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)-7s %(name)s: %(message)s")
    logging.getLogger("httpx").setLevel(logging.WARNING)  # one line per request is too noisy

    config = ScraperConfig()
    overrides = {
        "concurrency": args.concurrency,
        "extract_workers": args.workers,
        "max_pages": args.max_pages,
        "follow_links": False if args.no_follow_links else None,
        "data_dir": args.data_dir,
    }
    config = replace(config, **{k: v for k, v in overrides.items() if v is not None})
    store = RawPageStore(config.raw_dir, config.manifest_path)

    if args.command in ("crawl", "run"):
        asyncio.run(Crawler(config, store).crawl())
    if args.command in ("crawl", "network", "run"):
        asyncio.run(fetch_service_network(config))
    if args.command in ("extract", "run"):
        run_extraction(config, store)
    if args.command == "check":
        report = run_quality_checks(config, store, config.reports_dir / "00_data_quality.md")
        logging.getLogger("abb_scraper").info("Data quality report: %s", report)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="abb_scraper", description="Scrape the textual content of abb-bank.az")
    parser.add_argument("command", choices=("crawl", "network", "extract", "check", "run"))
    parser.add_argument("--concurrency", type=int, help="parallel requests (default: 6)")
    parser.add_argument("--workers", type=int, help="parallel processes for extraction (default: CPU count - 1)")
    parser.add_argument("--max-pages", type=int, help="stop after this many URLs (for trial runs)")
    parser.add_argument("--no-follow-links", action="store_true", help="only crawl URLs listed in the sitemap")
    parser.add_argument("--data-dir", type=Path, help="output directory (default: <repo>/data)")
    return parser.parse_args()


if __name__ == "__main__":
    main()
