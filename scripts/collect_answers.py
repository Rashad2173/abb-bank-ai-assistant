"""Ask the running chat service every question of an answer set and store the answers for grading.

    python scripts/collect_answers.py            # evaluation/answers/answer_set.json → evaluation/reports/07_answers_raw.json
"""

from __future__ import annotations

import argparse
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]


def ask(chat_url: str, item: dict) -> dict:
    response = httpx.post(f"{chat_url}/v1/chat", json={"question": item["question"], "session_id": "answer-eval"},
                          timeout=180)
    response.raise_for_status()
    body = response.json()
    return {
        **item,
        "status": body["status"],
        "answer": body["answer"],
        "cited": [{"id": s["id"], "url": s["url"], "title": s["title"]} for s in body["sources"]],
        "cites_expected_source": not item["sources"] or any(
            s["url"] in item["sources"] for s in body["sources"]),
        "reranked": body["reranked"],
        "total_ms": body["timings"]["total_ms"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--chat-url", default="http://localhost:8001")
    parser.add_argument("--questions", type=Path, default=ROOT / "evaluation" / "answers" / "answer_set.json")
    parser.add_argument("--out", type=Path, default=ROOT / "evaluation" / "reports" / "07_answers_raw.json")
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()

    items = json.loads(args.questions.read_text(encoding="utf-8"))
    with ThreadPoolExecutor(args.workers) as pool:
        results = list(pool.map(lambda item: ask(args.chat_url, item), items))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")
    cited = sum(r["cites_expected_source"] for r in results)
    print(f"{len(results)} answers → {args.out} ({cited} cite the expected source)")


if __name__ == "__main__":
    main()
