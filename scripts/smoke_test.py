"""End-to-end check of the running services.

    python scripts/smoke_test.py                       # health, readiness, chat → analytics
    python scripts/smoke_test.py --ingest data/abb_pages.jsonl   # also upload the data (diff → Milvus)

Exit code 0 when every check passes, 1 otherwise.
"""

from __future__ import annotations

import argparse
import json
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
        response = httpx.post(f"{SERVICES['chat']}/v1/chat", json={"question": question, "session_id": session},
                              timeout=120)
        if not report.check(response.status_code == 200, question, f"HTTP {response.status_code}"):
            print("       ", response.text[:300])
            continue
        body = response.json()
        request_ids.append(body["request_id"])
        timings = body["timings"]
        report.check(body["status"] == expected, f"status {body['status']!r} (expected {expected!r})",
                     f"reranked={body['reranked']}, {timings['total_ms']:.0f} ms "
                     f"(retrieval {timings['retrieval_ms']:.0f}, rerank {timings['rerank_ms']:.0f}, "
                     f"LLM {timings['generation_ms']:.0f})")
        print("        answer:", body["answer"][:200].replace("\n", " "))
        for source in body["sources"]:
            print(f"        [{source['id']}] {source['title']} — {source['url']}")
    return request_ids


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
    report.check(job["status"] == "done", "ingestion job",
                 f"{job['chunks']} chunks, {job['unchanged']} unchanged, {job['to_embed']} embedded, "
                 f"{job['deleted']} deleted" if job["status"] == "done" else job["error"])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ingest", type=Path, help="upload this abb_pages.jsonl through the ingestion service")
    args = parser.parse_args()
    report = Report()
    check_operations(report)
    request_ids = check_chat(report)
    check_analytics(report, request_ids)
    check_ingestion(report, args.ingest)
    print(f"\n{'All checks passed' if not report.failures else f'{report.failures} check(s) failed'}")
    sys.exit(1 if report.failures else 0)


if __name__ == "__main__":
    main()
