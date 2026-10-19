import pytest
from fastapi.testclient import TestClient

from abb_retrieval.milvus_store import content_hash
from ingestion_service.config import Settings
from ingestion_service.jobs import Ingestor, JobRunning
from ingestion_service.main import build_app
from service_common.inference_client import EmbeddingResult


def page(url, *paragraphs, title="Kart"):
    return {
        "url": url,
        "title": title,
        "lang": "az",
        "category": "individual",
        "sections": [{"heading_path": [title], "paragraphs": list(paragraphs)}],
        "faq": [],
    }


PAGES = [
    page("https://abb-bank.az/a", "Kartın illik xidmət haqqı 10 AZN təşkil edir."),
    page("https://abb-bank.az/b", "Kredit 36 aya qədər müddətə verilir və zaminsizdir.", title="Kredit"),
]


class MemoryStore:
    """In-memory stand-in for MilvusStore."""

    collection = "abb_chunks"

    def __init__(self):
        self.rows = {}
        self.created = False

    def exists(self):
        return self.created

    def recreate(self):
        self.created, self.rows = True, {}

    def content_hashes(self):
        return {cid: row["hash"] for cid, row in self.rows.items()}

    def upsert(self, chunks, embeddings):
        assert len(chunks) == len(embeddings.dense) == len(embeddings.sparse)
        self.rows |= {c.chunk_id: {"hash": content_hash(c), "text": c.text} for c in chunks}

    def delete(self, ids):
        for cid in ids:
            del self.rows[cid]

    def count(self):
        return len(self.rows)


class CountingInference:
    def __init__(self):
        self.embedded = 0

    async def embed(self, texts, kind="query"):
        assert kind == "document"
        self.embedded += len(texts)
        return EmbeddingResult(dense=[[1.0, 0.0]] * len(texts), sparse=[{1: 0.5}] * len(texts))

    async def ready(self):
        return "ok"


def word_count(text):
    return len(text.split())


async def run(ingestor, pages):
    job = ingestor.start(pages)
    await ingestor.wait()
    return job


async def test_first_upload_embeds_everything_then_only_changes():
    store, inference = MemoryStore(), CountingInference()
    ingestor = Ingestor(store, inference, word_count, embed_batch=1)

    first = await run(ingestor, PAGES)
    assert first.status == "done" and first.error is None
    assert first.chunks == 2 and first.to_embed == 2 and first.embedded == 2 and store.count() == 2

    again = await run(ingestor, PAGES)
    assert again.status == "done" and again.error is None
    assert again.unchanged == 2 and again.to_embed == 0 and inference.embedded == 2

    changed = [page("https://abb-bank.az/a", "Kartın illik xidmət haqqı 12 AZN təşkil edir.")]
    update = await run(ingestor, changed)
    assert update.status == "done" and update.to_embed == 1 and update.deleted == 1 and store.count() == 1
    assert "12 AZN" in next(iter(store.rows.values()))["text"]


async def test_a_failing_job_reports_its_error():
    class Down(CountingInference):
        async def embed(self, texts, kind="query"):
            raise ConnectionError("inference down")

    job = await run(Ingestor(MemoryStore(), Down(), word_count, embed_batch=8), PAGES)
    assert job.status == "failed" and "inference down" in job.error and job.finished_at


async def test_only_one_job_at_a_time():
    ingestor = Ingestor(MemoryStore(), CountingInference(), word_count, embed_batch=8)
    ingestor.start(PAGES)
    with pytest.raises(JobRunning):
        ingestor.start(PAGES)
    await ingestor.wait()


def test_api_upload_and_job_status():
    app = build_app(Settings(_env_file=None), count_tokens=word_count)
    with TestClient(app) as client:
        app.state.store = MemoryStore()
        app.state.ingestor = Ingestor(app.state.store, CountingInference(), word_count, embed_batch=8)

        accepted = client.post("/v1/ingest", json={"pages": PAGES})
        assert accepted.status_code == 202
        job_id = accepted.json()["job_id"]

        status = client.get(f"/v1/ingest/{job_id}").json()
        assert status["job_id"] == job_id and status["pages"] == 2
        assert client.get("/v1/ingest/unknown").status_code == 404
        assert client.post("/v1/ingest", json={"pages": []}).status_code == 422
        assert client.post("/v1/ingest", json={"pages": [{"url": "x"}]}).status_code == 422


async def test_append_mode_adds_without_deleting():
    store, inference = MemoryStore(), CountingInference()
    ingestor = Ingestor(store, inference, word_count, embed_batch=8)
    await run(ingestor, PAGES)

    wiki = [page("https://az.wikipedia.org/wiki/ABB", "ABB 1992-ci ildə yaradılıb və Bakıda yerləşir.", title="ABB")]
    added = ingestor.start(wiki, mode="append")
    await ingestor.wait()
    assert added.status == "done" and added.mode == "append"
    assert added.to_embed == 1 and added.deleted == 0 and store.count() == 3

    replaced = await run(ingestor, wiki)  # default: replace
    assert replaced.deleted == 2 and store.count() == 1


def test_api_passes_the_mode():
    app = build_app(Settings(_env_file=None), count_tokens=word_count)
    with TestClient(app) as client:
        app.state.store = MemoryStore()
        app.state.ingestor = Ingestor(app.state.store, CountingInference(), word_count, embed_batch=8)
        job = client.post("/v1/ingest", json={"pages": PAGES, "mode": "append"}).json()
        assert job["mode"] == "append"
        assert client.post("/v1/ingest", json={"pages": PAGES, "mode": "merge"}).status_code == 422
