from datetime import UTC, date, datetime

import pytest
from fastapi.testclient import TestClient

from analytics_service.config import Settings
from analytics_service.db import Interaction
from analytics_service.main import build_app
from analytics_service.stats import compute_stats, period_start


def interaction(**overrides):
    return {
        "request_id": "r1",
        "session_id": "s1",
        "question": "Zaqatalada neçə bankomat var?",
        "standalone_question": "Zaqatalada neçə bankomat var?",
        "answer": "12 [S1]",
        "status": "answered",
        "refusal_reason": "none",
        "language": "az",
        "grounded": True,
        "sources": [{"url": "https://abb-bank.az/atm#zaqatala", "title": "ATM — Zaqatala"}],
        "retrieved_chunk_ids": ["a"],
        "top_score": 0.9,
        "model": "gpt-6-luna",
        "reranked": True,
        "input_tokens": 100,
        "output_tokens": 20,
        "retrieval_ms": 10,
        "rerank_ms": 900,
        "generation_ms": 3000,
        "total_ms": 4000,
        **overrides,
    }


@pytest.fixture
def api():
    with TestClient(build_app(Settings(_env_file=None, database_url="sqlite://"))) as client:
        yield client


def test_interactions_are_stored_with_a_timestamp(api):
    response = api.post("/v1/interactions", json=interaction())
    assert response.status_code == 201
    body = response.json()
    assert body["id"] == 1 and body["question"] == "Zaqatalada neçə bankomat var?"
    assert datetime.fromisoformat(body["created_at"]).date() == datetime.now(UTC).date()


def test_browse_newest_first_with_status_filter(api):
    for i, status in enumerate(["answered", "out_of_scope", "answered"]):
        api.post("/v1/interactions", json=interaction(request_id=f"r{i}", status=status))

    page = api.get("/v1/interactions", params={"limit": 2}).json()
    assert page["total"] == 3 and [i["request_id"] for i in page["items"]] == ["r2", "r1"]
    refused = api.get("/v1/interactions", params={"status": "out_of_scope"}).json()
    assert refused["total"] == 1 and refused["items"][0]["request_id"] == "r1"


def test_stats_endpoint(api):
    api.post("/v1/interactions", json=interaction())
    api.post(
        "/v1/interactions",
        json=interaction(
            request_id="r2",
            status="out_of_scope",
            refusal_reason="other_bank",
            sources=[],
            grounded=False,
            reranked=False,
            total_ms=2000,
        ),
    )
    stats = api.get("/v1/stats", params={"days": 7}).json()
    assert stats["total"] == 2
    assert stats["by_status"] == {"answered": 1, "out_of_scope": 1}
    assert stats["by_refusal_reason"] == {"other_bank": 1}
    assert len(stats["per_day"]) == 7 and stats["per_day"][-1]["total"] == 2
    assert stats["reranked_share"] == 0.5 and stats["grounded_share"] == 1.0
    assert stats["top_sources"] == [{"url": "https://abb-bank.az/atm#zaqatala", "title": "ATM — Zaqatala", "count": 1}]
    assert sum(stats["by_hour"]) == 2


def test_stats_use_baku_days_and_percentiles():
    def row(hour_utc, total_ms, status="answered"):
        return Interaction(
            **interaction(status=status, total_ms=total_ms), created_at=datetime(2026, 10, 16, hour_utc, 30, tzinfo=UTC)
        )

    # 21:30 UTC on 16 Oct is 01:30 on 17 Oct in Baku.
    rows = [row(10, 1000), row(21, 3000), row(21, 5000, status="no_information")]
    stats = compute_stats(rows, days=2, today=date(2026, 10, 17))
    assert [(d.date.day, d.total) for d in stats.per_day] == [(16, 1), (17, 2)]
    assert stats.per_day[1].no_information == 1
    assert stats.by_hour[1] == 2 and stats.by_hour[14] == 1
    assert (stats.latency.p50_ms, stats.latency.p95_ms) == (3000, 5000)
    assert period_start(2, date(2026, 10, 17)) == datetime(2026, 10, 15, 20, tzinfo=UTC)


def test_ready_counts_stored_interactions(api):
    api.post("/v1/interactions", json=interaction())
    assert api.get("/ready").json()["checks"]["database"]["detail"] == "1 interactions stored"


def test_invalid_interaction_is_rejected(api):
    assert api.post("/v1/interactions", json={"question": "only this"}).status_code == 422
