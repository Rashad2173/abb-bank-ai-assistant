"""Common interface of all embedding models."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

import numpy as np

SparseVector = dict[int, float]
"""Token id → weight (bge-m3's learned lexical weights)."""


@dataclass
class Embeddings:
    dense: np.ndarray
    """``(n, dim)`` float32, L2-normalized — the dot product is the cosine similarity."""
    sparse: list[SparseVector] | None = None
    """Only for models that produce sparse vectors."""


class Embedder(ABC):
    name: str
    dimension: int

    @abstractmethod
    def embed_documents(self, texts: list[str]) -> Embeddings: ...

    @abstractmethod
    def embed_queries(self, texts: list[str]) -> Embeddings: ...


def normalize(vectors: np.ndarray) -> np.ndarray:
    vectors = np.asarray(vectors, dtype=np.float32)
    return vectors / np.clip(np.linalg.norm(vectors, axis=1, keepdims=True), 1e-12, None)
