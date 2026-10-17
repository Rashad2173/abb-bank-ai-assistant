"""JSON contracts of the endpoints every service has."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"
    service: str
    version: str


class CheckResult(BaseModel):
    ok: bool
    detail: str
    """What was found ("9604 chunks", "cuda") or why the check failed."""
    duration_ms: float


class ReadyResponse(BaseModel):
    status: Literal["ready", "not_ready"]
    service: str
    checks: dict[str, CheckResult]


class ErrorBody(BaseModel):
    code: str
    """Machine-readable: ``invalid_request``, ``not_found``, ``dependency_unavailable``, ``internal_error`` …"""
    message: str


class ErrorResponse(BaseModel):
    error: ErrorBody
    request_id: str
