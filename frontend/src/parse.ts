// Reading an uploaded data file: JSON Lines (abb_pages.jsonl) or a JSON array.

import type { Page } from "./types";

export interface ParsedData {
  pages: Page[];
  byLanguage: Record<string, number>;
  byCategory: Record<string, number>;
  skippedLines: number;
}

export class ParseError extends Error {}

const REQUIRED = ["url", "title", "lang", "category"] as const;

export function parseData(text: string): ParsedData {
  const trimmed = text.trim();
  if (!trimmed) throw new ParseError("empty");
  const records: unknown[] = trimmed.startsWith("[") ? parseArray(trimmed) : parseLines(trimmed);

  const pages: Page[] = [];
  let skippedLines = 0;
  for (const record of records) {
    if (isPage(record)) pages.push(record);
    else skippedLines++;
  }
  if (!pages.length) throw new ParseError("no_pages");
  return { pages, byLanguage: countBy(pages, "lang"), byCategory: countBy(pages, "category"), skippedLines };
}

function parseArray(text: string): unknown[] {
  try {
    const value = JSON.parse(text);
    if (Array.isArray(value)) return value;
  } catch {
    /* reported below */
  }
  throw new ParseError("invalid_json");
}

function parseLines(text: string): unknown[] {
  return text
    .split(/\r?\n/)
    .filter((line) => line.trim())
    .map((line) => {
      try {
        return JSON.parse(line);
      } catch {
        return null;
      }
    });
}

function isPage(value: unknown): value is Page {
  return (
    typeof value === "object" &&
    value !== null &&
    REQUIRED.every((key) => typeof (value as Record<string, unknown>)[key] === "string")
  );
}

function countBy(pages: Page[], key: "lang" | "category"): Record<string, number> {
  const counts: Record<string, number> = {};
  for (const page of pages) counts[page[key]] = (counts[page[key]] ?? 0) + 1;
  return counts;
}
