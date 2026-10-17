"""Inference service: the two local models behind one JSON API.

* ``POST /v1/embed``  — bge-m3 dense + sparse vectors (questions and documents),
* ``POST /v1/rerank`` — bge-reranker-v2-m3 relevance scores of (question, passage) pairs.

Both models need PyTorch and are much faster on a GPU, so they live in one
service: the chat and ingestion services stay small and can run anywhere, and
this one goes where the GPU is.
"""

__version__ = "1.0.0"
