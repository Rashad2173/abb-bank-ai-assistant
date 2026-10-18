"""From the user's message to what is searched.

Two problems the retrieval evaluation found:

* **Language.** Some pages exist only in Azerbaijani (the branch list, several
  Q&A pages). A Russian or English question retrieves Russian or English chunks
  and misses them. So non-Azerbaijani questions are searched twice — as asked
  and in Azerbaijani — and the two result lists are fused. The same step also
  fixes Azerbaijani typed without its letters ("kredit ucun senedler") and
  resolves follow-ups ("and in dollars?") using the conversation.
* **Procurement noise.** 3 069 of 9 604 chunks are tender notices; their wording
  ("kart pəstahları") can crowd out the answer to an unrelated question. They
  are searched only when the question is about procurement.

A question in proper Azerbaijani without history or quote needs no LLM call at all.
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import dataclass

from .generator import Generator
from .schemas import Turn

PROCUREMENT_FILTER = 'category != "procurement"'
_PROCUREMENT_RE = re.compile(
    r"tender|satınalma|satın alın|müsabiqə|kotirovka|iddiaçı|təchizatçı|podratçı|procurement|purchas|supplier|"
    r"\bbid|тендер|закуп|поставщик|конкурс|котировк",
    re.IGNORECASE,
)
_AZERBAIJANI_LETTER = "ə"  # in almost every Azerbaijani sentence and in no other language the bank uses


@dataclass
class SearchPlan:
    standalone: str
    """The question, understandable without the conversation — reranking and the response use it."""
    queries: list[str]
    """What Milvus searches: the standalone question, plus its Azerbaijani version when that differs."""
    include_procurement: bool


class QueryPlanner:
    def __init__(self, generator: Generator, expand: bool = True, procurement_filter: bool = True) -> None:
        self.generator = generator
        self.expand = expand
        self.procurement_filter = procurement_filter

    async def plan(self, question: str, history: Sequence[Turn], quoted: bool = False) -> SearchPlan:
        """``quoted``: the message replies to a quoted passage, so it always needs a standalone rewrite."""
        if self.expand and (history or quoted or not is_proper_azerbaijani(question)):
            standalone, azerbaijani = await self.generator.plan_search(question, history)
        else:
            standalone, azerbaijani = question, question
        queries = list(dict.fromkeys(q for q in (standalone, azerbaijani) if q.strip()))
        include = not self.procurement_filter or any(is_about_procurement(q) for q in (question, *queries))
        return SearchPlan(standalone=standalone, queries=queries, include_procurement=include)


def is_proper_azerbaijani(text: str) -> bool:
    return _AZERBAIJANI_LETTER in text.lower()


def is_about_procurement(text: str) -> bool:
    return bool(_PROCUREMENT_RE.search(text))
