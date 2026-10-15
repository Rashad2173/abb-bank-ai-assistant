"""Retrieval metrics.

A question can need several pieces of evidence (multi-source questions), and
one piece of evidence can be covered by more than one chunk (overlap, FAQ +
section). So:

* **Recall@k** — share of the question's evidence for which *at least one*
  covering chunk is in the top k. 1.0 means everything needed was retrieved.
* **Complete@k** — 1 if *all* evidence is covered in the top k, else 0.
* **MRR@10** — 1 / rank of the first relevant chunk (0 if none in the top 10).
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field

from .models import Question

K_VALUES = (1, 3, 5, 10)


@dataclass
class QuestionResult:
    question_id: str
    category: str
    lang: str
    recall: dict[int, float]
    complete: dict[int, float]
    reciprocal_rank: float
    first_relevant_rank: int | None
    """1-based rank of the first relevant chunk, ``None`` if not in the ranking."""


@dataclass
class Summary:
    count: int
    recall: dict[int, float]
    complete: dict[int, float]
    mrr: float
    by_category: dict[str, "Summary"] = field(default_factory=dict)
    by_lang: dict[str, "Summary"] = field(default_factory=dict)


def evaluate_question(question: Question, ranking: list[str]) -> QuestionResult:
    """``ranking`` is the list of retrieved chunk ids, best first."""
    positions = {chunk_id: index for index, chunk_id in enumerate(ranking)}
    evidence_ranks = [
        min((positions[cid] for cid in ref.chunk_ids if cid in positions), default=None)
        for ref in question.evidence
    ]
    found = [r for r in evidence_ranks if r is not None]
    first = min(found) + 1 if found else None
    return QuestionResult(
        question_id=question.id,
        category=question.category,
        lang=question.lang,
        recall={k: sum(r is not None and r < k for r in evidence_ranks) / len(evidence_ranks) for k in K_VALUES},
        complete={k: float(all(r is not None and r < k for r in evidence_ranks)) for k in K_VALUES},
        reciprocal_rank=1.0 / first if first and first <= 10 else 0.0,
        first_relevant_rank=first,
    )


def summarize(results: list[QuestionResult], breakdown: bool = True) -> Summary:
    def mean(values: list[float]) -> float:
        return sum(values) / len(values) if values else 0.0

    summary = Summary(
        count=len(results),
        recall={k: mean([r.recall[k] for r in results]) for k in K_VALUES},
        complete={k: mean([r.complete[k] for r in results]) for k in K_VALUES},
        mrr=mean([r.reciprocal_rank for r in results]),
    )
    if breakdown:
        for attribute, target in (("category", summary.by_category), ("lang", summary.by_lang)):
            groups: dict[str, list[QuestionResult]] = defaultdict(list)
            for result in results:
                groups[getattr(result, attribute)].append(result)
            target.update({key: summarize(group, breakdown=False) for key, group in sorted(groups.items())})
    return summary
