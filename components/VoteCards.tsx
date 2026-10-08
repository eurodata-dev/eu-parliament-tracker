import Link from "next/link";
import { formatDate } from "@/lib/format";
import type { Locale } from "@/lib/i18n/config";
import type { Dictionary } from "@/lib/i18n/dictionaries/en";
import { topicLabel } from "@/lib/i18n/server";
import type { Tally, VoteSummary } from "@/lib/types";
import { POSITION_COLOR } from "@/lib/votes";
import ResultTag from "./ResultTag";
import styles from "./VoteCards.module.css";

const R = 40;
const LENGTH = Math.PI * R;
const CAST = ["FOR", "AGAINST", "ABSTENTION"] as const;

function MiniArc({ tally }: { tally: Tally }) {
  const cast = CAST.reduce((n, p) => n + tally[p], 0) || 1;
  const lengths = CAST.map((p) => (tally[p] / cast) * LENGTH);
  const starts = lengths.map((_, i) => lengths.slice(0, i).reduce((a, b) => a + b, 0));
  const d = `M ${50 - R} 50 A ${R} ${R} 0 0 1 ${50 + R} 50`;
  return (
    <svg viewBox="0 0 100 54" className={styles.arc} aria-hidden="true">
      <path d={d} stroke="var(--line)" />
      {CAST.map((p, i) => (
        <path
          key={p}
          d={d}
          stroke={POSITION_COLOR[p]}
          strokeDasharray={`${lengths[i].toFixed(2)} ${LENGTH.toFixed(2)}`}
          strokeDashoffset={(-starts[i]).toFixed(2)}
        />
      ))}
    </svg>
  );
}

export default function VoteCards({
  votes,
  tallies,
  locale,
  t,
}: {
  votes: VoteSummary[];
  tallies: Record<string, Tally>;
  locale: Locale;
  t: Dictionary;
}) {
  return (
    <ol className={styles.grid}>
      {votes.map((vote) => {
        const tally = tallies[vote.id];
        return (
          <li key={vote.id}>
            <Link href={`/votes/${vote.id}`} className={styles.card}>
              <div className={styles.top}>
                <time dateTime={vote.timestamp}>{formatDate(vote.timestamp, locale)}</time>
                <ResultTag result={vote.result} labels={t.vote} />
              </div>
              <h3>{vote.display_title}</h3>
              {vote.topics[0] && <span className="chip">{topicLabel(t, vote.topics[0])}</span>}
              {tally && (
                <div className={styles.figures}>
                  <MiniArc tally={tally} />
                  <dl>
                    {CAST.map((p) => (
                      <div key={p}>
                        <dt>{t.vote[p]}</dt>
                        <dd className="num" style={{ color: POSITION_COLOR[p] }}>
                          {tally[p]}
                        </dd>
                      </div>
                    ))}
                  </dl>
                </div>
              )}
            </Link>
          </li>
        );
      })}
    </ol>
  );
}
