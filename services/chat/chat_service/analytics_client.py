"""Sends every interaction to the analytics service — after the user has the answer.

Recording must never break chatting: failures are logged, not raised.
"""

from __future__ import annotations

import logging

import httpx

from service_common.app import REQUEST_ID_HEADER

log = logging.getLogger(__name__)


class AnalyticsClient:
    def __init__(self, base_url: str, timeout: float) -> None:
        self._http = httpx.AsyncClient(base_url=base_url, timeout=timeout) if base_url else None

    async def record(self, interaction: dict) -> None:
        if self._http is None:
            return
        try:
            response = await self._http.post("/v1/interactions", json=interaction,
                                             headers={REQUEST_ID_HEADER: interaction["request_id"]})
            response.raise_for_status()
        except Exception as exc:
            log.warning("interaction not recorded", extra={"error": f"{type(exc).__name__}: {exc}"})

    async def close(self) -> None:
        if self._http is not None:
            await self._http.aclose()
