import type { Metadata } from "next";
import Link from "next/link";
import { Suspense } from "react";
import Pagination from "@/components/Pagination";
import TopicOverview, { TopicOverviewSkeleton } from "@/components/TopicOverview";
import VoteFilters from "@/components/VoteFilters";
import VoteList from "@/components/VoteList";
import { formatNumber } from "@/lib/format";
import { listVotes, TOPICS } from "@/lib/htv";
import { fill } from "@/lib/i18n/config";
import { getDictionary } from "@/lib/i18n/server";
import styles from "../listing.module.css";

export const metadata: Metadata = {
  title: "All European Parliament votes since 2019",
  description:
    "Search every roll-call vote of the European Parliament since July 2019 by subject, topic and date, with results by group, country and MEP.",
  alternates: { canonical: "/votes" },
};

type Params = { q?: string; topic?: string; from?: string; to?: string; page?: string };
type Props = { searchParams: Promise<Params> };

const DATE = /^\d{4}-\d{2}-\d{2}$/;

export default async function VotesPage({ searchParams }: Props) {
  const raw = await searchParams;
  const q = (raw.q ?? "").trim().slice(0, 120);
  const topic = (TOPICS as readonly string[]).includes(raw.topic ?? "") ? raw.topic! : "";
  const from = DATE.test(raw.from ?? "") ? raw.from! : "";
  const to = DATE.test(raw.to ?? "") ? raw.to! : "";
  const page = Math.max(1, Math.min(500, Number(raw.page) || 1));
  const { locale, t } = await getDictionary();

  const data = await listVotes({ q, topic, from, to, page });

  const href = (n: number) => {
    const params = new URLSearchParams();
    if (q) params.set("q", q);
    if (topic) params.set("topic", topic);
    if (from) params.set("from", from);
    if (to) params.set("to", to);
    if (n > 1) params.set("page", String(n));
    const s = params.toString();
    return s ? `/votes?${s}` : "/votes";
  };

  const topics = TOPICS.map((code) => ({ code, label: t.topics[code] })).sort((a, b) =>
    a.label.localeCompare(b.label, locale),
  );
  const filtered = Boolean(q || topic || from || to);
  const label = [q && `“${q}”`, topic && t.topics[topic as keyof typeof t.topics]].filter(Boolean).join(" · ");

  return (
    <div className="container">
      <header className={styles.head}>
        <h1>{t.votes.title}</h1>
        <p>{t.votes.lede}</p>
        <VoteFilters q={q} topic={topic} from={from} to={to} topics={topics} t={t.votes} />
        {!filtered && (
          <div className={styles.examples}>
            <span>{t.votes.popular}</span>
            {t.votes.examples.map((ex) => (
              <Link key={ex} href={`/votes?q=${encodeURIComponent(ex)}`}>
                {ex}
              </Link>
            ))}
          </div>
        )}
        {filtered && (
          <p className={styles.count}>
            {fill(t.votes.results, { n: data.total >= 500 ? "500+" : formatNumber(data.total, locale), q: label || "…" })}
          </p>
        )}
      </header>

      {(q || topic) && page === 1 && (
        <Suspense key={`${q}|${topic}`} fallback={<TopicOverviewSkeleton />}>
          <TopicOverview q={q} topic={topic} locale={locale} t={t} />
        </Suspense>
      )}

      {data.results.length ? (
        <VoteList votes={data.results} locale={locale} t={t} />
      ) : (
        <p className={styles.empty}>{t.votes.none}</p>
      )}

      <Pagination page={page} hasPrev={data.has_prev} hasNext={data.has_next} href={href} labels={t.votes} />
    </div>
  );
}
