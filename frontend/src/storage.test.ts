import { describe, expect, it } from "vitest";

import { ParseError, parseData } from "./parse";
import { compress, decompress, packBytes, unpackBytes } from "./storage";

describe("15-bit packing", () => {
  it("round-trips every length and byte value", () => {
    for (const length of [0, 1, 2, 14, 15, 16, 255, 1000]) {
      const bytes = Uint8Array.from({ length }, (_, i) => (i * 37 + length) % 256);
      expect(unpackBytes(packBytes(bytes))).toEqual(bytes);
    }
  });

  it("uses only storable characters below the surrogate range", () => {
    const packed = packBytes(Uint8Array.from({ length: 4096 }, (_, i) => (i * 101) % 256));
    const body = packed.slice(packed.indexOf(":") + 1);
    for (const char of body) {
      const code = char.charCodeAt(0);
      expect(code).toBeGreaterThanOrEqual(0x0800);
      expect(code).toBeLessThan(0xd800);
    }
  });

  it("compresses Azerbaijani text and restores it exactly", () => {
    const text =
      '{"url":"https://abb-bank.az/ferdi","title":"Əmanətlər — şərtlər","lang":"az","category":"individual"}\n'.repeat(
        500,
      );
    const packed = compress(text);
    expect(decompress(packed)).toBe(text);
    expect(packed.length).toBeLessThan(text.length / 10);
  });
});

describe("parseData", () => {
  const page = { url: "https://abb-bank.az/a", title: "A", lang: "az", category: "individual" };

  it("reads JSON Lines and counts languages and categories", () => {
    const text = [JSON.stringify(page), JSON.stringify({ ...page, lang: "en" }), "not json", ""].join("\n");
    const parsed = parseData(text);
    expect(parsed.pages).toHaveLength(2);
    expect(parsed.byLanguage).toEqual({ az: 1, en: 1 });
    expect(parsed.skippedLines).toBe(1);
  });

  it("reads a JSON array", () => {
    expect(parseData(JSON.stringify([page, page])).pages).toHaveLength(2);
  });

  it("rejects files without pages", () => {
    expect(() => parseData("")).toThrow(ParseError);
    expect(() => parseData('{"foo": 1}')).toThrow(ParseError);
    expect(() => parseData("[1, 2")).toThrow(ParseError);
  });
});
