"""Retrieval exactly as the chat service does it, with and without the query-planning improvements.

Runs the chat service's own QueryPlanner + Retriever against the live Milvus and
inference service (and OpenAI for planning), for four configurations:

* baseline            — the question as asked, tender notices included,
* procurement filter  — tender notices only for procurement questions,
* query expansion     — non-Azerbaijani questions also searched in Azerbaijani,
* both                — what the chat service uses.

Measured on the 200 retrieval questions (chunk-level evidence) and on the 56
answer-quality questions (source page among the chunks given to the LLM).

    python scripts/eval_retrieval_pipeline.py    # → evaluation/reports/08_retrieval_pipeline.md (+ .json)
    python scripts/eval_retrieval_pipeline.py --configs "both (chat service)" --report 09_retrieval_methods
        --methods dense+sparse dense+bm25 dense+sparse+bm25   # (one command)
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for package in ("services/common", "retrieval", "services/chat"):
    sys.path.insert(0, str(ROOT / package))

from openai import AsyncOpenAI  # noqa: E402

from abb_retrieval.config import Paths  # noqa: E402
from abb_retrieval.corpus import load_questions  # noqa: E402
from abb_retrieval.metrics import evaluate_question, summarize  # noqa: E402
from abb_retrieval.milvus_store import MilvusStore  # noqa: E402
from chat_service.config import Settings  # noqa: E402
from chat_service.generator import Generator  # noqa: E402
from chat_service.query import QueryPlanner  # noqa: E402
from chat_service.retrieval import Retriever  # noqa: E402
from service_common.inference_client import InferenceClient  # noqa: E402

REPORT = ROOT / "evaluation" / "reports" / "08_retrieval_pipeline.md"
CONFIGS = {
    "baseline": (False, False),
    "procurement filter": (False, True),
    "query expansion": (True, False),
    "both (chat service)": (True, True),
}


class CachedGenerator(Generator):
    """Plans each question once — the four configurations reuse the result."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.plans: dict[str, tuple[str, str]] = {}

    async def plan_search(self, question, history):
        if question not in self.plans:
            self.plans[question] = await super().plan_search(question, history)
        return self.plans[question]


async def run_config(name, expand, procurement_filter, questions, retriever, generator, workers=4):
    planner = QueryPlanner(generator, expand=expand, procurement_filter=procurement_filter)
    semaphore = asyncio.Semaphore(workers)

    async def one(text):
        async with semaphore:
            plan = await planner.plan(text, [])
            retrieval = await retriever.retrieve(plan)
            return [c["chunk_id"] for c in retrieval.chunks], [c["url"] for c in retrieval.chunks], plan.queries

    results = await asyncio.gather(*(one(q) for q in questions))
    print(f"  {name}: done")
    return results


def lang_breakdown(items, hits):
    by = {}
    for item, hit in zip(items, hits, strict=True):
        by.setdefault(item["lang"], []).append(hit)
    return {lang: f"{sum(v)}/{len(v)}" for lang, v in sorted(by.items())}


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--configs", nargs="+", default=list(CONFIGS), choices=list(CONFIGS))
    parser.add_argument("--methods", nargs="+", default=None, help="Milvus search methods (default: the chat setting)")
    parser.add_argument("--report", default=REPORT.stem)
    args = parser.parse_args()
    report = REPORT.with_name(f"{args.report}.md")

    settings = Settings()
    methods = args.methods or [settings.retrieval_method]
    paths = Paths()
    retrieval_questions = load_questions(paths.questions) + load_questions(paths.questions_b)
    answer_items = [
        q for q in json.loads((ROOT / "evaluation/answers/answer_set.json").read_text(encoding="utf-8")) if q["sources"]
    ]

    inference = InferenceClient(settings.inference_url, timeout=60)
    openai = AsyncOpenAI(api_key=settings.openai_api_key, max_retries=3)
    generator = CachedGenerator(openai, settings.openai_chat_model, settings.openai_reasoning_effort)
    store = MilvusStore(settings.milvus_uri, settings.milvus_collection)

    texts = [q.question for q in retrieval_questions] + [q["question"] for q in answer_items]
    table, details = [], {}
    runs = [(method, name) for method in methods for name in args.configs]
    for method, config in runs:
        name = config if len(methods) == 1 else f"{method} · {config}"
        expand, procurement_filter = CONFIGS[config]
        retriever = Retriever(store, inference, settings.model_copy(update={"retrieval_method": method}))
        results = await run_config(name, expand, procurement_filter, texts, retriever, generator)
        ranked = [ids for ids, _, _ in results[: len(retrieval_questions)]]
        summary = summarize(
            [evaluate_question(q, r) for q, r in zip(retrieval_questions, ranked, strict=True)], breakdown=True
        )
        page_hits = [
            any(u in item["sources"] for u in urls)
            for item, (_, urls, _) in zip(answer_items, results[len(retrieval_questions) :], strict=True)
        ]
        table.append((name, summary, sum(page_hits)))
        details[name] = {
            "retrieval": {
                "complete@5": summary.complete[5],
                "recall@5": summary.recall[5],
                "recall@10": summary.recall[10],
                "mrr": summary.mrr,
                "recall@5_by_lang": {k: v.recall[5] for k, v in summary.by_lang.items()},
            },
            "answer_set_source_in_context": f"{sum(page_hits)}/{len(page_hits)}",
            "answer_set_by_lang": lang_breakdown(answer_items, page_hits),
        }
    await inference.close()

    n, m = len(retrieval_questions), len(answer_items)
    lines = [
        "# Retrieval pipeline: query planning",
        "",
        f"The chat service's QueryPlanner + Retriever on live Milvus ({', '.join(methods)} → bge-reranker-v2-m3 → "
        f"top {settings.context_chunks} chunks). {n} retrieval questions (sets A + B, chunk-level evidence) and "
        f"{m} answer-quality questions with a known source page.",
        "",
        "| Configuration | All evidence in top 5 | R@5 | R@10 | MRR | R@5 EN | R@5 RU "
        "| Source page in context (answer set) |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for name, s, page_hits in table:
        lines.append(
            f"| {name} | {round(s.complete[5] * s.count)}/{s.count} | {s.recall[5]:.1%} | {s.recall[10]:.1%} | "
            f"{s.mrr:.3f} | {s.by_lang['en'].recall[5]:.0%} | {s.by_lang['ru'].recall[5]:.0%} | {page_hits}/{m} |"
        )
    lines += [
        "",
        "Answer set, source page in context, by language: "
        + "; ".join(f"{name}: {d['answer_set_by_lang']}" for name, d in details.items()),
        "",
    ]
    report.write_text("\n".join(lines), encoding="utf-8")
    report.with_suffix(".json").write_text(json.dumps(details, ensure_ascii=False, indent=1), encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    asyncio.run(main())
