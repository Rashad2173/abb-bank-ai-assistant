# Answer quality

56 new questions (`evaluation/answers/answer_set.json`) from pages that neither retrieval set uses — 44 Azerbaijani, 6 English, 6 Russian, incl. multi-source, ended-campaign and not-on-the-site questions. Answers from the running chat service (bge-m3 dense + sparse → reranker → 10 chunks → gpt-6-luna), each read next to its source text.

| | Result |
|---|---:|
| **Correct** | **51 / 56** (91%) |
| Partially correct | 2 / 56 |
| Wrong | 3 / 56 |
| **Hallucinated facts** | **0 / 56** |
| Not on the site → said so (no invention) | 3 / 3 |
| Ended campaigns / old offers presented as ended | 4 / 4 |
| Calculations from tariff tables (0.70% of 1 000 USD, 0.90% of 2 500 USD) | 2 / 2 |

All three wrong answers are *safe* failures: the right passage was not retrieved and the model said it had no information instead of guessing.

## By question type

| Type | Correct | Partial | Wrong |
|---|---:|---:|---:|
| campaign_ended | 2 | 1 | 0 |
| multi_source | 3 | 0 | 0 |
| multilingual | 9 | 0 | 2 |
| no_information | 3 | 0 | 0 |
| numeric | 9 | 0 | 0 |
| paraphrase | 1 | 0 | 1 |
| procedural | 7 | 0 | 0 |
| service_network | 2 | 0 | 0 |
| simple | 14 | 1 | 0 |
| terminology | 1 | 0 | 0 |

## What failed and what to do about it

| Cause | Questions | Fix |
|---|---|---|
| Russian / English question whose answer exists only on an Azerbaijani page (the branch list and some Q&A pages have no translation); retrieval returns same-language chunks | C-52, C-53 | Cross-lingual query expansion: also search with an Azerbaijani version of non-Azerbaijani questions and fuse the results |
| Word overlap with procurement notices ('kart məlumatları' ≈ 'kart pəstahları'); 3 069 tender chunks crowd the candidates | C-29 | Down-weight procurement chunks unless the question is about tenders |
| Two pages give different values (46 vs 50+ countries) and only one was retrieved | C-13 | Data issue on the website; the prompt already asks to mention conflicts when both are retrieved |

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
| C-13 | simple | az | partial | says 46 countries (transfers page); the DigiTransfer page says 50+ — conflict not mentioned |
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
| C-29 | paraphrase | az | wrong | retrieval miss: 'kart məlumatları / beh' matched card-blank tenders; said 'no information' |
| C-30 | campaign_ended | az | partial | ambiguous question: answered the newer (2024) tax & customs campaign correctly, not the 2022 one |
| C-31 | campaign_ended | az | correct | says it ended |
| C-32 | campaign_ended | az | correct | says it ended |
| C-33 | simple | az | correct |  |
| C-34 | simple | az | correct |  |
| C-35 | simple | az | correct | adds 'extendable to 30 working days' — in the source |
| C-36 | simple | az | correct |  |
| C-37 | simple | az | correct | lists 6 awards from 5 sources, all dated correctly |
| C-38 | service_network | az | correct |  |
| C-39 | service_network | az | correct |  |
| C-40 | multi_source | az | correct | two sources combined |
| C-41 | multi_source | az | correct | two sources combined |
| C-42 | multi_source | az | correct | comparison with caveat on currency |
| C-43 | no_information | az | correct | not on the site → 'no information', nothing invented |
| C-44 | no_information | az | correct | not on the site → 'no information', nothing invented |
| C-45 | multilingual | en | correct |  |
| C-46 | multilingual | en | correct | computed 0.90% of 2 500 USD = 22.50 USD |
| C-47 | multilingual | en | correct |  |
| C-48 | multilingual | en | correct | says the 2023 offer ended |
| C-49 | multilingual | en | correct |  |
| C-50 | multilingual | en | correct |  |
| C-51 | multilingual | ru | correct |  |
| C-52 | multilingual | ru | wrong | Russian question, answer only on an Azerbaijani page (no Russian version); said 'no information' |
| C-53 | multilingual | ru | wrong | Russian question, branch list exists only in Azerbaijani; said 'no information' |
| C-54 | multilingual | ru | correct |  |
| C-55 | multilingual | ru | correct |  |
| C-56 | no_information | ru | correct | not on the site → 'no information', nothing invented |