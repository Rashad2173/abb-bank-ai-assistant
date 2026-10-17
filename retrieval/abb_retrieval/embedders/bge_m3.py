"""BAAI/bge-m3 — multilingual (100+ languages), dense + learned sparse vectors, runs locally."""

from __future__ import annotations

from .base import Embedder, Embeddings, normalize


class BgeM3Embedder(Embedder):
    name = "bge-m3"
    dimension = 1024
    model_id = "BAAI/bge-m3"

    def __init__(self, batch_size: int = 16, use_fp16: bool = True, devices: str | None = None) -> None:
        """``devices``: "cuda", "cpu" … — ``None`` lets FlagEmbedding pick (all GPUs if any)."""
        from FlagEmbedding import BGEM3FlagModel

        self.batch_size = batch_size
        self.model = BGEM3FlagModel(self.model_id, use_fp16=use_fp16, devices=devices)

    def embed_documents(self, texts: list[str]) -> Embeddings:
        return self._encode(texts)

    def embed_queries(self, texts: list[str]) -> Embeddings:
        return self._encode(texts)  # bge-m3 needs no query instruction

    def _encode(self, texts: list[str]) -> Embeddings:
        output = self.model.encode(
            texts, batch_size=self.batch_size, max_length=1024,
            return_dense=True, return_sparse=True, return_colbert_vecs=False,
        )
        sparse = [{int(token): float(weight) for token, weight in weights.items()}
                  for weights in output["lexical_weights"]]
        return Embeddings(dense=normalize(output["dense_vecs"]), sparse=sparse)
