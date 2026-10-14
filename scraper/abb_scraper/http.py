"""Shared HTTP client setup and retry policy."""

from __future__ import annotations

from typing import Any

import httpx
from tenacity import AsyncRetrying, retry_if_exception_type, stop_after_attempt, wait_exponential_jitter

from .config import ScraperConfig

RETRYABLE_STATUSES = frozenset({429, 500, 502, 503, 504})


class RetryableStatusError(Exception):
    def __init__(self, status: int) -> None:
        super().__init__(f"HTTP {status}")
        self.status = status


def create_client(config: ScraperConfig) -> httpx.AsyncClient:
    return httpx.AsyncClient(
        http2=True,
        follow_redirects=True,
        timeout=config.request_timeout,
        headers={"User-Agent": config.user_agent},
        limits=httpx.Limits(max_connections=config.concurrency),
    )


async def request(
    client: httpx.AsyncClient, config: ScraperConfig, method: str, url: str, **kwargs: Any
) -> httpx.Response:
    """Send a request, retrying with exponential back-off on network errors and 429/5xx."""
    async for attempt in AsyncRetrying(
        stop=stop_after_attempt(config.max_retries),
        wait=wait_exponential_jitter(multiplier=config.retry_base_delay, max=30, jitter=config.retry_base_delay),
        retry=retry_if_exception_type((httpx.TransportError, RetryableStatusError)),
        reraise=True,
    ):
        with attempt:
            response = await client.request(method, url, **kwargs)
            if response.status_code in RETRYABLE_STATUSES:
                raise RetryableStatusError(response.status_code)
            return response
    raise AssertionError("unreachable")
