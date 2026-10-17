"""JSON contracts of the inference service."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class EmbedRequest(BaseModel):
    texts: list[str] = Field(min_length=1)
    kind: Literal["query", "document"] = "query"


class EmbedResponse(BaseModel):
    model: str
    dense: list[list[float]]
    """L2-normalized, 1 024 dimensions — the dot product is the cosine similarity."""
    sparse: list[dict[str, float]]
    """Token id (as a string — JSON object keys) → lexical weight."""


class RerankRequest(BaseModel):
    query: str = Field(min_length=1)
    documents: list[str] = Field(min_length=1)


class RerankResponse(BaseModel):
    model: str
    scores: list[float]
    """Relevance of each document in [0, 1] (sigmoid of the reranker logit), in request order."""
