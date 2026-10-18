from __future__ import annotations

from typing import Literal

from service_common import ServiceSettings


class Settings(ServiceSettings):
    """Environment variables (or ``.env``) of the same name, case-insensitive."""

    # Dependencies
    milvus_uri: str = "http://localhost:19530"
    milvus_collection: str = "abb_chunks"
    inference_url: str = "http://localhost:8004"
    analytics_url: str = "http://localhost:8002"
    """Empty: interactions are not recorded."""
    openai_api_key: str = ""
    openai_chat_model: str = "gpt-6-luna"
    openai_reasoning_effort: Literal["minimal", "low", "medium", "high"] = "low"

    # Retrieval
    retrieval_method: Literal["dense+sparse", "dense+bm25", "dense+sparse+bm25", "dense"] = "dense+sparse"
    retrieval_candidates: int = 30
    """Chunks Milvus returns and the reranker re-scores."""
    context_chunks: int = 10
    """Chunks given to the LLM."""
    min_rerank_score: float = 0.0
    """Reranked chunks below this relevance (0–1) are not given to the LLM; 0 keeps all."""
    reranker: Literal["http", "none"] = "http"
    """``http``: the inference service's reranker; ``none``: Milvus' order."""
    query_expansion: bool = True
    """Also search non-Azerbaijani questions in Azerbaijani (see :mod:`query`)."""
    procurement_filter: bool = True
    """Leave tender notices out unless the question is about procurement."""

    # Limits and timeouts (seconds)
    history_turns: int = 6
    embed_timeout: float = 10.0
    rerank_timeout: float = 5.0
    """Past this the answer is built from Milvus' order instead of failing."""
    llm_timeout: float = 60.0
    analytics_timeout: float = 3.0

    log_level: str = "INFO"
