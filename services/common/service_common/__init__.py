"""Building blocks shared by all ABB assistant services.

Every service is a FastAPI app created with :func:`create_app`, which adds the
same operational surface everywhere:

* ``GET /health`` — liveness: the process is up (no dependencies checked),
* ``GET /ready``  — readiness: every dependency (Milvus, Postgres, models …)
  answers; ``503`` with the failing checks otherwise,
* an ``X-Request-ID`` on every request and response, carried into the logs and
  forwarded to other services so one question can be followed across them,
* errors as JSON: ``{"error": {"code": …, "message": …}, "request_id": …}``.
"""

from .app import ReadyCheck, create_app, request_id
from .errors import DependencyUnavailable, dependency
from .logging import configure_logging
from .schemas import CheckResult, ErrorBody, ErrorResponse, HealthResponse, ReadyResponse
from .settings import ServiceSettings

__all__ = [
    "CheckResult",
    "DependencyUnavailable",
    "ErrorBody",
    "ErrorResponse",
    "HealthResponse",
    "ReadyCheck",
    "ReadyResponse",
    "ServiceSettings",
    "configure_logging",
    "create_app",
    "dependency",
    "request_id",
]
