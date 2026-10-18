import { lazy, Suspense, useCallback, useEffect, useMemo, useState } from "react";

import { api } from "./api";
import { ChatView } from "./components/ChatView";
import { UploadView } from "./components/UploadView";
import { I18nContext, LANGS, TEXTS, type Lang } from "./i18n";
import { loadMeta } from "./storage";
import type { CorpusInfo } from "./types";

// The dashboard (with the chart library) is loaded only when it is opened.
const DashboardView = lazy(() => import("./components/DashboardView").then((m) => ({ default: m.DashboardView })));

type Tab = "data" | "chat" | "dashboard";
const LANG_KEY = "abb.lang";

function initialLang(): Lang {
  try {
    const saved = localStorage.getItem(LANG_KEY) as Lang | null;
    return saved && LANGS.includes(saved) ? saved : "az";
  } catch {
    return "az";
  }
}

export default function App() {
  const [lang, setLang] = useState<Lang>(initialLang);
  const [corpus, setCorpus] = useState<CorpusInfo | null>(null);
  const [hasData, setHasData] = useState(() => loadMeta() !== null);
  const [tab, setTab] = useState<Tab>("data");
  const i18n = useMemo(() => ({ lang, t: TEXTS[lang] }), [lang]);
  const { t } = i18n;

  const refreshCorpus = useCallback(async () => {
    try {
      setCorpus(await api.corpus());
    } catch {
      setCorpus(null);
    }
  }, []);

  useEffect(() => {
    refreshCorpus();
  }, [refreshCorpus]);

  // Chat opens only after data was uploaded and processed (the brief's flow).
  const chatReady = hasData && (corpus?.chunks ?? 0) > 0;
  useEffect(() => {
    if (chatReady) setTab((current) => (current === "data" ? "chat" : current));
  }, [chatReady]);

  const changeLang = (next: Lang) => {
    setLang(next);
    try {
      localStorage.setItem(LANG_KEY, next);
    } catch {
      /* not persisted — fine */
    }
    document.documentElement.lang = next;
  };

  return (
    <I18nContext.Provider value={i18n}>
      <div className="app">
        <header className="topbar">
          <div className="brand">
            <span className="brand-mark" aria-hidden>ABB</span>
            <span className="brand-name">{t.appTitle}</span>
          </div>
          <nav className="tabs" role="tablist">
            {(["data", "chat", "dashboard"] as Tab[]).map((name) => (
              <button
                key={name}
                role="tab"
                aria-selected={tab === name}
                className={`tab ${tab === name ? "tab-active" : ""}`}
                disabled={name === "chat" && !chatReady}
                title={name === "chat" && !chatReady ? t.needData : undefined}
                onClick={() => setTab(name)}
              >
                {name === "data" ? t.tabData : name === "chat" ? t.tabChat : t.tabDashboard}
              </button>
            ))}
          </nav>
          <div className="lang-switch" role="group" aria-label="Language">
            {LANGS.map((code) => (
              <button key={code} className={`lang ${lang === code ? "lang-active" : ""}`} onClick={() => changeLang(code)}>
                {code.toUpperCase()}
              </button>
            ))}
          </div>
        </header>

        <main className="content">
          {tab === "data" && (
            <UploadView
              corpus={corpus}
              onStored={(stored) => setHasData(stored)}
              onProcessed={async () => {
                setHasData(true);
                await refreshCorpus();
                setTab("chat");
              }}
            />
          )}
          {tab === "chat" && chatReady && <ChatView />}
          {tab === "dashboard" && (
            <Suspense fallback={<p className="muted">…</p>}>
              <DashboardView />
            </Suspense>
          )}
        </main>
      </div>
    </I18nContext.Provider>
  );
}
