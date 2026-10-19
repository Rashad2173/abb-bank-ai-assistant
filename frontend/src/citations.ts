// From the model's citations to what the user sees.
//
// The model cites chunks (S1…S10). Several chunks can come from one page — a long
// list split in two — and would show up as two identical source chips. So the
// user sees pages, numbered 1, 2, 3 … in citation order, and a run of citations
// of the same page ("[S1][S2]") becomes a single mark.

import type { Source } from "./types";

const CITATION = /\[(S\d+)\]/g;
const CITATION_RUN = /(?:\s?\[S\d+\])+/g;

export interface CitedPages {
  /** One entry per cited page, in citation order. */
  pages: Source[];
  /** The answer with citations as Markdown links `[n](#source-n)` to page n. */
  markdown: string;
}

export function citedPages(answer: string, sources: Source[]): CitedPages {
  const pages: Source[] = [];
  const pageOf = new Map<string, number>();
  for (const source of sources) {
    let index = pages.findIndex((page) => page.url === source.url);
    if (index < 0) index = pages.push(source) - 1;
    pageOf.set(source.id, index + 1);
  }
  const markdown = answer.replace(CITATION_RUN, (run) => {
    const numbers = [...new Set(Array.from(run.matchAll(CITATION), (m) => pageOf.get(m[1])))].filter(
      (n) => n !== undefined,
    );
    if (numbers.length === 0) return "";
    return (run.startsWith(" ") ? " " : "") + numbers.map((n) => `[${n}](#source-${n})`).join("");
  });
  return { pages, markdown };
}

export function pageNumber(href: string | undefined): number | undefined {
  const match = href?.match(/^#source-(\d+)$/);
  return match ? Number(match[1]) : undefined;
}
