"""Checks on the model's answer before it reaches the user.

The model decides the scope (answer / refuse / no information) — see
:mod:`prompts`. Here the service enforces what it can verify itself:

* citations must point at sources that were actually given,
* refusals, greetings and "no information" answers carry no sources,
* an answer without any valid citation is flagged (logged and recorded).
"""

from __future__ import annotations

import logging
import re
from collections.abc import Sequence
from dataclasses import dataclass

from .generator import Generation
from .prompts import source_label

log = logging.getLogger(__name__)

_CITATION_RE = re.compile(r"\s?\[(S\d+)\]")


@dataclass
class CheckedAnswer:
    generation: Generation
    cited: list[dict]
    """The chunks the answer cites, in citation order."""
    labels: list[str]
    grounded: bool
    """An "answered" answer that cites at least one real source."""


def check_answer(generation: Generation, chunks: Sequence[dict]) -> CheckedAnswer:
    by_label = {source_label(i): chunk for i, chunk in enumerate(chunks)}
    answered = generation.status == "answered"

    # Labels in the order they appear in the text, then any listed only in source_ids.
    in_text = list(dict.fromkeys(_CITATION_RE.findall(generation.answer)))
    labels = [label for label in dict.fromkeys([*in_text, *generation.source_ids]) if label in by_label]
    unknown = set(in_text) - set(by_label)
    if unknown:
        log.warning("answer cites unknown sources", extra={"labels": sorted(unknown)})
        generation.answer = _CITATION_RE.sub(lambda m: "" if m.group(1) in unknown else m.group(0), generation.answer)

    if not answered:
        labels = []
        generation.answer = _CITATION_RE.sub("", generation.answer)
    grounded = answered and bool(labels)
    if answered and not grounded:
        log.warning("answer without citations", extra={"status": generation.status})
    return CheckedAnswer(
        generation=generation, cited=[by_label[label] for label in labels], labels=labels, grounded=grounded
    )
