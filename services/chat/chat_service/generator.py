"""The OpenAI calls: question rewriting and the structured answer (at once or streamed)."""

from __future__ import annotations

import json
from collections.abc import AsyncIterator, Sequence
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta

from openai import AsyncOpenAI, OpenAIError

from .prompts import OUTPUT_SCHEMA, SEARCH_PROMPT, SEARCH_SCHEMA, format_sources, system_prompt
from .schemas import Turn
from .streaming import AnswerTextStream

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


@dataclass
class AnswerDelta:
    """A piece of a streamed answer: the newly written answer text, and the status once it is known."""

    text: str
    status: str | None


class Generator:
    def __init__(self, client: AsyncOpenAI, model: str, reasoning_effort: str) -> None:
        self.client = client
        self.model = model
        self.reasoning_effort = reasoning_effort

    async def plan_search(self, question: str, history: Sequence[Turn]) -> tuple[str, str]:
        """``(standalone question, the same in Azerbaijani)`` — see :mod:`query`."""
        response = await self.client.responses.create(
            model=self.model,
            instructions=SEARCH_PROMPT,
            input=[*_messages(history), {"role": "user", "content": question}],
            text={"format": {"type": "json_schema", "name": "search", "schema": SEARCH_SCHEMA, "strict": True}},
            reasoning={"effort": "low"},
            max_output_tokens=1000,
        )
        data = json.loads(response.output_text)
        standalone = data["standalone_question"].strip() or question
        return standalone, data["azerbaijani_question"].strip() or standalone

    async def answer(self, question: str, chunks: Sequence[dict], history: Sequence[Turn]) -> Generation:
        response = await self.client.responses.create(**self._answer_request(question, chunks, history))
        return _generation(response)

    async def answer_stream(
        self, question: str, chunks: Sequence[dict], history: Sequence[Turn]
    ) -> AsyncIterator[AnswerDelta | Generation]:
        """The same answer, streamed: :class:`AnswerDelta` pieces, then the complete :class:`Generation`."""
        stream = await self.client.responses.create(**self._answer_request(question, chunks, history), stream=True)
        text = AnswerTextStream()
        async for event in stream:
            if event.type == "response.output_text.delta":
                yield AnswerDelta(text=text.feed(event.delta), status=text.status)
            elif event.type == "response.completed":
                yield _generation(event.response)
                return
            elif event.type in ("response.failed", "response.incomplete", "error"):
                raise OpenAIError(f"the answer stream ended with {event.type}")
        raise OpenAIError("the answer stream ended without a response")

    def _answer_request(self, question: str, chunks: Sequence[dict], history: Sequence[Turn]) -> dict:
        return {
            "model": self.model,
            "instructions": system_prompt(today()),
            "input": [
                *_messages(history),
                {"role": "user", "content": f"{format_sources(chunks)}\n\nQUESTION: {question}"},
            ],
            "text": {"format": {"type": "json_schema", "name": "abb_answer", "schema": OUTPUT_SCHEMA, "strict": True}},
            "reasoning": {"effort": self.reasoning_effort},
            "max_output_tokens": MAX_ANSWER_TOKENS,
        }


def _generation(response) -> Generation:
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
