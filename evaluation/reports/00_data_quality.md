# Data quality report

Corpus: `data/abb_pages.jsonl` — 4,223 documents.

## 1. CMS coverage

Every text line (≥ 20 characters) of each page's own CMS components looked up in the output. This measures *presence* of the text, not semantic correctness (table relations, conditions staying with their lists) — those are covered by the structure checks below and by manual review. PDF contents are out of scope; documents are kept as links.

| | Lines | Share |
|---|---:|---:|
| Checked | 15,646 | |
| On the page itself | 15,407 | 98.47% |
| Kept once on a more general page | 222 | 1.42% |
| **Missing** | **17** | **0.11%** |

- https://abb-bank.az/abb-depozit-faizleri — Depozit gəlirinizi indi hesablayın
- https://abb-bank.az/ehtiyac-krediti — Ehtiyac krediti hesablanması
- https://abb-bank.az/en/ehtiyac-krediti — Personal Loan Calculator
- https://abb-bank.az/en/kreditle-kondisoner — Tez-tez verilən suallar
- https://abb-bank.az/en/onlayn-bilet-almaq-abb-ile-aviabiletinizi-rahat-secin — Tez-tez verilən suallar
- https://abb-bank.az/ru/aqro-kredit-muracieti-online-var — Tez-tez verilən suallar
- https://abb-bank.az/ru/ehtiyac-krediti — Калькулятор потребительского кредита
- https://abb-bank.az/ru/kreditle-kondisoner — Tez-tez verilən suallar
- https://abb-bank.az/ru/kreditle-tur-paketleri — О сервисе «Купи сейчас, плати потом»
- https://abb-bank.az/biznes/mikro-biznes/teqib-ve-izleme-sistemi — Təqib və izləmə sistemi haqqında
- https://abb-bank.az/ferdi/kreditler/nagd-kredit — Nağd kredit haqqında sual-cavab
- https://abb-bank.az/ru/ferdi/butun-emeliyyatlar — Валютное регулирование
- https://abb-bank.az/en/biznes/mikro-biznes/biznes-krediti — bura metn yazilmalidir
- https://abb-bank.az/ferdi/butun-kartlar/debet-kartlari/metal-kart — Bura metn yazilmalidir
- https://abb-bank.az/ru/biznes/kicik-ve-orta-biznes/kocurmeler — Валютное регулирование
- https://abb-bank.az/ru/biznes/korporativ/kocurmeler-1 — Валютное регулирование
- https://abb-bank.az/ru/ferdi/kreditler/nagd-kredit — Вопросы и ответы о кредите наличными
## 2. Tables

Rows written as labelled values (`Column: value; …`): 1,026. Empty cells are kept as `–` so values cannot shift columns.

DigiDeposit, 1 month (AZN): `Müddət: 1 ay; Aylıq: –; Müddətin sonu: 6.5%`

## 3. Campaign validity

517 campaign pages: ended 506, active 11.

| Active campaigns (sample) | Period |
|---|---|
| ABB-də Nağd Kreditə 7%-dək Endirim! | 2026-09-03 – 2026-10-31 |
| ABB mobile-da yeni funksiya: Uşaq profili | 2026-07-20 – 2036-06-20 |
| "ABB Play - Master Liqa" ilə futbol həyəcanı qayıdır! | 2026-09-09 – 2027-06-05 |
| Green by Avant-da mənzil sahibi olmaq daha əlçatandır | 2026-08-27 – 2026-10-31 |
| Up to 7% Discount on Cash Loans at ABB! | 2026-09-03 – 2026-10-31 |
| New in ABB mobile: Kids Layout | 2026-07-20 – 2036-06-20 |
| The football excitement is back with “ABB Play – Master League”! | 2026-09-09 – 2027-06-05 |
| Owning a home at Green by Avant is now more accessible | 2026-08-27 – 2026-10-31 |
| Скидка до 7% на Кредит Наличными в ABB! | 2026-09-03 – 2026-10-31 |
| Новая функция в ABB mobile: Детский профиль | 2026-07-20 – 2036-06-20 |

## 4. Linked documents (PDF …)

744 unique documents linked from 114 pages; links are kept inline in the text, e.g.:

- Kapital strukturunda dəyişikliklər haqqında hesabat 2021-ci il, II rüb üzrə — <https://cdn.abb-bank.az/1626433959_Kapital_strukturunda_d_yisiklikl_r_haqqinda_hesabat_30_06_2021_97a7a04196.pdf>
- On different types of off-balance sheet liabilities - 2019, 12 months — <https://cdn.abb-bank.az/1596553896_2019_5_351535b6e1.pdf>
- По отдельным видам внебалансовых обязательств - 2021 год, 12 месяцев — <https://cdn.abb-bank.az/1643200163_Balansdank_nar_oehd_likl_rin_ayri_ayri_noevl_ri_bar_d_31_12_2021_55aae53fca.pdf>
- Распределение кредитов, в том числе просроченных, по экономическим регионам - 2024 г., IV кв. — <https://cdn.abb-bank.az/1736942188_Kreditl_rin_o_cueml_d_n_vaxti_kecmis_kreditl_rin_iqtisadi_rayonlar_uezr_80eddc22fd.pdf>
- Валютный риск - 2026, 3 квартал — <https://cdn.abb-bank.az/Valyuta_riski_9e4c3d6827.pdf>

## 5. FAQ placement

1,607 FAQ items. Items on up to 3 pages stay on each page (product context); 0 widely repeated items are kept once and list the other pages in `also_on`.

AZAL Miles Black Edition card page: 17 FAQ items.

## 6. Service network

219 documents; ATMs grouped into 72 cities (e.g. Abşeron, Astara, Ağcabədi, Ağdam, Ağdaş, Ağstafa, Ağsu, Babək); branch documents carry coordinates: 89.

## 7. Consistency

- Duplicate URLs: 0
- Pages with a generic site title instead of their own: 14
- Documents by language: {'az': 2613, 'en': 539, 'ru': 1071}
- Documents by category: {'procurement': 1321, 'news': 1207, 'campaigns': 517, 'general': 299, 'individual': 223, 'service_network': 219, 'business': 216, 'csr': 140, 'about': 46, 'press_releases': 29, 'home': 3, 'investor_relations': 3}

