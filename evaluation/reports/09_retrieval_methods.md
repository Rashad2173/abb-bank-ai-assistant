# Retrieval pipeline: query planning

The chat service's QueryPlanner + Retriever on live Milvus (dense+sparse, dense+bm25, dense+sparse+bm25 → bge-reranker-v2-m3 → top 10 chunks). 200 retrieval questions (sets A + B, chunk-level evidence) and 53 answer-quality questions with a known source page.

| Configuration | All evidence in top 5 | R@5 | R@10 | MRR | R@5 EN | R@5 RU | Source page in context (answer set) |
|---|---:|---:|---:|---:|---:|---:|---:|
| dense+sparse · both (chat service) | 173/200 | 88.5% | 93.8% | 0.734 | 57% | 89% | 51/53 |
| dense+bm25 · both (chat service) | 174/200 | 89.0% | 94.8% | 0.736 | 57% | 89% | 51/53 |
| dense+sparse+bm25 · both (chat service) | 174/200 | 89.0% | 94.0% | 0.737 | 57% | 89% | 52/53 |

Answer set, source page in context, by language: dense+sparse · both (chat service): {'az': '41/42', 'en': '5/6', 'ru': '5/5'}; dense+bm25 · both (chat service): {'az': '42/42', 'en': '4/6', 'ru': '5/5'}; dense+sparse+bm25 · both (chat service): {'az': '42/42', 'en': '5/6', 'ru': '5/5'}
