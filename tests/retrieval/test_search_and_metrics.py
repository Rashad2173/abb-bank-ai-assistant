import numpy as np
import pytest

from abb_retrieval.metrics import evaluate_question, summarize
from abb_retrieval.models import EvidenceRef, Question
from abb_retrieval.search import (
    BM25,
    dense_scores,
    rank,
    reciprocal_rank_fusion,
    sparse_matrix,
    sparse_scores,
    tokenize,
)


def test_rank_returns_best_first():
    scores = np.array([[0.1, 0.9, 0.5, 0.7]])
    assert rank(scores, top_k=3) == [[1, 3, 2]]


def test_dense_scores_are_cosine_for_normalized_vectors():
    docs = np.array([[1.0, 0.0], [0.0, 1.0]], dtype=np.float32)
    query = np.array([[0.6, 0.8]], dtype=np.float32)
    assert dense_scores(query, docs)[0].tolist() == pytest.approx([0.6, 0.8])


def test_sparse_scores_are_dot_products_of_lexical_weights():
    docs = sparse_matrix([{5: 0.5, 7: 0.2}, {7: 0.9}], vocabulary_size=10)
    query = sparse_matrix([{7: 1.0}], vocabulary_size=10)
    assert sparse_scores(query, docs)[0].tolist() == pytest.approx([0.2, 0.9])


def test_reciprocal_rank_fusion_rewards_agreement():
    dense = [[1, 2, 3]]
    keyword = [[2, 4, 1]]
    fused = reciprocal_rank_fusion(dense, keyword, top_k=3)
    assert fused[0][:2] == [2, 1]  # both lists have 2 and 1 near the top


def test_tokenize_treats_azerbaijani_i_variants_alike():
    assert tokenize("İLLİK faiz") == tokenize("illik FAIZ") == ["illik", "faiz"]


def test_bm25_prefers_documents_with_rare_query_terms():
    texts = ["TamKart kredit kartı faiz", "Depozit faiz dərəcəsi", "Kredit kartı tarifləri"]
    scores = BM25(texts).scores(["depozit faiz"])
    assert scores[0].argmax() == 1


def question(*evidence: list[str], category="simple", lang="az") -> Question:
    return Question(
        id="Q", question="?", lang=lang, category=category, expected_answer="",
        evidence=[EvidenceRef(url="u", page_index=0, positions=[], chunk_ids=ids) for ids in evidence],
    )


class TestEvaluateQuestion:
    def test_single_source(self):
        result = evaluate_question(question(["a"]), ["x", "a", "y"])
        assert result.recall == {1: 0.0, 3: 1.0, 5: 1.0, 10: 1.0}
        assert result.reciprocal_rank == 0.5
        assert result.first_relevant_rank == 2

    def test_evidence_covered_by_any_of_its_chunks(self):
        result = evaluate_question(question(["a", "b"]), ["b", "x"])
        assert result.recall[1] == 1.0

    def test_multi_source_needs_every_source(self):
        q = question(["a"], ["b"])
        result = evaluate_question(q, ["a", "x", "x", "x", "x", "x", "b"])
        assert result.recall[5] == 0.5
        assert result.complete[5] == 0.0
        assert result.recall[10] == 1.0
        assert result.complete[10] == 1.0

    def test_not_found(self):
        result = evaluate_question(question(["a"]), ["x", "y"])
        assert result.first_relevant_rank is None
        assert result.reciprocal_rank == 0.0


def test_summarize_breaks_down_by_category_and_language():
    results = [
        evaluate_question(question(["a"], category="simple", lang="az"), ["a"]),
        evaluate_question(question(["a"], category="numeric", lang="en"), ["x"]),
    ]
    summary = summarize(results)
    assert summary.recall[1] == 0.5
    assert summary.by_category["simple"].recall[1] == 1.0
    assert summary.by_lang["en"].recall[1] == 0.0
