"""Manual grading of the answer-quality run → evaluation/reports/07_answer_quality.md (+ .json).

Every answer in ``07_answers_raw.json`` was read next to its source text. Verdicts:

* ``correct``   — answers the question; every stated fact is in the cited source,
* ``partial``   — grounded, but misses or mis-scopes part of what was asked,
* ``wrong``     — does not answer (or answers incorrectly),
* plus a ``hallucination`` flag for any fact not found in the sources.

    python scripts/answer_grades.py
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "evaluation" / "reports" / "07_answers_raw.json"
REPORT = ROOT / "evaluation" / "reports" / "07_answer_quality.md"

# id → (verdict, note). Facts the model added beyond the expected list were checked in the source text.
GRADES = {
    "C-01": ("correct", ""),
    "C-02": ("correct", ""),
    "C-03": ("correct", "omits '2 copies' of the order; all listed fields right"),
    "C-04": ("correct", ""),
    "C-05": ("correct", ""),
    "C-06": ("correct", ""),
    "C-07": ("correct", ""),
    "C-08": ("correct", ""),
    "C-09": ("correct", ""),
    "C-10": ("correct", ""),
    "C-11": ("correct", "brief"),
    "C-12": ("correct", ""),
    "C-13": ("correct", "gives both values the site shows (46 / 50+ countries) — the conflict rule works"),
    "C-14": ("correct", ""),
    "C-15": ("correct", "computed 0.70% of 1 000 USD = 7 USD"),
    "C-16": ("correct", ""),
    "C-17": ("correct", "adds 'accrued daily, paid monthly' — in the source"),
    "C-18": ("correct", "gives the range per card type (Classic / Max)"),
    "C-19": ("correct", ""),
    "C-20": ("correct", ""),
    "C-21": ("correct", ""),
    "C-22": ("correct", ""),
    "C-23": ("correct", ""),
    "C-24": ("correct", "steps 5-6 (test, contract) — in the source"),
    "C-25": ("correct", "picked the corporate page (100 000 AZN), not the SME one (50 000)"),
    "C-26": ("correct", ""),
    "C-27": ("correct", "adds 'standard POS commission still applies' — in the source"),
    "C-28": ("correct", "adds PIN-change fee 1 AZN — in the tariff table"),
    "C-29": (
        "wrong",
        "retrieval miss: the passage is 1st in BM25 but outside the dense / sparse top 100; "
        "said 'no information' (dense + sparse + BM25 retrieves it — report 09)",
    ),
    "C-30": ("correct", "both tax-staff campaigns (2022 and 2024), each marked as ended, with their terms"),
    "C-31": ("correct", "says it ended; 'at most 3 times' — in the source"),
    "C-32": ("correct", "says it ended"),
    "C-33": ("correct", ""),
    "C-34": ("correct", ""),
    "C-35": ("correct", "adds 'extendable to 30 working days' — in the source"),
    "C-36": ("correct", ""),
    "C-37": ("correct", "awards from several sources, dated correctly; 'fifth year in a row' — in the source"),
    "C-38": ("correct", ""),
    "C-39": ("correct", ""),
    "C-40": ("correct", "two sources combined"),
    "C-41": ("correct", "two sources combined"),
    "C-42": ("correct", "comparison with caveat on currency"),
    "C-43": ("correct", "not on the site → 'no information', nothing invented"),
    "C-44": ("correct", "not on the site → 'no information', nothing invented"),
    "C-45": ("correct", ""),
    "C-46": (
        "partial",
        "22.50 USD is right (0.90% above 200 USD), but the stated bracket '2 000–3 000 USD' comes from "
        "the page's second (12-hour) table, where it is 1.5% — rows of two tables mixed",
    ),
    "C-47": ("correct", ""),
    "C-48": ("correct", "says the 2023 offer ended"),
    "C-49": ("correct", ""),
    "C-50": ("correct", ""),
    "C-51": ("correct", ""),
    "C-52": ("correct", "fixed by searching in Azerbaijani too (the page has no Russian version)"),
    "C-53": ("correct", "fixed by searching in Azerbaijani too (the branch list is Azerbaijani only)"),
    "C-54": ("correct", ""),
    "C-55": ("correct", ""),
    "C-56": ("correct", "not on the site → 'no information', nothing invented"),
}
HALLUCINATIONS: set[str] = set()  # facts not in any source: none found
INACCURATE: set[str] = {"C-46"}  # a detail stated wrongly from a source (rows of two tables mixed)


def main() -> None:
    answers = json.loads(RAW.read_text(encoding="utf-8"))
    graded = [
        {**a, "verdict": GRADES[a["id"]][0], "note": GRADES[a["id"]][1], "hallucination": a["id"] in HALLUCINATIONS}
        for a in answers
    ]
    verdicts = Counter(g["verdict"] for g in graded)
    total = len(graded)
    by_type: dict[str, Counter] = {}
    for g in graded:
        by_type.setdefault(g["type"], Counter())[g["verdict"]] += 1

    lines = [
        "# Answer quality",
        "",
        f"{total} new questions (`evaluation/answers/answer_set.json`) from pages that neither retrieval set uses — "
        "44 Azerbaijani, 6 English, 6 Russian, incl. multi-source, ended-campaign and not-on-the-site questions. "
        "Answers from the running chat "
        "service (query planning with Azerbaijani search → bge-m3 dense + sparse → reranker → 10 chunks → gpt-6-luna, "
        "answers with the details a customer needs next), each read next to its source text.",
        "",
        "| | Result |",
        "|---|---:|",
        f"| **Correct** | **{verdicts['correct']} / {total}** ({100 * verdicts['correct'] / total:.0f}%) |",
        f"| Partially correct | {verdicts['partial']} / {total} |",
        f"| Wrong | {verdicts['wrong']} / {total} |",
        f"| **Invented facts (not in any source)** | **{len(HALLUCINATIONS)} / {total}** |",
        f"| Detail stated wrongly from a source | {len(INACCURATE)} / {total} |",
        "| Not on the site → said so (no invention) | 3 / 3 |",
        "| Ended campaigns / old offers presented as ended | 4 / 4 |",
        "| Calculations from tariff tables (0.70% of 1 000 USD, 0.90% of 2 500 USD) | 2 / 2 |",
        "",
        "Previous run (before searching non-Azerbaijani questions in Azerbaijani and the fuller-answer prompt): "
        "51 correct, 2 partial, 3 wrong. The remaining wrong answer is a *safe* failure: the passage was not "
        "retrieved and the model said it had no information instead of guessing.",
        "",
        "## By question type",
        "",
        "| Type | Correct | Partial | Wrong |",
        "|---|---:|---:|---:|",
    ]
    for kind, counts in sorted(by_type.items()):
        lines.append(f"| {kind} | {counts['correct']} | {counts['partial']} | {counts['wrong']} |")
    lines += [
        "",
        "## What failed and what to do about it",
        "",
        "| Cause | Questions | Fix |",
        "|---|---|---|",
        "| A rare word ('beh') that only keyword search matches | C-29 | dense + sparse + BM25 retrieves the passage "
        "(report 09) — switch the retrieval method |",
        "| One page with two tariff tables of the same shape; the model combined rows of both | C-46 | Repeat each "
        "table's caption in its chunk, or ask the model to name the table it quotes |",
        "| Fixed since the previous run: Russian questions answered only by Azerbaijani pages | C-52, C-53 | "
        "Non-Azerbaijani questions are also searched in Azerbaijani |",
        "",
        "## Every answer",
        "",
        "| Id | Type | Lang | Verdict | Note |",
        "|---|---|---|---|---|",
    ]
    for g in graded:
        lines.append(f"| {g['id']} | {g['type']} | {g['lang']} | {g['verdict']} | {g['note']} |")
    REPORT.write_text("\n".join(lines), encoding="utf-8")
    REPORT.with_suffix(".json").write_text(json.dumps(graded, ensure_ascii=False, indent=1), encoding="utf-8")
    print("\n".join(lines[:22]))


if __name__ == "__main__":
    main()
