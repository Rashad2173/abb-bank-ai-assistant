"""Chat service: answers a question about ABB from the bank's own website.

Flow of ``POST /v1/chat``::

    question ──(with history: rewrite into a standalone question)──▶
    inference /v1/embed ──▶ Milvus hybrid search (dense + sparse, top 30) ──▶
    inference /v1/rerank (top 10 kept; Milvus order if the reranker is down) ──▶
    OpenAI (structured answer: status, language, answer with [S1] citations) ──▶
    guardrail checks ──▶ response  (+ the interaction sent to the analytics service)
"""

__version__ = "1.0.0"
