"""The OpenAI calls: question rewriting and the structured answer."""

from __future__ import annotations

import json
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta

from openai import AsyncOpenAI

from .prompts import OUTPUT_SCHEMA, REWRITE_PROMPT, format_sources, system_prompt
from .schemas import Turn

BAKU_OFFSET = timedelta(hours=4)  # Azerbaijan: UTC+4 all year
MAX_ANSWER_TOKENS = 4000  # includes the model's reasoning tokens


@dataclass
class Generation:
    status: str
    refusal_reason: str
    language: str
    answer: str
    source_ids: list[str]
    input_tokens: int
    output_tokens: int


class Generator:
    def __init__(self, client: AsyncOpenAI, model: str, reasoning_effort: str) -> None:
        self.client = client
        self.model = model
        self.reasoning_effort = reasoning_effort

    async def rewrite(self, question: str, history: Sequence[Turn]) -> str:
        """A standalone version of ``question`` for retrieval ("and in dollars?" → full question)."""
        if not history:
            return question
        response = await self.client.responses.create(
            model=self.model,
            instructions=REWRITE_PROMPT,
            input=[*_messages(history), {"role": "user", "content": question}],
            reasoning={"effort": "low"},
            max_output_tokens=1000,
        )
        return response.output_text.strip() or question

    async def answer(self, question: str, chunks: Sequence[dict], history: Sequence[Turn]) -> Generation:
        response = await self.client.responses.create(
            model=self.model,
            instructions=system_prompt(today()),
            input=[
                *_messages(history),
                {"role": "user", "content": f"{format_sources(chunks)}\n\nQUESTION: {question}"},
            ],
            text={"format": {"type": "json_schema", "name": "abb_answer", "schema": OUTPUT_SCHEMA, "strict": True}},
            reasoning={"effort": self.reasoning_effort},
            max_output_tokens=MAX_ANSWER_TOKENS,
        )
        data = json.loads(response.output_text)
        return Generation(
            status=data["status"],
            refusal_reason=data["refusal_reason"],
            language=data["language"],
            answer=data["answer"].strip(),
            source_ids=data["source_ids"],
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
        )


def today() -> date:
    return (datetime.now(UTC) + BAKU_OFFSET).date()


def _messages(history: Sequence[Turn]) -> list[dict]:
    return [{"role": turn.role, "content": turn.content} for turn in history]
