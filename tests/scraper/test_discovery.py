import pytest

from abb_scraper.discovery import (
    category_of,
    cms_path,
    extract_links,
    language_of,
    normalize_url,
    parse_sitemap,
)

HOST = "abb-bank.az"


def test_parse_sitemap():
    xml = """<?xml version="1.0" encoding="UTF-8"?>
    <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
      <url><loc>https://abb-bank.az/ferdi</loc><lastmod>2025-03-14T16:41:48+04:00</lastmod></url>
      <url><loc> https://abb-bank.az/biznes </loc></url>
    </urlset>"""
    assert parse_sitemap(xml) == {
        "https://abb-bank.az/ferdi": "2025-03-14T16:41:48+04:00",
        "https://abb-bank.az/biznes": None,
    }


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("https://abb-bank.az/ferdi/", "https://abb-bank.az/ferdi"),
        ("https://www.ABB-bank.az/ferdi?utm=x#top", "https://abb-bank.az/ferdi"),
        ("http://abb-bank.az//ferdi//kartlar", "https://abb-bank.az/ferdi/kartlar"),
        ("https://abb-bank.az/", "https://abb-bank.az/"),
    ],
)
def test_normalize_url_canonicalizes(raw, expected):
    assert normalize_url(raw, HOST) == expected


@pytest.mark.parametrize(
    "raw",
    [
        "https://cdn.abb-bank.az/tarif.pdf",  # other host
        "https://abb-bank.az/files/tarif.PDF",  # document
        "https://abb-bank.az/_next/static/chunk.js",  # framework asset
        "https://abb-bank.az/search?q=kredit",  # search results
        "mailto:office@abb-bank.az",
    ],
)
def test_normalize_url_rejects_non_pages(raw):
    assert normalize_url(raw, HOST) is None


def test_extract_links_resolves_relative_links_and_filters():
    html = '<a href="/ferdi/kartlar">x</a><a href="kreditler/">y</a><a href="https://google.com">z</a>'
    assert extract_links(html, "https://abb-bank.az/ferdi/", HOST) == {
        "https://abb-bank.az/ferdi/kartlar",
        "https://abb-bank.az/ferdi/kreditler",
    }


@pytest.mark.parametrize(
    ("url", "lang", "category"),
    [
        ("https://abb-bank.az/", "az", "home"),
        ("https://abb-bank.az/ferdi/kartlar", "az", "individual"),
        ("https://abb-bank.az/en/biznes", "en", "business"),
        ("https://abb-bank.az/ru", "ru", "home"),
        ("https://abb-bank.az/haqqimizda/rehberlik", "az", "about"),
        ("https://abb-bank.az/en/haqqimizda/satinalmalar/bildirisler", "en", "procurement"),
        ("https://abb-bank.az/500-azn-kredit", "az", "general"),
        ("https://abb-bank.az/ferdiler", "az", "general"),  # a prefix match must end at a "/"
    ],
)
def test_language_and_category(url, lang, category):
    assert language_of(url) == lang
    assert category_of(url) == category


def test_cms_path_strips_language_prefix_and_slashes():
    assert cms_path("https://abb-bank.az/en/ferdi/kartlar/") == "ferdi/kartlar"
    assert cms_path("https://abb-bank.az/") == ""
