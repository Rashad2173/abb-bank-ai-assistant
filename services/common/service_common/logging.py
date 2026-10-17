"""One JSON object per log line — readable by ``docker compose logs`` and log tools alike."""

from __future__ import annotations

import json
import logging
import sys
from contextvars import ContextVar
from datetime import UTC, datetime

current_request_id: ContextVar[str] = ContextVar("current_request_id", default="-")

_STANDARD_ATTRIBUTES = set(vars(logging.makeLogRecord({}))) | {"message", "asctime"}


class JsonFormatter(logging.Formatter):
    def __init__(self, service: str) -> None:
        super().__init__()
        self.service = service

    def format(self, record: logging.LogRecord) -> str:
        entry = {
            "time": datetime.fromtimestamp(record.created, UTC).isoformat(timespec="milliseconds"),
            "level": record.levelname,
            "service": self.service,
            "logger": record.name,
            "request_id": current_request_id.get(),
            "message": record.getMessage(),
        }
        # Fields passed with ``extra={...}`` (latency, status …) become JSON fields.
        entry |= {key: value for key, value in vars(record).items() if key not in _STANDARD_ATTRIBUTES}
        if record.exc_info:
            entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(entry, ensure_ascii=False, default=str)


def configure_logging(service: str, level: str = "INFO") -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter(service))
    root = logging.getLogger()
    root.handlers[:] = [handler]
    root.setLevel(level)
    for noisy in ("httpx", "httpcore", "uvicorn.access"):
        logging.getLogger(noisy).setLevel(logging.WARNING)
