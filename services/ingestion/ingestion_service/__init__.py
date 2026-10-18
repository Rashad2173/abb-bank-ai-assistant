"""Ingestion service: uploaded website data → chunks → Milvus.

``POST /v1/ingest`` takes the scraped pages (the format of ``abb_pages.jsonl``)
and starts a job; ``GET /v1/ingest/{job_id}`` reports its progress. A job

1. chunks the pages with the same chunker as the offline pipeline,
2. compares every chunk's content hash with what Milvus holds,
3. embeds only new or changed chunks (inference service) and upserts them,
4. in ``replace`` mode deletes chunks that are no longer in the data; in
   ``append`` mode keeps everything (another source can be added this way).

Uploading the data that is already indexed therefore finishes in seconds.
"""

__version__ = "1.0.0"
