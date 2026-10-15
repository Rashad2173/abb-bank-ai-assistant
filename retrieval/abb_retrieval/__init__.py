"""Retrieval for the ABB assistant: chunking, embedding benchmark and Milvus indexing.

1. **chunk**     — split ``data/abb_pages.jsonl`` into retrieval chunks.
2. **evalset**   — turn the question set into machine-readable form and map
   every question to the chunks that contain its evidence.
3. **benchmark** — embed all chunks with each candidate model and measure how
   often the right chunk is retrieved (Recall@k, MRR).
4. **index**     — store the chunks with the chosen model in Milvus.
"""
