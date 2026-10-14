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
            "Məbləğ | Müddət",
            "70 000 AZN | 60 ay",
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


def test_drops_truncated_preview_of_text_that_is_on_the_page():
    article = "VISA Beynəlxalq Ödəniş Sisteminin regiondakı əsas tərəfdaşlarından olan ABB mükafat aldı."
    parsed = parse_html(page_html(f"<p>VISA Beynəlxalq Ödəniş Sisteminin regiondakı...</p><p>{article}</p>"
                                  "<p>Başqa bir mətnin qısa versiyası belə görünür...</p>"))
    # the second preview has no full text on the page, so it is kept
    assert texts(parsed.blocks) == [article, "Başqa bir mətnin qısa versiyası belə görünür..."]


def test_html_fragment_to_text_converts_rich_text():
    fragment = "<ul><li>Əməkhaqqı alanlar üçün:</li></ul><p>Sənədlər <b>elektron</b> yoxlanılır.</p>"
    assert html_fragment_to_text(fragment) == "- Əməkhaqqı alanlar üçün:\nSənədlər elektron yoxlanılır."


def test_html_fragment_to_text_accepts_plain_text():
    assert html_fragment_to_text("  Sadə   mətn ") == "Sadə mətn"
