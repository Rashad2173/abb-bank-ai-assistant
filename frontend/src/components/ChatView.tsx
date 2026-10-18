// The conversation: messages, cited sources, quoting a passage of an answer.

import { useEffect, useRef, useState, type FormEvent } from "react";
import ReactMarkdown from "react-markdown";

import { api, ApiError } from "../api";
import { errorText, useI18n } from "../i18n";
import { sessionId } from "../storage";
import type { ChatResponse, Source, Turn } from "../types";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  quote?: string;
  response?: ChatResponse;
  error?: string;
}

const HISTORY_KEY = "abb.chat.v1";
const HISTORY_TURNS = 6;
const MAX_QUOTE = 1500;
const CITATION_RE = /\[(S\d+)\]/g;

function loadMessages(): Message[] {
  try {
    return JSON.parse(sessionStorage.getItem(HISTORY_KEY) ?? "[]") as Message[];
  } catch {
    return [];
  }
}

function plain(answer: string): string {
  return answer.replace(/\s?\[S\d+\]/g, "").trim();
}

export function ChatView() {
  const { t } = useI18n();
  const [messages, setMessages] = useState<Message[]>(loadMessages);
  const [draft, setDraft] = useState("");
  const [quote, setQuote] = useState<string | null>(null);
  const [pending, setPending] = useState(false);
  const selection = useRef<{ id: string; text: string } | null>(null);
  const bottom = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    try {
      sessionStorage.setItem(HISTORY_KEY, JSON.stringify(messages));
    } catch {
      /* not persisted — fine */
    }
    bottom.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, pending]);

  async function ask(question: string) {
    const text = question.trim();
    if (!text || pending) return;
    const history: Turn[] = messages
      .filter((m) => !m.error)
      .map((m) => ({ role: m.role, content: m.role === "assistant" ? plain(m.content) : m.content }))
      .slice(-HISTORY_TURNS);
    const sentQuote = quote ?? undefined;
    setMessages((all) => [...all, { id: crypto.randomUUID(), role: "user", content: text, quote: sentQuote }]);
    setDraft("");
    setQuote(null);
    setPending(true);
    try {
      const response = await api.chat(text, history, sessionId(), sentQuote);
      setMessages((all) => [...all, { id: response.request_id, role: "assistant", content: response.answer, response }]);
    } catch (exc) {
      const message = errorText(t, exc instanceof ApiError ? exc.code : "generic");
      const rid = exc instanceof ApiError && exc.requestId ? ` (request ${exc.requestId})` : "";
      setMessages((all) => [...all, { id: crypto.randomUUID(), role: "assistant", content: "", error: message + rid }]);
    } finally {
      setPending(false);
      inputRef.current?.focus();
    }
  }

  function quoteMessage(message: Message) {
    const selected = selection.current?.id === message.id ? selection.current.text : "";
    const text = (selected || plain(message.content)).slice(0, MAX_QUOTE);
    setQuote(text);
    inputRef.current?.focus();
  }

  function submit(event: FormEvent) {
    event.preventDefault();
    ask(draft);
  }

  return (
    <section className="chat">
      <div className="chat-log" aria-live="polite">
        {messages.length === 0 && (
          <div className="welcome">
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

        {pending && (
          <div className="msg msg-assistant msg-pending">
            <span className="dots" aria-hidden><i /><i /><i /></span> {t.thinking}
          </div>
        )}
        <div ref={bottom} />
      </div>

      <form className="composer" onSubmit={submit}>
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
        {messages.length > 0 && (
          <button type="button" className="link-button" onClick={() => setMessages([])}>{t.newChat}</button>
        )}
      </form>
    </section>
  );
}

function AssistantMessage({ message, onSelect, onQuote }: {
  message: Message;
  onSelect: (text: string) => void;
  onQuote: () => void;
}) {
  const { t } = useI18n();
  const [open, setOpen] = useState(false);
  const response = message.response;

  if (message.error) return <div className="msg msg-assistant msg-error" role="alert">{message.error}</div>;
  if (!response) return null;

  const byId = new Map(response.sources.map((source) => [source.id, source]));
  const markdown = message.content.replace(CITATION_RE, (_match, id: string) => (byId.has(id) ? `[${id}](#${id})` : ""));

  return (
    <div
      className={`msg msg-assistant status-${response.status}`}
      onMouseUp={() => {
        const text = window.getSelection()?.toString().trim();
        if (text) onSelect(text);
      }}
    >
      {response.status === "out_of_scope" && <div className="status-note">{t.refused}</div>}
      {response.status === "no_information" && <div className="status-note">{t.noInfo}</div>}

      <div className="answer">
        <ReactMarkdown
          components={{
            a: ({ href, children }) => {
              const source = href?.startsWith("#S") ? byId.get(href.slice(1)) : undefined;
              if (source) {
                return (
                  <a className="cite" href={source.url} target="_blank" rel="noreferrer" title={source.title}>
                    {source.id.slice(1)}
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
        <div className="sources">
          <div className="label">{t.sources}</div>
          {response.sources.map((source) => <SourceCard key={source.id} source={source} />)}
        </div>
      )}

      <div className="msg-actions">
        <button className="link-button" onClick={onQuote}>❝ {t.quote}</button>
        <button className="link-button" onClick={() => setOpen(!open)} aria-expanded={open}>{t.details}</button>
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
  );
}

function SourceCard({ source }: { source: Source }) {
  const { t } = useI18n();
  return (
    <a className="source" href={source.url} target="_blank" rel="noreferrer">
      <span className="source-id">{source.id.slice(1)}</span>
      <span className="source-body">
        <span className="source-title">{source.title}</span>
        <span className="source-meta">
          {source.is_active === false && <span className="badge badge-ended">{t.ended}</span>}
          {source.is_active === true && (
            <span className="badge badge-active">
              {t.active}{source.valid_until && ` · ${t.validUntil} ${source.valid_until}`}
            </span>
          )}
          {source.published && <span className="badge">{t.published}: {source.published}</span>}
          <span className="source-url">{source.url.replace("https://", "")}</span>
        </span>
      </span>
    </a>
  );
}
