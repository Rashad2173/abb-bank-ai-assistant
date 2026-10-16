# Embedding benchmark

100 questions (evaluation/abb_100_soru_kaynakli.md) against 9,604 chunks. Exact search over all chunks — no index approximation. Rerankers re-score the top 30 candidates of a method.

* **Recall@k** — share of a question's evidence found in the top k (multi-source questions need all sources).
* **Complete@5** — share of questions with *all* evidence in the top 5.
* **MRR@10** — 1 / rank of the first relevant chunk.

## Results (sorted by Recall@5)

| Method | R@1 | R@3 | R@5 | R@10 | Complete@5 | MRR@10 |
|---|---:|---:|---:|---:|---:|---:|
| **text-embedding-3-large dense + reranker** | 62% | 82% | 88% | 93% | 86% | 0.767 |
| text-embedding-3-large dense + BM25 + reranker | 62% | 81% | 88% | 94% | 85% | 0.761 |
| bge-m3 dense + sparse + reranker | 60% | 80% | 87% | 94% | 84% | 0.742 |
| bge-m3 dense + BM25 + reranker | 60% | 80% | 87% | 92% | 84% | 0.742 |
| multilingual-e5-large-instruct dense + reranker | 61% | 80% | 86% | 92% | 85% | 0.748 |
| bge-m3 dense + reranker | 60% | 78% | 84% | 92% | 82% | 0.740 |
| multilingual-e5-large-instruct dense + BM25 + reranker | 60% | 79% | 84% | 89% | 83% | 0.737 |
| bge-m3 sparse + reranker | 59% | 78% | 83% | 88% | 81% | 0.726 |
| text-embedding-3-large dense | 47% | 74% | 81% | 92% | 77% | 0.647 |
| bge-m3 dense | 44% | 66% | 80% | 89% | 77% | 0.608 |
| multilingual-e5-large-instruct dense | 49% | 74% | 78% | 84% | 74% | 0.651 |
| bge-m3 dense + BM25 | 50% | 66% | 76% | 87% | 72% | 0.648 |
| bge-m3 dense + sparse | 50% | 68% | 76% | 84% | 73% | 0.647 |
| multilingual-e5-large-instruct dense + BM25 | 48% | 68% | 76% | 84% | 72% | 0.637 |
| text-embedding-3-large dense + BM25 | 51% | 72% | 74% | 83% | 70% | 0.662 |
| bge-m3 sparse | 31% | 57% | 67% | 78% | 64% | 0.501 |
| BM25 | 38% | 57% | 62% | 70% | 58% | 0.517 |

## Recall@5 by question type (top 6 methods)

| Method | Simple | Paraphrase | Terminology | Numeric | Multi-source | Multilingual |
|---|---:|---:|---:|---:|---:|---:|
| text-embedding-3-large dense + reranker | 96% | 90% | 100% | 93% | 77% | 60% |
| text-embedding-3-large dense + BM25 + reranker | 96% | 90% | 100% | 93% | 73% | 60% |
| bge-m3 dense + sparse + reranker | 96% | 85% | 100% | 93% | 73% | 60% |
| bge-m3 dense + BM25 + reranker | 96% | 85% | 100% | 93% | 73% | 60% |
| multilingual-e5-large-instruct dense + reranker | 100% | 85% | 100% | 93% | 80% | 30% |
| bge-m3 dense + reranker | 96% | 85% | 93% | 93% | 63% | 60% |

## Recall@5 by question language (top 6 methods)

| Method | az (n=90) | en (n=7) | ru (n=3) |
|---|---:|---:|---:|
| text-embedding-3-large dense + reranker | 92% | 57% | 67% |
| text-embedding-3-large dense + BM25 + reranker | 91% | 57% | 67% |
| bge-m3 dense + sparse + reranker | 90% | 57% | 67% |
| bge-m3 dense + BM25 + reranker | 90% | 57% | 67% |
| multilingual-e5-large-instruct dense + reranker | 92% | 29% | 33% |
| bge-m3 dense + reranker | 87% | 57% | 67% |

## Speed, cost and deployment

| Model | Dimensions | Embedding all chunks | Per question | Cost | Deployment |
|---|---:|---:|---:|---:|---|
| bge-m3 | 1024 | 97 s | 2 ms | free | local model (~2.3 GB); needs ~2–3 GB RAM or a GPU on the server |
| multilingual-e5-large-instruct | 1024 | 116 s | 2 ms | free | local model (~2.2 GB); needs ~2–3 GB RAM or a GPU on the server |
| text-embedding-3-large | 3072 | 178 s | 10 ms | $0.73 (5,611,289 tokens) | hosted API — no model on the server; paid per token, network latency |

Reranker: ~964 ms per question for 30 candidates (local GPU, RTX 4060 Laptop).

## Questions not fully answered in the top 5 by the best method (text-embedding-3-large dense + reranker)

14 of 100.

### ABB-Q010 (simple, az) — first relevant at rank > 50

**Q:** ABB-də əmanət seyfi icarəyə götürmək üçün nə təqdim etməliyəm?

Expected: `8ce01394fd-000` Depozit və əmanət seyfləri › 

Top 3 retrieved:

1. `1a77ba3f38-000` Bank tərəfindən seyf paketlərin satın alınması › 
2. `6bd439de5c-000` Bank tərəfindən seyf avadanlığının satın alınması › 
3. `7e049a30cc-000` ABB yeni rəqəmsal əmanət məhsulunu təqdim etdi! › 

### ABB-Q034 (paraphrase, az) — first relevant at rank > 50

**Q:** Əvvəl tətbiqdən kredit götürməyi özüm bağlamışdım. İndi yenə müraciət etmək istəyirəm, nəyi açmalıyam?

Expected: `9c3a2fdf27-011` Güzəştli Şərtlərlə Tam Onlayn Nağd Kredit › Tez-tez verilən suallar

Top 3 retrieved:

1. `4ab35810cb-010` Krediti olanlara kredit › Tez-tez verilən suallar
2. `4ab35810cb-003` Krediti olanlara kredit › 
3. `74c42ceb6a-012` Mikro sahibkar krediti › Tez-tez verilən suallar

### ABB-Q036 (paraphrase, az) — first relevant at rank > 50

**Q:** Maaş arayışım yoxdur, amma mağazadan aldığım əşyanın pulunu sonra hissə-hissə ödəmək istəyirəm. “İndi al, sonra ödə” üçün müraciət edə bilərəm?

Expected: `3594a36863-006` İndi al, sonra ödə › Tez-tez verilən suallar

Top 3 retrieved:

1. `3594a36863-005` İndi al, sonra ödə › Tez-tez verilən suallar
2. `3594a36863-002` İndi al, sonra ödə › İndi al, sonra ödə xidmətin əsas üstünlükləri:
3. `3594a36863-001` İndi al, sonra ödə › İndi al, sonra ödə: ABB ilə alış-verişi daha rahat planlayın

### ABB-Q061 (numeric, az) — first relevant at rank 9

**Q:** ABB-nin onlayn nağd krediti üzrə maksimum məbləğ və maksimum müddət nə qədərdir?

Expected: `9c3a2fdf27-000` Güzəştli Şərtlərlə Tam Onlayn Nağd Kredit › 

Top 3 retrieved:

1. `fa9c85a0c0-003` İstəyinizə uyğun nağd krediti tam onlayn əldə edin! › Tez-tez verilən suallar
2. `10da5dc569-003` Получите наличный кредит онлайн для ваших нужд! › Часто задаваемые вопросы
3. `4f7fc21d59-004` 1000 AZN kredit › Tez-tez verilən suallar

### ABB-Q078 (multi_source, az) — first relevant at rank 8

**Q:** AZN ilə daha uzunmüddətli əmanət istəyirəm. DigiDeposit və Klassik əmanət üçün göstərilən müddət aralıqlarını müqayisə edin.

Expected: `95ea32e638-000` Yüksək faizli klassik əmanət › ; `b28ff9caed-000` DigiDeposit - Tamamilə rəqəmsal › 

Top 3 retrieved:

1. `96006c9198-000` ABB depozit faizləri 2026: Aylıq, müddətli və onlayn depozit müqayisəsi › 
2. `96006c9198-003` ABB depozit faizləri 2026: Aylıq, müddətli və onlayn depozit müqayisəsi › 
3. `2ae1a248c4-001` “Qış təklifi” depozit kampaniyası başladı! › ABB-də AZN valyutasında 6, 12, 18 və 24 ay müddətinə “Klassik” əmanət və DigiDeposit üzrə yeni kampaniya faizləri tətbiq olunur.

### ABB-Q081 (multi_source, az) — first relevant at rank 5

**Q:** Avans krediti ilə onlayn nağd kreditin müraciətçilərə dair əməkhaqqı və ya pensiya şərtləri necə fərqlənir?

Expected: `9c3a2fdf27-005` Güzəştli Şərtlərlə Tam Onlayn Nağd Kredit › Tez-tez verilən suallar; `f9b14edf31-002` 1000 AZN-dək Avans Krediti › Tez-tez verilən suallar

Top 3 retrieved:

1. `f9b14edf31-000` 1000 AZN-dək Avans Krediti › 
2. `9c3a2fdf27-002` Güzəştli Şərtlərlə Tam Onlayn Nağd Kredit › 
3. `9c3a2fdf27-008` Güzəştli Şərtlərlə Tam Onlayn Nağd Kredit › Tez-tez verilən suallar

### ABB-Q084 (multi_source, az) — first relevant at rank 2

**Q:** Travel Card Visa Signature və ABB–Sea Breeze Visa Platinum ilə lounge zallarından illik neçə dəfə istifadə etmək olar?

Expected: `8b1765f46a-000` ABB - Sea Breeze Visa Platinum › ; `8b1765f46a-001` ABB - Sea Breeze Visa Platinum › ; `ee1763e0d3-000` Travel Card Visa Signature › ; `ee1763e0d3-003` Travel Card Visa Signature › Bu kartı digərlərindən fərqləndirən səyahət imtiyazları nələrdir?

Top 3 retrieved:

1. `587f89743f-000` Lounge zallarına giriş › 
2. `ee1763e0d3-003` Travel Card Visa Signature › Bu kartı digərlərindən fərqləndirən səyahət imtiyazları nələrdir? ✅
3. `d71df3ecdd-000` ABB-AZAL Miles ilə bu yay ikiqat gözəl keçəcək! › 

### ABB-Q086 (multi_source, az) — first relevant at rank 1

**Q:** Onlayn mağazam üçün ePOS ilə satış nöqtəsində Mobil POS arasında əsas istifadə fərqi nədir?

Expected: `ae02d9c0d9-000` Mobil POS › ; `fc0edbd4b3-000` Elektron ticarət (ePOS) › 

Top 3 retrieved:

1. `fc0edbd4b3-000` Elektron ticarət (ePOS) ›  ✅
2. `2bba9fa4f4-000` E-commerce (ePOS) › 
3. `c5c34abd53-001` Mikro sahibkarlar üçün ödəniş həlləri › Tez-tez verilən suallar

### ABB-Q087 (multi_source, az) — first relevant at rank 1

**Q:** ABB-nin QR kod ödənişi hansı sistemlə işləyir, Mobil POS isə hansı tətbiqdə və cihaz platformasında təqdim olunur?

Expected: `332f20e950-000` QR kod › ; `332f20e950-001` QR kod › ; `ae02d9c0d9-000` Mobil POS › 

Top 3 retrieved:

1. `332f20e950-001` QR kod ›  ✅
2. `401aef0fa7-000` ABB müştərilər üçün AniPay inteqrasiyalı yeni QR ödəniş həllini təqdim etdi! › 
3. `1ef7e8e2f5-001` QR code › 

### ABB-Q088 (multi_source, az) — first relevant at rank 1

**Q:** Filialda adi cari hesab açmaqla tətbiqdən DigiHesab açmağın əsas addımları necə fərqlənir?

Expected: `83db745bf5-000` DigiHesab - Etibarlı və rəqəmsal › ; `84d4fa84f0-000` Bir neçə valyutada cari hesab › 

Top 3 retrieved:

1. `83db745bf5-000` DigiHesab - Etibarlı və rəqəmsal ›  ✅
2. `ee3c77f9ec-000` DigiHesab Max - hesab qalığından qazanın › 
3. `44d6554f51-000` DigiHesab — надежный и цифровой › 

### ABB-Q091 (multilingual, en) — first relevant at rank 14

**Q:** When are monthly instalments for a TamKart Max purchase due, and in which month do repayments start?

Expected: `ded8343d30-010` TamKart Max › Tez-tez verilən suallar

Top 3 retrieved:

1. `fe3d86ea7c-013` TamKart Max › Frequently asked questions
2. `b91f76e051-000` Buy Now, Pay in Summer! › 
3. `a92de21ccf-009` TamKart Max › Часто задаваемые вопросы

### ABB-Q097 (multilingual, ru) — first relevant at rank 8

**Q:** До какого момента нужно завершить уровни Fayda Max, чтобы получить награды в следующем месяце?

Expected: `13f45074a6-000` Fayda Max təkmilləşdirilmiş keşbek › 

Top 3 retrieved:

1. `705b4b8a1f-000` Fayda Max Subscription program by Bank ABB › 
2. `a91ea7edd8-000` Fayda Max повышенный кешбэк › 
3. `e7b5068628-000` Банк АВВ представляет новую программу лояльности – "Fayda Max"! › 

### ABB-Q098 (multilingual, en) — first relevant at rank 15

**Q:** After a purchase with TamKart Max at a partner store, how can I extend the instalment term and what is the deadline?

Expected: `ded8343d30-011` TamKart Max › Tez-tez verilən suallar

Top 3 retrieved:

1. `fe3d86ea7c-010` TamKart Max › Frequently asked questions
2. `fe3d86ea7c-005` TamKart Max › Frequently asked questions
3. `fe3d86ea7c-000` TamKart Max › 

### ABB-Q100 (multilingual, en) — first relevant at rank 16

**Q:** What security measures does ABB describe for Internet Banking transactions?

Expected: `4620f40a31-004` İnternet Banking - sizə bir addım daha yaxın › Tez-tez verilən suallar

Top 3 retrieved:

1. `0ad22c8fc4-008` ABB mobile Privacy Policy › Rules of use for Mobile and Internet banking > User rights and responsibilities:
2. `358b8d7960-002` İnternet bankçılıq › Tez-tez verilən suallar
3. `0180ef9381-000` ABB növbəti dəfə yüksək təhlükəsizlik sertifikatı aldı! › 

