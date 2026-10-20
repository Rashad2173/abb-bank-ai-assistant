# Retrieval without the reranker

The chat service's QueryPlanner + Retriever on live Milvus (dense+sparse+bm25), the same question plans in both modes: re-ranked by bge-reranker-v2-m3 (GPU mode), or Milvus' hybrid order (CPU mode, no reranker). 200 retrieval questions (sets A + B, chunk-level evidence) and 53 answer-quality questions with a known source page.

## Questions with all their evidence among the chunks given to the model

| Mode | top 5 | top 10 | top 15 | top 20 |
|---|---:|---:|---:|---:|
| reranker | 173/200 | 186/200 | 189/200 | 191/200 |
| no reranker | 163/200 | 180/200 | 185/200 | 189/200 |

## Answer set: the source page among the chunks given to the model

| Mode | top 5 | top 10 | top 15 | top 20 |
|---|---:|---:|---:|---:|
| reranker | 47/53 | 52/53 | 52/53 | 52/53 |
| no reranker | 46/53 | 50/53 | 51/53 | 51/53 |

## By question type (all evidence in the top 10)

| Type | reranker | no reranker |
|---|---:|---:|
| multi_source | 21/25 | 17/25 |
| multilingual | 19/23 | 19/23 |
| numeric | 40/41 | 41/41 |
| paraphrase | 30/34 | 28/34 |
| simple | 59/60 | 58/60 |
| terminology | 17/17 | 17/17 |

## Lost without the reranker (top 10): 8; gained: 2 (ABB-Q061, ABB-Q098)

Rank of each evidence passage (– = not in the top 20).

| Id | Type | Question | reranker | no reranker |
|---|---|---|---|---|
| ABB-Q012 | simple | ABB mobile-da onlayn kredit müraciəti imkanını necə söndürmək olar? | 1 | 11 |
| ABB-Q036 | paraphrase | Maaş arayışım yoxdur, amma mağazadan aldığım əşyanın pulunu sonra hissə-hissə ödəmək istəyirəm. “İndi al, sonra ödə” üçün müraciət edə bilərəm? | 8 | 16 |
| ABB-Q085 | multi_source | Ani kredit və Sahibkar krediti üçün maksimum kredit müddətlərini müqayisə edin; kredit xəttini nəzərə almayın. | 5, 2 | –, 4 |
| ABB-Q087 | multi_source | ABB-nin QR kod ödənişi hansı sistemlə işləyir, Mobil POS isə hansı tətbiqdə və cihaz platformasında təqdim olunur? | 2, 7 | 4, 12 |
| ABB-Q088 | multi_source | Filialda adi cari hesab açmaqla tətbiqdən DigiHesab açmağın əsas addımları necə fərqlənir? | 9, 1 | 16, 1 |
| B-039 | multilingual | What can a company do with ABB Internet Banking? | 4 | – |
| B-053 | paraphrase | Gəncədə həftə sonu da işləyən və karta pul yatırmaq olan bankomat haradadır? | 5 | 16 |
| B-092 | multi_source | TamKart Premium Kredit və ABB-Sea Breeze Visa Infinite kartlarında ildə neçə dəfə Fast Track pulsuzdur? | 2, 4 | 20, 2 |
