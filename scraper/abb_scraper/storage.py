"""On-disk cache of downloaded pages and the crawl manifest.

Raw HTML is stored gzip-compressed (pages are ~700 KB, mostly the RSC
payload), one file per URL. The manifest is an append-only JSONL log, which
makes an interrupted crawl resumable.
"""

from __future__ import annotations

import gzip
import hashlib
from collections.abc import Iterator
from pathlib import Path

from .models import FetchRecord


class RawPageStore:
    def __init__(self, raw_dir: Path, manifest_path: Path) -> None:
        self.pages_dir = raw_dir / "pages"
        self.manifest_path = manifest_path
        self.pages_dir.mkdir(parents=True, exist_ok=True)

    def save_html(self, url: str, html: str) -> str:
        """Store the page and return its cache file name."""
        name = hashlib.sha1(url.encode()).hexdigest()[:20] + ".html.gz"
        (self.pages_dir / name).write_bytes(gzip.compress(html.encode("utf-8")))
        return name

    def load_html(self, cache_file: str) -> str:
        return gzip.decompress((self.pages_dir / cache_file).read_bytes()).decode("utf-8")

    def append_record(self, record: FetchRecord) -> None:
        with self.manifest_path.open("a", encoding="utf-8") as fh:
            fh.write(record.model_dump_json() + "\n")

    def records(self) -> Iterator[FetchRecord]:
        """Latest manifest record per URL (a re-fetch overrides earlier ones)."""
        if not self.manifest_path.exists():
            return iter(())
        latest: dict[str, FetchRecord] = {}
        with self.manifest_path.open(encoding="utf-8") as fh:
            for line in fh:
                if line.strip():
                    record = FetchRecord.model_validate_json(line)
                    latest[record.url] = record
        return iter(latest.values())
