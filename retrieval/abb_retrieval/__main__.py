"""Command line interface.

Usage (from the ``retrieval/`` directory)::

    python -m abb_retrieval freeze --corpus data/abb_pages.v1-042c420d.jsonl
                                        # once: question set + the corpus version it was written for
                                        # → evaluation/questions.jsonl
    python -m abb_retrieval chunk       # data/chunks.jsonl + chunk quality report
    python -m abb_retrieval evalset     # map the questions' evidence to the current chunk ids
    python -m abb_retrieval benchmark   # embedding benchmark report
"""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

from .chunk_report import write_chunk_report
from .config import ChunkingConfig, Paths
from .corpus import chunk_corpus, load_chunks, load_pages, load_questions, write_jsonl
from .embedders import MODEL_NAMES
from .evalset import apply_additions, attach_chunks, corpus_sha_of, freeze_evidence, parse_question_set
from .tokens import load_token_counter

log = logging.getLogger("abb_retrieval")


def main() -> None:
    parser = argparse.ArgumentParser(prog="abb_retrieval")
    parser.add_argument("command", choices=("freeze", "chunk", "evalset", "benchmark"))
    parser.add_argument("--models", nargs="+", choices=MODEL_NAMES, default=list(MODEL_NAMES),
                        help="embedding models to benchmark (default: all)")
    parser.add_argument("--no-rerank", action="store_true", help="skip the reranker step of the benchmark")
    parser.add_argument("--corpus", type=Path,
                        help="freeze: the corpus version the question set was written for (default: data/abb_pages.jsonl)")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)-7s %(name)s: %(message)s")

    paths, config = Paths(), ChunkingConfig()
    if args.command == "freeze":
        run_freeze(paths, args.corpus or paths.pages)
    elif args.command == "chunk":
        run_chunking(paths, config)
    elif args.command == "evalset":
        run_evalset(paths)
    elif args.command == "benchmark":
        run_benchmark_command(paths, args.models, rerank=not args.no_rerank)


def run_chunking(paths: Paths, config: ChunkingConfig) -> None:
    pages = load_pages(paths.pages)
    chunks = chunk_corpus(pages, load_token_counter(config.tokenizer), config)
    write_jsonl(paths.chunks, chunks)
    write_chunk_report(chunks, config, paths.reports_dir / "01_chunk_quality.md", paths.data_dir / "chunks.csv")
    log.info("Wrote %d chunks from %d pages to %s", len(chunks), len(pages), paths.chunks)


def run_freeze(paths: Paths, corpus: Path) -> None:
    markdown = paths.question_set.read_text(encoding="utf-8")
    questions = parse_question_set(markdown)
    freeze_evidence(questions, load_pages(corpus), corpus, corpus_sha_of(markdown))
    write_jsonl(paths.questions, questions)
    log.info("Froze %d questions to %s", len(questions), paths.questions)


def run_evalset(paths: Paths) -> None:
    questions = load_questions(paths.questions)
    if paths.evidence_additions.exists():
        apply_additions(questions, json.loads(paths.evidence_additions.read_text(encoding="utf-8")))
    problems = attach_chunks(questions, load_chunks(paths.chunks), load_pages(paths.pages))
    write_jsonl(paths.questions, questions)
    for problem in problems:
        log.warning(problem)
    log.info("Mapped %d questions to chunks (%d unmapped evidence)", len(questions), len(problems))


def run_benchmark_command(paths: Paths, models: list[str], rerank: bool) -> None:
    from .benchmark import run_benchmark  # imports numpy/scipy/torch only when needed
    from .benchmark_report import write_benchmark_report

    chunks, questions = load_chunks(paths.chunks), load_questions(paths.questions)
    result = run_benchmark(chunks, questions, models, paths.embeddings_dir, rerank=rerank)
    report = write_benchmark_report(result, questions, chunks, paths.reports_dir)
    log.info("Benchmark report: %s", report)


if __name__ == "__main__":
    main()
