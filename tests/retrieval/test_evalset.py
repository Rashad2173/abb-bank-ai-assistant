import pytest

from abb_retrieval.evalset import (
    CorpusMismatchError,
    apply_additions,
    attach_chunks,
    freeze_evidence,
    parse_question_set,
    parse_snippet_set,
    position_text,
    table_cells,
)
from abb_retrieval.models import Chunk, ChunkAlias, EvidenceRef, Question

QUESTION_SET = """# Set

## 1. Basit, doğrudan bilgi — 1 soru

### ABB-Q001

**Soru (az):** Alpha Card sifarişini kim həyata keçirir?

**Beklenen cevap:** Valideyn.

**Kaynak 1:** [Alpha Card](https://abb-bank.az/ferdi/kartlar/debet-kartlari/alpha-card)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **2468**; `sections[0].paragraphs[0]`.

**Kanıt:**

> sifariş valideyn tərəfindən həyata keçirilir.

## 5. Çoklu chunk gerektiren — 1 soru

### ABB-Q076

**Soru (en):** Compare the limits of Tam DigiCard and Alpha Card.

**Beklenen cevap:** 3 000 AZN vs 500 AZN.

**Kaynak 1:** [Tam DigiCard](https://abb-bank.az/ferdi/kartlar/debet-kartlari/tam-digicard)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **2476**; `sections[9].paragraphs[4]; faq[2]`.

**Kanıt:**

> Aylıq 3 000 AZN-dək pulsuz

**Kaynak 2:** [Alpha Card](https://abb-bank.az/ferdi/kartlar/debet-kartlari/alpha-card)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **2468**; `sections[5].paragraphs[1]`.

**Kanıt:**

> Aylıq 500 AZN-dək pulsuz
"""


def test_parse_question_set():
    questions = parse_question_set(QUESTION_SET)
    assert [(q.id, q.category, q.lang) for q in questions] == [
        ("ABB-Q001", "simple", "az"),
        ("ABB-Q076", "multi_source", "en"),
    ]
    multi = questions[1]
    assert [(e.page_index, e.positions) for e in multi.evidence] == [
        (2475, ["sections[9].paragraphs[4]", "faq[2]"]),  # line 2476 counted from 1
        (2467, ["sections[5].paragraphs[1]"]),
    ]
    assert multi.evidence[1].quote == "Aylıq 500 AZN-dək pulsuz"
    assert questions[0].expected_answer == "Valideyn."


ALPHA = "https://abb-bank.az/ferdi/kartlar/debet-kartlari/alpha-card"
DIGI = "https://abb-bank.az/ferdi/kartlar/debet-kartlari/tam-digicard"


def corpus_v1() -> list[dict]:
    """The corpus version the question set was written for (only the pages it refers to)."""
    pages = [{"url": f"https://abb-bank.az/other/{i}", "sections": [], "faq": []} for i in range(2476)]
    pages[2467] = {"url": ALPHA, "faq": [], "sections": [
        {"paragraphs": ["7–17 yaşlı uşaqlar üçün – sifariş valideyn tərəfindən həyata keçirilir."]},
        *[{"paragraphs": ["x"]} for _ in range(4)],
        {"paragraphs": ["Tariflər", "Aylıq 500 AZN-dək pulsuz"]},
    ]}
    pages[2475] = {"url": DIGI, "faq": [{}, {}, {"question": "?", "answer": "Limit 3 000 AZN-dir."}],
                   "sections": [*[{"paragraphs": ["x"]} for _ in range(9)],
                                {"paragraphs": ["a", "b", "c", "d", "Aylıq 3 000 AZN-dək pulsuz"]}]}
    return pages


def frozen_questions():
    questions = parse_question_set(QUESTION_SET)
    pages = corpus_v1()
    for question in questions:
        for ref in question.evidence:
            ref.texts = [position_text(pages[ref.page_index], p) for p in ref.positions]
    return questions


def test_position_text():
    page = corpus_v1()[2475]
    assert position_text(page, "sections[9].paragraphs[4]") == "Aylıq 3 000 AZN-dək pulsuz"
    assert position_text(page, "faq[2]") == "Limit 3 000 AZN-dir."


def test_freeze_refuses_a_different_corpus_version(tmp_path):
    corpus = tmp_path / "abb_pages.jsonl"
    corpus.write_text("{}\n")
    with pytest.raises(CorpusMismatchError):
        freeze_evidence(parse_question_set(QUESTION_SET), corpus_v1(), corpus, expected_sha="0" * 64)


def make_chunk(chunk_id: str, url: str, page_index: int, sources: list[str]) -> Chunk:
    return Chunk(chunk_id=chunk_id, url=url, lang="az", category="c", title="t", heading_path=[],
                 chunk_type="section", text="x", token_count=1, page_index=page_index, sources=sources)


def test_attach_chunks_finds_evidence_by_text_after_the_corpus_changed():
    """In the new corpus version the pages moved and the sections were renumbered."""
    questions = frozen_questions()
    v1 = corpus_v1()
    new_pages = [
        {**v1[2475], "sections": v1[2475]["sections"][9:]},  # DigiCard: 9 sections fewer, now line 1
        {**v1[2467], "sections": [v1[2467]["sections"][0], v1[2467]["sections"][5]]},  # Alpha Card, line 2
    ]
    chunks = [
        make_chunk("digi-a", DIGI, 0, ["sections[0].paragraphs[3]", "sections[0].paragraphs[4]"]),
        make_chunk("digi-faq", DIGI, 0, ["faq[2]"]),
        make_chunk("alpha-a", ALPHA, 1, ["sections[0].paragraphs[0]"]),
        make_chunk("alpha-b", ALPHA, 1, ["sections[1].paragraphs[1]"]),
    ]
    problems = attach_chunks(questions, chunks, new_pages)

    assert problems == []
    assert questions[0].evidence[0].chunk_ids == ["alpha-a"]
    assert [e.chunk_ids for e in questions[1].evidence] == [["digi-a", "digi-faq"], ["alpha-b"]]


def test_table_cells_match_across_row_formats():
    old_row = table_cells("1 ay | 6.5%")
    new_row = table_cells("Müddət: 1 ay; Aylıq: –; Müddətin sonu: 6.5%")
    assert old_row[0] == new_row[0]                                   # values
    assert table_cells("Müddət | Aylıq | Müddətin sonu")[0] == new_row[1]  # header row ↔ labels
    assert table_cells("Sadə cümlə: izah") == []


def test_a_shared_table_header_is_not_enough_evidence():
    """Q072: the header row is in the AZN *and* the USD table; only the AZN data row counts."""
    question = Question(id="Q", question="?", lang="az", category="numeric", expected_answer="", evidence=[
        EvidenceRef(url="u", page_index=0, positions=[], texts=["Müddət | Aylıq | Müddətin sonu", "36 ay | 9.5% | 10.5%"]),
    ])
    page = {"url": "u", "faq": [], "sections": [
        {"paragraphs": ["Müddət: 36 ay; Aylıq: 9.5%; Müddətin sonu: 10.5%"]},  # AZN
        {"paragraphs": ["Müddət: 18 ay; Aylıq: 3%; Müddətin sonu: 3.5%"]},     # USD
    ]}
    chunks = [make_chunk("azn", "u", 0, ["sections[0].paragraphs[0]"]),
              make_chunk("usd", "u", 0, ["sections[1].paragraphs[0]"])]
    attach_chunks([question], chunks, [page])
    assert question.evidence[0].chunk_ids == ["azn"]


def test_a_sentence_in_two_tables_counts_only_in_its_own_section():
    """Q079: "no interest on early withdrawal" is under the AZN *and* the USD table."""
    rule = "- Əmanət məbləği vaxtından əvvəl çıxarıldığı halda heç bir faiz ödənilmir."
    question = Question(id="Q", question="?", lang="az", category="multi_source", expected_answer="", evidence=[
        EvidenceRef(url="u", page_index=0, positions=[], texts=[rule], section_paths=[["DigiDeposit", "AZN"]]),
    ])
    page = {"url": "u", "faq": [], "sections": [
        {"heading_path": ["DigiDeposit", "AZN"], "paragraphs": [rule]},
        {"heading_path": ["DigiDeposit", "USD"], "paragraphs": [rule]},
    ]}
    azn = make_chunk("azn", "u", 0, ["sections[0].paragraphs[0]"])
    azn.text = f"DigiDeposit\n\n## AZN\n{rule}"
    usd = make_chunk("usd", "u", 0, ["sections[1].paragraphs[0]"])
    usd.text = f"DigiDeposit\n\n## USD\n{rule}"
    attach_chunks([question], [azn, usd], [page])
    assert question.evidence[0].chunk_ids == ["azn"]


def test_reviewed_alternative_passages_count_as_evidence():
    questions = frozen_questions()
    apply_additions(questions, [{"question_id": "ABB-Q001", "evidence": 0, "url": ALPHA,
                                 "contains": "Valideyn sifariş verir"}])
    alternative = make_chunk("alpha-faq", ALPHA, 2467, ["faq[0]"])
    alternative.text = "Alpha Card\n\nSual: Kim sifariş edir?\nCavab: Valideyn sifariş verir."
    pages = corpus_v1()
    pages[2467] = {**pages[2467], "faq": [{"question": "Kim sifariş edir?", "answer": "Valideyn sifariş verir."}]}
    attach_chunks(questions, [make_chunk("alpha-0", ALPHA, 2467, ["sections[0].paragraphs[0]"]), alternative], pages)
    assert questions[0].evidence[0].chunk_ids == ["alpha-0", "alpha-faq"]


def test_merged_identical_chunks_still_cover_evidence_of_both_pages():
    question = Question(id="Q", question="?", lang="az", category="simple", expected_answer="", evidence=[
        EvidenceRef(url="https://abb-bank.az/ferdi", page_index=1, positions=[], texts=["Ortaq mətn"]),
    ])
    pages = [{"url": "https://abb-bank.az/", "faq": [], "sections": [{"paragraphs": ["Ortaq mətn"]}]},
             {"url": "https://abb-bank.az/ferdi", "faq": [], "sections": [{"paragraphs": ["Ortaq mətn"]}]}]
    chunk = make_chunk("home", "https://abb-bank.az/", 0, ["sections[0].paragraphs[0]"])
    chunk.aliases = [ChunkAlias(url="https://abb-bank.az/ferdi", page_index=1, sources=["sections[0].paragraphs[0]"])]
    attach_chunks([question], [chunk], pages)
    assert question.evidence[0].chunk_ids == ["home"]


def test_attach_chunks_reports_unmapped_evidence():
    problems = attach_chunks(frozen_questions(), [], [])
    assert len(problems) == 3
    assert problems[0].startswith("ABB-Q001")


def test_snippet_set_evidence_is_found_by_url_and_snippet():
    """Set B: a source is a URL plus verbatim snippets — no corpus positions."""
    questions = parse_snippet_set([{
        "id": "B-001", "question": "?", "lang": "az", "category": "simple", "expected_answer": "",
        "evidence": [{"url": "u", "contains": ["Rəhbər: Ramil Alıyev"]}],
    }])
    hit = make_chunk("branch", "u", 0, [])
    hit.text = "Filiallar\n\nÜnvan: Gədəbəy\nRəhbər:  Ramil   Alıyev"
    other_page = make_chunk("other", "v", 0, [])
    other_page.text = hit.text

    problems = attach_chunks(questions, [hit, other_page], [])

    assert problems == []
    assert questions[0].evidence[0].page_index is None
    assert questions[0].evidence[0].chunk_ids == ["branch"]
