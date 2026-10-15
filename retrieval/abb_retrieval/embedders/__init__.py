"""Embedding models compared in the benchmark.

Every model implements :class:`Embedder`. Models are loaded lazily, so only
the ones that are actually run need their (large) dependencies.
"""

from __future__ import annotations

from .base import Embedder, Embeddings


def create_embedder(name: str) -> Embedder:
    if name == "bge-m3":
        from .bge_m3 import BgeM3Embedder
        return BgeM3Embedder()
    if name == "multilingual-e5-large-instruct":
        from .e5 import E5Embedder
        return E5Embedder()
    if name == "text-embedding-3-large":
        from .openai_embedder import OpenAIEmbedder
        return OpenAIEmbedder()
    raise ValueError(f"Unknown embedding model: {name}")


MODEL_NAMES = ("bge-m3", "multilingual-e5-large-instruct", "text-embedding-3-large")

__all__ = ["Embedder", "Embeddings", "MODEL_NAMES", "create_embedder"]
