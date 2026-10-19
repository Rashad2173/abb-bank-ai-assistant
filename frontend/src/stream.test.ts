import { describe, expect, it } from "vitest";

import { citedSoFar, readableSoFar, type StreamEvent, streamEvents } from "./stream";
import type { Source } from "./types";

function body(chunks: Uint8Array[]): ReadableStream<Uint8Array> {
  return new ReadableStream({
    start(controller) {
      for (const chunk of chunks) controller.enqueue(chunk);
      controller.close();
    },
  });
}

async function collect(stream: ReadableStream<Uint8Array>): Promise<StreamEvent[]> {
  const events: StreamEvent[] = [];
  for await (const event of streamEvents(stream)) events.push(event);
  return events;
}

const source = (id: string, url: string): Source => ({ id, url, title: url }) as Source;

describe("stream events", () => {
  const lines = [
    { type: "status", status: "answered" },
    { type: "delta", text: "Kartın haqqı " },
    { type: "delta", text: "10 AZN-dir [S1]." },
  ];
  const bytes = new TextEncoder().encode(lines.map((line) => `${JSON.stringify(line)}\n`).join(""));

  it("reads one event per line", async () => {
    expect(await collect(body([bytes]))).toEqual(lines);
  });

  it("joins lines and letters split across network chunks", async () => {
    // Split at every byte: lines and the two-byte "ı" are cut in half.
    const chunks = Array.from(bytes, (byte) => Uint8Array.of(byte));
    expect(await collect(body(chunks))).toEqual(lines);
  });
});

describe("partial answers", () => {
  it("holds back a citation that is still being written", () => {
    expect(readableSoFar("10 AZN [S")).toBe("10 AZN ");
    expect(readableSoFar("10 AZN [S1")).toBe("10 AZN ");
    expect(readableSoFar("10 AZN [S1]")).toBe("10 AZN [S1]");
  });

  it("numbers sources by first citation, like the final answer", () => {
    const sources = [source("S1", "a"), source("S2", "b"), source("S3", "c")];
    expect(citedSoFar("X [S3]. Y [S1]. Z [S3].", sources).map((s) => s.id)).toEqual(["S3", "S1"]);
    expect(citedSoFar("No citation yet", sources)).toEqual([]);
  });
});
