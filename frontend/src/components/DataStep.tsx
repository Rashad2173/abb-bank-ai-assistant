// The data step: learn the site from its link, or upload a file of scraped data.

import { useState } from "react";

import { useI18n } from "../i18n";
import type { CorpusInfo } from "../types";
import { ScrapeFlow } from "./ScrapeFlow";
import { UploadView } from "./UploadView";

type Source = "link" | "file";

interface Props {
  corpus: CorpusInfo | null;
  onProcessed: () => void;
  onSkip: () => void;
}

export function DataStep({ corpus, onProcessed, onSkip }: Props) {
  const { t } = useI18n();
  const [source, setSource] = useState<Source>("link");
  return (
    <section className="data-view">
      <div className="segmented source-switch" role="tablist" aria-label={t.tabData}>
        <button
          type="button"
          role="tab"
          aria-selected={source === "link"}
          className={source === "link" ? "active" : ""}
          onClick={() => setSource("link")}
        >
          🔗 {t.sourceLink}
        </button>
        <button
          type="button"
          role="tab"
          aria-selected={source === "file"}
          className={source === "file" ? "active" : ""}
          onClick={() => setSource("file")}
        >
          📄 {t.sourceFile}
        </button>
      </div>
      {source === "link" ? (
        <ScrapeFlow corpus={corpus} onDone={onProcessed} />
      ) : (
        <UploadView corpus={corpus} onProcessed={onProcessed} onSkip={onSkip} />
      )}
      {source === "link" && corpus && corpus.chunks > 0 && (
        <div className="skip">
          <span className="muted">{t.skipHint}</span>
          <button type="button" className="button" onClick={onSkip}>
            {t.skip} ({corpus.chunks.toLocaleString()} {t.chunks})
          </button>
        </div>
      )}
    </section>
  );
}
