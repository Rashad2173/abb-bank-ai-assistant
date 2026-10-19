// A streamed answer (POST /v1/chat/stream): one JSON event per line.
//
// Network chunks do not follow lines — a line, or a multi-byte letter like "ə",
// can arrive in two pieces — so bytes are decoded as a stream and split at newlines.

import type { ChatResponse, ChatStatus, Source } from "./types";

export type StreamEvent =
  | { type: "sources"; sources: Source[] }
  | { type: "status"; status: ChatStatus }
  | { type: "delta"; text: string }
  | { type: "done"; response: ChatResponse }
  | { type: "error"; error: { code: string; message: string }; request_id: string };

export async function* streamEvents(body: ReadableStream<Uint8Array>): AsyncGenerator<StreamEvent> {
  const reader = body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  for (;;) {
    const { value, done } = await reader.read();
    if (done) {
      buffer += decoder.decode();
      break;
    }
    buffer += decoder.decode(value, { stream: true }); // keeps a letter cut in half until its second byte
    const lines = buffer.split("\n");
    buffer = lines.pop() ?? "";
    for (const line of lines) if (line.trim()) yield JSON.parse(line) as StreamEvent;
  }
  if (buffer.trim()) yield JSON.parse(buffer) as StreamEvent;
}

/** The text shown while it streams: a citation still being written ("[S", "[S1") is held back. */
export function readableSoFar(text: string): string {
  return text.replace(/\[S?\d*$/, "");
}

/** The sources a partial answer cites, in the order of their first citation — the order the final answer uses. */
export function citedSoFar(text: string, sources: Source[]): Source[] {
  const byId = new Map(sources.map((source) => [source.id, source]));
  const ids = [...new Set(Array.from(text.matchAll(/\[(S\d+)\]/g), (m) => m[1]))];
  return ids.map((id) => byId.get(id)).filter((source) => source !== undefined);
}
