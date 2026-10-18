"""Crawl phase: discover every page of the site and cache its raw HTML.

URLs come from two sources so that nothing is missed:

* the sitemap (``/sitemap.xml``), and
* links found on every downloaded page (pages missing from the sitemap).

Requests run concurrently with a fixed limit, failed requests are retried
with exponential back-off, and pages already in the cache are skipped, so an
interrupted crawl simply continues where it stopped.
"""

from __future__ import annotations

import asyncio
import logging
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timezone

import httpx

from .config import ScraperConfig
from .discovery import extract_links, normalize_url, parse_sitemap
from .http import RetryableStatusError, create_client, request
from .models import FetchRecord
from .storage import RawPageStore

log = logging.getLogger(__name__)

FINAL_STATUSES = frozenset({200, 404, 410})
"""Responses that will not change on a retry; anything else is re-tried on the next run."""


@dataclass
class CrawlSummary:
    fetched: int = 0
    failed: int = 0
    from_cache: int = 0
    found_via_links: int = 0


ProgressCallback = Callable[[str, str], None]
"""Called with ``(url, outcome)`` for every URL handled: ``"cached"``, ``"fetched"`` or ``"failed"``."""


class Crawler:
    def __init__(self, config: ScraperConfig, store: RawPageStore, on_url: ProgressCallback | None = None) -> None:
        self.config = config
        self.store = store
        self.on_url = on_url
        self.summary = CrawlSummary()
        self._seen: set[str] = set()
        self._lastmod: dict[str, str | None] = {}
        self._queue: asyncio.Queue[str] = asyncio.Queue()
        self._started = 0.0

    @property
    def discovered(self) -> int:
        """URLs found so far (sitemap + links) — for progress displays."""
        return len(self._seen)

    @property
    def remaining(self) -> int:
        """URLs still waiting in the queue."""
        return self._queue.qsize()

    async def crawl(self) -> CrawlSummary:
        self._started = time.monotonic()
        done = {
            record.url: record
            for record in self.store.records()
            if record.status in FINAL_STATUSES and record.error is None
        }

        async with create_client(self.config) as client:
            for url, lastmod in (await self._read_sitemap(client)).items():
                self._lastmod[url] = lastmod
                self._enqueue(url)
            self._enqueue(self.config.base_url + "/")

            if self.config.follow_links:
                self._enqueue_links_of_cached_pages(done.values())

            workers = [
                asyncio.create_task(self._worker(client, done))
                for _ in range(self.config.concurrency)
            ]
            await self._queue.join()
            for worker in workers:
                worker.cancel()

        log.info("Crawl finished: %s", self.summary)
        return self.summary

    # ------------------------------------------------------------------ #

    async def _read_sitemap(self, client: httpx.AsyncClient) -> dict[str, str | None]:
        response = await request(client, self.config, "GET", self.config.sitemap_url)
        response.raise_for_status()
        entries: dict[str, str | None] = {}
        for url, lastmod in parse_sitemap(response.text).items():
            normalized = normalize_url(url, self.config.host)
            if normalized:
                entries[normalized] = lastmod
        log.info("Sitemap lists %d page URLs", len(entries))
        return entries

    def _enqueue(self, url: str, *, from_link: bool = False) -> None:
        normalized = normalize_url(url, self.config.host)
        if normalized is None or normalized in self._seen:
            return
        if self.config.max_pages is not None and len(self._seen) >= self.config.max_pages:
            return
        self._seen.add(normalized)
        if from_link:
            self.summary.found_via_links += 1
        self._queue.put_nowait(normalized)

    def _enqueue_links(self, html: str, page_url: str) -> None:
        for link in extract_links(html, page_url, self.config.host):
            self._enqueue(link, from_link=True)

    def _enqueue_links_of_cached_pages(self, records) -> None:
        """On a resumed crawl, rediscover links from pages that are already cached."""
        for record in records:
            if record.cache_file:
                self._enqueue_links(self.store.load_html(record.cache_file), record.final_url)

    async def _worker(self, client: httpx.AsyncClient, done: dict[str, FetchRecord]) -> None:
        while True:
            url = await self._queue.get()
            try:
                if url in done:
                    self.summary.from_cache += 1
                    self._report(url, "cached")
                    continue
                record, html = await self._fetch(client, url)
                self.store.append_record(record)
                if record.error:
                    self.summary.failed += 1
                    log.warning("Failed %s: %s", url, record.error)
                    self._report(url, "failed")
                else:
                    self.summary.fetched += 1
                    self._log_progress()
                    self._report(url, "fetched")
                if html and self.config.follow_links:
                    self._enqueue_links(html, record.final_url)
            finally:
                self._queue.task_done()

    async def _fetch(self, client: httpx.AsyncClient, url: str) -> tuple[FetchRecord, str | None]:
        fetched_at = datetime.now(timezone.utc)
        try:
            response = await request(client, self.config, "GET", url)
        except (httpx.HTTPError, RetryableStatusError) as exc:
            error = f"{type(exc).__name__}: {exc}"
            return FetchRecord(url=url, status=0, final_url=url, fetched_at=fetched_at, error=error), None

        is_html = "text/html" in response.headers.get("content-type", "")
        html = response.text if response.status_code == 200 and is_html else None
        record = FetchRecord(
            url=url,
            status=response.status_code,
            final_url=normalize_url(str(response.url), self.config.host) or url,
            fetched_at=fetched_at,
            cache_file=self.store.save_html(url, html) if html else None,
            last_modified=self._lastmod.get(url),
        )
        return record, html

    def _report(self, url: str, outcome: str) -> None:
        if self.on_url is not None:
            self.on_url(url, outcome)

    def _log_progress(self) -> None:
        if self.summary.fetched % 100 == 0:
            elapsed = time.monotonic() - self._started
            log.info(
                "Fetched %d pages (%.1f pages/s), queue: %d, failed: %d",
                self.summary.fetched, self.summary.fetched / elapsed,
                self._queue.qsize(), self.summary.failed,
            )
