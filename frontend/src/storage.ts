// The uploaded data in the browser's localStorage.
//
// The scraped site is ~21 MB of JSON — four times the ~5 MB localStorage quota.
// It is gzip-compressed (→ ~2.8 MB) and the bytes are packed 15 bits per
// character (→ ~1.5 M characters). Base64 would need 4 bits more per 6, ~3.8 M
// characters, too close to the limit in browsers that count UTF-16 bytes.
// Packed characters start at U+0800 and stay below the surrogate range
// (U+D800–U+DFFF), so every character is a valid, storable code unit.

import { gunzipSync, gzipSync, strFromU8, strToU8 } from "fflate";

const DATA_KEY = "abb.data.v1";
const META_KEY = "abb.data.meta.v1";
const SESSION_KEY = "abb.session";
const OFFSET = 0x0800;
const BITS = 15;

export interface StoredMeta {
  fileName: string;
  pages: number;
  savedAt: string;
  characters: number;
}

export function packBytes(bytes: Uint8Array): string {
  const parts: string[] = [];
  let chunk: number[] = [];
  let buffer = 0;
  let bufferedBits = 0;
  for (const byte of bytes) {
    buffer = (buffer << 8) | byte;
    bufferedBits += 8;
    while (bufferedBits >= BITS) {
      bufferedBits -= BITS;
      chunk.push(OFFSET + ((buffer >> bufferedBits) & 0x7fff));
      if (chunk.length === 8192) {
        parts.push(String.fromCharCode(...chunk));
        chunk = [];
      }
    }
    buffer &= (1 << bufferedBits) - 1;
  }
  if (bufferedBits > 0) chunk.push(OFFSET + ((buffer << (BITS - bufferedBits)) & 0x7fff));
  parts.push(String.fromCharCode(...chunk));
  // Prefix: the byte length (the last character may hold padding bits).
  return `${bytes.length}:${parts.join("")}`;
}

export function unpackBytes(packed: string): Uint8Array {
  const separator = packed.indexOf(":");
  const length = Number(packed.slice(0, separator));
  const bytes = new Uint8Array(length);
  let buffer = 0;
  let bufferedBits = 0;
  let index = 0;
  for (let i = separator + 1; i < packed.length && index < length; i++) {
    buffer = (buffer << BITS) | (packed.charCodeAt(i) - OFFSET);
    bufferedBits += BITS;
    while (bufferedBits >= 8 && index < length) {
      bufferedBits -= 8;
      bytes[index++] = (buffer >> bufferedBits) & 0xff;
    }
    buffer &= (1 << bufferedBits) - 1;
  }
  return bytes;
}

export function compress(text: string): string {
  return packBytes(gzipSync(strToU8(text), { level: 9 }));
}

export function decompress(packed: string): string {
  return strFromU8(gunzipSync(unpackBytes(packed)));
}

/** Saves the raw upload; throws a QuotaExceededError (DOMException) when it does not fit. */
export function saveData(fileName: string, text: string, pages: number): StoredMeta {
  const packed = compress(text);
  const meta: StoredMeta = { fileName, pages, savedAt: new Date().toISOString(), characters: packed.length };
  localStorage.setItem(DATA_KEY, packed);
  localStorage.setItem(META_KEY, JSON.stringify(meta));
  return meta;
}

export function loadMeta(): StoredMeta | null {
  try {
    const meta = localStorage.getItem(META_KEY);
    return meta && localStorage.getItem(DATA_KEY) ? (JSON.parse(meta) as StoredMeta) : null;
  } catch {
    return null; // private window, blocked storage …
  }
}

export function loadData(): string | null {
  try {
    const packed = localStorage.getItem(DATA_KEY);
    return packed ? decompress(packed) : null;
  } catch {
    return null;
  }
}

export function clearData(): void {
  try {
    localStorage.removeItem(DATA_KEY);
    localStorage.removeItem(META_KEY);
  } catch {
    /* storage unavailable — nothing to clear */
  }
}

/** A per-browser id grouping one user's questions in the analytics. */
export function sessionId(): string {
  try {
    let id = localStorage.getItem(SESSION_KEY);
    if (!id) {
      id = crypto.randomUUID();
      localStorage.setItem(SESSION_KEY, id);
    }
    return id;
  } catch {
    return "anonymous";
  }
}
