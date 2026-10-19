from datetime import date

import pytest

from abb_scraper.extract.dates import published_date
from abb_scraper.extract.text import is_placeholder


@pytest.mark.parametrize(
    ("line", "expected"),
    [
        ("16 İyul, 2024", date(2024, 7, 16)),
        ("15 апреля, 2024", date(2024, 4, 15)),
        ("15 April, 2021", date(2021, 4, 15)),
        ("9 May 2025", date(2025, 5, 9)),
    ],
)
def test_published_date(line, expected):
    assert published_date(["Başlıq", line, "Mətn"]) == expected


def test_published_date_ignores_dates_inside_sentences():
    assert published_date(["Kampaniya 16 İyul, 2024 tarixinə qədər davam edir."]) is None


@pytest.mark.parametrize("text", ["dummy", "test test", "Bura metn yazilmalidir", "Bura mətn yazılmalıdır."])
def test_placeholders(text):
    assert is_placeholder(text)


@pytest.mark.parametrize("text", ["Test sürüşü pulsuzdur", "Kredit kartı nədir?", "Dummy kart yoxdur, real kart var"])
def test_real_text_is_not_a_placeholder(text):
    assert not is_placeholder(text)
