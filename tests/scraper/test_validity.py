from datetime import UTC, date, datetime

import pytest

from abb_scraper.extract.validity import campaign_validity

FETCHED = datetime(2026, 10, 14, tzinfo=UTC)


@pytest.mark.parametrize(
    "status",
    [
        "Aktiv deyil",
        "Qeyd: Kampaniya müddəti bitmişdir.",
        "Примечание: кампания завершена.",
        "Note* – The campaign has already ended.",
    ],
)
def test_explicit_end_status(status):
    validity = campaign_validity(["Kampaniya", "10.02.2026 - 24.12.2026", status], FETCHED)
    assert validity.is_active is False
    assert (validity.valid_from, validity.valid_until) == (date(2026, 2, 10), date(2026, 12, 24))


def test_without_status_the_end_date_decides():
    assert campaign_validity(["01.06.2026 - 31.12.2026"], FETCHED).is_active is True
    assert campaign_validity(["01.06.2024 - 02.06.2024"], FETCHED).is_active is False


def test_unknown_without_period_or_status():
    assert campaign_validity(["Taksit sayı qədər keşbek qazan!"], FETCHED).is_active is None


def test_end_words_inside_long_terms_do_not_count():
    terms = "Kampaniya şərtləri: ödəniş müddəti bitib, lakin yeni müraciətlər qəbul olunur. " * 3
    assert campaign_validity(["01.06.2026 - 31.12.2026", terms], FETCHED).is_active is True
