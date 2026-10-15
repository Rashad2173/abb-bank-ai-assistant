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


def sections_of(blocks):
    return [(s.heading_path, s.paragraphs) for s in build_sections(blocks)]


def test_build_sections_keeps_a_run_of_empty_headings_as_list_items():
    """The steps of "How to order" are headings without text below them."""
    blocks = [
        Block("Kart", 1),
        Block("Necə sifariş etmək olar?", 2),
        Block("Promokod xanasına klikləyin", 3),
        Block("FLYMC2 yazın", 3),
        Block("Sifarişi tamamlayın", 3),
        Block("Şərtlər", 2),
        Block("Pulsuz çatdırılma", 3),
        Block("Kuryerlə 1 iş günündə.", None),
    ]
    assert sections_of(blocks) == [
        (["Kart", "Necə sifariş etmək olar?"], ["Promokod xanasına klikləyin", "FLYMC2 yazın", "Sifarişi tamamlayın"]),
        (["Kart", "Şərtlər", "Pulsuz çatdırılma"], ["Kuryerlə 1 iş günündə."]),
    ]


def test_build_sections_drops_a_single_empty_heading():
    """E.g. a tab label "Detallar" whose content went to the FAQ."""
    blocks = [
        Block("Mikro kredit", 1),
        Block("500 000 AZN-dək", None),
        Block("Tez-tez verilən suallar", 2),
        Block("Detallar", 3),
        Block("ABB mobile", 1),
    ]
    assert sections_of(blocks) == [(["Mikro kredit"], ["500 000 AZN-dək"])]


def test_build_sections_empty_siblings_before_a_real_heading_are_a_list():
    blocks = [
        Block("Üstünlüklər", 2),
        Block("Pulsuz", 3),
        Block("Onlayn", 3),
        Block("Keşbek", 3),
        Block("10%-dək keşbek qazanın.", None),
    ]
    assert sections_of(blocks) == [
        (["Üstünlüklər"], ["Pulsuz", "Onlayn"]),
        (["Üstünlüklər", "Keşbek"], ["10%-dək keşbek qazanın."]),
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

    # An FAQ item shown on only a few product pages stays on each of them.
    assert [f.answer for f in pages["https://abb-bank.az/ferdi/kartlar"].faq] == ["Onlayn müraciət ilə."]
    assert [f.answer for f in pages["https://abb-bank.az/ferdi/kartlar/tam"].faq] == ["Onlayn müraciət ilə."]

    # The footer's contact details become part of the home page.
    assert "Tel: 937" in page_text("https://abb-bank.az/")

    assert report.skipped_empty == ["https://abb-bank.az/bos"]
    assert report.skipped_duplicate == {
        "https://abb-bank.az/ferdi/kartlar/tam/kopya": "https://abb-bank.az/ferdi/kartlar/tam",
    }

    summary = json.loads(config.report_path.read_text("utf-8"))
    assert summary["pages_written"] == 3
    assert summary["faq_items"] == 2


def test_short_labels_stay_on_every_page_while_repeated_sentences_are_kept_once(config):
    store = RawPageStore(config.raw_dir, config.manifest_path)
    banner = "<p>ABB mobile yükləmək üçün QR kodu skan edin.</p>"
    for i, amount in enumerate(["30 000 AZN-dək", "50 000 AZN-dək", "70 000 AZN-dək"]):
        body = f"<h1>Kredit {i}</h1><p>{amount}</p><p>Məbləğ</p><p>{LONG_TEXT} {i}</p>{banner}"
        cache_page(store, f"https://abb-bank.az/ferdi/kreditler/k{i}", page_html(body))

    run_extraction(config, store)

    pages = [Page.model_validate_json(line) for line in config.pages_path.read_text("utf-8").splitlines()]
    texts = [[p for s in page.sections for p in s.paragraphs] for page in pages]
    assert all("Məbləğ" in t for t in texts)                                            # label kept everywhere
    assert sum("ABB mobile yükləmək üçün QR kodu skan edin." in t for t in texts) == 1  # banner kept once


def test_widely_repeated_faq_is_kept_once_and_remembers_the_other_pages(config):
    config = replace(config, faq_max_shared_pages=1)
    store = RawPageStore(config.raw_dir, config.manifest_path)
    cache_page(store, "https://abb-bank.az/ferdi/kartlar", page_html(f"<h1>Kartlar</h1><p>{LONG_TEXT} A</p>" + FAQ))
    cache_page(store, "https://abb-bank.az/ferdi/kartlar/tam", page_html(f"<h1>Tam</h1><p>{LONG_TEXT} B</p>" + FAQ))

    run_extraction(config, store)

    pages = {p.url: p for p in map(Page.model_validate_json, config.pages_path.read_text("utf-8").splitlines())}
    general = pages["https://abb-bank.az/ferdi/kartlar"].faq
    assert [(f.answer, f.also_on) for f in general] == [("Onlayn müraciət ilə.", ["https://abb-bank.az/ferdi/kartlar/tam"])]
    assert pages["https://abb-bank.az/ferdi/kartlar/tam"].faq == []


def test_campaign_pages_get_validity_and_documents(config):
    store = RawPageStore(config.raw_dir, config.manifest_path)
    body = (f"<h1>Yay kampaniyası</h1><p>01.06.2024 - 31.08.2024</p><p>Aktiv deyil</p><p>{LONG_TEXT}</p>"
            '<p>Qaydalar: <a href="https://cdn.abb-bank.az/qaydalar.pdf">Yüklə</a></p>')
    cache_page(store, "https://abb-bank.az/kampaniyalar/yay", page_html(body))

    run_extraction(config, store)

    page = Page.model_validate_json(config.pages_path.read_text("utf-8").splitlines()[0])
    assert page.validity.is_active is False
    assert str(page.validity.valid_until) == "2024-08-31"
    assert [(d.title, d.url) for d in page.documents] == [("Qaydalar", "https://cdn.abb-bank.az/qaydalar.pdf")]


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
