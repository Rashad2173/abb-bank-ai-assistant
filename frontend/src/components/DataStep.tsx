// The data step: what the assistant knows, and three ways to give it knowledge —
// the data already indexed, the site learned from its link, or uploaded files.

import { type ReactNode, useState } from "react";

import { useI18n } from "../i18n";
import type { CorpusInfo } from "../types";
import { ScrapeFlow } from "./ScrapeFlow";
import { UploadView } from "./UploadView";

type Source = "ready" | "link" | "file";

interface Props {
  corpus: CorpusInfo | null;
  onProcessed: () => void;
  onSkip: () => void;
}

export function DataStep({ corpus, onProcessed, onSkip }: Props) {
  const { t } = useI18n();
  const indexed = corpus?.chunks ?? 0;
  const [chosen, setChosen] = useState<Source | null>(null);
  // With data already indexed, using it is the quickest way in; without, the link is.
  const source: Source = chosen ?? (indexed > 0 ? "ready" : "link");

  const options: { id: Source; icon: string; title: string; text: string; meta: string }[] = [
    ...(indexed > 0
      ? [{ id: "ready" as const, icon: "⚡", title: t.readyTitle, text: t.readyText, meta: t.readyMeta }]
      : []),
    { id: "link", icon: "🔗", title: t.sourceLink, text: t.linkCardText, meta: t.linkCardMeta },
    { id: "file", icon: "📄", title: t.sourceFile, text: t.fileCardText, meta: t.fileCardMeta },
  ];

  return (
    <section className="data-step">
      <header className="data-head">
        <h1>{t.dataTitle}</h1>
        <p className="muted">{t.dataIntro}</p>
        <CorpusStatus corpus={corpus} />
      </header>

      <div className="source-cards" role="tablist" aria-label={t.tabData}>
        {options.map((option) => (
          <button
            type="button"
            key={option.id}
            role="tab"
            id={`source-${option.id}`}
            aria-selected={source === option.id}
            aria-controls="source-panel"
            className={`source-card ${source === option.id ? "source-card-active" : ""}`}
            onClick={() => setChosen(option.id)}
          >
            <span className="source-card-icon" aria-hidden>
              {option.icon}
            </span>
            <span className="source-card-title">{option.title}</span>
            <span className="source-card-text">{option.text}</span>
            <span className="source-card-meta">{option.meta}</span>
          </button>
        ))}
      </div>

      <div className="source-panel" id="source-panel" role="tabpanel" aria-labelledby={`source-${source}`}>
        {source === "ready" && (
          <ReadyPanel>
            <button type="button" className="button button-primary button-large" onClick={onSkip}>
              {t.readyAction} →
            </button>
          </ReadyPanel>
        )}
        {source === "link" && <ScrapeFlow corpus={corpus} onDone={onProcessed} />}
        {source === "file" && <UploadView corpus={corpus} onProcessed={onProcessed} />}
      </div>
    </section>
  );
}

function CorpusStatus({ corpus }: { corpus: CorpusInfo | null }) {
  const { t } = useI18n();
  if (!corpus) return null;
  const finished = corpus.last_job?.finished_at;
  return (
    <p className={`corpus-status ${corpus.chunks > 0 ? "corpus-ready" : "corpus-empty"}`}>
      <span className="corpus-dot" aria-hidden />
      {corpus.chunks > 0 ? t.statusReady(corpus.chunks.toLocaleString()) : t.statusEmpty}
      {corpus.chunks > 0 && finished && (
        <span className="muted"> · {t.updatedAt(new Date(finished).toLocaleDateString())}</span>
      )}
    </p>
  );
}

function ReadyPanel({ children }: { children: ReactNode }) {
  const { t } = useI18n();
  return (
    <div className="card ready-panel">
      <div>
        <h2>{t.readyTitle}</h2>
        <p className="muted">{t.readyPanelText}</p>
      </div>
      <ul className="ready-facts">
        {t.readyFacts.map((fact) => (
          <li key={fact}>{fact}</li>
        ))}
      </ul>
      {children}
    </div>
  );
}
