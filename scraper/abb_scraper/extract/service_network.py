"""Turn the raw service network data into readable documents (in Azerbaijani).

* one document per branch, sub-branch ("şöbə") and office abroad,
* ATMs and payment terminals grouped by city (one document per city),
* an overview with the totals, so questions like "how many branches does ABB
  have?" or "which branches are open on weekends?" can be answered.
"""

from __future__ import annotations

import re
from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Any

from .html_content import Block
from .places import CityResolver
from .text import fingerprint, normalize_text

BASE_URL = "https://abb-bank.az"
BREADCRUMB_ROOT = "Xidmət şəbəkəsi"

_PHONE_RE = re.compile(r"[\d\s()+\-]*\d[\d\s()+\-]*")
_COORDINATES_RE = re.compile(r"\d+\.\d+,\s*\d+\.\d+")
_ASCII = str.maketrans("əğıöüşçƏĞIİÖÜŞÇ", "egiouscEGIIOUSC")

Coordinates = tuple[float, float]


@dataclass
class NetworkDocument:
    url: str
    title: str
    breadcrumbs: list[str]
    blocks: list[Block] = field(default_factory=list)
    coordinates: Coordinates | None = None


def service_network_documents(data: dict[str, Any]) -> list[NetworkDocument]:
    branches = data.get("branches", [])
    cities = CityResolver((b.get("address", ""), coordinates_of(b)) for b in branches)

    filters_by_branch: dict[int, list[str]] = defaultdict(list)
    for filter_title, branch_ids in data.get("branch_filters", {}).items():
        for branch_id in branch_ids:
            filters_by_branch[branch_id].append(filter_title)

    documents = [_overview(data, cities)]
    # The filters refer to branch ids; sub-branches and offices have their own id range.
    documents += [_branch_document(b, "filial", "Filiallar", cities, filters_by_branch[b.get("id")]) for b in branches]
    documents += [_branch_document(b, "sobe", "Şöbələr", cities) for b in data.get("sub_branches", [])]
    documents += [_branch_document(b, "xarici-ofis", "Xaricdəki ofislər", None) for b in data.get("abroad_offices", [])]
    documents += _grouped_by_city(data.get("atms", []), cities, "atm", "Bankomatlar", "ABB bankomatları (ATM)")
    documents += _grouped_by_city(
        data.get("terminals", []), cities, "terminallar", "Ödəniş terminalları", "ABB ödəniş terminalları"
    )
    return documents


def coordinates_of(point: dict[str, Any]) -> Coordinates | None:
    """Branches store ``coordinates: {lat, lng}``, ATMs ``location: {lat, lon}``."""
    raw = point.get("coordinates") or point.get("location") or {}
    lat, lng = raw.get("lat"), raw.get("lng", raw.get("lon"))
    return (float(lat), float(lng)) if lat is not None and lng is not None else None


# --------------------------------------------------------------------------- #


def _overview(data: dict[str, Any], cities: CityResolver) -> NetworkDocument:
    branches, atms = data.get("branches", []), data.get("atms", [])
    terminals = data.get("terminals", [])
    title = "ABB xidmət şəbəkəsi: filiallar, şöbələr, bankomatlar və terminallar"
    blocks = [
        Block(title, 1),
        Block(
            f"ABB-nin {len(branches)} filialı, {len(data.get('sub_branches', []))} şöbəsi "
            f"və xaricdə {len(data.get('abroad_offices', []))} ofisi var."
        ),
        Block(
            f"Bankomatlar (ATM): {len(atms)}; onlardan {sum(bool(a.get('atmCashIn')) for a in atms)}-i "
            f"nağd pul mədaxili (cash-in) qəbul edir, {sum(_is_24_7(a) for a in atms)}-i 24/7 işləyir."
        ),
        Block(f"Ödəniş terminalları: {len(terminals)}."),
    ]
    by_city: dict[str, list[str]] = defaultdict(list)
    for branch in branches:
        by_city[cities.city_of(branch.get("address", ""), coordinates_of(branch))].append(_text(branch.get("title")))
    # Counts are written out: the model miscounts long lists ("how many branches in Baku?").
    blocks += [
        Block("Filiallar şəhərlər üzrə", 2),
        Block(f"Filialı olan şəhər və rayonlar ({len(by_city)}): {', '.join(sorted(by_city))}."),
    ]
    blocks += [Block(f"{city} ({len(names)}): {', '.join(sorted(names))}") for city, names in sorted(by_city.items())]

    names_by_id = {b.get("id"): _text(b.get("title")) for b in branches}
    for filter_title, ids in data.get("branch_filters", {}).items():
        names = sorted(names_by_id[i] for i in ids if i in names_by_id)
        if names:
            blocks += [Block(_text(filter_title), 2), Block(", ".join(names))]
    return NetworkDocument(f"{BASE_URL}/filiallar", title, [BREADCRUMB_ROOT], blocks)


def _branch_document(
    branch: dict[str, Any], url_kind: str, label: str, cities: CityResolver | None, filters: Iterable[str] = ()
) -> NetworkDocument:
    title = _text(branch.get("title")) or label
    address = _text(branch.get("address"))
    coordinates = coordinates_of(branch)
    lines = [
        ("Ünvan", address),
        ("Şəhər", cities.city_of(address, coordinates) if cities and address else ""),
        ("İş saatları", _join(item.get("text") for item in branch.get("work_time") or [])),
        ("Telefon", _join(_phones(item.get("text") for item in branch.get("phone_numbers") or []))),
        ("E-poçt", _join(item.get("text") for item in branch.get("emails") or [])),
        ("Rəhbər", _text(branch.get("director"))),
        ("Yaxın metro stansiyası", _join(_subway(s) for s in branch.get("subways") or [])),
        ("Xidmətlər", _join(_name(s) for s in branch.get("services") or [])),
        ("Siyahılar", _join(filters)),
        ("Filial kodu", str(branch.get("branch_code") or "")),
        ("Xəritədə", _maps_link(coordinates)),
    ]
    blocks = [Block(title, 1)] + [Block(f"{name}: {value}") for name, value in lines if value]
    url = f"{BASE_URL}/filiallar#{url_kind}-{branch.get('id')}"
    return NetworkDocument(url, title, [BREADCRUMB_ROOT, label], blocks, coordinates)


def _grouped_by_city(
    points: list[dict[str, Any]], cities: CityResolver, page: str, label: str, title_prefix: str
) -> list[NetworkDocument]:
    by_city: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for point in points:
        by_city[cities.city_of(point.get("address", ""), coordinates_of(point))].append(point)

    documents = []
    for city, items in sorted(by_city.items()):
        title = f"{title_prefix} — {city}"
        cash_in = sum(bool(p.get("atmCashIn")) for p in items)
        blocks = [
            Block(title, 1),
            Block(f"{city} üzrə {len(items)} nöqtə; onlardan {cash_in}-i nağd pul mədaxili (cash-in) qəbul edir."),
        ]
        blocks += [Block(_point_line(p)) for p in sorted(items, key=lambda p: p.get("address", ""))]
        documents.append(NetworkDocument(f"{BASE_URL}/{page}#{slug(city)}", title, [BREADCRUMB_ROOT, label], blocks))
    return documents


def slug(text: str) -> str:
    """URL-safe ASCII form: "Gəncə" → "gence", "Şəki" → "seki"."""
    return re.sub(r"[^a-z0-9]+", "-", text.translate(_ASCII).lower()).strip("-") or "diger"


def _point_line(point: dict[str, Any]) -> str:
    features = []
    if point.get("atmCashIn"):
        features.append("nağd pul mədaxili (cash-in)")
    if _is_24_7(point):
        features.append("24/7")
    elif _text(point.get("workingTime")).strip(", "):
        features.append(f"iş vaxtı: {_text(point.get('workingTime'))}")
    if point.get("workOnWeekend"):
        features.append("həftə sonu işləyir")
    line = _text(point.get("address"))
    if features:
        line += f" — {', '.join(features)}"
    maps = _maps_link(coordinates_of(point))
    return f"{line} — xəritə: {maps}" if maps else line


def _is_24_7(point: dict[str, Any]) -> bool:
    working_time = fingerprint(_text(point.get("workingTime")))
    return bool(point.get("fullDay")) or working_time in ("24/7", "24 hours")


def _phones(numbers: Iterable[str | None]) -> list[str]:
    """Phone numbers without the junk some records contain (", ", coordinates)."""
    cleaned = (_text(n).strip(", ") for n in numbers)
    return [n for n in cleaned if _PHONE_RE.fullmatch(n) and not _COORDINATES_RE.search(n)]


def _subway(station: dict[str, Any]) -> str:
    name, time = _text(station.get("name")), _text(station.get("time"))
    return f"{name} ({time})" if time else name


def _name(item: Any) -> str:
    if isinstance(item, dict):
        return _text(item.get("title") or item.get("name"))
    return _text(item)


def _maps_link(coordinates: Coordinates | None) -> str:
    return f"https://www.google.com/maps?q={coordinates[0]},{coordinates[1]}" if coordinates else ""


def _join(values: Iterable[str | None]) -> str:
    return "; ".join(v for v in (_text(v) for v in values) if v)


def _text(value: Any) -> str:
    return normalize_text(value) if isinstance(value, str) else ""
