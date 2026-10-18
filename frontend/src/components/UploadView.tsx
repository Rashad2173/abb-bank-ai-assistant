// Upload → keep in localStorage → send to the ingestion service → follow the job.

import { useEffect, useRef, useState } from "react";

import { api, ApiError } from "../api";
import { errorText, useI18n } from "../i18n";
import { parseData, ParseError, type ParsedData } from "../parse";
import { clearData, loadData, loadMeta, saveData, type StoredMeta } from "../storage";
import type { CorpusInfo, IngestJob, IngestMode, JobStatus } from "../types";

const POLL_MS = 1500;
const STEPS: JobStatus[] = ["chunking", "comparing", "embedding", "writing", "done"];

interface Props {
  corpus: CorpusInfo | null;
  onProcessed: () => void;
  onSkip: () => void;
}

export function UploadView({ corpus, onProcessed, onSkip }: Props) {
  const { t } = useI18n();
  const [meta, setMeta] = useState<StoredMeta | null>(loadMeta);
  const [parsed, setParsed] = useState<ParsedData | null>(null);
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

  useEffect(() => () => stopPolling(), []);

  function stopPolling() {
    if (polling.current !== null) window.clearInterval(polling.current);
    polling.current = null;
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
      const data = parsed ?? parseStored();
      if (!data) {
        setBusy(false);
        setError(errorText(t, "empty"));
        return;
      }
      const started = await api.ingest(data.pages, mode);
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
      const code = exc instanceof ApiError ? (exc.status === 409 ? "busy" : exc.code) : "generic";
      setError(errorText(t, code));
    }
  }

  function remove() {
    clearData();
    setMeta(null);
    setParsed(null);
    setSavedLocally(null);
    setJob(null);
  }

  const hasData = parsed !== null || meta !== null;

  return (
    <section className="upload">
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
          const file = event.dataTransfer.files[0];
          if (file) readFile(file);
        }}
      >
        <h1>{t.uploadTitle}</h1>
        <p className="muted">{t.uploadHint}</p>
        <input
          ref={input}
          type="file"
          accept=".jsonl,.json,application/json"
          hidden
          onChange={(event) => {
            const file = event.target.files?.[0];
            if (file) readFile(file);
            event.target.value = "";
          }}
        />
        <button className="button" disabled={busy} onClick={() => input.current?.click()}>
          {busy && !job ? t.reading : hasData ? t.replace : t.chooseFile}
        </button>
      </div>

      {!hasData && (corpus?.chunks ?? 0) > 0 && (
        <div className="skip">
          <span className="muted">{t.skipHint}</span>
          <button className="button" onClick={onSkip}>
            {t.skip} ({corpus!.chunks.toLocaleString()} {t.chunks})
          </button>
        </div>
      )}

      {error && <p className="alert alert-error" role="alert">{error}</p>}

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

          {parsed && (
            <div className="facts">
              <Facts title={t.languages} counts={parsed.byLanguage} />
              <Facts title={t.categories} counts={parsed.byCategory} />
              {parsed.skippedLines > 0 && <p className="muted">{parsed.skippedLines} {t.skipped}</p>}
            </div>
          )}

          <fieldset className="mode" disabled={busy}>
            <legend className="label">{t.modeTitle}</legend>
            {(["append", "replace"] as IngestMode[]).map((option) => (
              <label key={option} className={`mode-option ${mode === option ? "mode-active" : ""}`}>
                <input type="radio" name="mode" value={option} checked={mode === option} onChange={() => { modeChosen.current = true; setMode(option); }} />
                <span>
                  <strong>{option === "append" ? t.modeAppend : t.modeReplace}</strong>
                  <span className="muted">{option === "append" ? t.modeAppendHint : t.modeReplaceHint}</span>
                </span>
              </label>
            ))}
          </fieldset>

          {job && <JobProgress job={job} />}

          <div className="card-actions">
            <button className="button button-primary" disabled={busy} onClick={process}>
              {busy && job ? t.processing : t.process}
            </button>
            {job?.status === "done" && (
              <button className="button" onClick={onProcessed}>{t.goToChat}</button>
            )}
            <button className="button button-quiet" disabled={busy} onClick={remove}>{t.clear}</button>
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
          <span key={name} className="chip">{name} <strong>{count.toLocaleString()}</strong></span>
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
          const state = job.status === "failed" ? "" : index < current || job.status === "done" ? "step-done" : index === current ? "step-current" : "";
          return (
            <li key={step} className={`step ${state}`}>
              {t.steps[step]}
              {step === "embedding" && job.status === "embedding" && job.to_embed > 0 && ` (${job.embedded}/${job.to_embed})`}
            </li>
          );
        })}
      </ol>
      {job.status === "done" && (
        <p className="hint-ok">
          {job.chunks.toLocaleString()} {t.chunks} · {t.jobResult(job.unchanged, job.to_embed, job.deleted)}
        </p>
      )}
      {job.status === "failed" && <p className="alert alert-error">{t.steps.failed}: {job.error}</p>}
    </div>
  );
}
