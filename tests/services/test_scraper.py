import json

import pytest
from fastapi.testclient import TestClient

from abb_scraper.config import ScraperConfig
from abb_scraper.crawler import CrawlSummary
from scraper_service import jobs
from scraper_service.config import Settings
from scraper_service.jobs import ScrapeRunner, UnsupportedSite, check_site
from scraper_service.main import build_app


@pytest.mark.parametrize(
    "url", ["https://abb-bank.az", "abb-bank.az", "https://www.abb-bank.az/az/ferdi", "HTTP://ABB-BANK.AZ/"]
)
def test_abb_links_are_accepted(url):
    assert check_site(url) == "https://abb-bank.az"


@pytest.mark.parametrize(
    "url", ["https://az.wikipedia.org/wiki/ABB", "https://kapitalbank.az", "abb-bank.az.evil.com", "nonsense"]
)
def test_other_sites_are_refused(url):
    with pytest.raises(UnsupportedSite):
        check_site(url)


class FakeCrawler:
    def __init__(self, config, store, on_url=None):
        self.summary, self.on_url = CrawlSummary(), on_url
        self.discovered, self.remaining = 0, 0

    async def crawl(self):
        for url, outcome in [("https://abb-bank.az/", "cached"), ("https://abb-bank.az/new", "fetched")]:
            self.discovered += 1
            setattr(
                self.summary,
                "from_cache" if outcome == "cached" else "fetched",
                getattr(self.summary, "from_cache" if outcome == "cached" else "fetched") + 1,
            )
            self.on_url(url, outcome)
        return self.summary


@pytest.fixture
def runner(tmp_path, monkeypatch):
    config = ScraperConfig(data_dir=tmp_path)
    page = {"url": "https://abb-bank.az/", "title": "ABB", "lang": "az", "category": "home", "sections": [], "faq": []}

    def extract(config, store):
        config.pages_path.write_text(json.dumps(page) + "\n", encoding="utf-8")
        return type("Report", (), {"pages_written": 1})()

    async def network(config):
        return {}

    sent = {}

    class FakeIngestion:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *exc):
            return False

        async def post(self, path, json, headers):
            sent.update(json)
            return FakeResponse(
                {
                    "job_id": "i1",
                    "status": "done",
                    "chunks": 3,
                    "unchanged": 2,
                    "to_embed": 1,
                    "embedded": 1,
                    "deleted": 0,
                    "error": None,
                }
            )

    monkeypatch.setattr(jobs, "Crawler", FakeCrawler)
    monkeypatch.setattr(jobs, "run_extraction", extract)
    monkeypatch.setattr(jobs, "fetch_service_network", network)
    monkeypatch.setattr(jobs.httpx, "AsyncClient", FakeIngestion)
    instance = ScrapeRunner(config, "http://ingestion")
    instance.sent = sent
    return instance


class FakeResponse:
    def __init__(self, body):
        self.body = body

    def raise_for_status(self):
        pass

    def json(self):
        return self.body


async def test_a_scrape_runs_every_step_and_indexes_the_pages(runner):
    job = runner.start("abb-bank.az", "append")
    await runner.wait()
    assert job.status == "done" and job.error is None
    assert (job.from_cache, job.fetched, job.discovered) == (1, 1, 2)
    assert [r.outcome for r in job.recent] == ["fetched", "cached"]  # newest first
    assert job.pages == 1 and job.chunks == 3 and job.to_embed == 1
    assert runner.sent["mode"] == "append" and len(runner.sent["pages"]) == 1


def test_api_refuses_other_sites_with_a_clear_message(runner):
    with TestClient(build_app(Settings(_env_file=None), runner=runner)) as client:
        response = client.post("/v1/scrape", json={"url": "https://az.wikipedia.org/wiki/ABB"})
        assert response.status_code == 422
        assert "built for abb-bank.az" in response.json()["error"]["message"]
        assert client.get("/v1/scrape/unknown").status_code == 404
