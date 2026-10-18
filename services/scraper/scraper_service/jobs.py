"""The scrape job: crawl → service network → extraction → ingestion (one at a time)."""

from __future__ import annotations

import asyncio
import json
import logging
import uuid
from collections import deque
from dataclasses import replace
from datetime import UTC, datetime
from urllib.parse import urlparse

import httpx
from starlette.concurrency import run_in_threadpool

from abb_scraper.config import ScraperConfig
from abb_scraper.crawler import Crawler
from abb_scraper.pipeline import run_extraction
from abb_scraper.service_network import fetch_service_network
from abb_scraper.storage import RawPageStore
from service_common.app import REQUEST_ID_HEADER

from .schemas import RecentUrl, ScrapeJob

log = logging.getLogger(__name__)

SUPPORTED_HOST = "abb-bank.az"
RECENT_URLS = 12
POLL_SECONDS = 0.5


class JobRunning(RuntimeError):
    pass


class UnsupportedSite(ValueError):
    pass


def check_site(url: str) -> str:
    """The canonical site URL, or :class:`UnsupportedSite` for anything but abb-bank.az."""
    parsed = urlparse(url if "://" in url else f"https://{url}")
    host = (parsed.hostname or "").lower().removeprefix("www.")
    if host != SUPPORTED_HOST:
        raise UnsupportedSite(
            f"This scraper is built for {SUPPORTED_HOST}: it reads that site's CMS data and APIs. "
            f"Other sites ({host or url}) are not supported."
        )
    return f"https://{SUPPORTED_HOST}"


class ScrapeRunner:
    def __init__(self, config: ScraperConfig, ingestion_url: str) -> None:
        self.config = config
        self.ingestion_url = ingestion_url
        self.jobs: dict[str, ScrapeJob] = {}
        self.last_job: ScrapeJob | None = None
        self._task: asyncio.Task | None = None

    def start(self, url: str, mode: str) -> ScrapeJob:
        site = check_site(url)
        if self._task is not None and not self._task.done():
            raise JobRunning(f"Job {self.last_job.job_id} is still running")
        job = ScrapeJob(job_id=uuid.uuid4().hex[:12], url=site, mode=mode, status="queued",
                        started_at=datetime.now(UTC))
        self.jobs[job.job_id] = self.last_job = job
        self._task = asyncio.create_task(self._run(job))
        return job

    async def wait(self) -> None:
        if self._task is not None:
            await asyncio.gather(self._task, return_exceptions=True)

    async def _run(self, job: ScrapeJob) -> None:
        try:
            config = replace(self.config, base_url=job.url)
            store = RawPageStore(config.raw_dir, config.manifest_path)
            await self._crawl(job, config, store)

            job.status = "network"
            await fetch_service_network(config)

            job.status = "extracting"
            report = await run_in_threadpool(run_extraction, config, store)
            job.pages = report.pages_written

            job.status = "indexing"
            await self._index(job, config)
            job.status = "done"
            log.info("scrape finished", extra=job.model_dump(mode="json", exclude={"recent"}))
        except Exception as exc:
            job.status, job.error = "failed", f"{type(exc).__name__}: {exc}"[:500]
            log.exception("scrape failed", extra={"job_id": job.job_id})
        finally:
            job.finished_at = datetime.now(UTC)

    async def _crawl(self, job: ScrapeJob, config: ScraperConfig, store: RawPageStore) -> None:
        recent: deque[RecentUrl] = deque(maxlen=RECENT_URLS)
        crawler = Crawler(config, store, on_url=lambda url, outcome: recent.appendleft(RecentUrl(url=url, outcome=outcome)))
        job.status = "discovering"
        # The crawler re-reads cached pages synchronously while discovering links, so it runs on
        # its own event loop in a worker thread: this loop stays free to answer progress requests.
        task = asyncio.ensure_future(run_in_threadpool(asyncio.run, crawler.crawl()))
        while not task.done():
            self._copy_progress(job, crawler, recent)
            await asyncio.sleep(POLL_SECONDS)
        await task  # re-raises a crawl failure
        self._copy_progress(job, crawler, recent)

    @staticmethod
    def _copy_progress(job: ScrapeJob, crawler: Crawler, recent: deque[RecentUrl]) -> None:
        summary = crawler.summary
        job.discovered, job.remaining = crawler.discovered, crawler.remaining
        job.fetched, job.from_cache, job.failed = summary.fetched, summary.from_cache, summary.failed
        job.recent = list(recent)
        if job.fetched or job.from_cache:
            job.status = "crawling"

    async def _index(self, job: ScrapeJob, config: ScraperConfig) -> None:
        """Hands the extracted pages to the ingestion service and follows its job."""
        pages = [json.loads(line) for line in config.pages_path.open(encoding="utf-8") if line.strip()]
        headers = {REQUEST_ID_HEADER: job.job_id}
        async with httpx.AsyncClient(base_url=self.ingestion_url, timeout=120) as client:
            response = await client.post("/v1/ingest", json={"pages": pages, "mode": job.mode}, headers=headers)
            response.raise_for_status()
            ingest = response.json()
            while ingest["status"] not in ("done", "failed"):
                await asyncio.sleep(POLL_SECONDS)
                ingest = (await client.get(f"/v1/ingest/{ingest['job_id']}", headers=headers)).json()
                for field in ("chunks", "unchanged", "to_embed", "embedded", "deleted"):
                    setattr(job, field, ingest[field])
        if ingest["status"] == "failed":
            raise RuntimeError(f"ingestion failed: {ingest['error']}")
        for field in ("chunks", "unchanged", "to_embed", "embedded", "deleted"):
            setattr(job, field, ingest[field])
