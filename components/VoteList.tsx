import Link from "next/link";
import { formatDate } from "@/lib/format";
import type { Locale } from "@/lib/i18n/config";
import type { Dictionary } from "@/lib/i18n/dictionaries/en";
import { topicLabel } from "@/lib/i18n/server";
import type { Position, Tally, VoteSummary } from "@/lib/types";
import ResultTag from "./ResultTag";
import TallyBar from "./TallyBar";
import styles from "./votes.module.css";

type Row = VoteSummary & { position?: Position };

export default function VoteList({
  votes,
  locale,
  t,
  showPosition = false,
  tallies,
}: {
  votes: Row[];
  locale: Locale;
  t: Dictionary;
  showPosition?: boolean;
  tallies?: Record<string, Tally>;
}) {
  return (
    <ol className={styles.list}>
      {votes.map((vote) => (
        <li key={vote.id}>
          <Link href={`/votes/${vote.id}`} className={styles.row}>
            <time className={styles.date} dateTime={vote.timestamp}>
              {formatDate(vote.timestamp, locale)}
            </time>
            <div className={styles.body}>
              <h3 className={styles.title}>{vote.display_title}</h3>
              <div className={styles.meta}>
                {vote.amendment_subject && <span className="chip">{vote.amendment_subject}</span>}
                {vote.topics.slice(0, 3).map((topic) => (
                  <span key={topic.code} className="chip">
                    {topicLabel(t, topic)}
                  </span>
                ))}
              </div>
            </div>
            <div className={styles.side}>
              {showPosition && vote.position ? (
                <span className={styles.position} data-position={vote.position}>
                  {t.vote[vote.position]}
                </span>
              ) : (
                <ResultTag result={vote.result} labels={t.vote} />
              )}
              {tallies?.[vote.id] && (
                <div className={styles.mini}>
                  <TallyBar tally={tallies[vote.id]} castOnly height={4} />
                  <span className="num">
                    <b style={{ color: "var(--for)" }}>{tallies[vote.id].FOR}</b>
                    {" · "}
                    <b style={{ color: "var(--against)" }}>{tallies[vote.id].AGAINST}</b>
                    {" · "}
                    <b style={{ color: "var(--abstain)" }}>{tallies[vote.id].ABSTENTION}</b>
                  </span>
                </div>
              )}
            </div>
          </Link>
        </li>
      ))}
    </ol>
  );
}
