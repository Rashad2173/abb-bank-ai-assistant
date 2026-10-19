"""Exact (brute-force) search used by the benchmark.

Exact search makes the model comparison independent of any index settings:
differences come from the embeddings alone. Scores are ``(queries, chunks)``
matrices; rankings are lists of chunk indices, best first.
"""

from __future__ import annotations

import math
import re
from collections import Counter

import numpy as np
from scipy import sparse as sp

from .embedders.base import SparseVector

RRF_K = 60
"""Standard constant of Reciprocal Rank Fusion (Cormack et al., 2009)."""

_WORD_RE = re.compile(r"\w+", re.UNICODE)
_I_VARIANTS = str.maketrans({"İ": "i", "I": "i", "ı": "i"})


def dense_scores(queries: np.ndarray, documents: np.ndarray) -> np.ndarray:
    """Cosine similarity of L2-normalized vectors."""
    return queries @ documents.T


def sparse_matrix(vectors: list[SparseVector], vocabulary_size: int) -> sp.csr_matrix:
    rows, cols, values = [], [], []
    for row, vector in enumerate(vectors):
        for token, weight in vector.items():
            rows.append(row)
            cols.append(token)
            values.append(weight)
    return sp.csr_matrix((values, (rows, cols)), shape=(len(vectors), vocabulary_size), dtype=np.float32)


def sparse_scores(queries: sp.csr_matrix, documents: sp.csr_matrix) -> np.ndarray:
    """Dot product of lexical weights (how bge-m3 scores its sparse vectors)."""
    return (queries @ documents.T).toarray()


def rank(scores: np.ndarray, top_k: int) -> list[list[int]]:
    """Indices of the ``top_k`` highest scores of every row."""
    top_k = min(top_k, scores.shape[1])
    top = np.argpartition(-scores, top_k - 1, axis=1)[:, :top_k]
    order = np.take_along_axis(scores, top, axis=1).argsort(axis=1)[:, ::-1]
    return np.take_along_axis(top, order, axis=1).tolist()


def reciprocal_rank_fusion(*rankings: list[list[int]], top_k: int, k: int = RRF_K) -> list[list[int]]:
    """Merge rankings of the same queries: score = Σ 1 / (k + rank)."""
    fused = []
    for per_query in zip(*rankings, strict=True):
        scores: Counter[int] = Counter()
        for ranking in per_query:
            for position, doc in enumerate(ranking):
                scores[doc] += 1.0 / (k + position + 1)
        fused.append([doc for doc, _ in scores.most_common(top_k)])
    return fused


def tokenize(text: str) -> list[str]:
    """Lower-cased words; Azerbaijani dotted/dotless I are treated alike."""
    return _WORD_RE.findall(text.translate(_I_VARIANTS).casefold())


class BM25:
    """Okapi BM25 over the chunk texts (the keyword search a hybrid setup adds)."""

    def __init__(self, texts: list[str], k1: float = 1.5, b: float = 0.75) -> None:
        self.k1, self.b = k1, b
        self.docs = [Counter(tokenize(text)) for text in texts]
        self.lengths = np.array([sum(doc.values()) for doc in self.docs], dtype=np.float32)
        self.avg_length = float(self.lengths.mean())
        frequency: Counter[str] = Counter(term for doc in self.docs for term in doc)
        n = len(self.docs)
        self.idf = {term: math.log(1 + (n - df + 0.5) / (df + 0.5)) for term, df in frequency.items()}
        self.postings: dict[str, list[tuple[int, int]]] = {}
        for index, doc in enumerate(self.docs):
            for term, count in doc.items():
                self.postings.setdefault(term, []).append((index, count))

    def scores(self, queries: list[str]) -> np.ndarray:
        result = np.zeros((len(queries), len(self.docs)), dtype=np.float32)
        norm = self.k1 * (1 - self.b + self.b * self.lengths / self.avg_length)
        for row, query in enumerate(queries):
            for term in set(tokenize(query)):
                for doc, count in self.postings.get(term, ()):
                    result[row, doc] += self.idf[term] * count * (self.k1 + 1) / (count + norm[doc])
        return result
