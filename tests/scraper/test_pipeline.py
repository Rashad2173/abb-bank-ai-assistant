import json
from dataclasses import replace
from datetime import datetime, timezone

from abb_scraper.extract.html_content import Block
from abb_scraper.models import FetchRecord, Page
from abb_scraper.pipeline import build_sections, run_extraction
from abb_scraper.storage import RawPageStore

from .helpers import flight_push, page_html

BANNER = "<section><h2>ABB mobile</h2><p>4.9 reytinqə malik innovativ bank tətbiqi!</p></section>"
FAQ = flight_push('1:{"trigger":"Kart necə sifariş edilir?","content":"<p>Onlayn müraciət ilə.</p>"}\n')
LONG_TEXT = "Bu səhifədə məhsulun bütün şərtləri ətraflı təsvir olunur. " * 4


def test_build_sections_follows_heading_hierarchy():
    blocks = [
        Block("Nağd kredit", 1),
        Block("Giriş mətni"),
        Block("Üstünlüklər", 2),
        Block("Rahat şərtlər", 3),
        Block("Zaminsiz"),
        Block("Sənədlər", 2),
        Block("Şəxsiyyət vəsiqəsi"),
    ]
    sections = [(s.heading_path, s.paragraphs) for s in build_sections(blocks)]
    assert sections == [
        (["Nağd kredit"], ["Giriş mətni"]),
        (["Nağd kredit", "Üstünlüklər", "Rahat şərtlər"], ["Zaminsiz"]),
        (["Nağd kredit", "Sənədlər"], ["Şəxsiyyət vəsiqəsi"]),
    ]


def test_build_sections_keeps_headings_without_content_as_list_items():
    blocks = [
        Block("Kart", 1),
        Block("Necə sifariş etmək olar?", 2),
        Block("Promokod xanasına klikləyin", 3),
        Block("FLYMC2 yazın", 3),
        Block("Sifarişi tamamlayın", 3),
        Block("Şərtlər", 2),
        Block("Pulsuz", 3),
    ]
    sections = [(s.heading_path, s.paragraphs) for s in build_sections(blocks)]
    assert sections == [
        (["Kart", "Necə sifariş etmək olar?"], ["Promokod xanasına klikləyin", "FLYMC2 yazın", "Sifarişi tamamlayın"]),
        (["Kart", "Şərtlər"], ["Pulsuz"]),
    ]


def cache_page(store: RawPageStore, url: str, html: str) -> None:
    store.append_record(FetchRecord(
        url=url, status=200, final_url=url, fetched_at=datetime.now(timezone.utc),
        cache_file=store.save_html(url, html),
    ))


def test_run_extraction_end_to_end(config):
    config = replace(config, boilerplate_min_pages=3)  # the banner is on 4 pages, page texts on at most 2
    store = RawPageStore(config.raw_dir, config.manifest_path)
    cache_page(store, "https://abb-bank.az/", page_html(f"<h1>ABB</h1><p>{LONG_TEXT}</p>{BANNER}"))
    cache_page(store, "https://abb-bank.az/ferdi/kartlar", page_html(f"<h1>Kartlar</h1><p>{LONG_TEXT} Kart.</p>{BANNER}" + FAQ))
    cache_page(store, "https://abb-bank.az/ferdi/kartlar/tam", page_html(f"<h1>Tam</h1><p>{LONG_TEXT} Tam.</p>{BANNER}" + FAQ))
    cache_page(store, "https://abb-bank.az/ferdi/kartlar/tam/kopya", page_html(f"<h1>Tam</h1><p>{LONG_TEXT} Tam.</p>{BANNER}" + FAQ))
    cache_page(store, "https://abb-bank.az/bos", page_html("<h1>Boş</h1>"))

    report = run_extraction(config, store)

    pages = {p.url: p for p in map(Page.model_validate_json, config.pages_path.read_text("utf-8").splitlines())}
    assert set(pages) == {"https://abb-bank.az/", "https://abb-bank.az/ferdi/kartlar", "https://abb-bank.az/ferdi/kartlar/tam"}

    def page_text(url: str) -> str:
        return " ".join(p for s in pages[url].sections for p in s.paragraphs)

    # The repeated banner is kept once — on the most general page.
    assert "reytinqə" in page_text("https://abb-bank.az/")
    assert "reytinqə" not in page_text("https://abb-bank.az/ferdi/kartlar")

    # The shared FAQ item is kept once as well.
    assert [f.answer for f in pages["https://abb-bank.az/ferdi/kartlar"].faq] == ["Onlayn müraciət ilə."]
    assert pages["https://abb-bank.az/ferdi/kartlar/tam"].faq == []

    # The footer's contact details become part of the home page.
    assert "Tel: 937" in page_text("https://abb-bank.az/")

    assert report.skipped_empty == ["https://abb-bank.az/bos"]
    assert report.skipped_duplicate == {
        "https://abb-bank.az/ferdi/kartlar/tam/kopya": "https://abb-bank.az/ferdi/kartlar/tam",
    }

    summary = json.loads(config.report_path.read_text("utf-8"))
    assert summary["pages_written"] == 3
    assert summary["faq_items"] == 1


AZ_TENDER = (
    "<h1>Tender</h1><p>Tenderin adı: ABB tərəfindən CyberArk lisenziyalarının satın alınması. "
    "Təkliflər elektron qaydada qəbul edilir, iddiaçılar sənədləri müəyyən edilmiş müddətdə təqdim etməlidirlər.</p>"
)


def test_untranslated_copies_are_dropped_when_the_original_exists(config):
    store = RawPageStore(config.raw_dir, config.manifest_path)
    cache_page(store, "https://abb-bank.az/tender/a", page_html(AZ_TENDER))
    cache_page(store, "https://abb-bank.az/en/tender/a", page_html(AZ_TENDER.replace("Tender<", "Tender (EN)<"), lang="en"))
    cache_page(store, "https://abb-bank.az/en/tender/b", page_html(AZ_TENDER.replace("CyberArk", "Oracle"), lang="en"))  # no AZ original

    report = run_extraction(config, store)

    pages = {p.url: p for p in map(Page.model_validate_json, config.pages_path.read_text("utf-8").splitlines())}
    assert report.skipped_untranslated == {"https://abb-bank.az/en/tender/a": "https://abb-bank.az/tender/a"}
    assert pages["https://abb-bank.az/en/tender/b"].lang == "az"  # kept, labelled with its real language
