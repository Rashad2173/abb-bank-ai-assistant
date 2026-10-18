"""The chunks in Milvus: schema, loading and hybrid search.

One collection, three ways to search it:

* ``dense``  — bge-m3 dense vectors (HNSW index, inner product = cosine),
* ``sparse`` — bge-m3 learned lexical weights (sparse inverted index),
* ``bm25``   — Milvus' built-in full-text search: a BM25 function turns
  ``lexical_text`` into a sparse vector inside Milvus, for chunks and queries.

Hybrid methods ("dense+sparse", "dense+bm25", …) run the searches in one
``hybrid_search`` call and fuse them with Reciprocal Rank Fusion, as the
benchmark did with exact search.
"""

from __future__ import annotations

import hashlib
from collections.abc import Iterator, Sequence
from dataclasses import dataclass

import numpy as np
from pymilvus import AnnSearchRequest, DataType, Function, FunctionType, MilvusClient, RRFRanker

from .embedders.base import Embeddings, SparseVector
from .models import Chunk
from .search import RRF_K
from .text import lexical_form

COLLECTION = "abb_chunks"
DENSE_DIMENSION = 1024  # bge-m3

# Field limits (VARCHAR lengths are bytes). Longest values in the corpus: url 310,
# title 322, text 4 470 bytes; at most 142 related URLs.
_URL_BYTES = 1024
_TEXT_BYTES = 16_384
_MAX_RELATED = 512

HNSW_PARAMS = {"M": 16, "efConstruction": 200}
HNSW_EF = 200
"""Search breadth of HNSW — must be ≥ the number of results asked for."""
BM25_PARAMS = {"bm25_k1": 1.5, "bm25_b": 0.75}  # same as the benchmark's BM25
LEXICAL_ANALYZER = {"tokenizer": "standard", "filter": ["asciifolding", "lowercase"]}
"""Words, accents folded (ş→s, ö→o …), lower-cased. ə and ı/İ are mapped before (see :func:`lexical_form`)."""

METHODS = {
    "dense": ("dense",),
    "sparse": ("sparse",),
    "bm25": ("bm25",),
    "dense+sparse": ("dense", "sparse"),
    "dense+bm25": ("dense", "bm25"),
    "dense+sparse+bm25": ("dense", "sparse", "bm25"),
}

_OUTPUT_FIELDS = ["chunk_id"]
CHUNK_FIELDS = ["chunk_id", "url", "title", "lang", "category", "chunk_type", "is_active", "valid_until",
                "published", "related_urls", "text"]
"""What the chat service shows the LLM and the user."""


@dataclass
class Query:
    """One question in all the forms the searches need."""

    text: str
    dense: np.ndarray
    sparse: SparseVector


class MilvusStore:
    def __init__(self, uri: str = "http://localhost:19530", collection: str = COLLECTION) -> None:
        self.uri = uri
        self.collection = collection
        self._client: MilvusClient | None = None

    @property
    def client(self) -> MilvusClient:
        """Connected on first use, so a service can start before Milvus is up."""
        if self._client is None:
            self._client = MilvusClient(self.uri)
        return self._client

    # ------------------------------------------------------------------ #
    # Loading
    # ------------------------------------------------------------------ #

    def recreate(self) -> None:
        """Drop and create the collection with its indexes (loading replaces everything)."""
        if self.client.has_collection(self.collection):
            self.client.drop_collection(self.collection)
        self.client.create_collection(self.collection, schema=self._schema(), index_params=self._indexes())

    def insert(self, chunks: Sequence[Chunk], embeddings: Embeddings, batch_size: int = 500) -> None:
        self._write(self.client.insert, chunks, embeddings, batch_size)
        self.client.load_collection(self.collection)

    def upsert(self, chunks: Sequence[Chunk], embeddings: Embeddings, batch_size: int = 500) -> None:
        """Insert new chunks, replace changed ones (same chunk id)."""
        self._write(self.client.upsert, chunks, embeddings, batch_size)

    def delete(self, chunk_ids: Sequence[str]) -> None:
        if chunk_ids:
            self.client.delete(self.collection, ids=list(chunk_ids))
            self.client.flush(self.collection)

    def _write(self, write, chunks: Sequence[Chunk], embeddings: Embeddings, batch_size: int) -> None:
        if embeddings.sparse is None:
            raise ValueError("bge-m3 embeddings with sparse vectors are required")
        for start in range(0, len(chunks), batch_size):
            rows = [_row(chunk, embeddings.dense[i], embeddings.sparse[i])
                    for i, chunk in enumerate(chunks[start:start + batch_size], start)]
            write(self.collection, rows)
        self.client.flush(self.collection)

    def count(self) -> int:
        """Exact number of stored chunks (collection statistics still count deleted rows until compaction)."""
        return int(self.client.query(self.collection, filter="", output_fields=["count(*)"])[0]["count(*)"])

    def exists(self) -> bool:
        return self.client.has_collection(self.collection)

    def content_hashes(self) -> dict[str, str]:
        """``chunk_id → content hash`` of everything stored — what ingestion compares against."""
        iterator = self.client.query_iterator(self.collection, batch_size=2000, filter="",
                                              output_fields=["chunk_id", "content_hash"])
        hashes: dict[str, str] = {}
        try:
            while batch := iterator.next():
                hashes |= {row["chunk_id"]: row["content_hash"] for row in batch}
        finally:
            iterator.close()
        return hashes

    def fetch(self, chunk_ids: Sequence[str]) -> list[dict]:
        """The stored chunks (:data:`CHUNK_FIELDS`) in the order of ``chunk_ids``."""
        if not chunk_ids:
            return []
        rows = {row["chunk_id"]: row for row in self.client.get(self.collection, ids=list(chunk_ids),
                                                                 output_fields=CHUNK_FIELDS)}
        return [rows[cid] for cid in chunk_ids if cid in rows]

    # ------------------------------------------------------------------ #
    # Search
    # ------------------------------------------------------------------ #

    def search(self, queries: Sequence[Query], method: str, limit: int, filter: str = "",
               batch_size: int = 50) -> list[list[str]]:
        """Chunk ids per query, best first."""
        searches = METHODS[method]
        results: list[list[str]] = []
        for batch in _batches(queries, batch_size):
            if len(searches) == 1:
                hits = self.client.search(
                    self.collection, data=_data(batch, searches[0]), anns_field=searches[0], limit=limit,
                    filter=filter, search_params=_search_params(searches[0]), output_fields=_OUTPUT_FIELDS,
                )
            else:
                requests = [AnnSearchRequest(data=_data(batch, field), anns_field=field, limit=limit,
                                             param=_search_params(field), expr=filter or None)
                            for field in searches]
                hits = self.client.hybrid_search(self.collection, requests, RRFRanker(RRF_K), limit=limit,
                                                 output_fields=_OUTPUT_FIELDS)
            results += [[hit["entity"]["chunk_id"] for hit in per_query] for per_query in hits]
        return results

    # ------------------------------------------------------------------ #
    # Schema
    # ------------------------------------------------------------------ #

    def _schema(self):
        schema = self.client.create_schema(auto_id=False, description="abb-bank.az chunks")
        schema.add_field("chunk_id", DataType.VARCHAR, is_primary=True, max_length=64)
        schema.add_field("url", DataType.VARCHAR, max_length=_URL_BYTES)
        schema.add_field("title", DataType.VARCHAR, max_length=_URL_BYTES)
        schema.add_field("lang", DataType.VARCHAR, max_length=8)
        schema.add_field("category", DataType.VARCHAR, max_length=32)
        schema.add_field("categories", DataType.ARRAY, element_type=DataType.VARCHAR, max_length=32, max_capacity=16)
        schema.add_field("chunk_type", DataType.VARCHAR, max_length=16)
        schema.add_field("is_active", DataType.BOOL, nullable=True)
        schema.add_field("valid_until", DataType.VARCHAR, max_length=10, nullable=True)  # ISO date
        schema.add_field("published", DataType.VARCHAR, max_length=10, nullable=True)
        schema.add_field("related_urls", DataType.ARRAY, element_type=DataType.VARCHAR, max_length=_URL_BYTES,
                         max_capacity=_MAX_RELATED)
        schema.add_field("text", DataType.VARCHAR, max_length=_TEXT_BYTES)
        schema.add_field("content_hash", DataType.VARCHAR, max_length=16)
        schema.add_field("lexical_text", DataType.VARCHAR, max_length=_TEXT_BYTES,
                         enable_analyzer=True, analyzer_params=LEXICAL_ANALYZER)
        schema.add_field("dense", DataType.FLOAT_VECTOR, dim=DENSE_DIMENSION)
        schema.add_field("sparse", DataType.SPARSE_FLOAT_VECTOR)
        schema.add_field("bm25", DataType.SPARSE_FLOAT_VECTOR)
        schema.add_function(Function(name="lexical_bm25", function_type=FunctionType.BM25,
                                     input_field_names=["lexical_text"], output_field_names=["bm25"]))
        return schema

    def _indexes(self):
        index = self.client.prepare_index_params()
        index.add_index("dense", index_type="HNSW", metric_type="IP", params=HNSW_PARAMS)
        index.add_index("sparse", index_type="SPARSE_INVERTED_INDEX", metric_type="IP")
        index.add_index("bm25", index_type="SPARSE_INVERTED_INDEX", metric_type="BM25", params=BM25_PARAMS)
        for field in ("lang", "category", "chunk_type"):
            index.add_index(field, index_type="INVERTED")
        return index


def _row(chunk: Chunk, dense: np.ndarray, sparse: SparseVector) -> dict:
    return {
        "chunk_id": chunk.chunk_id,
        "url": chunk.url,
        "title": chunk.title,
        "lang": chunk.lang,
        "category": chunk.category,
        "categories": chunk.categories,
        "chunk_type": chunk.chunk_type,
        "is_active": chunk.is_active,
        "valid_until": chunk.valid_until.isoformat() if chunk.valid_until else None,
        "published": chunk.published.isoformat() if chunk.published else None,
        "related_urls": chunk.related_urls,
        "text": chunk.text,
        "content_hash": content_hash(chunk),
        "lexical_text": lexical_form(chunk.text),
        "dense": dense.tolist(),
        "sparse": sparse,
    }


def content_hash(chunk: Chunk) -> str:
    """Changes whenever anything stored for the chunk changes (text or metadata)."""
    payload = chunk.model_dump_json(include={"url", "title", "lang", "category", "categories", "chunk_type",
                                             "is_active", "valid_until", "published", "related_urls", "text"})
    return hashlib.sha256(payload.encode()).hexdigest()[:16]


def _data(queries: Sequence[Query], field: str) -> list:
    if field == "dense":
        return [q.dense.tolist() for q in queries]
    if field == "sparse":
        return [q.sparse for q in queries]
    return [lexical_form(q.text) for q in queries]


def _search_params(field: str) -> dict:
    if field == "dense":
        return {"metric_type": "IP", "params": {"ef": HNSW_EF}}
    return {"metric_type": "BM25" if field == "bm25" else "IP"}


def _batches(items: Sequence, size: int) -> Iterator[Sequence]:
    for start in range(0, len(items), size):
        yield items[start:start + size]
