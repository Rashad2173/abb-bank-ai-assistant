# Embedding benchmark

100 questions (evaluation/retrieval/question_set_b.json) against 9,604 chunks. Exact search over all chunks — no index approximation. Rerankers re-score the top 30 candidates of a method.

* **Recall@k** — share of a question's evidence found in the top k (multi-source questions need all sources).
* **Complete@5** — share of questions with *all* evidence in the top 5.
* **MRR@10** — 1 / rank of the first relevant chunk.

## Results (sorted by Recall@5)

| Method | R@1 | R@3 | R@5 | R@10 | Complete@5 | MRR@10 |
|---|---:|---:|---:|---:|---:|---:|
| **bge-m3 dense + BM25 + reranker** | 56% | 80% | 91% | 94% | 90% | 0.728 |
| bge-m3 dense + reranker | 56% | 80% | 90% | 94% | 89% | 0.727 |
| bge-m3 dense + sparse + reranker | 56% | 80% | 90% | 92% | 89% | 0.724 |
| multilingual-e5-large-instruct dense + reranker | 56% | 82% | 90% | 92% | 88% | 0.734 |
| text-embedding-3-large dense + BM25 + reranker | 55% | 80% | 90% | 91% | 88% | 0.716 |
| multilingual-e5-large-instruct dense + BM25 + reranker | 56% | 80% | 88% | 89% | 86% | 0.721 |
| text-embedding-3-large dense + reranker | 52% | 78% | 86% | 90% | 85% | 0.693 |
| bge-m3 sparse + reranker | 58% | 78% | 86% | 89% | 85% | 0.721 |
| bge-m3 dense + sparse | 50% | 70% | 84% | 88% | 81% | 0.648 |
| bge-m3 dense | 50% | 71% | 80% | 88% | 77% | 0.639 |
| bge-m3 dense + BM25 | 47% | 74% | 80% | 87% | 77% | 0.632 |
| multilingual-e5-large-instruct dense + BM25 | 48% | 70% | 80% | 84% | 79% | 0.621 |
| bge-m3 sparse | 48% | 68% | 76% | 84% | 73% | 0.626 |
| multilingual-e5-large-instruct dense | 51% | 70% | 74% | 82% | 72% | 0.625 |
| text-embedding-3-large dense + BM25 | 43% | 64% | 73% | 84% | 70% | 0.584 |
| text-embedding-3-large dense | 36% | 60% | 68% | 82% | 65% | 0.533 |
| BM25 | 34% | 52% | 57% | 72% | 53% | 0.474 |

## Recall@5 by question type (top 6 methods)

| Method | Simple | Paraphrase | Terminology | Numeric | Multi-source | Multilingual |
|---|---:|---:|---:|---:|---:|---:|
| bge-m3 dense + BM25 + reranker | 97% | 86% | 100% | 96% | 80% | 77% |
| bge-m3 dense + reranker | 97% | 86% | 100% | 96% | 75% | 77% |
| bge-m3 dense + sparse + reranker | 97% | 79% | 100% | 96% | 80% | 77% |
| multilingual-e5-large-instruct dense + reranker | 97% | 93% | 100% | 100% | 85% | 46% |
| text-embedding-3-large dense + BM25 + reranker | 94% | 86% | 100% | 100% | 85% | 62% |
| multilingual-e5-large-instruct dense + BM25 + reranker | 97% | 93% | 100% | 100% | 85% | 31% |

## Recall@5 by question language (top 6 methods)

| Method | az (n=87) | en (n=7) | ru (n=6) |
|---|---:|---:|---:|
| bge-m3 dense + BM25 + reranker | 93% | 57% | 100% |
| bge-m3 dense + reranker | 93% | 57% | 100% |
| bge-m3 dense + sparse + reranker | 92% | 57% | 100% |
| multilingual-e5-large-instruct dense + reranker | 96% | 29% | 67% |
| text-embedding-3-large dense + BM25 + reranker | 94% | 43% | 83% |
| multilingual-e5-large-instruct dense + BM25 + reranker | 96% | 29% | 33% |

## Speed, cost and deployment

| Model | Dimensions | Embedding all chunks | Per question | Cost | Deployment |
|---|---:|---:|---:|---:|---|
| bge-m3 | 1024 | 97 s | 6 ms | free | local model (~2.3 GB); needs ~2–3 GB RAM or a GPU on the server |
| multilingual-e5-large-instruct | 1024 | 116 s | 2 ms | free | local model (~2.2 GB); needs ~2–3 GB RAM or a GPU on the server |
| text-embedding-3-large | 3072 | 178 s | 28 ms | $0.73 (5,611,289 tokens) | hosted API — no model on the server; paid per token, network latency |

Reranker: ~953 ms per question for 30 candidates (local GPU, RTX 4060 Laptop).

## Questions not fully answered in the top 5 by the best method (bge-m3 dense + BM25 + reranker)

10 of 100.

### B-010 (multilingual, en) — first relevant at rank > 50

**Q:** Can I compare flights and prices of different airlines in DigiTravel?

Expected: `d5e641fc96-004` Səyahətiniz üçün rəqəmsal həllər! › Tez-tez verilən suallar

Top 3 retrieved:

1. `d569cc60ae-004` Digital solutions for your travel! › Frequently asked questions
2. `5aa9a91d49-001` Tickets for Turkish Airlines and other airlines are now available with DigiTravel in the ABB mobile app! › 
3. `1a1875ec49-004` Buy Flight Tickets Online - Choose Your Flight Easily with ABB › 

### B-013 (paraphrase, az) — first relevant at rank 6

**Q:** AZAL Miles kartı ilə topladığım milləri başqa aviaşirkətin biletinə xərcləyə bilərəm?

Expected: `358d7ae83d-014` ABB-AZAL Miles MC World Elite / Visa Infinite › Tez-tez verilən suallar

Top 3 retrieved:

1. `47c3dca540-017` ABB-AZAL Miles MC Black Edition / Visa Platinum › Tez-tez verilən suallar
2. `61edd8e44b-020` ABB-AZAL Miles MC World Elite / Visa Infinite › Часто задаваемые вопросы
3. `58c12efa31-018` ABB-AZAL Miles MC Black Edition / Visa Platinum › Часто задаваемые вопросы

### B-018 (numeric, az) — first relevant at rank 6

**Q:** DigiTransfer ilə neçə ölkəyə pul göndərmək olar?

Expected: `96ed40e3df-000` Ölkədaxili və ölkəxarici köçürmələr › 

Top 3 retrieved:

1. `b84df7ed73-001` DigiTransfer/IBAN ilə köçürmə › 
2. `b84df7ed73-007` DigiTransfer/IBAN ilə köçürmə › Tez-tez verilən suallar
3. `b84df7ed73-002` DigiTransfer/IBAN ilə köçürmə › 

### B-024 (multilingual, en) — first relevant at rank > 50

**Q:** What are the advantages of ABB premium bank cards?

Expected: `650486ad4b-009` Tam DigiCard - Tam rəqəmsal, tam real! › Tez-tez verilən suallar

Top 3 retrieved:

1. `d3f4e497fa-001` Payment cards › 
2. `adc7f61b2e-000` ABB - Qarabağ FK MC World Elite › 
3. `a2c59af844-001` Payment cards › 

### B-056 (simple, az) — first relevant at rank > 50

**Q:** Xankəndidə ABB-nin filialı varmı?

Expected: `1da92a2622-000` Xankəndi filialı › 

Top 3 retrieved:

1. `b4becad24d-000` ABB-nin Xankəndi filialı fəaliyyətə başladı! › 
2. `22e3907b40-000` Xankəndidə ABB-nin Çağrı Mərkəzinin açılışı oldu › 
3. `985103439c-000` ABB Xankəndidə Çağrı Mərkəzi yaradır › 

### B-074 (multilingual, en) — first relevant at rank > 50

**Q:** What is a forward contract that ABB offers and what is it used for?

Expected: `e59355d1e8-001` Risklərinizi idarə edin, gəlirlərinizi qoruyun! › Təklif etdiyimiz törəmə maliyyə alətləri

Top 3 retrieved:

1. `a4ad1adac3-000` Bank Guarantee › 
2. `c1dd5f3006-000` Bank Guarantee › 
3. `26bae75610-000` Аванс Кредит до 1 000 AZN › 

### B-083 (paraphrase, az) — first relevant at rank > 50

**Q:** ABB podratçını hansı hallarda qara siyahıya sala bilər?

Expected: `262ff075ac-001` Bank tərəfindən Baş ofis Köhnə binada OTİS liftlərinə aylıq texniki xidmət işlərinin satın alınması › 

Top 3 retrieved:

1. `b08f48851f-001` Bank tərəfindən “Enterprise Vault” proqram təminatı üçün lisenziyaların satın alınması › 
2. `fe3af2e24d-002` Bank tərəfindən IBM SAN Switch-ə 48 ədəd port aktivasiyası üçün lisenziyaların satın alınması › 
3. `db6116bada-001` Bank tərəfindən Kart çiplərinin şifrələnməsi üçün avadanlığın satın alınması › 

### B-096 (multi_source, az) — first relevant at rank 8

**Q:** American Express Gold və ABB-AZAL Miles Visa Platinum kartlarının xidmət haqlarını müqayisə edin.

Expected: `47c3dca540-000` ABB-AZAL Miles MC Black Edition / Visa Platinum › ; `bebf300b82-000` American Express Gold › 

Top 3 retrieved:

1. `7149f90b3d-005` Daha çox kart - daha çox imkan! › Debet kartlar
2. `02fb1429c9-000` ABB-AZAL Miles Visa Platinum Abunəlik › 
3. `7149f90b3d-004` Daha çox kart - daha çox imkan! › Debet kartlar

### B-098 (multi_source, az) — first relevant at rank 1

**Q:** 2021-ci ildə səhiyyə işçiləri üçün nağd kredit kampaniyası ilə hazırkı “Nağd kreditə 7%-dək endirim” kampaniyası nə təklif edir?

Expected: `56b59fe14a-000` ABB-də Nağd Kreditə 7%-dək Endirim! › ; `d518ead8d6-000` ABB-də səhiyyə işçiləri üçün fürsətlər! › 

Top 3 retrieved:

1. `d518ead8d6-000` ABB-də səhiyyə işçiləri üçün fürsətlər! ›  ✅
2. `a80dde9dcb-000` ABB-də səhiyyə işçiləri üçün fürsətlər! › 
3. `67e3b3c04c-000` Новые возможности для работников здравоохранения от ABB! › 

### B-099 (multi_source, az) — first relevant at rank 1

**Q:** Gəncə filialının yeni ünvanı haradır və Gəncədə həftə sonu işləyən cash-in bankomat varmı?

Expected: `6ec5b6c611-004` ABB bankomatları (ATM) — Gəncə › ; `8fd1c6ad03-000` ABB-nin Gəncə filialı yenilənmiş binasında xidmətə başladı › 

Top 3 retrieved:

1. `6ec5b6c611-004` ABB bankomatları (ATM) — Gəncə ›  ✅
2. `6ec5b6c611-002` ABB bankomatları (ATM) — Gəncə › 
3. `6ec5b6c611-000` ABB bankomatları (ATM) — Gəncə › 

