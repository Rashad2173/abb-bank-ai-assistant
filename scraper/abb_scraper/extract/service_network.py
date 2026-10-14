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
from .text import fingerprint, normalize_text

BASE_URL = "https://abb-bank.az"
BREADCRUMB_ROOT = "Xidmət şəbəkəsi"

# Districts of Baku — an address naming one of them is in Baku.
_BAKU_DISTRICTS = frozenset(fingerprint(name) for name in (
    "Binəqədi", "Qaradağ", "Xəzər", "Səbail", "Sabunçu", "Suraxanı", "Nərimanov", "Nəsimi",
    "Nizami", "Pirallahı", "Xətai", "Yasamal",
))
_PLACE_SUFFIX_RE = re.compile(r"\s+(şəhəri|şəh\.?|ş\.?|rayonu|r\.?|qəsəbəsi|kəndi)$", re.IGNORECASE)
_PHONE_RE = re.compile(r"[\d\s()+\-]*\d[\d\s()+\-]*")
_COORDINATES_RE = re.compile(r"\d+\.\d+,\s*\d+\.\d+")
_ASCII = str.maketrans("əğıöüşçƏĞIİÖÜŞÇ", "egiouscEGIIOUSC")


@dataclass
class NetworkDocument:
    url: str
    title: str
    breadcrumbs: list[str]
    blocks: list[Block] = field(default_factory=list)


def service_network_documents(data: dict[str, Any]) -> list[NetworkDocument]:
    filters_by_branch: dict[int, list[str]] = defaultdict(list)
    for filter_title, branch_ids in data.get("branch_filters", {}).items():
        for branch_id in branch_ids:
            filters_by_branch[branch_id].append(filter_title)

    documents = [_overview(data)]
    # The filters refer to branch ids; sub-branches and offices have their own id range.
    documents += [_branch_document(b, "filial", "Filiallar", filters_by_branch[b.get("id")])
                  for b in data.get("branches", [])]
    documents += [_branch_document(b, "sobe", "Şöbələr", []) for b in data.get("sub_branches", [])]
    documents += [_branch_document(b, "xarici-ofis", "Xaricdəki ofislər", []) for b in data.get("abroad_offices", [])]
    documents += _grouped_by_city(data.get("atms", []), "atm", "Bankomatlar", "ABB bankomatları (ATM)")
    documents += _grouped_by_city(data.get("terminals", []), "terminallar", "Ödəniş terminalları",
                                  "ABB ödəniş terminalları")
    return documents


def city_of(address: str) -> str:
    """City of an address; Baku district names and spellings ("Bakı ş.", "Baku") map to "Bakı"."""
    parts = [part.strip() for part in address.split(",") if part.strip()]
    if any("baki" in fingerprint(part) or "baku" in fingerprint(part) for part in parts):
        return "Bakı"
    if not parts:
        return "Digər"
    place = _PLACE_SUFFIX_RE.sub("", parts[0]).strip()
    if fingerprint(place) in _BAKU_DISTRICTS:
        return "Bakı"
    return place or "Digər"


# --------------------------------------------------------------------------- #

def _overview(data: dict[str, Any]) -> NetworkDocument:
    branches, atms = data.get("branches", []), data.get("atms", [])
    terminals = data.get("terminals", [])
    title = "ABB xidmət şəbəkəsi: filiallar, şöbələr, bankomatlar və terminallar"
    blocks = [
        Block(title, 1),
        Block(f"ABB-nin {len(branches)} filialı, {len(data.get('sub_branches', []))} şöbəsi "
              f"və xaricdə {len(data.get('abroad_offices', []))} ofisi var."),
        Block(f"Bankomatlar (ATM): {len(atms)}; onlardan {sum(bool(a.get('atmCashIn')) for a in atms)}-i "
              f"nağd pul mədaxili (cash-in) qəbul edir, {sum(_is_24_7(a) for a in atms)}-i 24/7 işləyir."),
        Block(f"Ödəniş terminalları: {len(terminals)}."),
        Block("Filiallar şəhərlər üzrə", 2),
    ]
    by_city: dict[str, list[str]] = defaultdict(list)
    for branch in branches:
        by_city[city_of(branch.get("address", ""))].append(_text(branch.get("title")))
    blocks += [Block(f"{city}: {', '.join(sorted(names))}") for city, names in sorted(by_city.items())]

    names_by_id = {b.get("id"): _text(b.get("title")) for b in branches}
    for filter_title, ids in data.get("branch_filters", {}).items():
        names = sorted(names_by_id[i] for i in ids if i in names_by_id)
        if names:
            blocks += [Block(_text(filter_title), 2), Block(", ".join(names))]
    return NetworkDocument(f"{BASE_URL}/filiallar", title, [BREADCRUMB_ROOT], blocks)


def _branch_document(branch: dict[str, Any], url_kind: str, label: str, filters: list[str]) -> NetworkDocument:
    title = _text(branch.get("title")) or label
    address = _text(branch.get("address"))
    lines = [
        ("Ünvan", address),
        ("Şəhər", city_of(address) if address else ""),
        ("İş saatları", _join(item.get("text") for item in branch.get("work_time") or [])),
        ("Telefon", _join(_phones(item.get("text") for item in branch.get("phone_numbers") or []))),
        ("E-poçt", _join(item.get("text") for item in branch.get("emails") or [])),
        ("Rəhbər", _text(branch.get("director"))),
        ("Yaxın metro stansiyası", _join(_subway(s) for s in branch.get("subways") or [])),
        ("Xidmətlər", _join(_name(s) for s in branch.get("services") or [])),
        ("Siyahılar", _join(filters)),
        ("Filial kodu", str(branch.get("branch_code") or "")),
        ("Xəritədə", _maps_link(branch.get("coordinates"))),
    ]
    blocks = [Block(title, 1)] + [Block(f"{name}: {value}") for name, value in lines if value]
    url = f"{BASE_URL}/filiallar#{url_kind}-{branch.get('id')}"
    return NetworkDocument(url, title, [BREADCRUMB_ROOT, label], blocks)


def _grouped_by_city(points: list[dict[str, Any]], page: str, label: str, title_prefix: str) -> list[NetworkDocument]:
    by_city: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for point in points:
        by_city[city_of(point.get("address", ""))].append(point)

    documents = []
    for city, items in sorted(by_city.items()):
        title = f"{title_prefix} — {city}"
        cash_in = sum(bool(p.get("atmCashIn")) for p in items)
        blocks = [
            Block(title, 1),
            Block(f"{city} üzrə {len(items)} nöqtə; onlardan {cash_in}-i nağd pul mədaxili (cash-in) qəbul edir."),
        ]
        blocks += [Block(_point_line(p)) for p in sorted(items, key=lambda p: p.get("address", ""))]
        documents.append(NetworkDocument(f"{BASE_URL}/{page}#{_slug(city)}", title, [BREADCRUMB_ROOT, label], blocks))
    return documents


def _slug(text: str) -> str:
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
    address = _text(point.get("address"))
    return f"{address} — {', '.join(features)}" if features else address


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


def _maps_link(coordinates: dict[str, Any] | None) -> str:
    if not coordinates or coordinates.get("lat") is None or coordinates.get("lng") is None:
        return ""
    return f"https://www.google.com/maps?q={coordinates['lat']},{coordinates['lng']}"


def _join(values: Iterable[str | None]) -> str:
    return "; ".join(v for v in (_text(v) for v in values) if v)


def _text(value: Any) -> str:
    return normalize_text(value) if isinstance(value, str) else ""
