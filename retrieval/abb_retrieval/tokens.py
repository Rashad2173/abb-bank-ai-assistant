"""Token counting with the embedding model's tokenizer."""

from __future__ import annotations

from collections.abc import Callable
from functools import lru_cache

TokenCounter = Callable[[str], int]


def load_token_counter(tokenizer_name: str) -> TokenCounter:
    """A cached ``text -> number of tokens`` function for a Hugging Face tokenizer."""
    from transformers import AutoTokenizer  # heavy import, only when needed

    tokenizer = AutoTokenizer.from_pretrained(tokenizer_name)

    @lru_cache(maxsize=200_000)
    def count(text: str) -> int:
        return len(tokenizer(text, add_special_tokens=False, verbose=False)["input_ids"])

    return count
