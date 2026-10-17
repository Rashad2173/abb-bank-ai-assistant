"""Failures of other systems, reported to the caller as ``503 dependency_unavailable``."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager


class DependencyUnavailable(RuntimeError):
    def __init__(self, dependency: str, cause: BaseException | None = None) -> None:
        detail = f": {type(cause).__name__}" if cause else ""
        super().__init__(f"{dependency} is unavailable{detail}")
        self.dependency = dependency


@contextmanager
def dependency(name: str, *errors: type[BaseException]) -> Iterator[None]:
    """Turn ``errors`` raised inside the block into :class:`DependencyUnavailable` (``Exception`` if none given)."""
    try:
        yield
    except DependencyUnavailable:
        raise
    except (errors or (Exception,)) as exc:
        raise DependencyUnavailable(name, exc) from exc
