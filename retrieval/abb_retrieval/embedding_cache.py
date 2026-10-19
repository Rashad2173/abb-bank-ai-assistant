"""Embeddings with a disk cache (``data/embeddings/<model>/``).

Chunks are embedded once per corpus version and questions once per question
set; the benchmark, the Milvus loader and the Milvus check all read the same
files, so nothing is embedded twice.
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
from collections.abc import Callable
from pathlib import Path

import numpy as np
from scipy import sparse as sp

from .embedders import Embedder, create_embedder
from .embedders.base import Embeddings, SparseVector
from .search import sparse_matrix

log = logging.getLogger(__name__)

BGE_M3_VOCABULARY = 250_002
"""Size of bge-m3's token vocabulary — the dimension of its sparse vectors."""


class EmbeddingCache:
    """Cached embeddings of one model. The (large) model is only loaded if something is missing."""

    def __init__(self, name: str, cache_dir: Path) -> None:
        self.name = name
        self.directory = cache_dir / name
        self._model: Embedder | None = None

    def documents(self, texts: list[str]) -> tuple[Embeddings, dict]:
        """Embeddings of ``texts`` as documents, and ``{"seconds", "api_tokens"}`` of computing them."""
        return self._cached(f"docs-{fingerprint(texts)}", lambda model: model.embed_documents(texts))

    def queries(self, texts: list[str]) -> tuple[Embeddings, dict]:
        return self._cached(f"queries-{fingerprint(texts)}", lambda model: model.embed_queries(texts))

    def release(self) -> None:
        """Free the model (and GPU memory) before the next one is loaded."""
        if self._model is not None:
            self._model = None
            _free_gpu()

    def _cached(self, stem: str, compute: Callable[[Embedder], Embeddings]) -> tuple[Embeddings, dict]:
        path, meta_path = self.directory / f"{stem}.npz", self.directory / f"{stem}.json"
        if path.exists():
            log.info("using cached embeddings %s", path)
            return load(path), json.loads(meta_path.read_text())
        model = self._model = self._model or create_embedder(self.name)
        tokens_before, started = _tokens_used(model), time.perf_counter()
        embeddings = compute(model)
        meta = {"seconds": round(time.perf_counter() - started, 1), "api_tokens": _tokens_used(model) - tokens_before}
        self.directory.mkdir(parents=True, exist_ok=True)
        save(path, embeddings)
        meta_path.write_text(json.dumps(meta))
        return embeddings, meta


def fingerprint(texts: list[str]) -> str:
    return hashlib.sha256("\x1e".join(texts).encode()).hexdigest()[:12]


def save(path: Path, embeddings: Embeddings) -> None:
    arrays = {"dense": embeddings.dense}
    if embeddings.sparse is not None:
        matrix = to_csr(embeddings.sparse)
        arrays |= {"sp_data": matrix.data, "sp_indices": matrix.indices, "sp_indptr": matrix.indptr}
    np.savez_compressed(path, **arrays)


def load(path: Path) -> Embeddings:
    data = np.load(path)
    sparse = None
    if "sp_data" in data:
        matrix = sp.csr_matrix(
            (data["sp_data"], data["sp_indices"], data["sp_indptr"]), shape=(len(data["dense"]), BGE_M3_VOCABULARY)
        )
        sparse = [dict(zip(row.indices.tolist(), row.data.tolist(), strict=True)) for row in matrix]
    return Embeddings(data["dense"], sparse)


def to_csr(vectors: list[SparseVector]) -> sp.csr_matrix:
    return sparse_matrix(vectors, BGE_M3_VOCABULARY)


def _tokens_used(model: Embedder) -> int:
    """Tokens billed so far (hosted APIs only)."""
    return getattr(model, "tokens_used", 0)


def _free_gpu() -> None:
    try:
        import torch

        torch.cuda.empty_cache()
    except ImportError:
        pass
