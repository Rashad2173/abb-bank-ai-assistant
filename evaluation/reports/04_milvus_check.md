# Milvus retrieval check

9,604 chunks in Milvus (bge-m3 dense + sparse vectors, built-in BM25). Both question sets run through Milvus and compared with the exact search of the benchmark.

* Dense index: HNSW {'M': 16, 'efConstruction': 200}, search ef = 200, inner product (= cosine).
* Sparse: bge-m3 lexical weights, sparse inverted index. BM25: Milvus full-text search over the chunk text with Azerbaijani letters normalised (ə→e, ı/İ→i, accents folded).
* Hybrid methods: Reciprocal Rank Fusion (k = 60) inside Milvus' `hybrid_search`; reranker: bge-reranker-v2-m3 over the top 30.

## Set A (100 questions)

HNSW index recall: **99.7%** of the exact dense top 10 returned by Milvus.

| Method | Complete@5 | R@1 | R@5 | R@10 | MRR@10 | Exact search R@5 |
|---|---:|---:|---:|---:|---:|---:|
| dense | 77/100 | 44% | 80% | 89% | 0.608 | 80% |
| sparse | 64/100 | 31% | 67% | 78% | 0.501 | 67% |
| bm25 | 60/100 | 38% | 64% | 68% | 0.516 | – |
| dense+sparse | 73/100 | 48% | 76% | 84% | 0.633 | 76% |
| dense+bm25 | 72/100 | 48% | 76% | 87% | 0.626 | – |
| dense+sparse+bm25 | 69/100 | 44% | 73% | 85% | 0.602 | – |
| dense+sparse + reranker | 84/100 | 60% | 87% | 94% | 0.742 | – |
| dense+bm25 + reranker | 84/100 | 60% | 87% | 92% | 0.741 | – |

Search latency per question (Milvus only, embedding and reranking excluded): dense 9.5 ms, dense+sparse 9.6 ms, dense+bm25 9.4 ms

## Set B (100 questions)

HNSW index recall: **99.7%** of the exact dense top 10 returned by Milvus.

| Method | Complete@5 | R@1 | R@5 | R@10 | MRR@10 | Exact search R@5 |
|---|---:|---:|---:|---:|---:|---:|
| dense | 76/100 | 48% | 79% | 87% | 0.629 | 80% |
| sparse | 73/100 | 48% | 76% | 84% | 0.626 | 76% |
| bm25 | 54/100 | 32% | 57% | 72% | 0.462 | – |
| dense+sparse | 81/100 | 48% | 84% | 88% | 0.641 | 84% |
| dense+bm25 | 76/100 | 45% | 78% | 86% | 0.614 | – |
| dense+sparse+bm25 | 79/100 | 49% | 82% | 87% | 0.653 | – |
| dense+sparse + reranker | 89/100 | 56% | 90% | 92% | 0.724 | – |
| dense+bm25 + reranker | 90/100 | 56% | 91% | 94% | 0.728 | – |

Search latency per question (Milvus only, embedding and reranking excluded): dense 4.8 ms, dense+sparse 3.7 ms, dense+bm25 4.0 ms
