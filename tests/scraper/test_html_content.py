import pytest

from abb_scraper.extract.html_content import Block, html_fragment_to_text, parse_html

from .helpers import page_html


@pytest.fixture
def parsed(product_page_html):
    return parse_html(product_page_html)


def texts(blocks: list[Block]) -> list[str]:
    return [b.text for b in blocks]


class TestParseProductPage:
    def test_metadata(self, parsed):
        assert parsed.title == "Tam Onlayn Nağd Kredit"  # visible H1 wins over <title>
        assert parsed.description == "Nağd kredit sifarişini onlayn edin."
        assert parsed.lang == "az"
        assert parsed.breadcrumbs == ["Fərdi", "Nağd kredit"]

    def test_full_content_in_reading_order(self, parsed):
        """Streamed segment (S:0) is placed where its placeholder (B:0) was."""
        assert texts(parsed.blocks) == [
            "Tam Onlayn Nağd Kredit",
            "70 000 AZN-dək nağd krediti filiala gəlmədən əldə edin!",
            "10.9%-dən",
            "İllik faiz dərəcəsi",
            "Nağd kreditin üstünlükləri",
            "Rahat şərtlər",
            "Banka gəlmədən tam onlayn əldə edin.",
            "Məbləğ: 70 000 AZN; Müddət: 60 ay",
            "- Zaminsiz",
        ]

    def test_heading_levels_from_tags_and_typography_classes(self, parsed):
        headings = {b.text: b.heading_level for b in parsed.blocks if b.is_heading}
        assert headings == {
            "Tam Onlayn Nağd Kredit": 1,
            "Nağd kreditin üstünlükləri": 2,  # <p class="typography-title-heading-large">
            "Rahat şərtlər": 3,
        }

    def test_excludes_navigation_buttons_forms_and_widgets(self, parsed):
        all_text = " ".join(texts(parsed.blocks))
        for noise in ("Biznes", "İndi sifariş et", "FİN kod", "Səhifəni dəyərləndirin", "Tel:"):
            assert noise not in all_text

    def test_footer_is_kept_separately_with_decoded_email(self, parsed):
        assert texts(parsed.footer_blocks) == ["Tel: +994 12 493 00 91", "E-poçt: info@abb-bank.az"]


def test_title_falls_back_to_the_first_heading_without_h1():
    parsed = parse_html(page_html("<h3>CyberArk lisenziyalarının satın alınması</h3><p>Mətn</p>", title="ABB"))
    assert parsed.title == "CyberArk lisenziyalarının satın alınması"


def test_title_falls_back_to_html_title_without_headings():
    parsed = parse_html(page_html("<p>Mətn</p>", title="ABB | Kartlar"))
    assert parsed.title == "ABB | Kartlar"


def test_drops_carousel_step_numbers_and_separators():
    parsed = parse_html(page_html("<div><p>1</p><p>•</p><p>937</p><p>Addım</p></div>"))
    assert texts(parsed.blocks) == ["937", "Addım"]


class TestTables:
    def test_header_row_in_td_cells_and_empty_cells_keep_their_column(self):
        """The CMS writes headers as <td>; an empty cell must not shift the next value."""
        table = (
            "<table><tr><td>Müddət</td><td>Aylıq</td><td>Müddətin sonu</td></tr>"
            "<tr><td>1 ay</td><td></td><td>6.5%</td></tr>"
            "<tr><td>3 ay</td><td>7%</td><td>7.25%</td></tr></table>"
        )
        assert texts(parse_html(page_html(table)).blocks) == [
            "Müddət: 1 ay; Aylıq: –; Müddətin sonu: 6.5%",
            "Müddət: 3 ay; Aylıq: 7%; Müddətin sonu: 7.25%",
        ]

    def test_two_column_key_value_table_has_no_header(self):
        """Fitch ratings: the first row is data, even though it has no digits."""
        table = (
            "<table><tr><td>Uzunmüddətli defolt reytinqi</td><td>BB+</td></tr>"
            "<tr><td>Qısamüddətli reytinq</td><td>B</td></tr></table>"
        )
        assert texts(parse_html(page_html(table)).blocks) == [
            "Uzunmüddətli defolt reytinqi | BB+",
            "Qısamüddətli reytinq | B",
        ]

    def test_table_without_header_keeps_empty_cells(self):
        table = "<table><tr><td>Komissiya</td><td>1%</td></tr><tr><td>SMS</td><td></td></tr></table>"
        assert texts(parse_html(page_html(table)).blocks) == ["Komissiya | 1%", "SMS | –"]

    def test_merged_header_cells_label_every_column(self):
        table = (
            '<table><tr><th>Kart</th><th colspan="2">Limit</th></tr>'
            "<tr><td>Gold</td><td>AZN</td><td>USD</td></tr></table>"
        )
        assert texts(parse_html(page_html(table)).blocks) == ["Kart: Gold; Limit: AZN; Limit: USD"]

    def test_rows_wider_or_narrower_than_the_header_lose_no_cell(self):
        table = (
            "<table><tr><th>Kart</th><th>Limit</th></tr>"
            "<tr><td>Gold</td><td>5000 AZN</td><td>gündəlik</td></tr>"
            "<tr><td>Classic</td></tr></table>"
        )
        assert texts(parse_html(page_html(table)).blocks) == [
            "Kart: Gold; Limit: 5000 AZN; gündəlik",
            "Kart: Classic; Limit: –",
        ]


class TestInlineSpacing:
    def test_tags_inside_a_word_add_no_space(self):
        parsed = parse_html(page_html("<p>Məxfilik Siyas<span>ə</span>tinin <b>m</b>əqsədi</p>"))
        assert texts(parsed.blocks) == ["Məxfilik Siyasətinin məqsədi"]

    def test_spacing_of_the_html_is_kept(self):
        parsed = parse_html(page_html("<p>Kredit <a href='/x'>kalkulyatoru</a> ilə hesablayın</p>"))
        assert texts(parsed.blocks) == ["Kredit kalkulyatoru ilə hesablayın"]

    def test_line_breaks_and_block_styled_spans_separate_words(self):
        parsed = parse_html(
            page_html(
                "<p>70 000 AZN-dək<br>Məbləğ</p>"
                '<p><span class="lg:block">60 ay</span><span class="block">Müddət</span></p>'
            )
        )
        assert texts(parsed.blocks) == ["70 000 AZN-dək Məbləğ", "60 ay Müddət"]


def test_links_to_documents_keep_their_url():
    parsed = parse_html(page_html('<p>Kart <a href="https://cdn.abb-bank.az/tarif.pdf">tarifləri</a></p>'))
    assert texts(parsed.blocks) == ["Kart tarifləri (https://cdn.abb-bank.az/tarif.pdf)"]


def test_drops_truncated_preview_of_text_that_is_on_the_page():
    article = "VISA Beynəlxalq Ödəniş Sisteminin regiondakı əsas tərəfdaşlarından olan ABB mükafat aldı."
    parsed = parse_html(
        page_html(
            f"<p>VISA Beynəlxalq Ödəniş Sisteminin regiondakı...</p><p>{article}</p>"
            "<p>Başqa bir mətnin qısa versiyası belə görünür...</p>"
        )
    )
    # the second preview has no full text on the page, so it is kept
    assert texts(parsed.blocks) == [article, "Başqa bir mətnin qısa versiyası belə görünür..."]


def test_html_fragment_to_text_converts_rich_text():
    fragment = "<ul><li>Əməkhaqqı alanlar üçün:</li></ul><p>Sənədlər <b>elektron</b> yoxlanılır.</p>"
    assert html_fragment_to_text(fragment) == "- Əməkhaqqı alanlar üçün:\nSənədlər elektron yoxlanılır."


def test_html_fragment_to_text_accepts_plain_text():
    assert html_fragment_to_text("  Sadə   mətn ") == "Sadə mətn"
