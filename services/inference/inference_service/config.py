"""Settings of the inference service (``INFERENCE_`` environment variables): models and device.

Every field is read from ``INFERENCE_<FIELD>`` in the environment (or ``.env``).
"""

from __future__ import annotations

from typing import Literal

from pydantic_settings import SettingsConfigDict

from service_common import ServiceSettings


class Settings(ServiceSettings):
    model_config = SettingsConfigDict(env_prefix="INFERENCE_")

    device: Literal["auto", "cuda", "cpu"] = "auto"
    """``auto`` uses the GPU when PyTorch sees one."""
    load_reranker: bool = True
    """Off for a CPU-only host that uses a hosted reranker or none (the chat service falls back)."""
    max_batch: int = 64
    """Most texts per embedding request (ingestion sends documents in batches)."""
    rerank_max_documents: int = 100
    log_level: str = "INFO"
