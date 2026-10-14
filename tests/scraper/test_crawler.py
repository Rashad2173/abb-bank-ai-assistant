from dataclasses import replace

import httpx
import pytest
import respx

from abb_scraper.crawler import Crawler
from abb_scraper.storage import RawPageStore

BASE = "https://abb-bank.az"
SITEMAP = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>{BASE}/ferdi</loc><lastmod>2025-01-01</lastmod></url>
  <url><loc>{BASE}/flaky</loc></url>
  <url><loc>{BASE}/gone</loc></url>
</urlset>"""


def html(body: str) -> httpx.Response:
    return httpx.Response(200, text=f"<html><body>{body}</body></html>", headers={"content-type": "text/html"})


@pytest.fixture
def fast_config(config):
    return replace(config, retry_base_delay=0)


@pytest.fixture
def site():
    with respx.mock(assert_all_called=False) as mock:
        mock.get(f"{BASE}/sitemap.xml").respond(200, text=SITEMAP)
        mock.get(f"{BASE}/").mock(return_value=html("Ana səhifə"))
        mock.get(f"{BASE}/ferdi").mock(return_value=html('<a href="/ferdi/kartlar">Kartlar</a>'))
        mock.get(f"{BASE}/ferdi/kartlar").mock(return_value=html("Kartlar"))
        mock.get(f"{BASE}/flaky").mock(side_effect=[httpx.Response(503), html("OK")])
        mock.get(f"{BASE}/gone").respond(404)
        yield mock


async def test_crawls_sitemap_and_linked_pages(fast_config, site):
    store = RawPageStore(fast_config.raw_dir, fast_config.manifest_path)
    summary = await Crawler(fast_config, store).crawl()

    records = {r.url: r for r in store.records()}
    assert set(records) == {f"{BASE}/", f"{BASE}/ferdi", f"{BASE}/ferdi/kartlar", f"{BASE}/flaky", f"{BASE}/gone"}
    assert summary.found_via_links == 1                 # /ferdi/kartlar is not in the sitemap
    assert records[f"{BASE}/flaky"].status == 200       # retried after the 503
    assert records[f"{BASE}/gone"].cache_file is None   # 404s are recorded but not cached
    assert records[f"{BASE}/ferdi"].last_modified == "2025-01-01"
    assert "Kartlar" in store.load_html(records[f"{BASE}/ferdi/kartlar"].cache_file)


async def test_resumed_crawl_uses_the_cache(fast_config, site):
    store = RawPageStore(fast_config.raw_dir, fast_config.manifest_path)
    await Crawler(fast_config, store).crawl()
    second = await Crawler(fast_config, store).crawl()

    assert second.fetched == 0
    assert second.from_cache == 5


async def test_max_pages_limits_the_crawl(fast_config, site):
    store = RawPageStore(fast_config.raw_dir, fast_config.manifest_path)
    summary = await Crawler(replace(fast_config, max_pages=2), store).crawl()
    assert summary.fetched == 2
