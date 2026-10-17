"""Benchmark report: Markdown for reading, JSON + CSV for further analysis."""

from __future__ import annotations

import csv
import json
from dataclasses import asdict
from pathlib import Path

from .benchmark import RERANK_CANDIDATES, BenchmarkResult
from .metrics import K_VALUES, Summary, summarize
from .models import Chunk, Question

CATEGORY_LABELS = {
    "simple": "Simple", "paraphrase": "Paraphrase", "terminology": "Terminology",
    "numeric": "Numeric", "multi_source": "Multi-source", "multilingual": "Multilingual",
}
DEPLOYMENT_NOTES = {
    "bge-m3": "local model (~2.3 GB); needs ~2–3 GB RAM or a GPU on the server",
    "multilingual-e5-large-instruct": "local model (~2.2 GB); needs ~2–3 GB RAM or a GPU on the server",
    "text-embedding-3-large": "hosted API — no model on the server; paid per token, network latency",
}
OPENAI_PRICE_PER_MILLION = 0.13  # USD, text-embedding-3-large


def write_benchmark_report(
    result: BenchmarkResult, questions: list[Question], chunks: list[Chunk], directory: Path,
    name: str = "02_embedding_benchmark", source: str = "evaluation/retrieval/abb_100_soru_kaynakli.md",
) -> Path:
    """Write ``<name>.md``, ``<name>.json`` and ``<name>_per_question.csv``; ``source`` names the question set."""
    directory.mkdir(parents=True, exist_ok=True)
    summaries = {method: summarize(results) for method, results in result.results.items()}
    ordered = sorted(summaries, key=lambda m: (-summaries[m].recall[5], -summaries[m].mrr))

    markdown = directory / f"{name}.md"
    markdown.write_text(_markdown(result, summaries, ordered, questions, chunks, source), encoding="utf-8")
    (directory / f"{name}.json").write_text(json.dumps({
        "chunks": result.chunk_count,
        "questions": result.question_count,
        "models": [asdict(s) for s in result.model_stats],
        "methods": {m: _summary_dict(summaries[m]) for m in ordered},
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    _write_per_question_csv(result, questions, ordered, directory / f"{name}_per_question.csv")
    return markdown


def _markdown(result, summaries: dict[str, Summary], ordered: list[str], questions, chunks, source: str) -> str:
    best = ordered[0]
    lines = [
        "# Embedding benchmark",
        "",
        f"{result.question_count} questions ({source}) against "
        f"{result.chunk_count:,} chunks. Exact search over all chunks — no index approximation. "
        f"Rerankers re-score the top {RERANK_CANDIDATES} candidates of a method.",
        "",
        "* **Recall@k** — share of a question's evidence found in the top k (multi-source questions need all sources).",
        "* **Complete@5** — share of questions with *all* evidence in the top 5.",
        "* **MRR@10** — 1 / rank of the first relevant chunk.",
        "",
        "## Results (sorted by Recall@5)",
        "",
        "| Method | " + " | ".join(f"R@{k}" for k in K_VALUES) + " | Complete@5 | MRR@10 |",
        "|---|" + "---:|" * (len(K_VALUES) + 2),
    ]
    for method in ordered:
        s = summaries[method]
        name = f"**{method}**" if method == best else method
        lines.append(f"| {name} | " + " | ".join(_pct(s.recall[k]) for k in K_VALUES)
                     + f" | {_pct(s.complete[5])} | {s.mrr:.3f} |")

    top = ordered[:6]
    lines += ["", "## Recall@5 by question type (top 6 methods)", "",
              "| Method | " + " | ".join(CATEGORY_LABELS[c] for c in CATEGORY_LABELS) + " |",
              "|---|" + "---:|" * len(CATEGORY_LABELS)]
    for method in top:
        cats = summaries[method].by_category
        lines.append(f"| {method} | " + " | ".join(_pct(cats[c].recall[5]) if c in cats else "–"
                                                   for c in CATEGORY_LABELS) + " |")

    langs = sorted({q.lang for q in questions})
    counts = {lang: sum(q.lang == lang for q in questions) for lang in langs}
    lines += ["", "## Recall@5 by question language (top 6 methods)", "",
              "| Method | " + " | ".join(f"{lang} (n={counts[lang]})" for lang in langs) + " |",
              "|---|" + "---:|" * len(langs)]
    for method in top:
        by_lang = summaries[method].by_lang
        lines.append(f"| {method} | " + " | ".join(_pct(by_lang[lang].recall[5]) for lang in langs) + " |")

    lines += ["", "## Speed, cost and deployment", "",
              "| Model | Dimensions | Embedding all chunks | Per question | Cost | Deployment |",
              "|---|---:|---:|---:|---:|---|"]
    for s in result.model_stats:
        cost = f"${s.api_tokens / 1e6 * OPENAI_PRICE_PER_MILLION:.2f} ({s.api_tokens:,} tokens)" if s.api_tokens else "free"
        lines.append(f"| {s.model} | {s.dimension} | {s.documents_seconds:.0f} s | {s.query_ms:.0f} ms | {cost} | "
                     f"{DEPLOYMENT_NOTES.get(s.model, '')} |")
    if result.rerank_seconds:
        per_question = 1000 * max(result.rerank_seconds.values()) / result.question_count
        lines.append(f"\nReranker: ~{per_question:.0f} ms per question for {RERANK_CANDIDATES} candidates "
                     "(local GPU, RTX 4060 Laptop).")

    lines += _misses(best, result, questions, chunks)
    return "\n".join(lines) + "\n"


def _misses(method: str, result: BenchmarkResult, questions: list[Question], chunks: list[Chunk]) -> list[str]:
    by_id = {c.chunk_id: c for c in chunks}
    misses = [(q, r) for q, r in zip(questions, result.results[method]) if r.recall[5] < 1.0]
    lines = ["", f"## Questions not fully answered in the top 5 by the best method ({method})", "",
             f"{len(misses)} of {len(questions)}.", ""]
    for question, outcome in misses:
        ranking = result.rankings[method][questions.index(question)]
        expected = {cid for ref in question.evidence for cid in ref.chunk_ids}
        lines += [
            f"### {question.id} ({question.category}, {question.lang}) — first relevant at rank "
            f"{outcome.first_relevant_rank or '> 50'}",
            "",
            f"**Q:** {question.question}",
            "",
            "Expected: " + "; ".join(f"`{cid}` {by_id[cid].title} › {' > '.join(by_id[cid].heading_path)}"
                                     for cid in sorted(expected) if cid in by_id),
            "",
            "Top 3 retrieved:",
            "",
        ]
        lines += [f"{i}. `{cid}` {by_id[cid].title} › {' > '.join(by_id[cid].heading_path)}"
                  f"{' ✅' if cid in expected else ''}" for i, cid in enumerate(ranking[:3], 1)]
        lines.append("")
    return lines


def _write_per_question_csv(result: BenchmarkResult, questions: list[Question], methods: list[str], path: Path) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["question_id", "category", "lang", "question", *[f"{m} · first rank" for m in methods]])
        for index, question in enumerate(questions):
            ranks = [result.results[m][index].first_relevant_rank for m in methods]
            writer.writerow([question.id, question.category, question.lang, question.question,
                             *[r if r is not None else ">50" for r in ranks]])


def _summary_dict(s: Summary) -> dict:
    return {
        "recall": {str(k): round(v, 4) for k, v in s.recall.items()},
        "complete": {str(k): round(v, 4) for k, v in s.complete.items()},
        "mrr": round(s.mrr, 4),
        "by_category": {c: {"recall@5": round(x.recall[5], 4), "mrr": round(x.mrr, 4)} for c, x in s.by_category.items()},
        "by_lang": {c: {"recall@5": round(x.recall[5], 4), "mrr": round(x.mrr, 4)} for c, x in s.by_lang.items()},
    }


def _pct(value: float) -> str:
    return f"{100 * value:.0f}%"
