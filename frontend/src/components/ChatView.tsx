// The conversations: a sidebar of past chats, messages with cited sources,
// quoting a passage of an answer.

import { useEffect, useRef, useState, type FormEvent } from "react";
import ReactMarkdown from "react-markdown";

import { api, ApiError } from "../api";
import { useConversations, type Conversation, type Message } from "../conversations";
import { errorText, useI18n } from "../i18n";
import type { Source, Turn } from "../types";

const HISTORY_TURNS = 6;
const SIDEBAR_KEY = "abb.sidebar";
const MOBILE = "(max-width: 720px)";
const MAX_QUOTE = 1500;
const CITATION_RE = /\[(S\d+)\]/g;

function initialSidebar(): boolean {
  if (window.matchMedia(MOBILE).matches) return false;
  try {
    return localStorage.getItem(SIDEBAR_KEY) !== "closed";
  } catch {
    return true;
  }
}

function plain(answer: string): string {
  return answer.replace(/\s?\[S\d+\]/g, "").trim();
}

export function ChatView() {
  const { t } = useI18n();
  const { conversations, active, select, append, start, remove } = useConversations();
  const [draft, setDraft] = useState("");
  const [quote, setQuote] = useState<string | null>(null);
  const [pendingIn, setPendingIn] = useState<string | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(initialSidebar);
  const selection = useRef<{ id: string; text: string } | null>(null);
  const bottom = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const messages = active.messages;
  const pending = pendingIn !== null;

  useEffect(() => {
    bottom.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages.length, pendingIn, active.id]);

  async function ask(question: string) {
    const text = question.trim();
    if (!text || pending) return;
    const conversationId = active.id;
    const history: Turn[] = messages
      .filter((m) => !m.error)
      .map((m) => ({ role: m.role, content: m.role === "assistant" ? plain(m.content) : m.content }))
      .slice(-HISTORY_TURNS);
    const sentQuote = quote ?? undefined;
    append(conversationId, { id: crypto.randomUUID(), role: "user", content: text, quote: sentQuote });
    setDraft("");
    setQuote(null);
    setPendingIn(conversationId);
    try {
      // One conversation = one session in the analytics.
      const response = await api.chat(text, history, conversationId, sentQuote);
      append(conversationId, { id: response.request_id, role: "assistant", content: response.answer, response });
    } catch (exc) {
      const message = errorText(t, exc instanceof ApiError ? exc.code : "generic");
      const rid = exc instanceof ApiError && exc.requestId ? ` (request ${exc.requestId})` : "";
      append(conversationId, { id: crypto.randomUUID(), role: "assistant", content: "", error: message + rid });
    } finally {
      setPendingIn(null);
      inputRef.current?.focus();
    }
  }

  function quoteMessage(message: Message) {
    const selected = selection.current?.id === message.id ? selection.current.text : "";
    setQuote((selected || plain(message.content)).slice(0, MAX_QUOTE));
    inputRef.current?.focus();
  }

  function setSidebar(next: boolean) {
    setSidebarOpen(next);
    try {
      localStorage.setItem(SIDEBAR_KEY, next ? "open" : "closed");
    } catch {
      /* not remembered — fine */
    }
  }

  /** On a phone the sidebar is a drawer over the chat — close it after a choice. */
  function closeOnMobile() {
    if (window.matchMedia(MOBILE).matches) setSidebarOpen(false);
  }

  function open(id: string) {
    select(id);
    setQuote(null);
    closeOnMobile();
  }

  function submit(event: FormEvent) {
    event.preventDefault();
    ask(draft);
  }

  return (
    <div className={`chat-layout ${sidebarOpen ? "sidebar-open" : "sidebar-closed"}`}>
      <aside className="sidebar" aria-label={t.conversations} aria-hidden={!sidebarOpen}>
        <div className="sidebar-head">
          <span className="label">{t.conversations}</span>
          <button className="icon-button" onClick={() => setSidebar(false)} aria-label={t.hideChats} title={t.hideChats}>«</button>
        </div>
        <button className="button new-chat" disabled={pending} onClick={() => { start(); closeOnMobile(); }}>
          <span aria-hidden>＋</span> {t.newChat}
        </button>
        <ul className="conversation-list">
          {conversations.filter((c) => c.messages.length || c.id === active.id).map((c) => (
            <ConversationItem key={c.id} conversation={c} active={c.id === active.id} disabled={pending}
                              onOpen={() => open(c.id)} onRemove={() => remove(c.id)} />
          ))}
        </ul>
      </aside>
      {sidebarOpen && <div className="sidebar-backdrop" onClick={() => setSidebar(false)} aria-hidden />}

      <section className="chat">
        {!sidebarOpen && (
          <button className="icon-button sidebar-show" onClick={() => setSidebar(true)} aria-label={t.showChats} title={t.showChats}>☰</button>
        )}
        <div className="chat-log" aria-live="polite">
          <div className="chat-column">
            {messages.length === 0 && (
              <div className="welcome">
                <img className="welcome-mascot" src="/assistant-mascot.png" alt="" aria-hidden />
                <p>{t.welcome}</p>
                <div className="examples">
                  {t.examples.map((example) => (
                    <button key={example} className="chip chip-button" onClick={() => ask(example)}>{example}</button>
                  ))}
                </div>
              </div>
            )}

            {messages.map((message) =>
              message.role === "user" ? (
                <div key={message.id} className="msg msg-user">
                  {message.quote && <blockquote className="msg-quote">{message.quote}</blockquote>}
                  <p>{message.content}</p>
                </div>
              ) : (
                <AssistantMessage
                  key={message.id}
                  message={message}
                  onSelect={(text) => (selection.current = { id: message.id, text })}
                  onQuote={() => quoteMessage(message)}
                />
              ),
            )}

            {pendingIn === active.id && (
              <div className="msg-assistant msg-pending">
                <img className="avatar" src="/assistant-avatar.png" alt="" aria-hidden />
                <div className="msg-body"><span className="dots" aria-hidden><i /><i /><i /></span> {t.thinking}</div>
              </div>
            )}
            <div ref={bottom} />
          </div>
        </div>

        <form className="composer" onSubmit={submit}>
          <div className="chat-column">
            {quote && (
              <div className="quote-bar">
                <span className="label">{t.quoting}</span>
                <span className="quote-text">{quote}</span>
                <button type="button" className="icon-button" aria-label={t.removeQuote} onClick={() => setQuote(null)}>×</button>
              </div>
            )}
            <div className="composer-row">
              <textarea
                ref={inputRef}
                value={draft}
                maxLength={1000}
                rows={1}
                placeholder={t.chatPlaceholder}
                onChange={(event) => setDraft(event.target.value)}
                onKeyDown={(event) => {
                  if (event.key === "Enter" && !event.shiftKey) {
                    event.preventDefault();
                    ask(draft);
                  }
                }}
              />
              <button className="button button-primary" disabled={pending || !draft.trim()}>{t.send}</button>
            </div>
            <p className="disclaimer">{t.disclaimer}</p>
          </div>
        </form>
      </section>
    </div>
  );
}

function ConversationItem({ conversation, active, disabled, onOpen, onRemove }: {
  conversation: Conversation; active: boolean; disabled: boolean; onOpen: () => void; onRemove: () => void;
}) {
  const { t } = useI18n();
  return (
    <li className={`conversation ${active ? "conversation-active" : ""}`}>
      <button className="conversation-open" disabled={disabled && !active} onClick={onOpen} title={conversation.title}>
        {conversation.title || t.newChat}
      </button>
      {conversation.messages.length > 0 && (
        <button className="icon-button" aria-label={t.deleteChat} disabled={disabled} onClick={onRemove}>×</button>
      )}
    </li>
  );
}

function AssistantMessage({ message, onSelect, onQuote }: {
  message: Message;
  onSelect: (text: string) => void;
  onQuote: () => void;
}) {
  const { t } = useI18n();
  const [open, setOpen] = useState(false);
  const [copied, setCopied] = useState(false);
  const response = message.response;

  if (message.error) {
    return (
      <div className="msg-assistant">
        <img className="avatar" src="/assistant-avatar.png" alt="" aria-hidden />
        <div className="msg-body msg-error" role="alert">{message.error}</div>
      </div>
    );
  }
  if (!response) return null;

  const byId = new Map(response.sources.map((source) => [source.id, source]));
  // The model's labels refer to all chunks it was given (S1…S10); the user sees the cited ones numbered 1, 2, 3 …
  const numberOf = new Map(response.sources.map((source, index) => [source.id, index + 1]));
  const markdown = message.content.replace(CITATION_RE, (_match, id: string) => (byId.has(id) ? `[${id}](#${id})` : ""));

  async function copy() {
    try {
      await navigator.clipboard.writeText(plain(message.content));
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1500);
    } catch {
      /* clipboard blocked — nothing to do */
    }
  }

  return (
    <div className={`msg-assistant status-${response.status}`}>
      <img className="avatar" src="/assistant-avatar.png" alt="" aria-hidden />
      <div
        className="msg-body"
        onMouseUp={() => {
          const text = window.getSelection()?.toString().trim();
          if (text) onSelect(text);
        }}
      >
        {response.status === "out_of_scope" && <span className="status-pill">{t.refused}</span>}
        {response.status === "no_information" && <span className="status-pill">{t.noInfo}</span>}

        <div className="answer">
          <ReactMarkdown
            components={{
              a: ({ href, children }) => {
                const source = href?.startsWith("#S") ? byId.get(href.slice(1)) : undefined;
                if (source) {
                  return (
                    <a className="cite" href={source.url} target="_blank" rel="noreferrer" title={source.title}>
                      {numberOf.get(source.id)}
                    </a>
                  );
                }
                return <a href={href} target="_blank" rel="noreferrer">{children}</a>;
              },
            }}
          >
            {markdown}
          </ReactMarkdown>
        </div>

        {response.sources.length > 0 && (
          <div className="sources" aria-label={t.sources}>
            {response.sources.map((source, index) => <SourceChip key={source.id} source={source} number={index + 1} />)}
          </div>
        )}

        <div className="msg-actions">
          <button className="action" onClick={onQuote} title={t.quote}><span aria-hidden>❝</span> {t.quote}</button>
          <button className="action" onClick={copy} title={t.copy}>
            <span aria-hidden>{copied ? "✓" : "⧉"}</span> {copied ? t.copied : t.copy}
          </button>
          <button className="action" onClick={() => setOpen(!open)} aria-expanded={open} title={t.details}>
            <span aria-hidden>ⓘ</span> {t.details}
          </button>
          {!response.reranked && response.status === "answered" && <span className="hint-warn">{t.noReranker}</span>}
        </div>

        {open && (
          <dl className="details">
            <dt>{t.searchedFor}</dt>
            <dd>{response.search_queries.join(" · ")}</dd>
            <dt>ms</dt>
            <dd>
              total {Math.round(response.timings.total_ms)} · search {Math.round(response.timings.retrieval_ms)} · rerank{" "}
              {Math.round(response.timings.rerank_ms)} · LLM {Math.round(response.timings.generation_ms)}
              {response.timings.rewrite_ms > 1 && ` · plan ${Math.round(response.timings.rewrite_ms)}`}
            </dd>
            <dt>model</dt>
            <dd>{response.model} · request {response.request_id}</dd>
          </dl>
        )}
      </div>
    </div>
  );
}

function SourceChip({ source, number }: { source: Source; number: number }) {
  const { t } = useI18n();
  const status = source.is_active === false ? t.ended
    : source.is_active === true ? `${t.active}${source.valid_until ? ` · ${t.validUntil} ${source.valid_until}` : ""}`
    : null;
  return (
    <a className="source" href={source.url} target="_blank" rel="noreferrer" title={source.url}>
      <span className="source-id">{number}</span>
      <span className="source-title">{source.title}</span>
      {status && <span className={`badge ${source.is_active ? "badge-active" : "badge-ended"}`}>{status}</span>}
      {source.published && <span className="source-date">{source.published}</span>}
    </a>
  );
}
