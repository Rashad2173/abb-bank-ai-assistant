from itertools import pairwise

from abb_retrieval.chunking import chunk_page
from abb_retrieval.config import ChunkingConfig


def words(text: str) -> int:
    """Stand-in tokenizer for tests: one token per word."""
    return len(text.split())


CONFIG = ChunkingConfig(target_tokens=30, max_tokens=40, overlap_paragraphs=1)


def page(sections=(), faq=(), lang="az", title="TamKart Gold") -> dict:
    return {
        "url": "https://abb-bank.az/ferdi/kartlar/tamkart-gold",
        "lang": lang,
        "category": "individual",
        "title": title,
        "sections": [{"heading_path": path, "paragraphs": paragraphs} for path, paragraphs in sections],
        "faq": [{"question": q, "answer": a} for q, a in faq],
    }


def chunk(p: dict):
    return chunk_page(p, page_index=7, count_tokens=words, config=CONFIG)


def test_small_sections_are_packed_with_sub_headings_and_context_header():
    chunks = chunk(
        page(
            sections=[
                (["TamKart Gold", "Tariflər"], ["İllik faiz dərəcəsi: 22%"]),
                (["TamKart Gold", "Tariflər", "Komissiya"], ["Nağdlaşdırma: 1%"]),
            ]
        )
    )
    assert len(chunks) == 1
    assert chunks[0].text == ("TamKart Gold\nTariflər\n\nİllik faiz dərəcəsi: 22%\n## Komissiya\nNağdlaşdırma: 1%")
    assert chunks[0].heading_path == ["Tariflər"]
    assert chunks[0].sources == ["sections[0].paragraphs[0]", "sections[1].paragraphs[0]"]
    assert chunks[0].page_index == 7


def test_packing_stops_at_the_target_size():
    sentence = " ".join(["söz"] * 12)
    chunks = chunk(page(sections=[([f"Bölmə {i}"], [sentence]) for i in range(4)]))
    assert [c.sources for c in chunks] == [
        ["sections[0].paragraphs[0]", "sections[1].paragraphs[0]"],
        ["sections[2].paragraphs[0]", "sections[3].paragraphs[0]"],
    ]


def test_large_section_is_split_into_windows_with_one_paragraph_overlap():
    paragraphs = [" ".join([f"p{i}"] * 12) for i in range(5)]
    chunks = chunk(page(sections=[(["TamKart Gold", "Şərtlər"], paragraphs)]))
    assert len(chunks) > 1
    assert all(c.token_count <= CONFIG.max_tokens for c in chunks)
    # the last paragraph of a window starts the next one
    for previous, current in pairwise(chunks):
        assert previous.sources[-1] == current.sources[0]
    covered = {s for c in chunks for s in c.sources}
    assert covered == {f"sections[0].paragraphs[{i}]" for i in range(5)}


def test_oversized_paragraph_is_split_at_sentences():
    long_paragraph = " ".join(f"Cümlə {i} burada bitir." for i in range(30))
    chunks = chunk(page(sections=[(["Qaydalar"], [long_paragraph])]))
    assert len(chunks) > 1
    assert all(c.token_count <= CONFIG.max_tokens for c in chunks)
    assert all(c.sources == ["sections[0].paragraphs[0]"] for c in chunks)


def test_every_faq_item_is_its_own_chunk_with_localized_labels():
    chunks = chunk(page(faq=[("Kart pulsuzdur?", "Bəli."), ("Limit nə qədərdir?", "30 000 AZN.")]))
    assert [c.chunk_type for c in chunks] == ["faq", "faq"]
    assert chunks[0].text == "TamKart Gold\nTez-tez verilən suallar\n\nSual: Kart pulsuzdur?\nCavab: Bəli."
    assert [c.sources for c in chunks] == [["faq[0]"], ["faq[1]"]]

    english = chunk(page(faq=[("Is the card free?", "Yes.")], lang="en"))
    assert english[0].text.endswith("Question: Is the card free?\nAnswer: Yes.")


def test_long_faq_answer_keeps_the_question_in_every_part():
    answer = " ".join(f"Addım {i} tamamlanır." for i in range(30))
    chunks = chunk(page(faq=[("Kartı necə sifariş edim?", answer)]))
    assert len(chunks) > 1
    assert all("Sual: Kartı necə sifariş edim?" in c.text for c in chunks)


def test_campaign_status_is_in_the_header_and_metadata():
    p = page(sections=[(["Şərtlər"], ["15% endirim"])], faq=[("Kim qatıla bilər?", "Hamı.")])
    p["validity"] = {"valid_from": "2025-05-07", "valid_until": "2025-05-23", "is_active": False}
    chunks = chunk(p)
    assert all(c.text.startswith("TamKart Gold\nKampaniya statusu: bitib (07.05.2025 – 23.05.2025)\n") for c in chunks)
    assert all(c.is_active is False and str(c.valid_until) == "2025-05-23" for c in chunks)


def test_faq_chunks_remember_the_other_pages_of_the_question():
    p = page(faq=[("Sual?", "Cavab.")])
    p["faq"][0]["also_on"] = ["https://abb-bank.az/ferdi/kartlar/tam"]
    assert chunk(p)[0].related_urls == ["https://abb-bank.az/ferdi/kartlar/tam"]


def test_a_window_starting_inside_a_list_repeats_the_lead_in():
    """The list items must keep the condition they belong to."""
    lead_in = "Aşağıdakı gəlirlər vergidən azaddır:"
    items = [f"- Gəlir növü {i} " + " ".join(["söz"] * 8) for i in range(6)]
    chunks = chunk(page(sections=[(["Vergi"], [lead_in, *items])]))
    assert len(chunks) > 1
    assert all(lead_in in c.text for c in chunks)


def test_news_chunks_show_the_publication_date():
    p = page(sections=[(["Xəbər"], ["ABB yeni kampaniya elan edir."])])
    p["published"] = "2022-06-09"
    c = chunk(p)[0]
    assert c.text.startswith("TamKart Gold\nTarix: 09.06.2022\n")
    assert str(c.published) == "2022-06-09"


def test_identical_chunks_of_different_pages_are_merged_with_their_categories():
    from abb_retrieval.merging import merge_identical_chunks

    first = chunk(page(sections=[(["A"], ["Eyni mətn burada yazılıb."])]))[0]
    second = first.model_copy(
        update={
            "url": "https://abb-bank.az/ferdi",
            "chunk_id": "other",
            "page_index": 9,
            "category": "home",
            "categories": ["home"],
        }
    )
    merged = merge_identical_chunks([first, second])
    assert [c.chunk_id for c in merged] == [first.chunk_id]
    assert merged[0].related_urls == ["https://abb-bank.az/ferdi"]
    assert merged[0].categories == ["individual", "home"]
    assert (merged[0].aliases[0].page_index, merged[0].aliases[0].category) == (9, "home")


def test_sections_shared_by_many_tenders_become_one_common_chunk():
    from abb_retrieval.merging import merge_shared_sections

    config = ChunkingConfig(shared_section_min_pages=3)

    def tender(i: int, body: str):
        p = page(sections=[(["Tələblər"], [body])], title=f"Tender {i}")
        p.update(url=f"https://abb-bank.az/haqqimizda/satinalmalar/t{i}", category="procurement")
        return chunk_page(p, i, words, config)[0]

    common = "Qara siyahı meyarları bütün təchizatçılara şamil olunur."
    chunks = [tender(i, common) for i in range(3)] + [tender(9, "Lot 1 üzrə 100 manat iştirak haqqı.")]
    merged = merge_shared_sections(chunks, config, words)

    assert len(merged) == 2
    shared = merged[0]
    assert shared.text.startswith("Satınalmalar (bütün tenderlər üçün ümumi)\nTələblər\n\n")
    assert shared.token_count == words(shared.text)  # recounted for the new header
    assert len(shared.related_urls) == 2 and len({a.url for a in shared.aliases}) == 3
    assert merged[1].text.startswith("Tender 9")  # a tender's own facts stay with the tender


def test_sections_without_information_are_not_chunked():
    assert chunk(page(sections=[(["Profil"], ["Все"])])) == []


def test_chunk_ids_are_stable_and_unique():
    p = page(sections=[(["A"], ["mətn"])], faq=[("Sual?", "Cavab.")])
    first, second = chunk(p), chunk(p)
    assert [c.chunk_id for c in first] == [c.chunk_id for c in second]
    assert len({c.chunk_id for c in first}) == len(first)
