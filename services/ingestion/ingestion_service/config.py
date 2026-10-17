from __future__ import annotations

from service_common import ServiceSettings


class Settings(ServiceSettings):
    milvus_uri: str = "http://localhost:19530"
    milvus_collection: str = "abb_chunks"
    inference_url: str = "http://localhost:8004"
    embed_batch: int = 32
    """Chunks per embedding request."""
    embed_timeout: float = 300.0
    """One batch of documents can take long on a CPU."""
    max_pages: int = 20_000
    log_level: str = "INFO"
