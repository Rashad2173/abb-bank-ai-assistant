"""Central configuration for the scraper."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class ScraperConfig:
    """All tunable settings in one place. Defaults are polite to the target site."""

    base_url: str = "https://abb-bank.az"
    sitemap_path: str = "/sitemap.xml"
    user_agent: str = "Mozilla/5.0 (compatible; ABB-CaseStudy-Scraper/1.0)"

    # Crawling
    concurrency: int = 6
    request_timeout: float = 30.0
    max_retries: int = 4
    retry_base_delay: float = 1.0
    """First back-off delay in seconds; it doubles on every further attempt."""
    follow_links: bool = True
    max_pages: int | None = None

    # Extraction
    extract_workers: int = field(default_factory=lambda: max(1, (os.cpu_count() or 2) - 1))
    """Parallel processes for HTML parsing (CPU bound)."""
    min_page_chars: int = 150
    """Pages with less extracted text than this are treated as empty."""
    boilerplate_min_pages: int = 25
    boilerplate_page_ratio: float = 0.10
    """A text block is boilerplate when it occurs on at least ``boilerplate_min_pages``
    pages *and* on at least this share of all pages in the same language."""

    data_dir: Path = field(default=PROJECT_ROOT / "data")

    @property
    def host(self) -> str:
        return self.base_url.split("://", 1)[1]

    @property
    def sitemap_url(self) -> str:
        return self.base_url + self.sitemap_path

    @property
    def raw_dir(self) -> Path:
        return self.data_dir / "raw"

    @property
    def manifest_path(self) -> Path:
        return self.data_dir / "raw" / "manifest.jsonl"

    @property
    def service_network_path(self) -> Path:
        return self.data_dir / "raw" / "service_network.json"

    @property
    def pages_path(self) -> Path:
        return self.data_dir / "abb_pages.jsonl"

    @property
    def report_path(self) -> Path:
        return self.data_dir / "scrape_report.json"
