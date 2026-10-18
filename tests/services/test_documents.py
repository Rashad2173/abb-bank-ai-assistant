import pytest
from fastapi.testclient import TestClient

from ingestion_service.config import Settings
from ingestion_service.documents import UnreadableDocument, detect_language, page_from_file, to_paragraphs
from ingestion_service.jobs import Ingestor
from ingestion_service.main import build_app
from tests.services.test_ingestion import CountingInference, MemoryStore, word_count


def make_pdf(pages: list[list[str]], title: str | None = None) -> bytes:
    """A minimal valid PDF with one text line per entry (Helvetica, ASCII only)."""
    objects = ["<</Type/Catalog/Pages 2 0 R>>", ""]
    kids = []
    for lines in pages:
        content = "BT /F1 11 Tf 72 740 Td 14 TL " + " ".join(f"({line}) Tj T*" for line in lines) + " ET"
        page_id, content_id = len(objects) + 1, len(objects) + 2
        kids.append(f"{page_id} 0 R")
        objects.append(f"<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]/Contents {content_id} 0 R"
                       f"/Resources<</Font<</F1 {len(pages) * 2 + 3} 0 R>>>>>>")
        objects.append(f"<</Length {len(content)}>>stream\n{content}\nendstream")
    objects[1] = f"<</Type/Pages/Kids[{' '.join(kids)}]/Count {len(pages)}>>"
    objects.append("<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>")
    if title:
        objects.append(f"<</Title({title})>>")
    out, offsets = "%PDF-1.4\n", []
    for number, body in enumerate(objects, start=1):
        offsets.append(len(out.encode("latin-1")))
        out += f"{number} 0 obj{body}endobj\n"
    xref = len(out.encode("latin-1"))
    out += f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n" + "".join(f"{o:010d} 00000 n \n" for o in offsets)
    info = f"/Info {len(objects)} 0 R" if title else ""
    out += f"trailer<</Size {len(objects) + 1}/Root 1 0 R{info}>>\nstartxref\n{xref}\n%%EOF"
    return out.encode("latin-1")


TARIFF = make_pdf([
    ["ABB card tariffs for individuals.", "Annual service fee of the classic card is 10 AZN.",
     "Cash withdrawal at ABB ATMs is free of charge."],
    ["SMS notifications cost 1 AZN per month and", "can be switched off in ABB mobile."],
], title="ABB Tariffs")


def test_a_pdf_becomes_one_page_with_a_section_per_pdf_page():
    page = page_from_file("abb_kart_tarifleri.pdf", TARIFF)
    assert page["title"] == "abb kart tarifleri" and page["url"] == "upload://abb_kart_tarifleri.pdf"
    assert page["category"] == "document" and page["lang"] == "en"
    assert [s["heading_path"] for s in page["sections"]] == [["abb kart tarifleri", "Page 1"], ["abb kart tarifleri", "Page 2"]]
    # the wrapped line "… per month and / can be switched off …" is one paragraph again
    assert page["sections"][1]["paragraphs"] == ["SMS notifications cost 1 AZN per month and can be switched off in ABB mobile."]


def test_text_files_and_languages():
    page = page_from_file("qeyd.txt", "Kartın illik xidmət haqqı 10 AZN təşkil edir.\n\nSMS xidməti ayda 1 AZN-dir və ödənişsiz söndürülə bilər.".encode())
    assert page["lang"] == "az" and page["title"] == "qeyd" and len(page["sections"]) == 1
    assert detect_language("Годовая плата за обслуживание карты составляет 10 манат") == "ru"


def test_paragraphs_are_rebuilt_from_wrapped_lines():
    assert to_paragraphs("First line that wraps\ninto the next.\nNew sentence:\n\nAfter a blank") == [
        "First line that wraps into the next.", "New sentence:", "After a blank"]


@pytest.mark.parametrize("name, data", [("scan.pdf", make_pdf([["x"]])), ("bad.pdf", b"not a pdf"), ("sheet.xlsx", b"x")])
def test_unreadable_documents_are_refused(name, data):
    with pytest.raises(UnreadableDocument):
        page_from_file(name, data)


def test_upload_endpoint_adds_documents_and_returns_their_pages():
    app = build_app(Settings(_env_file=None), count_tokens=word_count)
    with TestClient(app) as client:
        app.state.store = MemoryStore()
        app.state.ingestor = Ingestor(app.state.store, CountingInference(), word_count, embed_batch=8)
        response = client.post("/v1/ingest/files", files=[("files", ("tarif.pdf", TARIFF, "application/pdf"))])
        assert response.status_code == 202
        body = response.json()
        assert body["job"]["mode"] == "append" and body["pages"][0]["title"] == "tarif"

        bad = client.post("/v1/ingest/files", files=[("files", ("bad.pdf", b"nope", "application/pdf"))])
        assert bad.status_code == 422 and "not a readable PDF" in bad.json()["error"]["message"]


def test_glyph_names_left_by_some_fonts_become_letters():
    from ingestion_service.documents import _fix_glyph_names
    assert _fix_glyph_names("Münd/uni0259ricat /uni018Fsas") == "Mündəricat Əsas"
