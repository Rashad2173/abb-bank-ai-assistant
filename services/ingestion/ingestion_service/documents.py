"""Uploaded documents (PDF, plain text) → pages in the ``abb_pages.jsonl`` format.

Every PDF page becomes a section ("<title> > Page 3"), so an answer can cite
the page it comes from. Paragraphs are rebuilt from the PDF's text lines: a
line that does not end a sentence continues on the next one.
"""

from __future__ import annotations

import logging
import re
from io import BytesIO
from pathlib import PurePath
from urllib.parse import quote

from pypdf import PdfReader
from pypdf.errors import PdfReadError

SUPPORTED_SUFFIXES = (".pdf", ".txt", ".md")
PAGE_LABEL = {"az": "Səhifə", "en": "Page", "ru": "Страница"}
_SENTENCE_END = re.compile(r"[.!?:;…»\"”)]$")
_AZERBAIJANI_LETTERS = set("əğıöüşçƏĞİÖÜŞÇ")
_MIN_LETTERS = 40
_GLYPH_NAME_RE = re.compile(r"/uni([0-9A-Fa-f]{4})")
"""Glyph names some fonts leave in extracted text ("/uni0259" is "ə") — the hex is the code point."""

logging.getLogger("pypdf").setLevel(logging.ERROR)  # font-encoding warnings are noise here


class UnreadableDocument(ValueError):
    pass


def page_from_file(filename: str, data: bytes) -> dict:
    name = PurePath(filename).name or "document"
    suffix = PurePath(name).suffix.lower()
    if suffix == ".pdf":
        title, page_texts = _read_pdf(name, data)
    elif suffix in (".txt", ".md"):
        title, page_texts = _title(name), [_decode(data)]
    else:
        raise UnreadableDocument(f"{name}: only {', '.join(SUPPORTED_SUFFIXES)} files can be uploaded as documents")

    text = "\n".join(page_texts)
    if sum(char.isalpha() for char in text) < _MIN_LETTERS:
        raise UnreadableDocument(f"{name}: no readable text (a scanned PDF needs OCR)")
    lang = detect_language(text)
    label = PAGE_LABEL[lang]
    sections = [
        {"heading_path": [title, f"{label} {number}"] if len(page_texts) > 1 else [title], "paragraphs": paragraphs}
        for number, page_text in enumerate(page_texts, start=1)
        if (paragraphs := to_paragraphs(page_text))
    ]
    return {"url": f"upload://{quote(name)}", "title": title, "lang": lang, "category": "document",
            "sections": sections, "faq": []}


def to_paragraphs(text: str) -> list[str]:
    """Joins wrapped lines back into paragraphs; blank lines always end one."""
    paragraphs: list[str] = []
    current: list[str] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            if current:
                paragraphs.append(" ".join(current))
                current = []
            continue
        current.append(line)
        if _SENTENCE_END.search(line):
            paragraphs.append(" ".join(current))
            current = []
    if current:
        paragraphs.append(" ".join(current))
    return [re.sub(r"\s+", " ", p).strip() for p in paragraphs if p.strip()]


def detect_language(text: str) -> str:
    letters = [char for char in text if char.isalpha()]
    if not letters:
        return "en"
    if sum("Ѐ" <= char <= "ӿ" for char in letters) / len(letters) >= 0.4:
        return "ru"
    return "az" if sum(char in _AZERBAIJANI_LETTERS for char in letters) / len(letters) >= 0.025 else "en"


def _read_pdf(name: str, data: bytes) -> tuple[str, list[str]]:
    try:
        reader = PdfReader(BytesIO(data))
        if reader.is_encrypted:
            reader.decrypt("")  # many "protected" PDFs only restrict editing
        return _title(name), [_fix_glyph_names(page.extract_text() or "") for page in reader.pages]
    except (PdfReadError, ValueError, KeyError) as exc:
        raise UnreadableDocument(f"{name}: not a readable PDF ({type(exc).__name__})") from exc


def _fix_glyph_names(text: str) -> str:
    return _GLYPH_NAME_RE.sub(lambda match: chr(int(match.group(1), 16)), text)


def _title(filename: str) -> str:
    """The file name, readable. A PDF's own title field is unreliable (often a table cell or
    "Microsoft Word - draft.docx"), so it is not used."""
    return re.sub(r"[_\s]+", " ", PurePath(filename).stem).strip() or "document"


def _decode(data: bytes) -> str:
    for encoding in ("utf-8-sig", "cp1251", "latin-1"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")
