"""Retrieval with and without the reranker — what a machine without a GPU loses, and how to make up for it.

Runs the chat service's QueryPlanner + Retriever on the live Milvus twice with
the same question plans: once re-ranked by bge-reranker-v2-m3, once in Milvus'
own hybrid order (the CPU mode). Each returns its top 20 chunks, so the report
shows what giving the model 5, 10, 15 or 20 chunks would mean.

    python scripts/eval_without_reranker.py    # → evaluation/reports/10_without_reranker.md (+ .json)
"""

from __future__ import annotations

import asyncio
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for package in ("services/common", "retrieval", "services/chat"):
    sys.path.insert(0, str(ROOT / package))

from openai import AsyncOpenAI  # noqa: E402

from abb_retrieval.config import Paths  # noqa: E402
from abb_retrieval.corpus import load_questions  # noqa: E402
from abb_retrieval.milvus_store import MilvusStore  # noqa: E402
from chat_service.config import Settings  # noqa: E402
from chat_service.generator import Generator  # noqa: E402
from chat_service.query import QueryPlanner  # noqa: E402
from chat_service.retrieval import Retriever  # noqa: E402
from service_common.inference_client import InferenceClient  # noqa: E402

REPORT = ROOT / "evaluation" / "reports" / "10_without_reranker.md"
DEPTHS = (5, 10, 15, 20)
MODES = {"reranker": "http", "no reranker": "none"}


def evidence_ranks(question, chunk_ids: list[str]) -> list[int | None]:
    """0-based rank of each evidence passage in the result list (``None``: not retrieved)."""
    position = {chunk_id: i for i, chunk_id in enumerate(chunk_ids)}
    return [min((position[c] for c in ref.chunk_ids if c in position), default=None) for ref in question.evidence]


def complete(ranks: list[int | None], k: int) -> bool:
    return all(r is not None and r < k for r in ranks)


async def retrieve_all(settings: Settings, texts: list[str]) -> dict[str, list[tuple[list[str], list[str]]]]:
    inference = InferenceClient(settings.inference_url, timeout=60)
    generator = Generator(
        AsyncOpenAI(api_key=settings.openai_api_key, max_retries=3),
        settings.openai_chat_model,
        settings.openai_reasoning_effort,
    )
    store = MilvusStore(settings.milvus_uri, settings.milvus_collection)
    planner = QueryPlanner(generator, settings.query_expansion, settings.procurement_filter)
    semaphore = asyncio.Semaphore(4)

    async def plan(text):
        async with semaphore:
            return await planner.plan(text, [])

    plans = await asyncio.gather(*(plan(t) for t in texts))  # the same plans for both modes
    results = {}
    for mode, reranker in MODES.items():
        retriever = Retriever(
            store, inference, settings.model_copy(update={"reranker": reranker, "context_chunks": max(DEPTHS)})
        )

        async def one(search_plan, retriever=retriever):
            async with semaphore:
                retrieval = await retriever.retrieve(search_plan)
                return [c["chunk_id"] for c in retrieval.chunks], [c["url"] for c in retrieval.chunks]

        results[mode] = await asyncio.gather(*(one(p) for p in plans))
        print(f"  {mode}: done")
    await inference.close()
    return results


async def main() -> None:
    settings = Settings()
    paths = Paths()
    questions = load_questions(paths.questions) + load_questions(paths.questions_b)
    answer_items = [
        q for q in json.loads((ROOT / "evaluation/answers/answer_set.json").read_text(encoding="utf-8")) if q["sources"]
    ]
    texts = [q.question for q in questions] + [item["question"] for item in answer_items]
    results = await retrieve_all(settings, texts)

    n = len(questions)
    ranks = {
        mode: [evidence_ranks(q, ids) for q, (ids, _) in zip(questions, rows[:n], strict=True)]
        for mode, rows in results.items()
    }
    page_hits = {
        mode: {
            k: sum(
                any(url in item["sources"] for url in urls[:k])
                for item, (_, urls) in zip(answer_items, rows[n:], strict=True)
            )
            for k in DEPTHS
        }
        for mode, rows in results.items()
    }
    lost = [
        (q, a, b)
        for q, a, b in zip(questions, ranks["reranker"], ranks["no reranker"], strict=True)
        if complete(a, 10) and not complete(b, 10)
    ]
    won = [
        q.id
        for q, a, b in zip(questions, ranks["reranker"], ranks["no reranker"], strict=True)
        if complete(b, 10) and not complete(a, 10)
    ]
    by_category = defaultdict(list)
    for i, q in enumerate(questions):
        by_category[q.category].append(i)

    def row(mode: str) -> str:
        cells = [f"{sum(complete(r, k) for r in ranks[mode])}/{n}" for k in DEPTHS]
        return f"| {mode} | " + " | ".join(cells) + " |"

    def shown(rs: list[int | None]) -> str:
        return ", ".join("–" if r is None else str(r + 1) for r in rs)

    lines = [
        "# Retrieval without the reranker",
        "",
        f"The chat service's QueryPlanner + Retriever on live Milvus ({settings.retrieval_method}), the same "
        f"question plans in both modes: re-ranked by bge-reranker-v2-m3 (GPU mode), or Milvus' hybrid order (CPU "
        f"mode, no reranker). {n} retrieval questions (sets A + B, chunk-level evidence) and {len(answer_items)} "
        "answer-quality questions with a known source page.",
        "",
        "## Questions with all their evidence among the chunks given to the model",
        "",
        "| Mode | top 5 | top 10 | top 15 | top 20 |",
        "|---|---:|---:|---:|---:|",
        row("reranker"),
        row("no reranker"),
        "",
        "## Answer set: the source page among the chunks given to the model",
        "",
        "| Mode | top 5 | top 10 | top 15 | top 20 |",
        "|---|---:|---:|---:|---:|",
        *(
            f"| {mode} | " + " | ".join(f"{hits[k]}/{len(answer_items)}" for k in DEPTHS) + " |"
            for mode, hits in page_hits.items()
        ),
        "",
        "## By question type (all evidence in the top 10)",
        "",
        "| Type | reranker | no reranker |",
        "|---|---:|---:|",
        *(
            f"| {category} | {sum(complete(ranks['reranker'][i], 10) for i in idx)}/{len(idx)} | "
            f"{sum(complete(ranks['no reranker'][i], 10) for i in idx)}/{len(idx)} |"
            for category, idx in sorted(by_category.items())
        ),
        "",
        f"## Lost without the reranker (top 10): {len(lost)}; gained: {len(won)} ({', '.join(won) or '–'})",
        "",
        "Rank of each evidence passage (– = not in the top 20).",
        "",
        "| Id | Type | Question | reranker | no reranker |",
        "|---|---|---|---|---|",
        *(f"| {q.id} | {q.category} | {q.question} | {shown(a)} | {shown(b)} |" for q, a, b in lost),
        "",
    ]
    REPORT.write_text("\n".join(lines), encoding="utf-8")
    details = {
        "complete": {mode: {k: sum(complete(r, k) for r in rs) for k in DEPTHS} for mode, rs in ranks.items()},
        "answer_set_source_page": page_hits,
        "lost": [q.id for q, _, _ in lost],
        "won": won,
    }
    REPORT.with_suffix(".json").write_text(json.dumps(details, indent=1), encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    asyncio.run(main())
