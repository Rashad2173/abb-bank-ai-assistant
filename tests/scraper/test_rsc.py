import json

from abb_scraper.extract.rsc import (
    extract_accordion_items,
    extract_flight_payload,
    iter_dicts,
    parse_flight_rows,
)

from .helpers import flight_push, flight_text_row


def test_extract_flight_payload_concatenates_all_chunks():
    html = flight_push('0:{"a":1}\n') + "<p>ignored</p>" + flight_push('1:["x"]\n')
    assert extract_flight_payload(html) == '0:{"a":1}\n1:["x"]\n'


class TestParseFlightRows:
    def test_decodes_json_rows(self):
        rows = parse_flight_rows('0:{"title":"Kredit"}\n1:[1,2]\n')
        assert rows == {"0": {"title": "Kredit"}, "1": [1, 2]}

    def test_text_row_length_is_counted_in_utf8_bytes(self):
        # "ə" and "ş" are 2 bytes each: a char-based parser would cut the text.
        text = "Əmanət şərtləri\nikinci sətir"
        payload = flight_text_row("a", text) + '2:{"after":true}\n'
        rows = parse_flight_rows(payload)
        assert rows["a"] == text
        assert rows["2"] == {"after": True}

    def test_skips_import_and_hint_rows(self):
        rows = parse_flight_rows('1:I["chunk.js"]\n2:HL["font.woff2"]\n3:"ok"\n')
        assert rows == {"3": "ok"}

    def test_ignores_malformed_json(self):
        assert parse_flight_rows("1:{broken\n2:true\n") == {"2": True}


def test_iter_dicts_preserves_document_order():
    tree = {"id": 1, "items": [{"id": 2, "child": {"id": 3}}, {"id": 4}]}
    assert [d["id"] for d in iter_dicts(tree)] == [1, 2, 3, 4]


class TestExtractAccordionItems:
    def test_finds_items_anywhere_in_the_tree(self):
        faq = {"groups": [{"items": [
            {"id": 1, "trigger": "Kimlər kredit ala bilər?", "content": "<p>20 yaşdan yuxarı</p>"},
            {"id": 2, "trigger": "Faiz nə qədərdir?", "content": "<p>10.9%-dən</p>"},
        ]}]}
        rows = parse_flight_rows(f"5:{json.dumps(faq)}\n")
        assert extract_accordion_items(list(rows.values()), rows) == [
            ("Kimlər kredit ala bilər?", "<p>20 yaşdan yuxarı</p>"),
            ("Faiz nə qədərdir?", "<p>10.9%-dən</p>"),
        ]

    def test_resolves_answers_stored_in_text_rows(self):
        payload = flight_text_row("9", "<p>Uzun cavab</p>") + '\n1:{"trigger":"Sual?","content":"$9"}\n'
        rows = parse_flight_rows(payload)
        assert extract_accordion_items(rows["1"], rows) == [("Sual?", "<p>Uzun cavab</p>")]

    def test_searches_only_the_given_scope(self):
        rows = parse_flight_rows(
            '1:{"url":"ferdi/kartlar","sections":[{"trigger":"Bu səhifə?","content":"Bəli"}]}\n'
            '2:{"url":"ferdi","sections":[{"trigger":"Üst səhifə?","content":"Bəli"}]}\n'
        )
        assert extract_accordion_items(rows["1"], rows) == [("Bu səhifə?", "Bəli")]

    def test_drops_duplicate_and_empty_items(self):
        items = [
            {"trigger": "Sual?", "content": "Cavab"},
            {"trigger": "Sual?", "content": "Cavab"},
            {"trigger": "Boş", "content": " "},
        ]
        rows = parse_flight_rows(f"1:{json.dumps(items)}\n")
        assert extract_accordion_items(rows["1"], rows) == [("Sual?", "Cavab")]

    def test_keeps_the_same_question_with_different_answers(self):
        items = [
            {"trigger": "Nə ödənilir?", "content": "KASKO: avtomobilin zərəri"},
            {"trigger": "Nə ödənilir?", "content": "İcbari sığorta: üçüncü şəxslərin zərəri"},
        ]
        rows = parse_flight_rows(f"1:{json.dumps(items, ensure_ascii=False)}\n")
        assert len(extract_accordion_items(rows["1"], rows)) == 2
