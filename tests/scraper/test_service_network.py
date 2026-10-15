import json
from dataclasses import replace

import httpx
import pytest
import respx

from abb_scraper.extract.service_network import service_network_documents
from abb_scraper.service_network import ServiceNetworkError, fetch_service_network

BASE = "https://abb-bank.az"

BRANCH = {
    "id": 288, "title": "Zaqatala filialı", "address": "Zaqatala, Vidadi küçəsi 28a", "director": "Qalib Tahirzadə",
    "branch_code": 269, "coordinates": {"lat": 41.62, "lng": 46.64},
    "work_time": [{"text": "Bazar ertəsi – Cümə: 09:00-17:00"}],
    "phone_numbers": [{"text": "(+994 12) 493 00 91"}, {"text": " 937"}, {"text": ", "},
                      {"text": "40.11618294614122,48.10036742797913"}],
    "subways": [], "services": [], "emails": [],
}
DATA = {
    "fetched_at": "2026-10-14T17:00:00+00:00",
    "branches": [BRANCH, {**BRANCH, "id": 1, "title": "Nərimanov filialı", "address": "Bakı ş., Nərimanov r."}],
    "sub_branches": [{"id": 288, "title": "BP şöbəsi", "address": "Bakı, Neftçilər prospekti 153"}],
    "abroad_offices": [],
    "branch_filters": {"Həftəsonu işləyən filiallar": [288]},
    "atms": [
        {"address": "Gəncə ş., Atatürk prospekti 1", "atmCashIn": True, "fullDay": True,
         "location": {"lat": 40.68, "lon": 46.36}},
        {"address": "GANCA, Nizami küçəsi 5", "atmCashIn": False, "workOnWeekend": True},
    ],
    "terminals": [],
}


class TestDocuments:
    @pytest.fixture
    def documents(self):
        return {doc.url: doc for doc in service_network_documents(DATA)}

    def test_branch_document_has_labelled_details(self, documents):
        doc = documents[f"{BASE}/filiallar#filial-288"]
        assert doc.title == "Zaqatala filialı"
        assert [b.text for b in doc.blocks] == [
            "Zaqatala filialı",
            "Ünvan: Zaqatala, Vidadi küçəsi 28a",
            "Şəhər: Zaqatala",
            "İş saatları: Bazar ertəsi – Cümə: 09:00-17:00",
            "Telefon: (+994 12) 493 00 91; 937",  # junk entries (", ", coordinates) are dropped
            "Rəhbər: Qalib Tahirzadə",
            "Siyahılar: Həftəsonu işləyən filiallar",
            "Filial kodu: 269",
            "Xəritədə: https://www.google.com/maps?q=41.62,46.64",
        ]

    def test_branch_filters_do_not_leak_to_sub_branches_with_the_same_id(self, documents):
        texts = [b.text for b in documents[f"{BASE}/filiallar#sobe-288"].blocks]
        assert not any(t.startswith("Siyahılar") for t in texts)

    def test_atms_are_grouped_by_city_whatever_the_spelling(self, documents):
        doc = documents[f"{BASE}/atm#gence"]
        assert [b.text for b in doc.blocks] == [
            "ABB bankomatları (ATM) — Gəncə",
            "Gəncə üzrə 2 nöqtə; onlardan 1-i nağd pul mədaxili (cash-in) qəbul edir.",
            "GANCA, Nizami küçəsi 5 — həftə sonu işləyir",
            "Gəncə ş., Atatürk prospekti 1 — nağd pul mədaxili (cash-in), 24/7"
            " — xəritə: https://www.google.com/maps?q=40.68,46.36",
        ]

    def test_branch_documents_carry_coordinates(self, documents):
        assert documents[f"{BASE}/filiallar#filial-288"].coordinates == (41.62, 46.64)

    def test_overview_has_totals_and_filters(self, documents):
        texts = [b.text for b in documents[f"{BASE}/filiallar"].blocks]
        assert "ABB-nin 2 filialı, 1 şöbəsi və xaricdə 0 ofisi var." in texts
        assert "Bakı: Nərimanov filialı" in texts
        assert "Zaqatala: Zaqatala filialı" in texts
        assert texts[texts.index("Həftəsonu işləyən filiallar") + 1] == "Zaqatala filialı"


# --------------------------------------------------------------------------- #
# Fetching
# --------------------------------------------------------------------------- #

ACTIONS_JS = "".join(
    f'x=(0,v.createServerReference)("{action_id}",v.callServer,void 0,v.findSourceMapURL,"{name}"),'
    for name, action_id in [("getBranchFilters", "00aa"), ("getBranches", "40bb"),
                            ("getSubBranches", "00cc"), ("getAbroadOffices", "00dd")]
)


def flight(value) -> httpx.Response:
    return httpx.Response(200, text=f'0:{{"a":"$@1"}}\n1:{json.dumps(value, ensure_ascii=False)}\n')


def action_response(request: httpx.Request) -> httpx.Response:
    action, args = request.headers["Next-Action"], json.loads(request.content)
    if action == "00aa":
        return flight({"data": [{"title": "Həftəsonu işləyən filiallar", "key": "open_on_weekends"}]})
    if action == "40bb":
        return flight([BRANCH] if args == ["open_on_weekends"] else DATA["branches"])
    return flight([])


@pytest.fixture
def site():
    with respx.mock(assert_all_called=False) as mock:
        mock.get(f"{BASE}/filiallar").respond(200, text='<script src="/_next/static/chunks/app.js"></script>')
        mock.get(f"{BASE}/_next/static/chunks/app.js").respond(200, text=ACTIONS_JS)
        mock.post(f"{BASE}/filiallar").mock(side_effect=action_response)
        mock.get(f"{BASE}/web-api/service-network/atm").respond(200, json={"data": DATA["atms"]})
        mock.get(f"{BASE}/web-api/service-network/terminal").respond(200, json={"data": []})
        yield mock


async def test_fetch_service_network(config, site):
    data = await fetch_service_network(replace(config, retry_base_delay=0))

    assert [b["title"] for b in data["branches"]] == ["Zaqatala filialı", "Nərimanov filialı"]
    assert data["branch_filters"] == {"Həftəsonu işləyən filiallar": [288]}
    assert len(data["atms"]) == 2
    assert json.loads(config.service_network_path.read_text("utf-8"))["branches"] == data["branches"]


async def test_fetch_fails_clearly_when_the_site_changed(config, site):
    site.get(f"{BASE}/_next/static/chunks/app.js").respond(200, text="no actions here")
    with pytest.raises(ServiceNetworkError, match="getBranches"):
        await fetch_service_network(replace(config, retry_base_delay=0))
