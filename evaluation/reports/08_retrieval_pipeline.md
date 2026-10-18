# Retrieval pipeline: query planning

The chat service's QueryPlanner + Retriever on live Milvus (bge-m3 dense + sparse → bge-reranker-v2-m3 → top 10 chunks). 200 retrieval questions (sets A + B, chunk-level evidence) and 53 answer-quality questions with a known source page.

| Configuration | All evidence in top 5 | R@5 | R@10 | MRR | R@5 EN | R@5 RU | Source page in context (answer set) |
|---|---:|---:|---:|---:|---:|---:|---:|
| baseline | 173/200 | 88.5% | 93.2% | 0.734 | 57% | 89% | 49/53 |
| procurement filter | 173/200 | 88.5% | 93.2% | 0.733 | 57% | 89% | 49/53 |
| query expansion | 173/200 | 88.5% | 93.8% | 0.733 | 57% | 89% | 51/53 |
| both (chat service) | 173/200 | 88.5% | 93.8% | 0.732 | 57% | 89% | 51/53 |

Answer set, source page in context, by language: baseline: {'az': '41/42', 'en': '5/6', 'ru': '3/5'}; procurement filter: {'az': '41/42', 'en': '5/6', 'ru': '3/5'}; query expansion: {'az': '41/42', 'en': '5/6', 'ru': '5/5'}; both (chat service): {'az': '41/42', 'en': '5/6', 'ru': '5/5'}
