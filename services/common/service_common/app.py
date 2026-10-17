"""FastAPI app factory with health, readiness, request ids and JSON errors."""

from __future__ import annotations

import asyncio
import logging
import time
import uuid
from collections.abc import Awaitable, Callable, Mapping
from contextlib import AbstractAsyncContextManager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from .errors import DependencyUnavailable
from .logging import current_request_id
from .schemas import CheckResult, ErrorBody, ErrorResponse, HealthResponse, ReadyResponse

log = logging.getLogger(__name__)

REQUEST_ID_HEADER = "X-Request-ID"
READY_CHECK_TIMEOUT = 5.0  # seconds per dependency

ReadyCheck = Callable[[], Awaitable[str]]
"""Returns a short detail ("9604 chunks") or raises if the dependency is not usable."""

_ERROR_CODES = {400: "invalid_request", 401: "unauthorized", 403: "forbidden", 404: "not_found",
                405: "method_not_allowed", 413: "payload_too_large", 422: "invalid_request",
                429: "rate_limited", 503: "dependency_unavailable"}


def request_id() -> str:
    """Id of the request being handled — forward it when calling another service."""
    return current_request_id.get()


def create_app(
    service: str,
    version: str,
    ready_checks: Callable[[FastAPI], Mapping[str, ReadyCheck]],
    lifespan: Callable[[FastAPI], AbstractAsyncContextManager[None]] | None = None,
) -> FastAPI:
    """``ready_checks`` gets the app (whose ``state`` holds the clients) and returns the checks."""
    app = FastAPI(title=f"ABB assistant — {service}", version=version, lifespan=lifespan)

    @app.middleware("http")
    async def with_request_id(request: Request, call_next):
        rid = request.headers.get(REQUEST_ID_HEADER) or uuid.uuid4().hex[:16]
        request.state.request_id = rid  # error handlers outside this middleware read it from here
        token = current_request_id.set(rid)
        started = time.perf_counter()
        try:
            response = await call_next(request)
            response.headers[REQUEST_ID_HEADER] = rid
            if request.url.path not in ("/health", "/ready"):
                log.info("%s %s -> %d", request.method, request.url.path, response.status_code,
                         extra={"duration_ms": round(1000 * (time.perf_counter() - started), 1)})
            return response
        finally:
            current_request_id.reset(token)

    @app.exception_handler(StarletteHTTPException)
    async def http_error(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        return _error(request, exc.status_code, _ERROR_CODES.get(exc.status_code, "error"), str(exc.detail))

    @app.exception_handler(RequestValidationError)
    async def validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
        problems = "; ".join(f"{'.'.join(str(p) for p in e['loc'])}: {e['msg']}" for e in exc.errors())
        return _error(request, 422, "invalid_request", problems)

    @app.exception_handler(DependencyUnavailable)
    async def dependency_error(request: Request, exc: DependencyUnavailable) -> JSONResponse:
        log.error("dependency unavailable", exc_info=exc.__cause__ or exc,
                  extra={"dependency": exc.dependency, "request_id": _request_id_of(request)})
        return _error(request, 503, "dependency_unavailable", str(exc))

    @app.exception_handler(Exception)
    async def unexpected_error(request: Request, exc: Exception) -> JSONResponse:
        log.exception("unhandled error", extra={"request_id": _request_id_of(request)})
        response = _error(request, 500, "internal_error", "Internal error - see the service log for this request id.")
        response.headers[REQUEST_ID_HEADER] = _request_id_of(request)
        return response

    @app.get("/health", response_model=HealthResponse, tags=["operations"])
    async def health() -> HealthResponse:
        return HealthResponse(service=service, version=version)

    @app.get("/ready", response_model=ReadyResponse, tags=["operations"],
             responses={503: {"model": ReadyResponse}})
    async def ready() -> JSONResponse:
        checks = ready_checks(app)
        results = dict(zip(checks, await asyncio.gather(*(_run_check(c) for c in checks.values()))))
        status = "ready" if all(r.ok for r in results.values()) else "not_ready"
        body = ReadyResponse(status=status, service=service, checks=results)
        return JSONResponse(body.model_dump(), status_code=200 if status == "ready" else 503)

    return app


async def _run_check(check: ReadyCheck) -> CheckResult:
    started = time.perf_counter()
    try:
        detail, ok = await asyncio.wait_for(check(), READY_CHECK_TIMEOUT), True
    except TimeoutError:
        detail, ok = f"no answer within {READY_CHECK_TIMEOUT:.0f} s", False
    except Exception as exc:  # any failure means "not ready"; the reason is reported
        detail, ok = f"{type(exc).__name__}: {exc}"[:300], False
    return CheckResult(ok=ok, detail=detail, duration_ms=round(1000 * (time.perf_counter() - started), 1))


def _request_id_of(request: Request) -> str:
    return getattr(request.state, "request_id", current_request_id.get())


def _error(request: Request, status: int, code: str, message: str) -> JSONResponse:
    body = ErrorResponse(error=ErrorBody(code=code, message=message), request_id=_request_id_of(request))
    return JSONResponse(body.model_dump(), status_code=status)
