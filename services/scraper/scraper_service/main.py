"""Scraper service API.  Run: ``uvicorn scraper_service.main:app --port 8005``"""

from __future__ import annotations

from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse

from abb_scraper.config import ScraperConfig
from service_common import configure_logging, create_app

from . import __version__
from .config import Settings
from .jobs import JobRunning, ScrapeRunner, UnsupportedSite
from .schemas import ScrapeJob, ScrapeRequest

SERVICE = "scraper"


def build_app(settings: Settings | None = None, runner: ScrapeRunner | None = None) -> FastAPI:
    settings = settings or Settings()
    configure_logging(SERVICE, settings.log_level)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        config = ScraperConfig(data_dir=settings.scraper_data_dir, concurrency=settings.scraper_concurrency)
        app.state.config = config
        app.state.runner = runner or ScrapeRunner(config, settings.ingestion_url)
        yield
        await app.state.runner.wait()

    app = create_app(SERVICE, __version__, ready_checks=_ready_checks(settings), lifespan=lifespan)

    @app.post("/v1/scrape", response_model=ScrapeJob, status_code=202, tags=["scraper"])
    async def scrape(body: ScrapeRequest, request: Request) -> ScrapeJob:
        try:
            return request.app.state.runner.start(body.url, body.mode)
        except UnsupportedSite as exc:
            raise HTTPException(422, str(exc)) from exc
        except JobRunning as exc:
            raise HTTPException(409, str(exc)) from exc

    @app.get("/v1/scrape/{job_id}", response_model=ScrapeJob, tags=["scraper"])
    async def job_status(job_id: str, request: Request) -> ScrapeJob:
        job = request.app.state.runner.jobs.get(job_id)
        if job is None:
            raise HTTPException(404, f"Unknown job {job_id}")
        return job

    @app.get("/v1/scrape/{job_id}/pages", tags=["scraper"], response_class=FileResponse)
    async def pages(job_id: str, request: Request) -> FileResponse:
        """The extracted pages (abb_pages.jsonl) of a finished job — the UI keeps them in localStorage."""
        job = request.app.state.runner.jobs.get(job_id)
        if job is None or job.status != "done":
            raise HTTPException(404, "No finished job with this id")
        return FileResponse(request.app.state.config.pages_path, media_type="application/x-ndjson",
                            filename="abb_pages.jsonl")

    return app


def _ready_checks(settings: Settings):
    def checks(app: FastAPI):
        async def data_dir() -> str:
            config: ScraperConfig = app.state.config
            config.data_dir.mkdir(parents=True, exist_ok=True)
            cached = sum(1 for _ in config.raw_dir.glob("**/*.gz")) if config.raw_dir.exists() else 0
            return f"{config.data_dir} ({cached} cached pages)"

        async def ingestion() -> str:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(f"{settings.ingestion_url}/health")
                response.raise_for_status()
            return "reachable"

        return {"data_dir": data_dir, "ingestion": ingestion}

    return checks


app = build_app()
