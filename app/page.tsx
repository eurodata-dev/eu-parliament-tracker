import Link from "next/link";
import { Suspense } from "react";
import AiNote, { AiSkeleton, Paragraphs } from "@/components/AiNote";
import AskBox from "@/components/AskBox";
import FeaturedVote from "@/components/FeaturedVote";
import GroupGuide from "@/components/GroupGuide";
import HeroArc from "@/components/HeroArc";
import MatchTeaser from "@/components/MatchTeaser";
import MepWall from "@/components/MepWall";
import StartHere from "@/components/StartHere";
import TopicGrid from "@/components/TopicGrid";
import TrendFigures from "@/components/TrendFigures";
import VoteCards from "@/components/VoteCards";
import { aiEnabled, weeklyBriefing } from "@/lib/ai";
import { trends } from "@/lib/analysis";
import { formatDate, formatNumber } from "@/lib/format";
import { currentMembers, getVote, latestVotes } from "@/lib/htv";
import { fill, type Locale } from "@/lib/i18n/config";
import type { Dictionary } from "@/lib/i18n/dictionaries/en";
import { getDictionary } from "@/lib/i18n/server";
import type { Tally, VoteDetail } from "@/lib/types";
import { cast, lastSession } from "@/lib/votes";
import styles from "./home.module.css";

async function RecentChanges({ t }: { t: Dictionary }) {
  const data = await trends().catch(() => null);
  if (!data) return null;
  return (
    <section className="container section">
      <div className="section-head">
        <h2>{t.trends.title}</h2>
        <Link href="/trends" className="more-link">
          {t.trends.seeAll} →
        </Link>
      </div>
      <p className={styles.trendLede}>{t.trends.homeLede}</p>
      <TrendFigures data={data} t={t} />
    </section>
  );
}

async function Briefing({
  session,
  ids,
  locale,
  t,
}: {
  session: string;
  ids: string[];
  locale: Locale;
  t: Dictionary;
}) {
  let text: string | null = null;
  try {
    text = await weeklyBriefing(session, ids, locale);
  } catch (err) {
    console.error("briefing failed", err);
  }
  return text ? <Paragraphs text={text} /> : <p className="muted">{t.ai.unavailable}</p>;
}

// closest vote of the session (min 300 votes cast)
function closest(votes: VoteDetail[]) {
  return votes
    .filter((v) => cast(v.stats.total) > 300)
    .sort(
      (a, b) =>
        Math.abs(a.stats.total.FOR - a.stats.total.AGAINST) / cast(a.stats.total) -
        Math.abs(b.stats.total.FOR - b.stats.total.AGAINST) / cast(b.stats.total),
    )[0];
}

export default async function HomePage() {
  const { locale, t } = await getDictionary();
  const [latest, members] = await Promise.all([latestVotes(1, 30), currentMembers()]);
  const votes = latest.results;
  const session = lastSession(votes);
  const shown = votes.slice(0, 6);

  // details for the cards and for the session's closest vote
  const wanted = [...new Map([...shown, ...session.slice(0, 15)].map((v) => [v.id, v])).values()];
  const details = (await Promise.all(wanted.map((v) => getVote(v.id).catch(() => null)))).filter(
    (d): d is VoteDetail => d !== null,
  );
  const tallies: Record<string, Tally> = {};
  details.forEach((d) => (tallies[d.id] = d.stats.total));
  const sessionIds = new Set(session.map((v) => v.id));
  const featured = closest(details.filter((d) => sessionIds.has(d.id)));

  const countries = [...new Map(members.map((m) => [m.country.code, m.country])).values()]
    .map((c) => ({ code: c.code, label: c.label }))
    .sort((a, b) => a.label.localeCompare(b.label, locale));

  return (
    <>
      <section className={`container ${styles.hero}`}>
        <HeroArc className={styles.arc} />
        <h1>
          {t.home.titleA}
          <br />
          <span>{t.home.titleB}</span>
        </h1>
        <p className={styles.lede}>{t.home.lede}</p>
        <div className={styles.ask}>
          <p className="eyebrow">{t.ask.label}</p>
          <AskBox t={t.ask} />
        </div>
      </section>

      <StartHere t={t} countries={countries} />

      <MatchTeaser t={t} />

      <div className="paper">
        <section id="week" className={`container section ${styles.split}`}>
          <div>
            {session.length > 0 && (
              <AiNote title={t.home.briefing} note={t.ai.note} badge={t.ai.badge} wide>
                <p className={styles.session}>
                  {fill(t.home.briefingSession, { date: formatDate(session[0].timestamp, locale, { month: "long" }) })}
                </p>
                {aiEnabled() ? (
                  <Suspense fallback={<AiSkeleton lines={7} />}>
                    <Briefing
                      session={session[0].timestamp.slice(0, 10)}
                      ids={session.slice(0, 12).map((v) => v.id)}
                      locale={locale}
                      t={t}
                    />
                  </Suspense>
                ) : (
                  <p className="muted">{t.ai.unavailable}</p>
                )}
              </AiNote>
            )}
          </div>

          <dl className={styles.stats}>
            <div>
              <dt>{t.home.statVotes}</dt>
              <dd className="num">{formatNumber(latest.total, locale)}</dd>
            </div>
            <div>
              <dt>{t.home.statMeps}</dt>
              <dd className="num">{members.length}</dd>
            </div>
            {votes[0] && (
              <div>
                <dt>{t.home.statLast}</dt>
                <dd className="num">{formatDate(votes[0].timestamp, locale)}</dd>
              </div>
            )}
          </dl>
        </section>
      </div>

      {featured && <FeaturedVote vote={featured} locale={locale} t={t} />}

      <div className="band">
        <section className="container section">
          <div className="section-head">
            <h2>{t.home.latest}</h2>
            <Link href="/votes" className="more-link">
              {t.home.allVotes} →
            </Link>
          </div>
          <VoteCards votes={shown} tallies={tallies} locale={locale} t={t} />
        </section>
      </div>

      <MepWall members={members} countries={countries} t={t} />

      <Suspense fallback={null}>
        <TopicGrid locale={locale} t={t} />
      </Suspense>

      <div className="paper">
        <Suspense fallback={null}>
          <RecentChanges t={t} />
        </Suspense>
      </div>

      <GroupGuide members={members} t={t} />
    </>
  );
}
