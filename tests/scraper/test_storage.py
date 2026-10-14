from datetime import datetime, timezone

from abb_scraper.models import FetchRecord
from abb_scraper.storage import RawPageStore


def make_store(tmp_path) -> RawPageStore:
    return RawPageStore(tmp_path / "raw", tmp_path / "raw" / "manifest.jsonl")


def record(url: str, status: int) -> FetchRecord:
    return FetchRecord(url=url, status=status, final_url=url, fetched_at=datetime.now(timezone.utc))


def test_html_round_trip(tmp_path):
    store = make_store(tmp_path)
    name = store.save_html("https://abb-bank.az/ferdi", "<p>Əmanət</p>")
    assert name.endswith(".html.gz")
    assert store.load_html(name) == "<p>Əmanət</p>"


def test_records_returns_latest_entry_per_url(tmp_path):
    store = make_store(tmp_path)
    store.append_record(record("https://abb-bank.az/a", 503))
    store.append_record(record("https://abb-bank.az/b", 200))
    store.append_record(record("https://abb-bank.az/a", 200))

    statuses = {r.url: r.status for r in store.records()}
    assert statuses == {"https://abb-bank.az/a": 200, "https://abb-bank.az/b": 200}


def test_records_is_empty_without_manifest(tmp_path):
    assert list(make_store(tmp_path).records()) == []
