// From a link to an indexed knowledge base, with the work shown as it happens:
// a stage-by-stage pipeline, live counters, the URLs being read and short facts
// about what the system does — so the minutes of waiting are worth watching.

import { type FormEvent, useEffect, useRef, useState } from "react";

import { ApiError, api } from "../api";
import { errorText, useI18n } from "../i18n";
import { parseData } from "../parse";
import { saveData } from "../storage";
import type { CorpusInfo, IngestMode, ScrapeJob, ScrapeStatus } from "../types";
import { ModeChoice } from "./ModeChoice";

const POLL_MS = 800;
const FACT_MS = 6000;
const STAGES: ScrapeStatus[] = ["discovering", "crawling", "network", "extracting", "indexing", "done"];
// Share of the progress bar per stage (roughly their duration on a cached run).
const WEIGHTS: Partial<Record<ScrapeStatus, number>> = {
  discovering: 10,
  crawling: 15,
  network: 5,
  extracting: 50,
  indexing: 20,
};

interface Props {
  corpus: CorpusInfo | null;
  onDone: () => void;
}

export function ScrapeFlow({ corpus, onDone }: Props) {
  const { t } = useI18n();
  const [url, setUrl] = useState("https://abb-bank.az");
  const [mode, setMode] = useState<IngestMode>("replace");
  const modeChosen = useRef(false);
  const [job, setJob] = useState<ScrapeJob | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [saved, setSaved] = useState<boolean | null>(null);
  const [now, setNow] = useState(Date.now());
  const [fact, setFact] = useState(0);
  const polling = useRef<number | null>(null);

  useEffect(() => {
    if (!modeChosen.current) setMode((corpus?.chunks ?? 0) > 0 ? "append" : "replace");
  }, [corpus?.chunks]);

  const running = job !== null && job.status !== "done" && job.status !== "failed";

  // Clock and rotating facts only while running.
  useEffect(() => {
    if (!running) return;
    const clock = window.setInterval(() => setNow(Date.now()), 1000);
    const facts = window.setInterval(() => setFact((f) => (f + 1) % t.facts.length), FACT_MS);
    return () => {
      window.clearInterval(clock);
      window.clearInterval(facts);
    };
  }, [running, t.facts.length]);

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

  async function start(event: FormEvent) {
    event.preventDefault();
    setError(null);
    setSaved(null);
    try {
      const started = await api.scrape(url.trim(), mode);
      setJob(started);
      setNow(Date.now());
      polling.current = window.setInterval(async () => {
        try {
          const current = await api.scrapeJob(started.job_id);
          setJob(current);
          if (current.status === "done") {
            stopPolling();
            await keepInBrowser(current.job_id);
          } else if (current.status === "failed") {
            stopPolling();
          }
        } catch (exc) {
          stopPolling();
          setError(errorText(t, exc instanceof ApiError ? exc.code : "generic"));
        }
      }, POLL_MS);
    } catch (exc) {
      if (exc instanceof ApiError && exc.status === 422) setError(t.unsupportedSite);
      else setError(errorText(t, exc instanceof ApiError ? (exc.status === 409 ? "busy" : exc.code) : "generic"));
    }
  }

  /** The brief keeps the data in localStorage — the scraped pages too, like an uploaded file. */
  async function keepInBrowser(jobId: string) {
    try {
      const text = await api.scrapedPages(jobId);
      saveData("abb-bank.az (live)", text, parseData(text).pages.length);
      setSaved(true);
    } catch {
      setSaved(false);
    }
  }

  const elapsed = job
    ? Math.max(
        0,
        Math.round(((job.finished_at ? Date.parse(job.finished_at) : now) - Date.parse(job.started_at)) / 1000),
      )
    : 0;

  return (
    <div className="scrape">
      {!job || job.status === "failed" ? (
        <form className="card scrape-form" onSubmit={start}>
          <div>
            <h2>{t.scrapeTitle}</h2>
            <p className="muted">{t.scrapeHint}</p>
          </div>
          <div className="url-row">
            <input
              className="url-input"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://abb-bank.az"
              aria-label="URL"
              spellCheck={false}
            />
            <button type="submit" className="button button-primary" disabled={!url.trim()}>
              {t.scrapeStart}
            </button>
          </div>
          <div className="stage-preview">
            <div className="label">{t.whatHappens}</div>
            <ol>
              {STAGES.filter((stage) => stage !== "done").map((stage) => (
                <li key={stage}>{t.scrapeStages[stage]}</li>
              ))}
            </ol>
          </div>
          <ModeChoice
            mode={mode}
            onChange={(m) => {
              modeChosen.current = true;
              setMode(m);
            }}
          />
          {job?.status === "failed" && (
            <p className="alert alert-error">
              {t.steps.failed}: {job.error}
            </p>
          )}
          {error && (
            <p className="alert alert-error" role="alert">
              {error}
            </p>
          )}
        </form>
      ) : (
        <div className="card pipeline">
          <div className="pipeline-head">
            <img
              className={`pipeline-mascot ${running ? "bobbing" : ""}`}
              src="/assistant-mascot.png"
              alt=""
              aria-hidden
            />
            <div>
              <h1>{job.status === "done" ? t.scrapeDone : t.scrapeRunning}</h1>
              <p className="muted">
                {job.url} · {formatClock(elapsed)}
              </p>
            </div>
          </div>

          <div
            className="progress"
            role="progressbar"
            aria-valuemin={0}
            aria-valuemax={100}
            aria-valuenow={Math.round(progress(job))}
          >
            <div className="progress-fill" style={{ width: `${progress(job)}%` }} />
          </div>

          <div className="counters">
            <Counter label={t.counterPages} value={job.discovered} />
            <Counter label={t.counterDocuments} value={job.pages} />
            <Counter label={t.counterChunks} value={job.chunks} />
          </div>

          <ol className="stages">
            {STAGES.map((stage) => (
              <li key={stage} className={`stage stage-${stageState(job.status, stage)}`}>
                <span className="stage-icon" aria-hidden>
                  {stageState(job.status, stage) === "done" ? "✓" : ""}
                </span>
                <span className="stage-body">
                  <span className="stage-title">{t.scrapeStages[stage]}</span>
                  <span className="stage-detail">{stageDetail(job, stage, t)}</span>
                </span>
              </li>
            ))}
          </ol>

          {running && job.recent.length > 0 && (
            <section className="ticker" aria-label={t.readingNow}>
              <div className="label">{t.readingNow}</div>
              <ul>
                {job.recent.slice(0, 6).map((r, i) => (
                  // biome-ignore lint/suspicious/noArrayIndexKey: a retried URL can appear twice; the list is replaced on every poll
                  <li key={`${r.url}-${i}`}>
                    <span className={`badge badge-${r.outcome}`}>{t.outcomes[r.outcome]}</span>
                    <span className="ticker-url">{r.url.replace(/^https:\/\/abb-bank\.az/, "") || "/"}</span>
                  </li>
                ))}
              </ul>
            </section>
          )}

          {running && (
            <div className="fact" key={fact}>
              <span className="label">{t.didYouKnow}</span>
              <p>{t.facts[fact]}</p>
            </div>
          )}

          {job.status === "done" && (
            <div className="scrape-result">
              <p className="hint-ok">
                {t.jobResult(job.unchanged, job.to_embed, job.deleted)}
                {saved === true && ` · ${t.savedLocally}`}
                {saved === false && ` · ${t.notSavedLocally}`}
              </p>
              <div className="card-actions">
                <button type="button" className="button button-primary" onClick={onDone}>
                  {t.goToChat}
                </button>
                <button type="button" className="button button-quiet" onClick={() => setJob(null)}>
                  {t.scrapeAgain}
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function Counter({ label, value }: { label: string; value: number }) {
  return (
    <div className="counter">
      <div className="counter-value">{value ? value.toLocaleString() : "—"}</div>
      <div className="label">{label}</div>
    </div>
  );
}

function stageState(current: ScrapeStatus, stage: ScrapeStatus): "done" | "active" | "pending" {
  const at = STAGES.indexOf(current === "queued" ? "discovering" : current);
  const index = STAGES.indexOf(stage);
  if (current === "done" || index < at) return "done";
  return index === at ? "active" : "pending";
}

function progress(job: ScrapeJob): number {
  if (job.status === "done") return 100;
  let total = 0;
  for (const stage of STAGES) {
    const weight = WEIGHTS[stage] ?? 0;
    const state = stageState(job.status, stage);
    if (state === "done") total += weight;
    else if (state === "active") total += weight * stageFraction(job, stage);
  }
  return Math.min(99, total);
}

function stageFraction(job: ScrapeJob, stage: ScrapeStatus): number {
  if (stage === "crawling" && job.discovered) return (job.fetched + job.from_cache + job.failed) / job.discovered;
  if (stage === "indexing" && job.to_embed) return 0.3 + 0.7 * (job.embedded / job.to_embed);
  return 0.35; // stages without a count: show them as under way
}

function stageDetail(job: ScrapeJob, stage: ScrapeStatus, t: ReturnType<typeof useI18n>["t"]): string {
  const state = stageState(job.status, stage);
  if (state === "pending") return "";
  switch (stage) {
    case "discovering":
      return `${job.discovered.toLocaleString()} ${t.urls}`;
    case "crawling":
      return t.crawlDetail(job.fetched + job.from_cache, job.discovered, job.fetched, job.from_cache, job.failed);
    case "extracting":
      return state === "done" ? `${job.pages.toLocaleString()} ${t.pages}` : t.extractDetail;
    case "indexing":
      return job.chunks ? t.indexDetail(job.chunks, job.embedded, job.to_embed) : t.indexStarting;
    default:
      return "";
  }
}

function formatClock(seconds: number): string {
  return `${Math.floor(seconds / 60)}:${String(seconds % 60).padStart(2, "0")}`;
}
