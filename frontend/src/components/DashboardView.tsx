// Statistics of the stored questions and answers (analytics service).
//
// Chart rules: categorical colors in a fixed order per outcome (validated for
// colour-vision deficiency in light and dark mode), one axis per chart, legend
// with the numbers next to every multi-series chart, a table view for each chart.

import { useCallback, useEffect, useState, type ReactNode } from "react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { api, ApiError } from "../api";
import { errorText, useI18n } from "../i18n";
import type { Interaction, Stats } from "../types";

const PERIODS = [7, 30, 90];
// Outcome → categorical slot (fixed: a filter never repaints an outcome).
const OUTCOMES = [
  { key: "answered", color: "var(--series-1)" },
  { key: "out_of_scope", color: "var(--series-2)" },
  { key: "no_information", color: "var(--series-3)" },
  { key: "greeting", color: "var(--series-4)" },
] as const;

export function DashboardView() {
  const { t } = useI18n();
  const [days, setDays] = useState(30);
  const [stats, setStats] = useState<Stats | null>(null);
  const [recent, setRecent] = useState<Interaction[]>([]);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setError(null);
    try {
      const [s, r] = await Promise.all([api.stats(days), api.interactions(10)]);
      setStats(s);
      setRecent(r.items);
    } catch (exc) {
      setError(errorText(t, exc instanceof ApiError ? exc.code : "generic"));
    }
  }, [days, t]);

  useEffect(() => {
    load();
  }, [load]);

  if (error) return <p className="alert alert-error">{error}</p>;
  if (!stats) return <p className="muted">…</p>;

  const share = (n: number) => (stats.total ? `${Math.round((100 * n) / stats.total)}%` : "—");
  const perDay = stats.per_day.map((d) => ({
    date: d.date.slice(5),
    answered: d.answered,
    out_of_scope: d.refused,
    no_information: d.no_information,
    greeting: Math.max(0, d.total - d.answered - d.refused - d.no_information),
  }));
  const outcomeTotals = OUTCOMES.map((o) => ({ ...o, label: t.statuses[o.key], value: stats.by_status[o.key] ?? 0 }));

  return (
    <section className="dashboard">
      <div className="toolbar">
        <div className="segmented" role="group" aria-label={t.period}>
          {PERIODS.map((n) => (
            <button key={n} className={days === n ? "active" : ""} onClick={() => setDays(n)}>{t.days(n)}</button>
          ))}
        </div>
        <button className="button button-quiet" onClick={load}>{t.refresh}</button>
      </div>

      <div className="kpis">
        <Kpi label={t.totalQuestions} value={stats.total.toLocaleString()} />
        <Kpi label={t.answeredShare} value={share(stats.by_status.answered ?? 0)} />
        <Kpi label={t.refusedShare} value={share(stats.by_status.out_of_scope ?? 0)} />
        <Kpi
          label={t.latency}
          value={stats.total ? `${(stats.latency.avg_ms / 1000).toFixed(1)} s` : "—"}
          note={stats.total ? `${t.p95} ${(stats.latency.p95_ms / 1000).toFixed(1)} s` : undefined}
        />
      </div>

      {stats.total === 0 ? (
        <p className="muted empty">{t.noData}</p>
      ) : (
        <div className="grid">
          <Panel
            title={t.perDay}
            wide
            legend={<Legend items={outcomeTotals} />}
            table={
              <Table
                head={[t.date, ...outcomeTotals.map((o) => o.label)]}
                rows={perDay.filter((d) => OUTCOMES.some((o) => d[o.key] > 0)).map((d) => [d.date, ...OUTCOMES.map((o) => d[o.key])])}
              />
            }
          >
            <ResponsiveContainer width="100%" height={240}>
              <BarChart data={perDay} margin={{ top: 8, right: 8, bottom: 0, left: -16 }}>
                <CartesianGrid vertical={false} stroke="var(--grid)" />
                <XAxis dataKey="date" tickLine={false} axisLine={false} interval="preserveStartEnd" tick={{ fill: "var(--text-muted)", fontSize: 12 }} />
                <YAxis allowDecimals={false} tickLine={false} axisLine={false} tick={{ fill: "var(--text-muted)", fontSize: 12 }} />
                <Tooltip content={<ChartTooltip labels={Object.fromEntries(outcomeTotals.map((o) => [o.key, o.label]))} />} cursor={{ fill: "var(--hover)" }} />
                {OUTCOMES.map((o, index) => (
                  <Bar key={o.key} dataKey={o.key} stackId="day" fill={o.color} stroke="var(--surface)" strokeWidth={2}
                       radius={index === OUTCOMES.length - 1 ? [4, 4, 0, 0] : 0} maxBarSize={28} />
                ))}
              </BarChart>
            </ResponsiveContainer>
          </Panel>

          <Panel
            title={t.perHour}
            table={<Table head={[t.hour, t.count]} rows={stats.by_hour.map((n, h) => [`${h}:00`, n]).filter((r) => r[1] !== 0)} />}
          >
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={stats.by_hour.map((count, hour) => ({ hour: String(hour), count }))} margin={{ top: 8, right: 8, bottom: 0, left: -16 }}>
                <CartesianGrid vertical={false} stroke="var(--grid)" />
                <XAxis dataKey="hour" tickLine={false} axisLine={false} interval={2} tick={{ fill: "var(--text-muted)", fontSize: 12 }} />
                <YAxis allowDecimals={false} tickLine={false} axisLine={false} tick={{ fill: "var(--text-muted)", fontSize: 12 }} />
                <Tooltip content={<ChartTooltip labels={{ count: t.count }} suffix=":00" />} cursor={{ fill: "var(--hover)" }} />
                <Bar dataKey="count" fill="var(--series-1)" radius={[4, 4, 0, 0]} maxBarSize={18} />
              </BarChart>
            </ResponsiveContainer>
          </Panel>

          <Panel title={t.byStatus}>
            <HorizontalBars items={outcomeTotals} total={stats.total} />
          </Panel>

          <Panel title={t.byLanguage}>
            <HorizontalBars
              items={Object.entries(stats.by_language).sort((a, b) => b[1] - a[1]).map(([lang, value]) => ({ key: lang, label: lang.toUpperCase(), value, color: "var(--series-1)" }))}
              total={stats.total}
            />
          </Panel>

          <Panel title={t.refusalReasons}>
            {Object.keys(stats.by_refusal_reason).length ? (
              <HorizontalBars
                items={Object.entries(stats.by_refusal_reason).sort((a, b) => b[1] - a[1]).map(([reason, value]) => ({
                  key: reason, label: (t.reasons as Record<string, string>)[reason] ?? reason, value, color: "var(--series-2)",
                }))}
                total={Object.values(stats.by_refusal_reason).reduce((a, b) => a + b, 0)}
              />
            ) : <p className="muted">—</p>}
          </Panel>

          <Panel title={t.topSources} wide>
            <Table
              head={["", t.count]}
              rows={stats.top_sources.map((s) => [
                <a key={s.url} href={s.url} target="_blank" rel="noreferrer">{s.title}</a>, s.count,
              ])}
            />
          </Panel>

          <Panel title={t.recent} wide>
            <Table
              head={[t.time, t.question, t.result, "ms"]}
              rows={recent.map((r) => [
                new Date(r.created_at).toLocaleString(),
                r.question,
                <span key="s" className={`badge badge-${r.status}`}>{t.statuses[r.status] ?? r.status}</span>,
                Math.round(r.total_ms).toLocaleString(),
              ])}
            />
          </Panel>
        </div>
      )}
    </section>
  );
}

function Kpi({ label, value, note }: { label: string; value: string; note?: string }) {
  return (
    <div className="kpi">
      <div className="label">{label}</div>
      <div className="kpi-value">{value}</div>
      {note && <div className="muted">{note}</div>}
    </div>
  );
}

function Panel({ title, children, table, legend, wide }: {
  title: string; children: ReactNode; table?: ReactNode; legend?: ReactNode; wide?: boolean;
}) {
  const { t } = useI18n();
  const [asTable, setAsTable] = useState(false);
  return (
    <div className={`panel ${wide ? "panel-wide" : ""}`}>
      <div className="panel-head">
        <h2>{title}</h2>
        {table && (
          <button className="link-button" onClick={() => setAsTable(!asTable)}>{asTable ? t.showChart : t.showTable}</button>
        )}
      </div>
      {legend && !asTable && legend}
      {asTable ? table : children}
    </div>
  );
}

interface Item { key: string; label: string; value: number; color: string }

function Legend({ items }: { items: Item[] }) {
  return (
    <ul className="legend">
      {items.map((item) => (
        <li key={item.key}><span className="swatch" style={{ background: item.color }} />{item.label} <strong>{item.value}</strong></li>
      ))}
    </ul>
  );
}

/** Magnitude per category as labelled bars (values always written out). */
function HorizontalBars({ items, total }: { items: Item[]; total: number }) {
  const max = Math.max(1, ...items.map((i) => i.value));
  return (
    <ul className="hbars">
      {items.map((item) => (
        <li key={item.key} title={`${item.label}: ${item.value}`}>
          <span className="hbar-label">{item.label}</span>
          <span className="hbar-track">
            <span className="hbar-fill" style={{ width: `${(100 * item.value) / max}%`, background: item.color }} />
          </span>
          <span className="hbar-value">{item.value}{total ? ` · ${Math.round((100 * item.value) / total)}%` : ""}</span>
        </li>
      ))}
    </ul>
  );
}

function ChartTooltip({ active, payload, label, labels, suffix = "" }: {
  active?: boolean; payload?: { dataKey: string; value: number; color: string }[]; label?: string;
  labels: Record<string, string>; suffix?: string;
}) {
  if (!active || !payload?.length) return null;
  return (
    <div className="tooltip">
      <div className="tooltip-title">{label}{suffix}</div>
      {payload.filter((p) => p.value > 0).map((p) => (
        <div key={p.dataKey} className="tooltip-row">
          <span className="swatch" style={{ background: p.color }} />{labels[p.dataKey] ?? p.dataKey}<strong>{p.value}</strong>
        </div>
      ))}
    </div>
  );
}

function Table({ head, rows }: { head: ReactNode[]; rows: ReactNode[][] }) {
  return (
    <div className="table-wrap">
      <table>
        <thead><tr>{head.map((h, i) => <th key={i}>{h}</th>)}</tr></thead>
        <tbody>{rows.map((row, i) => <tr key={i}>{row.map((cell, j) => <td key={j}>{cell}</td>)}</tr>)}</tbody>
      </table>
    </div>
  );
}
