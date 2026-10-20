// Upload → keep in localStorage → send to the ingestion service → follow the job.

import { useEffect, useRef, useState } from "react";

import { ApiError, api } from "../api";
import { errorText, useI18n } from "../i18n";
import { type ParsedData, ParseError, parseData } from "../parse";
import { clearData, loadData, loadMeta, type StoredMeta, saveData } from "../storage";
import type { CorpusInfo, IngestJob, IngestMode, JobStatus, Page } from "../types";
import { ModeChoice } from "./ModeChoice";

const POLL_MS = 1500;
const DOCUMENT_RE = /\.(pdf|txt|md)$/i;
const STEPS: JobStatus[] = ["chunking", "comparing", "embedding", "writing", "done"];

interface Props {
  corpus: CorpusInfo | null;
  onProcessed: () => void;
}

export function UploadView({ corpus, onProcessed }: Props) {
  const { t } = useI18n();
  const [meta, setMeta] = useState<StoredMeta | null>(loadMeta);
  const [parsed, setParsed] = useState<ParsedData | null>(null);
  const [documents, setDocuments] = useState<File[] | null>(null);
  const [savedLocally, setSavedLocally] = useState<boolean | null>(null);
  const [busy, setBusy] = useState(false);
  const [job, setJob] = useState<IngestJob | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [dragging, setDragging] = useState(false);
  // With data already indexed, adding is the safe default: replacing deletes what the upload lacks.
  const [mode, setMode] = useState<IngestMode>("replace");
  const modeChosen = useRef(false);
  useEffect(() => {
    if (!modeChosen.current) setMode((corpus?.chunks ?? 0) > 0 ? "append" : "replace");
  }, [corpus?.chunks]);
  const input = useRef<HTMLInputElement>(null);
  const polling = useRef<number | null>(null);

  // Stop polling when the view is left.
  useEffect(
    () => () => {
      if (polling.current !== null) window.clearInterval(polling.current);
    },
    [],
  );

  function stopPolling() {
    if (polling.current !== null) window.clearInterval(polling.current);
    polling.current = null;
  }

  /** JSON(L) of scraped pages is parsed here; PDF / TXT documents are read by the ingestion service. */
  async function readFiles(files: File[]) {
    if (!files.length) return;
    const docs = files.filter((file) => DOCUMENT_RE.test(file.name));
    if (docs.length) {
      setError(null);
      setJob(null);
      setParsed(null);
      setDocuments(docs);
      return;
    }
    setDocuments(null);
    await readFile(files[0]);
  }

  async function readFile(file: File) {
    setError(null);
    setJob(null);
    setBusy(true);
    try {
      const text = await file.text();
      const data = parseData(text);
      setParsed(data);
      try {
        setMeta(saveData(file.name, text, data.pages.length));
        setSavedLocally(true);
      } catch {
        setSavedLocally(false); // quota exceeded / storage blocked — keep it in memory
      }
    } catch (exc) {
      setError(errorText(t, exc instanceof ParseError ? exc.message : "generic"));
    } finally {
      setBusy(false);
    }
  }

  async function process() {
    setError(null);
    setBusy(true);
    try {
      let started: IngestJob;
      if (documents) {
        const result = await api.ingestFiles(documents, mode);
        started = result.job;
        keepDocuments(documents, result.pages);
      } else {
        const data = parsed ?? parseStored();
        if (!data) {
          setBusy(false);
          setError(errorText(t, "empty"));
          return;
        }
        started = await api.ingest(data.pages, mode);
      }
      setJob(started);
      polling.current = window.setInterval(async () => {
        try {
          const current = await api.job(started.job_id);
          setJob(current);
          if (current.status === "done" || current.status === "failed") {
            stopPolling();
            setBusy(false);
            if (current.status === "done") onProcessed();
          }
        } catch (exc) {
          stopPolling();
          setBusy(false);
          setError(errorText(t, exc instanceof ApiError ? exc.code : "generic"));
        }
      }, POLL_MS);
    } catch (exc) {
      setBusy(false);
      if (exc instanceof ApiError && exc.status === 422 && documents) {
        setError(`${t.errors.unreadable} (${exc.message})`);
        return;
      }
      const code = exc instanceof ApiError ? (exc.status === 409 ? "busy" : exc.code) : "generic";
      setError(errorText(t, code));
    }
  }

  /** The text extracted from the documents is what the browser keeps (like an uploaded data file). */
  function keepDocuments(files: File[], pages: Page[]) {
    const name = files.map((file) => file.name).join(", ");
    try {
      setMeta(saveData(name, pages.map((page) => JSON.stringify(page)).join("\n"), pages.length));
      setSavedLocally(true);
    } catch {
      setSavedLocally(false);
    }
  }

  function remove() {
    clearData();
    setMeta(null);
    setParsed(null);
    setDocuments(null);
    setSavedLocally(null);
    setJob(null);
  }

  const hasData = parsed !== null || documents !== null || meta !== null;

  return (
    <section className="upload">
      {/* biome-ignore lint/a11y/noStaticElementInteractions: drag and drop is a mouse shortcut; the "choose file" button inside is the keyboard path */}
      <div
        className={`dropzone ${dragging ? "dropzone-active" : ""}`}
        onDragOver={(event) => {
          event.preventDefault();
          setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={(event) => {
          event.preventDefault();
          setDragging(false);
          readFiles(Array.from(event.dataTransfer.files));
        }}
      >
        <h2>{t.uploadTitle}</h2>
        <p className="muted">{t.uploadHint}</p>
        <input
          ref={input}
          type="file"
          accept=".jsonl,.json,.pdf,.txt,.md,application/json,application/pdf,text/plain"
          multiple
          hidden
          onChange={(event) => {
            readFiles(Array.from(event.target.files ?? []));
            event.target.value = "";
          }}
        />
        <button type="button" className="button" disabled={busy} onClick={() => input.current?.click()}>
          {busy && !job ? t.reading : hasData ? t.replace : t.chooseFile}
        </button>
      </div>

      {error && (
        <p className="alert alert-error" role="alert">
          {error}
        </p>
      )}

      {hasData && (
        <div className="card">
          <div className="card-row">
            <div>
              <div className="label">{t.stored}</div>
              <div className="value">
                {meta?.fileName ?? "—"} · {(parsed?.pages.length ?? meta?.pages ?? 0).toLocaleString()} {t.pages}
              </div>
              {savedLocally !== null && (
                <div className={savedLocally ? "hint-ok" : "hint-warn"}>
                  {savedLocally ? t.savedLocally : t.notSavedLocally}
                  {savedLocally && meta && ` · ${formatSize(meta.characters)}`}
                </div>
              )}
            </div>
            <div>
              <div className="label">{t.indexed}</div>
              <div className="value">{corpus ? `${corpus.chunks.toLocaleString()} ${t.chunks}` : "—"}</div>
            </div>
          </div>

          {documents && (
            <div>
              <div className="label">{t.documentsLabel}</div>
              <ul className="doc-list">
                {documents.map((file) => (
                  <li key={file.name}>
                    📄 {file.name} <span className="muted">· {Math.max(1, Math.round(file.size / 1024))} KB</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {parsed && (
            <div className="facts">
              <Facts title={t.languages} counts={parsed.byLanguage} />
              <Facts title={t.categories} counts={parsed.byCategory} />
              {parsed.skippedLines > 0 && (
                <p className="muted">
                  {parsed.skippedLines} {t.skipped}
                </p>
              )}
            </div>
          )}

          <ModeChoice
            mode={mode}
            disabled={busy}
            onChange={(option) => {
              modeChosen.current = true;
              setMode(option);
            }}
          />

          {job && <JobProgress job={job} />}

          <div className="card-actions">
            <button type="button" className="button button-primary" disabled={busy} onClick={process}>
              {busy && job ? t.processing : t.process}
            </button>
            {job?.status === "done" && (
              <button type="button" className="button" onClick={onProcessed}>
                {t.goToChat}
              </button>
            )}
            <button type="button" className="button button-quiet" disabled={busy} onClick={remove}>
              {t.clear}
            </button>
          </div>
        </div>
      )}
    </section>
  );
}

/** Stored characters as "1.5 M" / "23 K". */
function formatSize(characters: number): string {
  return characters >= 1e6 ? `${(characters / 1e6).toFixed(1)} M` : `${Math.max(1, Math.round(characters / 1e3))} K`;
}

/** The upload kept in localStorage from an earlier visit. */
function parseStored(): ParsedData | null {
  const text = loadData();
  return text ? parseData(text) : null;
}

function Facts({ title, counts }: { title: string; counts: Record<string, number> }) {
  const entries = Object.entries(counts).sort((a, b) => b[1] - a[1]);
  return (
    <div>
      <div className="label">{title}</div>
      <div className="chips">
        {entries.map(([name, count]) => (
          <span key={name} className="chip">
            {name} <strong>{count.toLocaleString()}</strong>
          </span>
        ))}
      </div>
    </div>
  );
}

function JobProgress({ job }: { job: IngestJob }) {
  const { t } = useI18n();
  const current = STEPS.indexOf(job.status);
  return (
    <div className="job">
      <ol className="steps">
        {STEPS.map((step, index) => {
          const state =
            job.status === "failed"
              ? ""
              : index < current || job.status === "done"
                ? "step-done"
                : index === current
                  ? "step-current"
                  : "";
          return (
            <li key={step} className={`step ${state}`}>
              {t.steps[step]}
              {step === "embedding" &&
                job.status === "embedding" &&
                job.to_embed > 0 &&
                ` (${job.embedded}/${job.to_embed})`}
            </li>
          );
        })}
      </ol>
      {job.status === "done" && (
        <p className="hint-ok">
          {job.chunks.toLocaleString()} {t.chunks} · {t.jobResult(job.unchanged, job.to_embed, job.deleted)}
        </p>
      )}
      {job.status === "failed" && (
        <p className="alert alert-error">
          {t.steps.failed}: {job.error}
        </p>
      )}
    </div>
  );
}
