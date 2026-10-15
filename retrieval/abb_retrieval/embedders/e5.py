"""intfloat/multilingual-e5-large-instruct — multilingual dense model, runs locally.

The model expects an instruction in front of *queries* (not documents).
"""

from __future__ import annotations

from .base import Embedder, Embeddings, normalize

QUERY_INSTRUCTION = "Given a customer question about a bank, retrieve web page passages that answer it"


class E5Embedder(Embedder):
    name = "multilingual-e5-large-instruct"
    dimension = 1024
    model_id = "intfloat/multilingual-e5-large-instruct"

    def __init__(self, batch_size: int = 16) -> None:
        from sentence_transformers import SentenceTransformer

        self.batch_size = batch_size
        self.model = SentenceTransformer(self.model_id)
        self.model.max_seq_length = 512
        self.model.half()

    def embed_documents(self, texts: list[str]) -> Embeddings:
        return self._encode(texts)

    def embed_queries(self, texts: list[str]) -> Embeddings:
        return self._encode([f"Instruct: {QUERY_INSTRUCTION}\nQuery: {text}" for text in texts])

    def _encode(self, texts: list[str]) -> Embeddings:
        vectors = self.model.encode(texts, batch_size=self.batch_size, show_progress_bar=True)
        return Embeddings(dense=normalize(vectors))
