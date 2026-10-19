from datetime import date

import numpy as np

from abb_retrieval.embedders.base import Embeddings
from abb_retrieval.embedding_cache import load, save
from abb_retrieval.milvus_store import METHODS, Query, _data, _row
from abb_retrieval.models import Chunk
from abb_retrieval.text import lexical_form


def test_lexical_form_maps_letters_typed_without_an_azerbaijani_keyboard():
    assert lexical_form("İPOTEKA KREDİTİ, ilkin ödəniş, ıslak") == "iPOTEKA KREDiTi, ilkin ödeniş, islak"


def test_embedding_cache_round_trip(tmp_path):
    original = Embeddings(dense=np.eye(2, 3, dtype=np.float32), sparse=[{5: 0.5, 9: 0.25}, {}])
    save(tmp_path / "e.npz", original)
    restored = load(tmp_path / "e.npz")
    assert np.array_equal(restored.dense, original.dense)
    assert restored.sparse == original.sparse


def test_row_holds_metadata_and_the_normalised_keyword_text():
    chunk = Chunk(
        chunk_id="c-000",
        url="https://abb-bank.az/x",
        lang="az",
        category="campaigns",
        title="Kampaniya",
        heading_path=[],
        chunk_type="section",
        text="Kampaniya\n\nNağd kreditə endirim",
        token_count=5,
        page_index=0,
        sources=[],
        is_active=False,
        valid_until=date(2026, 10, 31),
        categories=["campaigns"],
    )
    row = _row(chunk, np.array([0.6, 0.8], dtype=np.float32), {3: 0.4})

    assert row["text"] == chunk.text
    assert row["lexical_text"] == "Kampaniya\n\nNağd kredite endirim"
    assert row["valid_until"] == "2026-10-31" and row["published"] is None
    assert row["is_active"] is False
    assert row["dense"] == [np.float32(0.6), np.float32(0.8)]


def test_every_search_gets_the_query_in_its_own_form():
    query = Query("Kredit nədir?", np.array([1.0, 0.0], dtype=np.float32), {7: 0.3})
    assert _data([query], "dense") == [[1.0, 0.0]]
    assert _data([query], "sparse") == [{7: 0.3}]
    assert _data([query], "bm25") == ["Kredit nedir?"]
    assert set(METHODS["dense+sparse+bm25"]) == {"dense", "sparse", "bm25"}


def test_rerank_ids_rescores_only_the_top_candidates():
    from abb_retrieval import milvus_check

    class LengthReranker:  # longer text = more relevant
        def compute_score(self, pairs, max_length):
            return [len(text) for _, text in pairs]

    texts = {f"c{i}": "x" * i for i in range(1, 41)}
    ranking = [f"c{i}" for i in range(1, 41)]  # 40 results, only the first 30 are re-scored
    reranked = milvus_check._rerank_ids(LengthReranker(), ["q"], [ranking], texts)[0]
    assert reranked[0] == "c30" and len(reranked) == milvus_check.RERANK_CANDIDATES
