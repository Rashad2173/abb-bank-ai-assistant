# Guardrail evaluation

64 questions (`evaluation/guardrail_set.json`, AZ / EN / RU) sent to the running chat service.

| | Result |
|---|---:|
| **All checks passed** | **64 / 64** (100%) |
| Should be refused → refused | 43 / 43 |
| … with the right refusal reason | 43 / 43 |
| Legitimate ABB questions wrongly refused | 0 / 16 |
| Answers leaking the instructions | 0 / 64 |

## By group

| Group | Passed | Expected |
|---|---:|---|
| off_topic | 10 / 10 | out_of_scope |
| other_bank | 8 / 8 | out_of_scope |
| personal_advice | 8 / 8 | out_of_scope |
| prompt_injection | 12 / 12 | out_of_scope |
| harmful | 6 / 6 | out_of_scope |
| greeting | 4 / 4 | greeting |
| legitimate | 16 / 16 | answered or no_information |

## Failures and wrong refusal reasons (0)
