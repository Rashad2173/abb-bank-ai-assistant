import json

import pytest

from chat_service.streaming import AnswerTextStream

ANSWERS = [
    "12 bankomat var [S1].",
    "Kartın illik xidmət haqqı: **10 AZN** [S2].\n\n- Keşbek: 1%\n- Müddət: 5 il",
    'Он сказал: "ABB" — банк\\филиал [S1]',
    "Emoji 🙂 və ə, ı, ş, ç, ğ, ö, ü — İ",
    "",
]


def payload(answer: str) -> dict:
    return {"status": "answered", "refusal_reason": "none", "language": "az", "answer": answer, "source_ids": ["S1"]}


def streamed(pieces) -> tuple[str, AnswerTextStream]:
    stream = AnswerTextStream()
    return "".join(stream.feed(piece) for piece in pieces), stream


@pytest.mark.parametrize("ensure_ascii", [False, True])  # True: every non-ASCII letter as \\uXXXX, emoji as a pair
@pytest.mark.parametrize("answer", ANSWERS)
def test_the_answer_comes_out_exactly_when_fed_one_character_at_a_time(answer, ensure_ascii):
    text, stream = streamed(json.dumps(payload(answer), ensure_ascii=ensure_ascii))
    assert text == answer
    assert stream.status == "answered"


@pytest.mark.parametrize("answer", ANSWERS)
def test_any_split_into_two_pieces_gives_the_same_text(answer):
    raw = json.dumps(payload(answer), ensure_ascii=True)
    for cut in range(len(raw) + 1):
        assert streamed([raw[:cut], raw[cut:]])[0] == answer, cut


def test_the_status_is_known_before_the_answer_starts():
    stream = AnswerTextStream()
    assert stream.feed('{"status":"out_of_scope","refusal_reason":"other_bank",') == ""
    assert stream.status == "out_of_scope"
    assert stream.feed('"language":"az","answer":"Bu ') == "Bu "


def test_text_after_the_answer_is_ignored():
    stream = AnswerTextStream()
    assert stream.feed('{"status":"answered","answer":"A [S1]."') == "A [S1]."
    assert stream.feed(',"source_ids":["S1"]}') == ""
