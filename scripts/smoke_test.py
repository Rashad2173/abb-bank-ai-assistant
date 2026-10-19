"""End-to-end check of the running services.

    python scripts/smoke_test.py                       # health, readiness, chat (also streamed) → analytics
    python scripts/smoke_test.py --ingest data/abb_pages.jsonl   # also upload the data (diff → Milvus)

Exit code 0 when every check passes, 1 otherwise.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import uuid
from pathlib import Path

import httpx

SERVICES = {
    "chat": "http://localhost:8001",
    "analytics": "http://localhost:8002",
    "ingestion": "http://localhost:8003",
    "inference": "http://localhost:8004",
    "scraper": "http://localhost:8005",
}

QUESTIONS = [
    ("Zaqatalada ABB-nin neçə bankomatı var?", "answered"),
    ("Salam!", "greeting"),
    ("What is the capital of France?", "out_of_scope"),
]


class Report:
    def __init__(self) -> None:
        self.failures = 0

    def check(self, ok: bool, label: str, detail: str = "") -> bool:
        self.failures += not ok
        print(f"  {'PASS' if ok else 'FAIL'}  {label}{f' — {detail}' if detail else ''}")
        return ok


def check_operations(report: Report) -> None:
    print("Health and readiness")
    for name, url in SERVICES.items():
        try:
            health = httpx.get(f"{url}/health", timeout=5)
            ready = httpx.get(f"{url}/ready", timeout=15)
        except httpx.HTTPError as exc:
            report.check(False, name, f"not reachable ({type(exc).__name__})")
            continue
        report.check(health.status_code == 200, f"{name} /health")
        checks = ready.json().get("checks", {})
        detail = "; ".join(f"{k}: {v['detail']}" for k, v in checks.items())
        report.check(ready.status_code == 200, f"{name} /ready", detail)


def check_chat(report: Report) -> list[str]:
    print("\nChat")
    session = f"smoke-{uuid.uuid4().hex[:8]}"
    request_ids = []
    for question, expected in QUESTIONS:
        response = httpx.post(
            f"{SERVICES['chat']}/v1/chat", json={"question": question, "session_id": session}, timeout=120
        )
        if not report.check(response.status_code == 200, question, f"HTTP {response.status_code}"):
            print("       ", response.text[:300])
            continue
        body = response.json()
        request_ids.append(body["request_id"])
        timings = body["timings"]
        report.check(
            body["status"] == expected,
            f"status {body['status']!r} (expected {expected!r})",
            f"reranked={body['reranked']}, {timings['total_ms']:.0f} ms "
            f"(retrieval {timings['retrieval_ms']:.0f}, rerank {timings['rerank_ms']:.0f}, "
            f"LLM {timings['generation_ms']:.0f})",
        )
        print("        answer:", body["answer"][:200].replace("\n", " "))
        for source in body["sources"]:
            print(f"        [{source['id']}] {source['title']} — {source['url']}")
    return request_ids


def check_stream(report: Report) -> list[str]:
    """The streamed answer: text arrives before the end, and the final answer is the usual contract."""
    print("\nChat (streamed)")
    question = "TamKart Classic kartının illik xidmət haqqı nə qədərdir?"
    started = time.perf_counter()
    first_word = completed = None
    events = []
    with httpx.stream("POST", f"{SERVICES['chat']}/v1/chat/stream", json={"question": question}, timeout=120) as r:
        if not report.check(r.status_code == 200, question, f"HTTP {r.status_code}"):
            return []
        for line in r.iter_lines():
            if not line:
                continue
            event = json.loads(line)
            events.append(event)
            if event["type"] == "delta" and first_word is None:
                first_word = time.perf_counter() - started
            elif event["type"] == "done":
                completed = time.perf_counter() - started
    kinds = [event["type"] for event in events]
    report.check(kinds[:2] == ["sources", "status"] and kinds[-1] == "done", "events: sources, status, delta …, done")
    if completed is None:
        return []
    report.check(
        first_word is not None and first_word < completed,
        "the first word arrives before the answer is complete",
        f"first word {first_word:.1f} s, complete {completed:.1f} s, {kinds.count('delta')} pieces"
        if first_word is not None
        else "no text",
    )
    done = events[-1]["response"]
    streamed = "".join(event["text"] for event in events if event["type"] == "delta")
    # The checked answer may drop a citation label the model invented; the words are the same.
    report.check(_words(streamed) == _words(done["answer"]), "the streamed text is the final answer")
    print("        answer:", done["answer"][:200].replace("\n", " "))
    return [done["request_id"]]


def _words(answer: str) -> str:
    return " ".join(re.sub(r"\[S\d+\]", "", answer).split())


def check_analytics(report: Report, request_ids: list[str]) -> None:
    print("\nAnalytics")
    time.sleep(1)  # the chat service records after it has answered
    recent = httpx.get(f"{SERVICES['analytics']}/v1/interactions", params={"limit": 20}, timeout=10).json()
    stored = {item["request_id"] for item in recent["items"]}
    report.check(set(request_ids) <= stored, "every chat request was recorded", f"{len(request_ids)} requests")
    stats = httpx.get(f"{SERVICES['analytics']}/v1/stats", params={"days": 7}, timeout=10).json()
    report.check(stats["total"] >= len(request_ids), "stats", json.dumps(stats["by_status"]))


def check_ingestion(report: Report, data: Path | None) -> None:
    print("\nIngestion")
    corpus = httpx.get(f"{SERVICES['ingestion']}/v1/corpus", timeout=30).json()
    report.check(corpus["chunks"] > 0, "corpus", f"{corpus['chunks']} chunks in {corpus['collection']!r}")
    if data is None:
        return
    pages = [json.loads(line) for line in data.open(encoding="utf-8") if line.strip()]
    job = httpx.post(f"{SERVICES['ingestion']}/v1/ingest", json={"pages": pages}, timeout=120).json()
    print(f"        job {job['job_id']} started for {len(pages)} pages")
    while job["status"] not in ("done", "failed"):
        time.sleep(2)
        job = httpx.get(f"{SERVICES['ingestion']}/v1/ingest/{job['job_id']}", timeout=10).json()
        print(f"        {job['status']}: {job['embedded']}/{job['to_embed']} embedded")
    report.check(
        job["status"] == "done",
        "ingestion job",
        f"{job['chunks']} chunks, {job['unchanged']} unchanged, {job['to_embed']} embedded, {job['deleted']} deleted"
        if job["status"] == "done"
        else job["error"],
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ingest", type=Path, help="upload this abb_pages.jsonl through the ingestion service")
    args = parser.parse_args()
    report = Report()
    check_operations(report)
    request_ids = check_chat(report) + check_stream(report)
    check_analytics(report, request_ids)
    check_ingestion(report, args.ingest)
    print(f"\n{'All checks passed' if not report.failures else f'{report.failures} check(s) failed'}")
    sys.exit(1 if report.failures else 0)


if __name__ == "__main__":
    main()
