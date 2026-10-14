import json

from abb_scraper.extract.page import extract_page

from .helpers import flight_push, page_html


def page_entity(url: str, sections: list, parent: dict | None = None) -> dict:
    return {"url": url, "locale": "az", "sections": sections, "parent": parent}


def html_with_payload(body: str, *entities: dict) -> str:
    payload = "".join(f"{i}:{json.dumps(e, ensure_ascii=False)}\n" for i, e in enumerate(entities))
    return page_html(body + flight_push(payload))


def test_combines_html_cms_and_faq():
    tabs = {"__component": "ui-sections.spain", "tabs": [{
        "trigger": [{"title": "Tariflər"}],
        "content": [{"terms": [{"label": "İllik faiz", "term": "22%"}]}],
    }]}
    faq = {"__component": "faq.repeatable-faq-group",
           "groups": [{"items": [{"trigger": "Kart pulsuzdur?", "content": "<p>Bəli.</p>"}]}]}
    html = html_with_payload("<h1>TamKart Gold</h1><p>Kredit kartı</p>", page_entity("ferdi/kartlar/tam", [tabs, faq]))

    content = extract_page("https://abb-bank.az/ferdi/kartlar/tam", "az", html)

    assert content.has_cms_entity
    assert [(b.text, b.heading_level) for b in content.blocks] == [
        ("TamKart Gold", 1),
        ("Kredit kartı", None),
        ("TamKart Gold", 1),  # CMS sections are re-anchored under the page title
        ("Tariflər", 3),
        ("İllik faiz: 22%", None),
    ]
    assert [(f.question, f.answer) for f in content.faq] == [("Kart pulsuzdur?", "Bəli.")]


def test_ignores_content_of_parent_pages():
    parent_faq = {"__component": "faq.repeatable-faq-group",
                  "groups": [{"items": [{"trigger": "Üst səhifənin sualı?", "content": "Cavab"}]}]}
    parent = page_entity("ferdi/kartlar", [parent_faq, {"__component": "ui-sections.usa", "title": "Üst bölmə",
                                                       "description": "Üst səhifənin mətni"}])
    html = html_with_payload("<h1>Tam</h1>", page_entity("ferdi/kartlar/tam", [], parent=parent))

    content = extract_page("https://abb-bank.az/ferdi/kartlar/tam", "az", html)

    assert content.faq == []
    assert [b.text for b in content.blocks] == ["Tam"]


def test_matches_language_prefixed_urls_to_cms_paths():
    entity = {**page_entity("ferdi", [{"title": "Cards", "description": "Only in CMS"}]), "locale": "en"}
    html = html_with_payload("<h1>Individuals</h1>", entity)

    content = extract_page("https://abb-bank.az/en/ferdi", "en", html)

    assert content.has_cms_entity
    assert "Cards: Only in CMS" in [b.text for b in content.blocks]


def test_without_cms_data_falls_back_to_html_only():
    content = extract_page("https://abb-bank.az/xeberler/x", "az", page_html("<h1>Xəbər</h1><p>Mətn</p>"))
    assert not content.has_cms_entity
    assert [b.text for b in content.blocks] == ["Xəbər", "Mətn"]
