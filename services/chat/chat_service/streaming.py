"""The answer text, read out of the model's JSON while it is still being written.

The model answers in one JSON object (strict schema, see :mod:`prompts`), and
streams it as small pieces of JSON text: ``{"``, ``status``, ``":"``,
``answered`` … The user should see the *answer* field as it grows, not the
JSON around it. :class:`AnswerTextStream` is fed the pieces and returns the
newly readable answer text each time.

Strict structured output writes the keys in schema order, so ``status`` is
known before the answer starts — the UI can show a refusal as one from the
first word.
"""

from __future__ import annotations

import json
import re

_ANSWER_START = re.compile(r'"answer"\s*:\s*"')
_STATUS = re.compile(r'"status"\s*:\s*"([a-z_]+)"')


class AnswerTextStream:
    def __init__(self) -> None:
        self._json = ""
        self._answer_start: int | None = None
        self._finished = False
        self._decoded = ""
        self.status: str | None = None

    def feed(self, piece: str) -> str:
        """Add the next piece of the JSON; returns the answer text that became readable."""
        self._json += piece
        if self.status is None and (match := _STATUS.search(self._json)):
            self.status = match.group(1)
        if self._finished:
            return ""
        if self._answer_start is None:
            match = _ANSWER_START.search(self._json)
            if match is None:
                return ""
            self._answer_start = match.end()

        raw = self._json[self._answer_start :]
        end = _closing_quote(raw)
        if end is None:
            raw = _without_partial_escape(raw)
        else:
            raw, self._finished = raw[:end], True
        text = json.loads(f'"{raw}"', strict=False)
        new, self._decoded = text[len(self._decoded) :], text
        return new


def _closing_quote(raw: str) -> int | None:
    """Index of the quote that ends the JSON string, if it has arrived."""
    i = 0
    while i < len(raw):
        if raw[i] == "\\":
            i += 2
        elif raw[i] == '"':
            return i
        else:
            i += 1
    return None


def _without_partial_escape(raw: str) -> str:
    """``raw`` without an escape sequence cut off at its end (``\\``, ``\\u02``, half a surrogate pair)."""
    i = 0
    while i < len(raw):
        if raw[i] != "\\":
            i += 1
            continue
        if i + 1 >= len(raw):
            return raw[:i]
        if raw[i + 1] != "u":
            i += 2
            continue
        if i + 6 > len(raw):
            return raw[:i]
        if 0xD800 <= int(raw[i + 2 : i + 6], 16) <= 0xDBFF:  # high surrogate: needs the low half too
            if i + 12 > len(raw):
                return raw[:i]
            i += 12
        else:
            i += 6
    return raw
