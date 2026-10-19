"""Settings of the analytics service: the database.

Every field is read from the environment variable of the same name (or ``.env``).
"""

from __future__ import annotations

from service_common import ServiceSettings


class Settings(ServiceSettings):
    database_url: str = "postgresql+psycopg://abb:abb@localhost:5433/abb_analytics"
    log_level: str = "INFO"
