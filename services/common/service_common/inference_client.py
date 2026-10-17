"""Client of the inference service (used by the chat and ingestion services)."""

from __future__ import annotations

from dataclasses import dataclass

import httpx

from .app import REQUEST_ID_HEADER, request_id


@dataclass
class EmbeddingResult:
    dense: list[list[float]]
    sparse: list[dict[int, float]]


class InferenceClient:
    def __init__(self, base_url: str, timeout: float = 30.0) -> None:
        self._http = httpx.AsyncClient(base_url=base_url, timeout=timeout)

    async def embed(self, texts: list[str], kind: str = "query") -> EmbeddingResult:
        body = await self._post("/v1/embed", {"texts": texts, "kind": kind})
        return EmbeddingResult(
            dense=body["dense"],
            sparse=[{int(token): weight for token, weight in vector.items()} for vector in body["sparse"]],
        )

    async def rerank(self, query: str, documents: list[str], timeout: float | None = None) -> list[float]:
        body = await self._post("/v1/rerank", {"query": query, "documents": documents}, timeout=timeout)
        return body["scores"]

    async def ready(self) -> str:
        response = await self._http.get("/ready", timeout=5.0)
        response.raise_for_status()
        checks = response.json()["checks"]
        return "; ".join(f"{name}: {check['detail']}" for name, check in checks.items())

    async def close(self) -> None:
        await self._http.aclose()

    async def _post(self, path: str, payload: dict, timeout: float | None = None) -> dict:
        extra = {"timeout": timeout} if timeout is not None else {}
        response = await self._http.post(path, json=payload, headers={REQUEST_ID_HEADER: request_id()}, **extra)
        response.raise_for_status()
        return response.json()
