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
const LANGUAGE_NAMES: Record<Lang, string> = { az: "AZ · Azərbaycanca", en: "EN · English", ru: "RU · Русский" };
const THEME_KEY = "abb.theme";
type Theme = "light" | "dark";
const STARTED_KEY = "abb.started";

/** Has this browser been through the data step (processed an upload or chose the indexed data)? */
function hasStarted(): boolean {
  try {
    return localStorage.getItem(STARTED_KEY) === "1" || loadMeta() !== null;
  } catch {
    return false;
  }
}

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
  const [theme, setTheme] = useState<Theme>(() => (document.documentElement.dataset.theme as Theme) ?? "light");
  const [corpus, setCorpus] = useState<CorpusInfo | null>(null);
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

  // The brief's flow: upload → processing → chat. A first visit therefore opens on the
  // data step; the chat unlocks once the search index holds processed data. Visitors
  // without a file can continue with the data that is already indexed, and returning
  // visitors open straight on the chat.
  const chatReady = (corpus?.chunks ?? 0) > 0;
  useEffect(() => {
    if (chatReady && hasStarted()) setTab((current) => (current === "data" ? "chat" : current));
  }, [chatReady]);

  const startChat = () => {
    try {
      localStorage.setItem(STARTED_KEY, "1");
    } catch {
      /* not remembered — fine */
    }
    setTab("chat");
  };

  const toggleTheme = () => {
    const next: Theme = theme === "dark" ? "light" : "dark";
    setTheme(next);
    document.documentElement.dataset.theme = next;
    try {
      localStorage.setItem(THEME_KEY, next);
    } catch {
      /* not remembered — fine */
    }
  };

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
            <img className="brand-logo" src="/abb-logo.png" alt="ABB — Azərbaycan Beynəlxalq Bankı" height={30} />
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
          <button className="theme-toggle" onClick={toggleTheme} aria-label={theme === "dark" ? t.themeLight : t.themeDark}
                  title={theme === "dark" ? t.themeLight : t.themeDark}>
            {theme === "dark" ? "☀" : "☾"}
          </button>
          <select className="lang-select" value={lang} aria-label="Language / Dil / Язык"
                  onChange={(event) => changeLang(event.target.value as Lang)}>
            {LANGS.map((code) => (
              <option key={code} value={code}>{LANGUAGE_NAMES[code]}</option>
            ))}
          </select>
        </header>

        <main className="content">
          {tab === "data" && (
            <UploadView
              corpus={corpus}
              onProcessed={async () => {
                await refreshCorpus();
                startChat();
              }}
              onSkip={startChat}
            />
          )}
          {tab === "chat" && chatReady && <ChatView />}
          {tab === "dashboard" && (
            <Suspense fallback={<p className="muted">…</p>}>
              <DashboardView />
            </Suspense>
          )}
        </main>
        <footer className="footer">{t.footer}</footer>
      </div>
    </I18nContext.Provider>
  );
}
