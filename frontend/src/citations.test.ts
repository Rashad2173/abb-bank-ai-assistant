import { describe, expect, it } from "vitest";

import { citedPages, pageNumber } from "./citations";
import type { Source } from "./types";

const source = (id: string, url: string): Source => ({ id, url, title: url }) as Source;

describe("cited pages", () => {
  const sources = [
    source("S1", "https://abb-bank.az/filiallar"),
    source("S4", "https://abb-bank.az/filiallar"),
    source("S7", "https://abb-bank.az/xeberler/a"),
  ];

  it("shows one chip per page, numbered in citation order", () => {
    const { pages } = citedPages("", sources);
    expect(pages.map((page) => page.url)).toEqual(["https://abb-bank.az/filiallar", "https://abb-bank.az/xeberler/a"]);
  });

  it("merges a run of citations of the same page into one mark", () => {
    expect(citedPages("28 filial [S1][S4].", sources).markdown).toBe("28 filial [1](#source-1).");
    expect(citedPages("Bakı [S1] [S7] və Gəncə [S4].", sources).markdown).toBe(
      "Bakı [1](#source-1)[2](#source-2) və Gəncə [1](#source-1).",
    );
  });

  it("drops labels of sources that were not returned", () => {
    expect(citedPages("Text [S9].", sources).markdown).toBe("Text.");
  });

  it("reads the page number back from a link", () => {
    expect(pageNumber("#source-2")).toBe(2);
    expect(pageNumber("https://abb-bank.az")).toBeUndefined();
  });
});
