import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { Suspense } from "react";
import AiGenerate from "@/components/AiGenerate";
import AiNote from "@/components/AiNote";
import CountryList from "@/components/CountryList";
import GroupTable from "@/components/GroupTable";
import Hemicycle from "@/components/Hemicycle";
import MemberVotes from "@/components/MemberVotes";
import ResultTag from "@/components/ResultTag";
import ShareLinks from "@/components/ShareLinks";
import TallyBar from "@/components/TallyBar";
import { aiEnabled } from "@/lib/ai";
import { formatDate, percent } from "@/lib/format";
import VoteList from "@/components/VoteList";
import { getVote, NotFound, search } from "@/lib/htv";
import { fill, type Locale } from "@/lib/i18n/config";
import type { VoteDetail, VoteSummary } from "@/lib/types";
import type { Dictionary } from "@/lib/i18n/dictionaries/en";
import { getDictionary, topicLabel } from "@/lib/i18n/server";
import { cast, POSITIONS, POSITION_COLOR, seats } from "@/lib/votes";
import styles from "./vote.module.css";

type Props = { params: Promise<{ id: string }> };

async function load(id: string) {
  try {
    return await getVote(id);
  } catch (err) {
    if (err instanceof NotFound) notFound();
    throw err;
  }
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const vote = await load((await params).id);
  const t = vote.stats.total;
  return {
    title: vote.display_title,
    alternates: { canonical: `/votes/${vote.id}` },
    description: `${vote.result === "ADOPTED" ? "Adopted" : "Rejected"} on ${vote.timestamp.slice(0, 10)}: ${t.FOR} for, ${t.AGAINST} against, ${t.ABSTENTION} abstentions. See how every group, country and MEP voted.`,
  };
}


async function Related({ vote, locale, t }: { vote: VoteDetail; locale: Locale; t: Dictionary }) {
  const topic = vote.topics[0];
  if (!topic) return null;
  const { results } = await search({ topic: topic.code, size: 7 }).catch(() => ({ results: [] as VoteSummary[] }));
  const list = results.filter((v) => v.id !== vote.id).slice(0, 6);
  if (!list.length) return null;
  return (
    <section className="section">
      <div className="section-head">
        <h2>{fill(t.vote.related, { topic: topicLabel(t, topic) })}</h2>
        <Link href={`/votes?topic=${topic.code}`} className="more-link">
          {t.home.allVotes} →
        </Link>
      </div>
      <VoteList votes={list} locale={locale} t={t} />
    </section>
  );
}

function stripTags(html: string) {
  return html
    .replace(/<\/li>/g, "\n")
    .replace(/<[^>]+>/g, "")
    .split("\n")
    .map((s) => s.trim())
    .filter(Boolean);
}

export default async function VotePage({ params }: Props) {
  const { id } = await params;
  const [vote, { locale, t }] = await Promise.all([load(id), getDictionary()]);
  const total = vote.stats.total;
  const margin = total.FOR - total.AGAINST;

  return (
    <article className="container">
      <header className={styles.head}>
        <nav className={styles.crumbs}>
          <Link href="/votes">{t.nav.votes}</Link>
          <span>/</span>
          <time dateTime={vote.timestamp}>{formatDate(vote.timestamp, locale, { month: "long" })}</time>
        </nav>
        <h1>{vote.display_title}</h1>
        <div className={styles.facts}>
          <ResultTag result={vote.result} labels={t.vote} />
          {vote.amendment_subject && <span className="chip">{vote.amendment_subject}</span>}
          {vote.reference && (
            <span className={styles.fact}>
              {t.vote.reference} <b className="num">{vote.reference}</b>
            </span>
          )}
          {vote.responsible_committees.length > 0 && (
            <span className={styles.fact}>
              {t.vote.committee} <b>{vote.responsible_committees.map((c) => c.abbreviation).join(", ")}</b>
            </span>
          )}
          {vote.topics.map((topic) => (
            <Link key={topic.code} href={`/votes?topic=${topic.code}`} className="chip">
              {topicLabel(t, topic)}
            </Link>
          ))}
        </div>
        <ShareLinks path={`/votes/${vote.id}`} title={vote.display_title} t={t.share} />
      </header>

      <div className={styles.top}>
        <AiNote title={t.ai.shortVersion} note={t.ai.note} badge={t.ai.badge}>
          {aiEnabled() ? (
            <AiGenerate url={`/api/summary?kind=vote&id=${vote.id}`} labels={t.ai} />
          ) : (
            <p className="muted">{t.ai.unavailable}</p>
          )}
        </AiNote>

        <div className={styles.result}>
          <Hemicycle vote={vote} label={`${total.FOR} ${t.vote.FOR}, ${total.AGAINST} ${t.vote.AGAINST}`} />
          <ul className={styles.legend}>
            {POSITIONS.map((p) => (
              <li key={p}>
                <i style={{ background: POSITION_COLOR[p] }} />
                <span>{t.vote[p]}</span>
                <b className="num">{total[p]}</b>
              </li>
            ))}
          </ul>
          <TallyBar tally={total} castOnly height={8} />
          <dl className={styles.numbers}>
            <div>
              <dt>{t.vote.margin}</dt>
              <dd className="num">{margin > 0 ? `+${margin}` : margin}</dd>
            </div>
            <div>
              <dt>{t.vote.turnout}</dt>
              <dd className="num">{percent(cast(total), seats(total), locale)}</dd>
            </div>
          </dl>
        </div>
      </div>

      <section className="section">
        <div className="section-head">
          <h2>{t.vote.byGroup}</h2>
        </div>
        <GroupTable vote={vote} locale={locale} t={t} />
        <p className={styles.footnote}>{t.vote.byGroupNote}</p>
      </section>

      <section className="section">
        <div className="section-head">
          <h2>{t.vote.byCountry}</h2>
        </div>
        <CountryList vote={vote} t={t} />
      </section>

      <section className="section">
        <div className="section-head">
          <h2>{t.vote.everyMep}</h2>
        </div>
        <MemberVotes votes={vote.member_votes} t={t.vote} />
      </section>

      {(vote.snippet || vote.document || vote.procedure) && (
        <section className={`section ${styles.sources} ${vote.snippet ? "" : styles.single}`}>
          {vote.snippet && (
            <div>
              <h2 className="eyebrow">{t.vote.press}</h2>
              <ul className={styles.points}>
                {stripTags(vote.snippet.text).map((point) => (
                  <li key={point}>{point}</li>
                ))}
              </ul>
              <a href={vote.snippet.source_url} target="_blank" rel="noopener" className="more-link">
                europarl.europa.eu ↗
              </a>
            </div>
          )}
          <div>
            <h2 className="eyebrow">{t.vote.documents}</h2>
            <ul className={styles.docs}>
              {vote.document && (
                <li>
                  <a href={vote.document.url} target="_blank" rel="noopener">
                    {t.vote.report} <span className="num">{vote.document.reference}</span> ↗
                  </a>
                </li>
              )}
              {vote.procedure && (
                <li>
                  <a href={vote.procedure.url} target="_blank" rel="noopener">
                    {t.vote.procedure} <span className="num">{vote.procedure.reference}</span> ↗
                  </a>
                </li>
              )}
              <li>
                <a href={`https://howtheyvote.eu/votes/${vote.id}`} target="_blank" rel="noopener">
                  HowTheyVote.eu <span className="num">#{vote.id}</span> ↗
                </a>
              </li>
            </ul>
          </div>
        </section>
      )}

      <Suspense fallback={null}>
        <Related vote={vote} locale={locale} t={t} />
      </Suspense>
    </article>
  );
}
