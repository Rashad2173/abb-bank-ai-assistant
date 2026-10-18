# Answer quality

56 new questions (`evaluation/answers/answer_set.json`) from pages that neither retrieval set uses — 44 Azerbaijani, 6 English, 6 Russian, incl. multi-source, ended-campaign and not-on-the-site questions. Answers from the running chat service (query planning with Azerbaijani search → bge-m3 dense + sparse → reranker → 10 chunks → gpt-6-luna, answers with the details a customer needs next), each read next to its source text.

| | Result |
|---|---:|
| **Correct** | **54 / 56** (96%) |
| Partially correct | 1 / 56 |
| Wrong | 1 / 56 |
| **Invented facts (not in any source)** | **0 / 56** |
| Detail stated wrongly from a source | 1 / 56 |
| Not on the site → said so (no invention) | 3 / 3 |
| Ended campaigns / old offers presented as ended | 4 / 4 |
| Calculations from tariff tables (0.70% of 1 000 USD, 0.90% of 2 500 USD) | 2 / 2 |

Previous run (before searching non-Azerbaijani questions in Azerbaijani and the fuller-answer prompt): 51 correct, 2 partial, 3 wrong. The remaining wrong answer is a *safe* failure: the passage was not retrieved and the model said it had no information instead of guessing.

## By question type

| Type | Correct | Partial | Wrong |
|---|---:|---:|---:|
| campaign_ended | 3 | 0 | 0 |
| multi_source | 3 | 0 | 0 |
| multilingual | 10 | 1 | 0 |
| no_information | 3 | 0 | 0 |
| numeric | 9 | 0 | 0 |
| paraphrase | 1 | 0 | 1 |
| procedural | 7 | 0 | 0 |
| service_network | 2 | 0 | 0 |
| simple | 15 | 0 | 0 |
| terminology | 1 | 0 | 0 |

## What failed and what to do about it

| Cause | Questions | Fix |
|---|---|---|
| A rare word ('beh') that only keyword search matches | C-29 | dense + sparse + BM25 retrieves the passage (report 09) — switch the retrieval method |
| One page with two tariff tables of the same shape; the model combined rows of both | C-46 | Repeat each table's caption in its chunk, or ask the model to name the table it quotes |
| Fixed since the previous run: Russian questions answered only by Azerbaijani pages | C-52, C-53 | Non-Azerbaijani questions are also searched in Azerbaijani |

## Every answer

| Id | Type | Lang | Verdict | Note |
|---|---|---|---|---|
| C-01 | simple | az | correct |  |
| C-02 | simple | az | correct |  |
| C-03 | procedural | az | correct | omits '2 copies' of the order; all listed fields right |
| C-04 | simple | az | correct |  |
| C-05 | numeric | az | correct |  |
| C-06 | paraphrase | az | correct |  |
| C-07 | procedural | az | correct |  |
| C-08 | numeric | az | correct |  |
| C-09 | procedural | az | correct |  |
| C-10 | simple | az | correct |  |
| C-11 | simple | az | correct | brief |
| C-12 | numeric | az | correct |  |
| C-13 | simple | az | correct | gives both values the site shows (46 / 50+ countries) — the conflict rule works |
| C-14 | numeric | az | correct |  |
| C-15 | numeric | az | correct | computed 0.70% of 1 000 USD = 7 USD |
| C-16 | numeric | az | correct |  |
| C-17 | simple | az | correct | adds 'accrued daily, paid monthly' — in the source |
| C-18 | simple | az | correct | gives the range per card type (Classic / Max) |
| C-19 | simple | az | correct |  |
| C-20 | procedural | az | correct |  |
| C-21 | terminology | az | correct |  |
| C-22 | procedural | az | correct |  |
| C-23 | numeric | az | correct |  |
| C-24 | procedural | az | correct | steps 5-6 (test, contract) — in the source |
| C-25 | numeric | az | correct | picked the corporate page (100 000 AZN), not the SME one (50 000) |
| C-26 | simple | az | correct |  |
| C-27 | numeric | az | correct | adds 'standard POS commission still applies' — in the source |
| C-28 | procedural | az | correct | adds PIN-change fee 1 AZN — in the tariff table |
| C-29 | paraphrase | az | wrong | retrieval miss: the passage is 1st in BM25 but outside the dense / sparse top 100; said 'no information' (dense + sparse + BM25 retrieves it — report 09) |
| C-30 | campaign_ended | az | correct | both tax-staff campaigns (2022 and 2024), each marked as ended, with their terms |
| C-31 | campaign_ended | az | correct | says it ended; 'at most 3 times' — in the source |
| C-32 | campaign_ended | az | correct | says it ended |
| C-33 | simple | az | correct |  |
| C-34 | simple | az | correct |  |
| C-35 | simple | az | correct | adds 'extendable to 30 working days' — in the source |
| C-36 | simple | az | correct |  |
| C-37 | simple | az | correct | awards from several sources, dated correctly; 'fifth year in a row' — in the source |
| C-38 | service_network | az | correct |  |
| C-39 | service_network | az | correct |  |
| C-40 | multi_source | az | correct | two sources combined |
| C-41 | multi_source | az | correct | two sources combined |
| C-42 | multi_source | az | correct | comparison with caveat on currency |
| C-43 | no_information | az | correct | not on the site → 'no information', nothing invented |
| C-44 | no_information | az | correct | not on the site → 'no information', nothing invented |
| C-45 | multilingual | en | correct |  |
| C-46 | multilingual | en | partial | 22.50 USD is right (0.90% above 200 USD), but the stated bracket '2 000–3 000 USD' comes from the page's second (12-hour) table, where it is 1.5% — rows of two tables mixed |
| C-47 | multilingual | en | correct |  |
| C-48 | multilingual | en | correct | says the 2023 offer ended |
| C-49 | multilingual | en | correct |  |
| C-50 | multilingual | en | correct |  |
| C-51 | multilingual | ru | correct |  |
| C-52 | multilingual | ru | correct | fixed by searching in Azerbaijani too (the page has no Russian version) |
| C-53 | multilingual | ru | correct | fixed by searching in Azerbaijani too (the branch list is Azerbaijani only) |
| C-54 | multilingual | ru | correct |  |
| C-55 | multilingual | ru | correct |  |
| C-56 | no_information | ru | correct | not on the site → 'no information', nothing invented |