# Guardrail evaluation

80 questions (`evaluation/guardrail/guardrail_set_independent.json`) sent to the running chat service.

| | Result |
|---|---:|
| **All checks passed** | **80 / 80** (100%) |
| Should be refused → refused | 52 / 52 |
| … with the right refusal reason | 52 / 52 |
| Legitimate ABB questions wrongly refused | 0 / 20 |
| Answers leaking the instructions | 0 / 80 |

## By group

| Group | Passed | Expected |
|---|---:|---|
| off_topic | 10 / 10 | out_of_scope |
| other_bank | 10 / 10 | out_of_scope |
| personal_advice | 10 / 10 | out_of_scope |
| prompt_injection | 16 / 16 | out_of_scope |
| harmful | 10 / 10 | out_of_scope |
| greeting | 4 / 4 | greeting |
| legitimate | 20 / 20 | answered or no_information |

## Failures and wrong refusal reasons (0)
