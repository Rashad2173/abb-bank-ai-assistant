import json
from types import SimpleNamespace

import httpx
import pytest
from fastapi.testclient import TestClient

from chat_service.config import Settings
from chat_service.generator import Generation, Generator
from chat_service.guardrail import check_answer
from chat_service.main import build_app
from chat_service.pipeline import ChatPipeline
from chat_service.prompts import format_sources
from chat_service.query import is_about_procurement, is_proper_azerbaijani
from chat_service.retrieval import Retriever
from chat_service.schemas import ChatRequest, Turn
from service_common.inference_client import EmbeddingResult

CHUNKS = {
    "a": {
        "chunk_id": "a",
        "url": "https://abb-bank.az/atm#zaqatala",
        "title": "ATM — Zaqatala",
        "text": "Zaqatala üzrə 12 nöqtə",
        "published": None,
        "is_active": None,
        "valid_until": None,
    },
    "b": {
        "chunk_id": "b",
        "url": "https://abb-bank.az/filiallar",
        "title": "Filiallar",
        "text": "Zaqatala filialı",
        "published": None,
        "is_active": None,
        "valid_until": None,
    },
    "c": {
        "chunk_id": "c",
        "url": "https://abb-bank.az/kampaniyalar/x",
        "title": "Kampaniya",
        "text": "Kampaniya başa çatıb",
        "published": None,
        "is_active": False,
        "valid_until": "2026-01-31",
    },
}


class FakeStore:
    collection = "abb_chunks"

    def __init__(self, order=("b", "a", "c"), per_query=None):
        self.order = list(order)
        self.per_query = per_query or {}
        """Query text → its own ranking (default: ``order`` for every query)."""
        self.searches = []

    def search(self, queries, method, limit, filter=""):
        self.searches.append((method, limit, filter, [q.text for q in queries]))
        return [self.per_query.get(q.text, self.order)[:limit] for q in queries]

    def fetch(self, ids):
        return [CHUNKS[i] for i in ids]

    def count(self):
        return 3


class FakeInference:
    def __init__(self, scores=None, rerank_error=None):
        self.scores = scores or {"a": 0.9, "b": 0.4, "c": 0.01}
        self.rerank_error = rerank_error

    async def embed(self, texts, kind="query"):
        return EmbeddingResult(dense=[[0.6, 0.8]] * len(texts), sparse=[{1: 0.5}] * len(texts))

    async def rerank(self, query, documents, timeout=None):
        if self.rerank_error:
            raise self.rerank_error
        by_text = {c["text"]: self.scores[cid] for cid, c in CHUNKS.items()}
        return [by_text[d] for d in documents]

    async def ready(self):
        return "ok"


class FakeGenerator:
    """Answers with the first two given sources; records what it was given."""

    def __init__(self, status="answered", answer="12 bankomat var [S1] [S2].", source_ids=("S1", "S2")):
        self.status, self.answer_text, self.source_ids = status, answer, list(source_ids)
        self.seen_chunks = None
        self.planned = []

    async def plan_search(self, question, history):
        self.planned.append(question)
        standalone = f"{question} (standalone)" if history else question
        return standalone, f"{standalone} [az]"

    async def answer(self, question, chunks, history):
        self.seen_chunks = list(chunks)
        return Generation(
            status=self.status,
            refusal_reason="none" if self.status != "out_of_scope" else "off_topic",
            language="az",
            answer=self.answer_text,
            source_ids=self.source_ids,
            input_tokens=100,
            output_tokens=20,
        )


def pipeline(settings=None, inference=None, generator=None, store=None):
    settings = settings or Settings(_env_file=None, openai_api_key="x")
    generator = generator or FakeGenerator()
    return ChatPipeline(
        Retriever(store or FakeStore(), inference or FakeInference(), settings), generator, settings
    ), generator


# --------------------------------------------------------------------------- #
# Retrieval and reranking
# --------------------------------------------------------------------------- #


async def test_reranked_chunks_go_to_the_llm_best_first():
    chat, generator = pipeline()
    outcome = await chat.run(ChatRequest(question="Zaqatalada neçə bankomat var?"))

    assert [c["chunk_id"] for c in generator.seen_chunks] == ["a", "b", "c"]
    assert outcome.response.reranked is True
    assert [s.url for s in outcome.response.sources] == [CHUNKS["a"]["url"], CHUNKS["b"]["url"]]


async def test_low_relevance_chunks_are_dropped():
    settings = Settings(_env_file=None, openai_api_key="x", min_rerank_score=0.1)
    chat, generator = pipeline(settings=settings)
    await chat.run(ChatRequest(question="?"))
    assert [c["chunk_id"] for c in generator.seen_chunks] == ["a", "b"]


async def test_milvus_order_is_used_when_the_reranker_fails():
    chat, generator = pipeline(inference=FakeInference(rerank_error=httpx.ReadTimeout("slow")))
    outcome = await chat.run(ChatRequest(question="?"))

    assert outcome.response.reranked is False
    assert [c["chunk_id"] for c in generator.seen_chunks] == ["b", "a", "c"]
    assert all(c["score"] is None for c in generator.seen_chunks)


async def test_without_reranker_milvus_returns_only_the_context_size():
    store = FakeStore()
    settings = Settings(_env_file=None, openai_api_key="x", reranker="none", context_chunks=2)
    chat, generator = pipeline(settings=settings, store=store)
    await chat.run(ChatRequest(question="?"))
    assert [(method, limit) for method, limit, *_ in store.searches] == [("dense+sparse+bm25", 2)]
    assert len(generator.seen_chunks) == 2


async def test_history_is_rewritten_into_a_standalone_question():
    chat, _ = pipeline()
    outcome = await chat.run(ChatRequest(question="dollarla?", history=[Turn(role="user", content="Depozit faizi?")]))
    assert outcome.response.standalone_question == "dollarla? (standalone)"
    assert outcome.response.search_queries == ["dollarla? (standalone)", "dollarla? (standalone) [az]"]


async def test_proper_azerbaijani_needs_no_planning_call_and_skips_tenders():
    store = FakeStore()
    chat, generator = pipeline(store=store)
    outcome = await chat.run(ChatRequest(question="Zaqatalada neçə bankomat var?"))
    assert generator.planned == []
    assert outcome.response.search_queries == ["Zaqatalada neçə bankomat var?"]
    assert store.searches[0][2] == 'category != "procurement"'


async def test_other_languages_are_also_searched_in_azerbaijani_and_fused():
    question = "Сколько банкоматов ABB в Загатале?"
    store = FakeStore(per_query={question: ["c", "b"], f"{question} [az]": ["a", "b"]})
    chat, generator = pipeline(store=store, inference=FakeInference(rerank_error=RuntimeError("off")))
    await chat.run(ChatRequest(question=question))
    assert generator.planned == [question]
    assert store.searches[0][3] == [question, f"{question} [az]"]
    # "b" is in both lists → first after fusion; then the two first places
    assert [c["chunk_id"] for c in generator.seen_chunks] == ["b", "c", "a"]


async def test_procurement_questions_search_tender_notices():
    store = FakeStore()
    chat, _ = pipeline(store=store)
    await chat.run(ChatRequest(question="PaloAlto tenderində iştirak üçün hansı sənədlər lazımdır?"))
    assert store.searches[0][2] == ""


def test_language_and_procurement_detection():
    assert is_proper_azerbaijani("Kredit üçün hansı sənədlər lazımdır?")
    assert not is_proper_azerbaijani("kredit ucun hansi senedler lazimdir")
    assert not is_proper_azerbaijani("Какие документы нужны?")
    assert is_about_procurement("Satınalmalar haqqında") and is_about_procurement("тендер на закупку")
    assert not is_about_procurement("Kart məlumatlarımı soruşurlar")


async def test_the_interaction_holds_question_answer_and_timings():
    chat, _ = pipeline()
    interaction = (await chat.run(ChatRequest(question="Q?", session_id="s1"))).interaction
    assert interaction["question"] == "Q?" and interaction["session_id"] == "s1"
    assert interaction["status"] == "answered" and interaction["grounded"] is True
    assert interaction["retrieved_chunk_ids"] == ["a", "b", "c"]
    assert interaction["total_ms"] >= interaction["generation_ms"] >= 0


# --------------------------------------------------------------------------- #
# Guardrail
# --------------------------------------------------------------------------- #


def generation(status="answered", answer="", source_ids=()):
    return Generation(
        status=status,
        refusal_reason="none",
        language="az",
        answer=answer,
        source_ids=list(source_ids),
        input_tokens=0,
        output_tokens=0,
    )


def test_citations_follow_the_text_order_and_unknown_labels_are_removed():
    chunks = [CHUNKS["a"], CHUNKS["b"]]
    checked = check_answer(generation(answer="X [S2]. Y [S1]. Z [S7].", source_ids=["S1", "S2", "S7"]), chunks)
    assert checked.labels == ["S2", "S1"]
    assert checked.generation.answer == "X [S2]. Y [S1]. Z."
    assert checked.grounded


def test_refusals_carry_no_sources():
    checked = check_answer(
        generation(status="out_of_scope", answer="Bu mövzuda kömək edə bilmirəm [S1].", source_ids=["S1"]),
        [CHUNKS["a"]],
    )
    assert checked.labels == [] and checked.cited == []
    assert checked.generation.answer == "Bu mövzuda kömək edə bilmirəm."


def test_an_answer_without_citations_is_not_grounded():
    checked = check_answer(generation(answer="12 bankomat var."), [CHUNKS["a"]])
    assert not checked.grounded and checked.labels == []


def test_sources_are_labelled_for_the_prompt():
    text = format_sources([CHUNKS["a"], CHUNKS["b"]])
    assert "[S1] https://abb-bank.az/atm#zaqatala\nZaqatala üzrə 12 nöqtə" in text
    assert "[S2] https://abb-bank.az/filiallar" in text
    assert format_sources([]) == "SOURCES:\n(no sources found)"


async def test_generator_sends_strict_schema_and_parses_the_answer():
    calls = []

    async def create(**kwargs):
        calls.append(kwargs)
        payload = {
            "status": "answered",
            "refusal_reason": "none",
            "language": "az",
            "answer": " 12 [S1] ",
            "source_ids": ["S1"],
        }
        return SimpleNamespace(
            output_text=json.dumps(payload), usage=SimpleNamespace(input_tokens=50, output_tokens=10)
        )

    client = SimpleNamespace(responses=SimpleNamespace(create=create))
    result = await Generator(client, "gpt-6-luna", "low").answer("Q?", [CHUNKS["a"]], [])

    assert result.answer == "12 [S1]" and result.source_ids == ["S1"]
    assert calls[0]["text"]["format"]["strict"] is True
    assert "QUESTION: Q?" in calls[0]["input"][-1]["content"]


# --------------------------------------------------------------------------- #
# API
# --------------------------------------------------------------------------- #


@pytest.fixture
def api():
    app = build_app(Settings(_env_file=None, openai_api_key="x", analytics_url=""))
    with TestClient(app) as client:
        app.state.pipeline, _ = pipeline()
        yield client


def test_chat_endpoint_returns_the_answer_contract(api):
    response = api.post("/v1/chat", json={"question": "Zaqatalada neçə bankomat var?"}, headers={"X-Request-ID": "q1"})
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "answered" and body["request_id"] == "q1"
    assert [s["id"] for s in body["sources"]] == ["S1", "S2"]
    assert set(body["timings"]) == {"rewrite_ms", "retrieval_ms", "rerank_ms", "generation_ms", "total_ms"}


def test_blank_and_too_long_questions_are_rejected(api):
    assert api.post("/v1/chat", json={"question": "   "}).status_code == 422
    assert api.post("/v1/chat", json={"question": "x" * 1001}).status_code == 422


def test_ready_lists_its_dependencies(api):
    async def retrieve(model):
        return SimpleNamespace(id=model)

    api.app.state.store = FakeStore()
    api.app.state.inference = FakeInference()
    api.app.state.openai = SimpleNamespace(models=SimpleNamespace(retrieve=retrieve))
    response = api.get("/ready")
    assert response.status_code == 200
    checks = response.json()["checks"]
    assert set(checks) == {"milvus", "inference", "openai"}
    assert checks["milvus"]["detail"] == "3 chunks in 'abb_chunks'"
    assert checks["openai"]["detail"] == "model gpt-6-luna available"


async def test_a_quoted_passage_reaches_planning_and_answering():
    chat, generator = pipeline()
    await chat.run(ChatRequest(question="Hansılardır?", quote="Zaqatalada 12 bankomat var, 3-ü cash-in qəbul edir."))
    assert len(generator.planned) == 1  # rewritten although the text contains "ə"
    assert "Zaqatalada 12 bankomat var" in generator.planned[0] and generator.planned[0].endswith("Hansılardır?")


def test_with_quote_leaves_plain_questions_alone():
    from chat_service.prompts import with_quote

    assert with_quote("Q?", None) == "Q?" and with_quote("Q?", "  ") == "Q?"
    assert with_quote("Q?", "passage").startswith("The user is replying to this part of an earlier answer:")
