"""City of a service point (ATM, terminal, branch) from its address and coordinates.

Addresses in the source data are free text with many spellings ("Gəncə",
"Gence", "GANCA", "Gəncə şəh."), typos ("Sumqayt") and street names that are
also place names ("Babək pr.", "N.Nərimanov küç."). The city is found by:

1. the first known place name in the address (cities, districts, Baku's
   districts and settlements) that is not part of a street name;
2. otherwise the city of the nearest branch (branch addresses are clean),
   using the point's coordinates.
"""

from __future__ import annotations

import math
import re
from collections.abc import Iterable

BAKU = "Bakı"
UNKNOWN = "Digər"

# Cities and districts of Azerbaijan (canonical spelling).
_PLACES = (
    "Abşeron",
    "Ağcabədi",
    "Ağdam",
    "Ağdaş",
    "Ağdərə",
    "Ağstafa",
    "Ağsu",
    "Astara",
    "Babək",
    "Balakən",
    "Bərdə",
    "Beyləqan",
    "Biləsuvar",
    "Cəbrayıl",
    "Cəlilabad",
    "Culfa",
    "Daşkəsən",
    "Füzuli",
    "Gədəbəy",
    "Gəncə",
    "Goranboy",
    "Göyçay",
    "Göygöl",
    "Hacıqabul",
    "İmişli",
    "İsmayıllı",
    "Kəlbəcər",
    "Kəngərli",
    "Kürdəmir",
    "Laçın",
    "Lənkəran",
    "Lerik",
    "Masallı",
    "Mingəçevir",
    "Naftalan",
    "Naxçıvan",
    "Neftçala",
    "Oğuz",
    "Ordubad",
    "Qəbələ",
    "Qax",
    "Qazax",
    "Qobustan",
    "Quba",
    "Qubadlı",
    "Qusar",
    "Saatlı",
    "Sabirabad",
    "Sədərək",
    "Salyan",
    "Samux",
    "Şabran",
    "Şahbuz",
    "Şamaxı",
    "Şəki",
    "Şəmkir",
    "Şərur",
    "Şirvan",
    "Siyəzən",
    "Sumqayıt",
    "Şuşa",
    "Tərtər",
    "Tovuz",
    "Ucar",
    "Xaçmaz",
    "Xankəndi",
    "Xızı",
    "Xocalı",
    "Xocavənd",
    "Yardımlı",
    "Yevlax",
    "Zəngilan",
    "Zaqatala",
    "Zərdab",
)
# Districts and settlements of Baku, and other spellings → canonical name.
_ALIASES = {
    **dict.fromkeys(
        (
            "Bakı",
            "Baku",
            "Binəqədi",
            "Qaradağ",
            "Xəzər",
            "Səbail",
            "Sabunçu",
            "Suraxanı",
            "Nərimanov",
            "Nəsimi",
            "Nizami",
            "Pirallahı",
            "Xətai",
            "Yasamal",
            "Bakıxanov",
            "Bilgəh",
            "Binə",
            "Buzovna",
            "Əmircan",
            "Hövsan",
            "Lökbatan",
            "Mərdəkan",
            "Məştağa",
            "Nardaran",
            "Sahil",
            "Şüvəlan",
            "Zabrat",
            "Ramana",
            "Bülbülə",
            "Badamdar",
            "Biləcəri",
            "Türkan",
            "Zığ",
        ),
        BAKU,
    ),
    "Xırdalan": "Abşeron",
    "Ganca": "Gəncə",
    "Sumqayt": "Sumqayıt",
    "Sumaqyıt": "Sumqayıt",
}
# A place name directly followed by one of these is a street, not the location.
_STREET_MARKERS = frozenset({"pr", "prospekt", "prospekti", "kuc", "kucesi", "k", "kucə", "ave", "avenue", "st", "str"})
_FOLD = str.maketrans("əğıöüşçƏĞIİÖÜŞÇ", "egiouscEGIIOUSC")
_WORD_RE = re.compile(r"[^\W\d_]+")


def _fold(text: str) -> str:
    """ASCII form for matching: "Gəncə" → "gence", "GƏNCƏ" → "gence"."""
    return text.translate(_FOLD).lower()


_LOOKUP: dict[str, str] = {_fold(name): name for name in _PLACES}
_LOOKUP |= {_fold(alias): canonical for alias, canonical in _ALIASES.items()}


def place_in_address(address: str) -> str | None:
    """The first place name mentioned in the address, ignoring street names."""
    words = [_fold(word) for word in _WORD_RE.findall(address)]
    for index, word in enumerate(words):
        if word in _LOOKUP and (index + 1 == len(words) or words[index + 1] not in _STREET_MARKERS):
            return _LOOKUP[word]
    return None


class CityResolver:
    """Resolves cities, falling back to the nearest branch for unclear addresses."""

    def __init__(self, branches: Iterable[tuple[str, tuple[float, float] | None]]) -> None:
        """``branches``: ``(address, (lat, lng))`` of the branches used as reference points."""
        self._reference = [
            (place, coordinates)
            for address, coordinates in branches
            if coordinates and (place := place_in_address(address))
        ]

    def city_of(self, address: str, coordinates: tuple[float, float] | None = None) -> str:
        place = place_in_address(address)
        if place:
            return place
        if coordinates and self._reference:
            return min(self._reference, key=lambda ref: _distance_km(coordinates, ref[1]))[0]
        return UNKNOWN


def _distance_km(a: tuple[float, float], b: tuple[float, float]) -> float:
    """Great-circle (haversine) distance."""
    lat1, lon1, lat2, lon2 = map(math.radians, (*a, *b))
    h = math.sin((lat2 - lat1) / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2
    return 6371 * 2 * math.asin(math.sqrt(h))
