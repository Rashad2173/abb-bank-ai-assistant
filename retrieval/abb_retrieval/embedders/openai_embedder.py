"""OpenAI text-embedding-3-large — hosted API, no local GPU or RAM needed."""

from __future__ import annotations

import os

from .base import Embedder, Embeddings, normalize

_MAX_INPUTS_PER_REQUEST = 256  # well below the API limits (2048 inputs / 300k tokens)


class OpenAIEmbedder(Embedder):
    name = "text-embedding-3-large"
    dimension = 3072
    model_id = "text-embedding-3-large"

    def __init__(self) -> None:
        from dotenv import load_dotenv
        from openai import OpenAI

        load_dotenv(override=True)  # the project's .env wins over a key inherited from the system environment
        if not os.getenv("OPENAI_API_KEY"):
            raise RuntimeError("OPENAI_API_KEY is not set (put it into the .env file)")
        self.client = OpenAI(max_retries=5)
        self.tokens_used = 0

    def embed_documents(self, texts: list[str]) -> Embeddings:
        return self._encode(texts)

    def embed_queries(self, texts: list[str]) -> Embeddings:
        return self._encode(texts)

    def _encode(self, texts: list[str]) -> Embeddings:
        vectors = []
        for start in range(0, len(texts), _MAX_INPUTS_PER_REQUEST):
            response = self.client.embeddings.create(
                model=self.model_id, input=texts[start : start + _MAX_INPUTS_PER_REQUEST]
            )
            vectors += [item.embedding for item in sorted(response.data, key=lambda d: d.index)]
            self.tokens_used += response.usage.total_tokens
        return Embeddings(dense=normalize(vectors))
