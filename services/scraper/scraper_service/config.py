"""Settings of the scraper service: the page cache, politeness and the ingestion service.

Every field is read from the environment variable of the same name (or ``.env``).
"""

from __future__ import annotations

from pathlib import Path

from abb_scraper.config import PROJECT_ROOT
from service_common import ServiceSettings


class Settings(ServiceSettings):
    ingestion_url: str = "http://localhost:8003"
    scraper_data_dir: Path = PROJECT_ROOT / "data"
    """Holds the page cache (``raw/``) and the output (``abb_pages.jsonl``); a volume in Docker."""
    scraper_concurrency: int = 6
    """Parallel requests to abb-bank.az — polite by default."""
    log_level: str = "INFO"
