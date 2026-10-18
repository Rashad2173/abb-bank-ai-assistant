"""Instructions and output formats for the LLM.

The prompt texts live next to this module as Markdown files, so they can be
read, reviewed and changed without touching code:

* ``system.md`` — answering: scope, grounding and citation rules, refusals (the guardrail),
* ``search.md`` — turning a message into search queries (standalone + Azerbaijani version),
* ``quote.md``  — a message that replies to a quoted part of an earlier answer.

The model answers in one structured JSON object (OpenAI structured outputs,
strict schema), so the service never has to parse free text to find out whether
a question was answered, refused or not covered by the sources.
"""

from __future__ import annotations

from collections.abc import Sequence
from datetime import date
from pathlib import Path

_DIRECTORY = Path(__file__).parent
SYSTEM_PROMPT = (_DIRECTORY / "system.md").read_text(encoding="utf-8")
SEARCH_PROMPT = (_DIRECTORY / "search.md").read_text(encoding="utf-8")
QUOTE_TEMPLATE = (_DIRECTORY / "quote.md").read_text(encoding="utf-8")

SEARCH_SCHEMA = {
    "type": "object",
    "properties": {
        "standalone_question": {"type": "string"},
        "azerbaijani_question": {"type": "string"},
    },
    "required": ["standalone_question", "azerbaijani_question"],
    "additionalProperties": False,
}

OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "status": {"type": "string", "enum": ["answered", "greeting", "out_of_scope", "no_information"]},
        "refusal_reason": {
            "type": "string",
            "enum": ["none", "off_topic", "other_bank", "personal_advice", "prompt_injection", "harmful"],
        },
        "language": {"type": "string", "description": "ISO 639-1 code of the question's language, e.g. az, en, ru"},
        "answer": {"type": "string", "description": "Markdown answer with [S1]-style citations"},
        "source_ids": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["status", "refusal_reason", "language", "answer", "source_ids"],
    "additionalProperties": False,
}


def system_prompt(today: date) -> str:
    return SYSTEM_PROMPT.format(today=today.isoformat())


def with_quote(question: str, quote: str | None) -> str:
    """The user's message as the model sees it — with the quoted passage, if any."""
    if not quote or not quote.strip():
        return question
    return QUOTE_TEMPLATE.format(quote=quote.strip(), question=question).strip()


def source_label(index: int) -> str:
    return f"S{index + 1}"


def format_sources(chunks: Sequence[dict]) -> str:
    """The context block: every chunk with its label and page URL, best first.

    Each chunk's text already starts with its context header (page title,
    section, campaign status, date) — written by the chunker.
    """
    if not chunks:
        return "SOURCES:\n(no sources found)"
    blocks = [f"[{source_label(i)}] {chunk['url']}\n{chunk['text']}" for i, chunk in enumerate(chunks)]
    return "SOURCES:\n\n" + "\n\n---\n\n".join(blocks)
