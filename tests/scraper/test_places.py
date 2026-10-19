import pytest

from abb_scraper.extract.places import CityResolver, place_in_address


@pytest.mark.parametrize(
    ("address", "city"),
    [
        ("Zaqatala, Vidadi küçəsi 28a", "Zaqatala"),
        ("Bakı şəhəri, Suraxanı rayonu, Əmircan qəsəbəsi", "Bakı"),
        ("Xətai rayonu, Babək prospekti 10", "Bakı"),  # a district of Baku
        ("Sabunçu qəs, 5", "Bakı"),  # a settlement of Baku
        ("Khurshidbanu Natavan Monument, Baku", "Bakı"),
        ("Abşeron r., Xırdalan ş., Sahə 1287", "Abşeron"),
        ("GƏNCƏ ŞƏH.FƏTƏLİ XAN XOYSKİ KÜÇ", "Gəncə"),  # upper case
        ("Ganca shah Gulustan qas (Oba market 61)", "Gəncə"),  # Latin transliteration
        ("Sumqayt, 9-cu mkr", "Sumqayıt"),  # typo
        ("Gəncə şəh.Nizami rayonu Qəmbər Hüseyinli küç.2", "Gəncə"),  # Gəncə also has a "Nizami" district
        ("Balakən şəh. N.Nərimanov küç 50", "Balakən"),
    ],
)
def test_place_in_address(address, city):
    assert place_in_address(address) == city


def test_street_names_are_not_places():
    assert place_in_address("Babək pr. yolun sol tərəfi") is None
    assert place_in_address("H.Əliyev pr., 73A") is None


def test_unclear_addresses_use_the_nearest_branch():
    resolver = CityResolver(
        [
            ("Bakı, Nizami küçəsi 67", (40.37, 49.84)),
            ("Gəncə, Atatürk prospekti 1", (40.68, 46.36)),
        ]
    )
    assert resolver.city_of("Ş.İ.Xətai pr. Ev 97 (MEQA market)", (40.69, 46.37)) == "Gəncə"
    assert resolver.city_of("Heydər Əliyev prospekti, stadion", (40.40, 49.90)) == "Bakı"
    assert resolver.city_of("Naməlum ünvan") == "Digər"
