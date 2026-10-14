"""Shared fixtures for the scraper tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from abb_scraper.config import ScraperConfig

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def product_page_html() -> str:
    """A trimmed-down page with the same structure as a real abb-bank.az product page."""
    return (FIXTURES / "product_page.html").read_text(encoding="utf-8")


@pytest.fixture
def config(tmp_path: Path) -> ScraperConfig:
    return ScraperConfig(
        data_dir=tmp_path, concurrency=2, max_retries=2, boilerplate_min_pages=2, extract_workers=1
    )
