"""URL discovery: sitemap parsing, link extraction and URL normalization."""

from __future__ import annotations

import re
from urllib.parse import urljoin, urlsplit, urlunsplit
from xml.etree import ElementTree

from .models import Language

_SITEMAP_NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
_HREF_RE = re.compile(r'href="([^"]+)"')

# Paths that never contain page content.
_EXCLUDED_PREFIXES = ("/_next/", "/cdn-cgi/", "/api/", "/search")
_EXCLUDED_EXTENSIONS = (
    ".pdf",
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".svg",
    ".webp",
    ".ico",
    ".zip",
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
    ".mp4",
    ".css",
    ".js",
    ".json",
    ".xml",
    ".txt",
)
_LANGUAGE_PREFIXES: tuple[Language, ...] = ("en", "ru")

# Site sections → category. Checked in order, so the more specific prefix first.
# Pages outside these sections (mostly SEO landing pages such as /500-azn-kredit)
# are "general".
_CATEGORIES = (
    ("haqqimizda/satinalmalar", "procurement"),
    ("haqqimizda", "about"),
    ("ferdi", "individual"),
    ("biznes", "business"),
    ("xeberler", "news"),
    ("kampaniyalar", "campaigns"),
    ("korporativ-sosial-mesuliyyet", "csr"),
    ("investorlarla-elaqe", "investor_relations"),
    ("press-relizler", "press_releases"),
)


def parse_sitemap(xml: str) -> dict[str, str | None]:
    """Return ``{url: lastmod}`` for every ``<url>`` entry of a sitemap."""
    root = ElementTree.fromstring(xml)
    entries: dict[str, str | None] = {}
    for url_node in root.findall("sm:url", _SITEMAP_NS):
        loc = url_node.findtext("sm:loc", default="", namespaces=_SITEMAP_NS).strip()
        if loc:
            entries[loc] = url_node.findtext("sm:lastmod", namespaces=_SITEMAP_NS)
    return entries


def normalize_url(url: str, host: str) -> str | None:
    """Canonical form of an on-site page URL, or ``None`` if it is not a page.

    Query strings and fragments are dropped, the trailing slash removed and the
    ``www.`` prefix unified, so the same page is never fetched twice.
    """
    parts = urlsplit(url.strip())
    if parts.scheme not in ("http", "https"):
        return None
    netloc = parts.netloc.lower().removeprefix("www.")
    if netloc != host:
        return None

    path = re.sub(r"/{2,}", "/", parts.path) or "/"
    if path != "/":
        path = path.rstrip("/")
    lowered = path.lower()
    if lowered.startswith(_EXCLUDED_PREFIXES) or lowered.endswith(_EXCLUDED_EXTENSIONS):
        return None
    return urlunsplit(("https", host, path, "", ""))


def extract_links(html: str, page_url: str, host: str) -> set[str]:
    """All normalized on-site page links found in ``html``."""
    links = set()
    for href in _HREF_RE.findall(html):
        url = normalize_url(urljoin(page_url, href), host)
        if url:
            links.add(url)
    return links


def language_of(url: str) -> Language:
    """Language of a page from its URL (``/en/...``, ``/ru/...``, otherwise ``az``)."""
    first_segment = urlsplit(url).path.strip("/").split("/", 1)[0]
    return first_segment if first_segment in _LANGUAGE_PREFIXES else "az"


def category_of(url: str) -> str:
    """Site section of a page, e.g. ``individual``, ``business``, ``news``, ``procurement``."""
    path = cms_path(url)
    if not path:
        return "home"
    for prefix, category in _CATEGORIES:
        if path == prefix or path.startswith(prefix + "/"):
            return category
    return "general"


def cms_path(url: str) -> str:
    """URL path without slashes and language prefix, as the CMS stores it (``"ferdi/kartlar"``)."""
    segments = [s for s in urlsplit(url).path.split("/") if s]
    if segments and segments[0] in _LANGUAGE_PREFIXES:
        segments = segments[1:]
    return "/".join(segments)
