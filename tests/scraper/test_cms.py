import pytest

from abb_scraper.extract.cms import KnownText, component_blocks, find_page_entity


def render(sections: list, known: tuple[str, ...] = (), rows: dict | None = None) -> list[tuple[str, int | None]]:
    entity = {"url": "ferdi/kartlar", "sections": sections}
    blocks = component_blocks(entity, rows or {}, html_texts=known)
    return [(b.text, b.heading_level) for b in blocks]


class TestKnownText:
    def test_ignores_case_spacing_and_list_markers(self):
        known = KnownText(["Əmanət məbləği vaxtından əvvəl çıxarıldıqda faiz ödənilmir."])
        assert "1. əmanət  məbləği vaxtından əvvəl çıxarıldıqda faiz ödənilmir." in known
        assert "- Əmanət məbləği vaxtından əvvəl çıxarıldıqda faiz ödənilmir." in known

    def test_long_lines_inside_a_longer_html_block_are_known(self):
        known = KnownText(["Birinci cümlə. Kart müddəti 1 ildən çox olduqda uzadılır. Üçüncü cümlə."])
        assert "Kart müddəti 1 ildən çox olduqda uzadılır." in known

    def test_short_lines_must_match_exactly(self):
        known = KnownText(["İllik faiz dərəcəsi 22%-dən başlayır"])
        assert "22%" not in known


class TestFindPageEntity:
    @pytest.fixture
    def rows(self):
        page = {"url": "ferdi/kartlar/tam", "locale": "az", "sections": [{"id": 1}],
                "parent": {"url": "ferdi/kartlar", "locale": "az", "sections": [{"id": 2}]}}
        return {"1": ["$", "div", None, {"page": page}]}

    def test_returns_the_entity_of_the_requested_page(self, rows):
        assert find_page_entity(rows, "/ferdi/kartlar/tam/", "az")["sections"] == [{"id": 1}]

    def test_can_find_a_parent_entity_by_its_own_path(self, rows):
        assert find_page_entity(rows, "ferdi/kartlar", "az")["sections"] == [{"id": 2}]

    def test_respects_the_language(self, rows):
        assert find_page_entity(rows, "ferdi/kartlar/tam", "en") is None


def test_tariff_rows_become_label_value_lines():
    tab = {"title": "Tariflər / TamKart Gold / Kredit",  # internal CMS name, must not appear
           "trigger": [{"title": "Tariflər", "__component": "tabs.default-trigger"}],
           "content": [{"__component": "tabs.terms-grid", "terms": [
               {"id": 1, "label": "İllik faiz dərəcəsi", "term": "22%"},
               {"id": 2, "label": "Komissiya", "term": "[Yüklə](https://cdn.abb-bank.az/tarif.pdf)"},
           ]}]}
    blocks = render([{"__component": "ui-sections.spain", "tabs": [tab]}])
    assert blocks == [
        ("Tariflər", 3),
        ("İllik faiz dərəcəsi: 22%", None),
        ("Komissiya: Yüklə", None),
    ]


def test_cards_keep_their_title_as_heading_and_all_their_details():
    """Cards sharing a description or a statistic must each stay complete."""
    card = {"description": "Keşbek qazanın.", "statistics": [{"title": "Kredit limiti", "value": "30 000 AZN"}]}
    section = {"__component": "repeatable-cards.moscow-repeatable", "title": "Kredit kartları",
               "cards": [{"title": "TamKart Gold", **card}, {"title": "TamKart Premium", **card}]}
    assert render([section]) == [
        ("Kredit kartları", 2),
        ("TamKart Gold", 3), ("Keşbek qazanın.", None), ("Kredit limiti: 30 000 AZN", None),
        ("TamKart Premium", 3), ("Keşbek qazanın.", None), ("Kredit limiti: 30 000 AZN", None),
    ]


def test_skips_text_already_rendered_in_html_but_keeps_label_value_pairs_together():
    section = {"__component": "hero-sections.thor", "title": "TamKart Gold",
               "description": "Görünən mətn", "statistics": [
                   {"title": "Kredit limiti", "value": "30 000 AZN"},   # both parts in HTML
                   {"title": "Güzəşt müddəti", "value": "60 günədək"},  # only the label in HTML
               ]}
    known = ("TamKart Gold", "Görünən mətn", "Kredit limiti", "30 000 AZN", "Güzəşt müddəti")
    assert render([section], known) == [("TamKart Gold", 2), ("Güzəşt müddəti: 60 günədək", None)]


def test_ignores_media_buttons_technical_values_faq_and_excluded_components():
    section = {
        "__component": "ui-sections.usa", "title": "Üstünlüklər",
        "image": {"url": "https://cdn.abb-bank.az/a.png", "mime": "image/png", "name": "a.png"},
        "buttons": [{"title": "Ətraflı"}],
        "background": "gray", "layout": "grid", "spacing": {"value": "spacing-400"},
        "items": [{"trigger": "Sual?", "content": "Cavab"}, {"title": "Pulsuz kart"}],
    }
    excluded = {"__component": "tabs.loan-calculator", "title": "Kalkulyator"}
    assert render([section, excluded]) == [("Üstünlüklər", 2), ("Pulsuz kart", None)]


def test_items_whose_only_children_are_media_keep_their_title():
    """E.g. a list of downloadable reports: each item is a title plus a PDF file."""
    pdf = {"url": "https://cdn.abb-bank.az/report.pdf", "mime": "application/pdf", "name": "report.pdf"}
    section = {"__component": "ui-sections.business-account", "title": "Hesabatlar", "items": [
        {"title": "Bank kapitalının strukturu - 2026, I rüb", "file": pdf},
        {"title": "İllik hesabat - 2025", "file": pdf},
    ]}
    assert render([section]) == [
        ("Hesabatlar", 2),
        ("Bank kapitalının strukturu - 2026, I rüb", None),
        ("İllik hesabat - 2025", None),
    ]


def test_numbers_are_content_not_technical_values():
    section = {"__component": "ui-sections.bank-numbers", "title": "Çağrı mərkəzi", "description": "937",
               "theme": "dark", "variant": "spacing-400"}
    assert render([section]) == [("Çağrı mərkəzi: 937", None)]


def test_rich_text_bodies_and_row_references():
    rows = {"25": "<table><tr><th>Xidmət</th><th>Çevik</th></tr><tr><td>Hesab açılışı</td><td>✔</td></tr></table>"}
    section = {"__component": "ui-sections.single-table", "title": "Paketlər", "table": "$25",
               "content": [{"body": "<p><strong>Şərtlər</strong></p><ul><li>VÖEN</li></ul>"}]}
    assert render([section], rows=rows) == [
        ("Paketlər", 2),
        ("Xidmət | Çevik", None),
        ("Hesab açılışı | ✔", None),
        ("Şərtlər", None),
        ("- VÖEN", None),
    ]


def test_split_headings_are_joined():
    section = {"__component": "ui-sections.find-out-your-credit-limit",
               "heading_before": "Kredit", "heading_gradient": "limitinizi", "heading_after": "öyrənin",
               "description": "70 000 AZN-dək"}
    assert render([section]) == [("Kredit limitinizi öyrənin: 70 000 AZN-dək", None)]
