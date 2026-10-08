import type { Metadata } from "next";
import Link from "next/link";
import { Suspense } from "react";
import AiGenerate from "@/components/AiGenerate";
import AiNote, { AiSkeleton } from "@/components/AiNote";
import TrendFigures from "@/components/TrendFigures";
import { aiEnabled } from "@/lib/ai";
import { trends } from "@/lib/analysis";
import { formatDate } from "@/lib/format";
import { groupColor } from "@/lib/groups";
import { fill, type Locale } from "@/lib/i18n/config";
import type { Dictionary } from "@/lib/i18n/dictionaries/en";
import { getDictionary, topicLabel } from "@/lib/i18n/server";
import styles from "./trends.module.css";

export const metadata: Metadata = {
  title: "Recent political changes in the European Parliament",
  description:
    "How each political group in the European Parliament voted over the last 30 days compared with the months before: shifts, topics and polarisation.",
  alternates: { canonical: "/trends" },
};

export const maxDuration = 60;

function signed(n: number) {
  if (Math.abs(n) < 0.05) return "0.0";
  return `${n > 0 ? "+" : "−"}${Math.abs(n).toFixed(1)}`;
}

function Shares({ s }: { s: { FOR: number; AGAINST: number; ABSTENTION: number } }) {
  return (
    <span className={styles.bar}>
      <span style={{ width: `${s.FOR}%`, background: "var(--for)" }} />
      <span style={{ width: `${s.AGAINST}%`, background: "var(--against)" }} />
      <span style={{ width: `${s.ABSTENTION}%`, background: "var(--abstain)" }} />
    </span>
  );
}


async function Content({ locale, t }: { locale: Locale; t: Dictionary }) {
  const data = await trends().catch((err) => {
    console.error("trends failed", err);
    return null;
  });
  if (!data) return <p className="muted">{t.trends.unavailable}</p>;

  const period = (a: string, b: string) => `${formatDate(a, locale)} – ${formatDate(b, locale)}`;

  return (
    <>
      <p className={styles.periods}>
        <span>
          {t.trends.after}: <b>{period(data.recentFrom, data.recentTo)}</b> ·{" "}
          <span className="num">{fill(t.trends.votes, { n: data.recentCount })}</span>
        </span>
        <span>
          {t.trends.before}: <b>{period(data.baselineFrom, data.baselineTo)}</b> ·{" "}
          <span className="num">{fill(t.trends.votes, { n: data.baselineCount })}</span>
        </span>
      </p>

      <TrendFigures data={data} t={t} />

      <div className={styles.ai}>
        <AiNote title={t.trends.aiTitle} note={t.ai.note} badge={t.ai.badge}>
          {aiEnabled() ? (
            <AiGenerate url={`/api/summary?kind=trends&id=${data.recentTo}`} labels={t.ai} lines={6} />
          ) : (
            <p className="muted">{t.ai.unavailable}</p>
          )}
        </AiNote>
      </div>

      <section className="section">
        <div className="section-head">
          <h2>{t.trends.groupsTitle}</h2>
        </div>
        <div className={styles.table} role="table">
          <div className={`${styles.tr} ${styles.th}`} role="row">
            <span role="columnheader">{t.vote.group}</span>
            <span role="columnheader">{t.trends.before}</span>
            <span role="columnheader">{t.trends.after}</span>
            <span role="columnheader" className={styles.n}>{t.vote.FOR}</span>
            <span role="columnheader" className={styles.n}>{t.vote.AGAINST}</span>
            <span role="columnheader" className={styles.n}>{t.vote.ABSTENTION}</span>
          </div>
          {data.groups.map((g) => (
            <div className={styles.tr} role="row" key={g.group.code}>
              <span role="cell" className={styles.name} title={g.group.label}>
                <i style={{ background: groupColor(g.group.code) }} />
                {g.group.short_label}
              </span>
              <span role="cell">
                <Shares s={g.before} />
                <small className="num">
                  {g.before.FOR.toFixed(0)} / {g.before.AGAINST.toFixed(0)} / {g.before.ABSTENTION.toFixed(0)}
                </small>
              </span>
              <span role="cell">
                <Shares s={g.after} />
                <small className="num">
                  {g.after.FOR.toFixed(0)} / {g.after.AGAINST.toFixed(0)} / {g.after.ABSTENTION.toFixed(0)}
                </small>
              </span>
              {(["FOR", "AGAINST", "ABSTENTION"] as const).map((p) => (
                <span
                  key={p}
                  role="cell"
                  className={`${styles.n} num`}
                  data-strong={Math.abs(g.delta[p]) >= 5 || undefined}
                >
                  {signed(g.delta[p])}
                </span>
              ))}
            </div>
          ))}
        </div>
        <p className={styles.footnote}>{t.trends.groupsNote}</p>
      </section>

      {data.topics.length > 0 && (
        <section className="section">
          <div className="section-head">
            <h2>{t.trends.topicsTitle}</h2>
          </div>
          <ul className={styles.topics}>
            {data.topics.map((tp) => (
              <li key={tp.code}>
                <Link href={`/votes?topic=${tp.code}`}>{topicLabel(t, tp)}</Link>
                <span className="num muted">{tp.before.toFixed(0)}%</span>
                <span className={styles.arrow}>→</span>
                <span className="num">{tp.after.toFixed(0)}%</span>
                <span className="num" data-up={tp.delta > 0 || undefined} data-down={tp.delta < 0 || undefined}>
                  {signed(tp.delta)}
                </span>
              </li>
            ))}
          </ul>
          <p className={styles.footnote}>{t.trends.topicsNote}</p>
        </section>
      )}

      <section className={`section ${styles.method}`}>
        <h2 className="eyebrow">{t.trends.methodTitle}</h2>
        <p>{t.trends.method}</p>
      </section>
    </>
  );
}

export default async function TrendsPage() {
  const { locale, t } = await getDictionary();
  return (
    <div className="container">
      <header className={styles.head}>
        <h1>{t.trends.title}</h1>
        <p>{t.trends.lede}</p>
      </header>
      <Suspense fallback={<AiSkeleton lines={8} />}>
        <Content locale={locale} t={t} />
      </Suspense>
    </div>
  );
}
