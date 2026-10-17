import numpy as np
import pytest
from fastapi.testclient import TestClient

from abb_retrieval.embedders.base import Embeddings
from inference_service.config import Settings
from inference_service.main import build_app
from inference_service.models import ModelUnavailable


class FakeModels:
    embed_model, rerank_model, device = "BAAI/bge-m3", "BAAI/bge-reranker-v2-m3", "cpu"

    def __init__(self, reranker=True):
        self.embedder = object()
        self.reranker = object() if reranker else None
        self.settings = Settings(_env_file=None, load_reranker=reranker)

    async def embed(self, texts, kind):
        return Embeddings(dense=np.ones((len(texts), 3), dtype=np.float32), sparse=[{7: 0.25}] * len(texts))

    async def rerank(self, query, documents):
        if self.reranker is None:
            raise ModelUnavailable("The reranker is not loaded on this instance")
        return [len(d) / 10 for d in documents]


@pytest.fixture
def client():
    with TestClient(build_app(Settings(_env_file=None, max_batch=2), models=FakeModels())) as c:
        yield c


def test_embed_returns_dense_and_sparse_vectors(client):
    body = client.post("/v1/embed", json={"texts": ["a", "b"], "kind": "document"}).json()
    assert body["model"] == "BAAI/bge-m3"
    assert body["dense"] == [[1.0, 1.0, 1.0]] * 2
    assert body["sparse"] == [{"7": 0.25}] * 2


def test_embed_limits_the_batch(client):
    assert client.post("/v1/embed", json={"texts": ["a", "b", "c"]}).status_code == 413
    assert client.post("/v1/embed", json={"texts": []}).status_code == 422


def test_rerank_scores_in_request_order(client):
    body = client.post("/v1/rerank", json={"query": "q", "documents": ["abcde", "ab"]}).json()
    assert body["scores"] == [0.5, 0.2]


def test_without_reranker_rerank_is_503_but_the_service_is_ready():
    with TestClient(build_app(Settings(_env_file=None), models=FakeModels(reranker=False))) as c:
        response = c.post("/v1/rerank", json={"query": "q", "documents": ["d"]})
        assert response.status_code == 503 and response.json()["error"]["code"] == "dependency_unavailable"
        ready = c.get("/ready").json()
        assert ready["status"] == "ready" and ready["checks"]["reranker"]["detail"] == "disabled on this instance"
